import json
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from connectors import CONNECTOR_REGISTRY
from connectors.base_connector import ConnectorResult
from config import (
    get_firm_config,
    get_routing_rules_for_task,
    get_firm_risk_rules,
    get_program_scaling_rules,
    get_account_breach_rules,
    get_unified_program_metadata,
)
from risk_engine import RiskCheckResult, evaluate_task_risk
from program_engine import compute_contract_size_for_program, SizingResult
from account_engine import AccountBreachResult, evaluate_account_breach, check_order_enforcement


class ExecutionRouter:
    """
    Background worker that pulls pending execution tasks from the database
    and routes them to external prop firm APIs.
    
    Stage 13B (Execution Queue) runs in DRY-RUN mode by default:
    - It does NOT call any external APIs yet.
    - It marks tasks as SUCCESS with a simulated result.
    - This provides durable plumbing and logging without affecting live trading.
    """
    
    def __init__(
        self,
        poll_interval: float = 2.0,
        batch_size: int = 20,
        dry_run: bool = True,
        logger: Optional[logging.Logger] = None,
        account_state_manager=None,
    ) -> None:
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.dry_run = dry_run
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.logger = logger or logging.getLogger(__name__)
        self.account_state_manager = account_state_manager
    
    def start(self) -> None:
        """Start the background worker thread (idempotent)."""
        if self._thread is not None and self._thread.is_alive():
            self.logger.info("ExecutionRouter worker already running")
            return
        
        self._thread = threading.Thread(
            target=self._run_loop,
            name="ExecutionRouterWorker",
            daemon=True,
        )
        self._thread.start()
        self.logger.info("ExecutionRouter worker started (dry_run=%s)", self.dry_run)
    
    def stop(self) -> None:
        """Signal the worker loop to stop."""
        self._stop_event.set()
    
    def _get_connection(self):
        """
        Obtain a fresh database connection using DATABASE_URL.
        We intentionally do not reuse the main app connection to
        keep the router resilient to main-thread transaction state.
        """
        dsn = os.environ.get("DATABASE_URL")
        if not dsn:
            raise RuntimeError("ExecutionRouter: DATABASE_URL is not configured")
        return psycopg2.connect(dsn, cursor_factory=RealDictCursor)
    
    def _run_loop(self) -> None:
        """Main polling loop."""
        while not self._stop_event.is_set():
            try:
                processed = self._process_batch()
                # Back off a bit if nothing was processed
                if processed == 0:
                    time.sleep(self.poll_interval)
            except Exception as e:
                # Never crash the process; just log and retry later
                self.logger.error("ExecutionRouter loop error: %s", e, exc_info=True)
                time.sleep(self.poll_interval * 2)
    
    def _process_batch(self) -> int:
        """
        Fetch up to batch_size pending tasks, lock them, and process them.
        Returns the number of tasks processed in this batch.
        """
        conn = None
        cur = None
        processed = 0
        
        try:
            conn = self._get_connection()
            conn.autocommit = False
            cur = conn.cursor()
            
            # Select a batch of PENDING tasks with row-level locking
            cur.execute(
                """
                SELECT id, trade_id, event_type, payload, attempts
                FROM execution_tasks
                WHERE status = 'PENDING'
                ORDER BY created_at
                FOR UPDATE SKIP LOCKED
                LIMIT %s
                """,
                (self.batch_size,),
            )
            rows = cur.fetchall()
            if not rows:
                conn.commit()
                return 0
            
            for row in rows:
                task_id = row["id"]
                trade_id = row.get("trade_id")
                event_type = row.get("event_type")
                payload = row.get("payload") or {}
                attempts = row.get("attempts") or 0
                
                status = "SUCCESS"
                error_message = None
                result: Dict[str, Any] = {}
                
                try:
                    result = self._handle_task(task_id, trade_id, event_type, payload)
                except Exception as task_err:
                    status = "FAILED"
                    error_message = str(task_err)
                    self.logger.error(
                        "ExecutionRouter task %s for trade %s failed: %s",
                        task_id,
                        trade_id,
                        error_message,
                        exc_info=True,
                    )
                
                # Update task status
                cur.execute(
                    """
                    UPDATE execution_tasks
                    SET status = %s,
                        attempts = %s,
                        last_error = %s,
                        last_attempt_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, attempts + 1, error_message, task_id),
                )
                
                # Log the attempt
                cur.execute(
                    """
                    INSERT INTO execution_logs (
                        task_id,
                        status,
                        response_code,
                        response_body,
                        created_at
                    ) VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (
                        task_id,
                        status,
                        result.get("response_code"),
                        json.dumps(result) if result else None,
                    ),
                )
                
                processed += 1
            
            conn.commit()
            return processed
        
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cur is not None:
                try:
                    cur.close()
                except Exception:
                    pass
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def _build_order_payload(self, task_payload: Dict[str, Any], routing_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Build normalized order payload for connector."""
        try:
            direction = task_payload.get("direction", "LONG")
            side = "BUY" if direction == "LONG" else "SELL"
            
            normalized_order = {
                "symbol": routing_meta.get("symbol", "NQ"),
                "side": side,
                "quantity": routing_meta.get("quantity", 1),
                "order_type": "MARKET",
                "session": routing_meta.get("session"),
                "bias": routing_meta.get("bias"),
                "risk_percent": routing_meta.get("risk_percent"),
                "program_ids": routing_meta.get("program_ids", [])
            }
            
            if task_payload.get("entry_price"):
                normalized_order["entry_price"] = float(task_payload["entry_price"])
            if task_payload.get("stop_loss"):
                normalized_order["stop_loss"] = float(task_payload["stop_loss"])
            
            return {k: v for k, v in normalized_order.items() if v is not None}
        
        except Exception as e:
            self.logger.error("Error building order payload: %s", e)
            return {}
    
    def _run_risk_checks_for_task(
        self,
        task_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Stage 13D: Run per-firm risk checks for a single execution task.
        
        Returns a list of dicts suitable for logging in execution_logs.
        """
        firm_codes, routing_meta = get_routing_rules_for_task(task_payload)
        results: List[Dict[str, Any]] = []
        
        if not firm_codes:
            return results
        
        for firm_code in firm_codes:
            firm_config = get_firm_config(firm_code)
            firm_risk_rules = get_firm_risk_rules(firm_code)
            
            try:
                rc: RiskCheckResult = evaluate_task_risk(
                    firm_code=firm_code,
                    task_payload=task_payload,
                    routing_meta=routing_meta,
                    firm_config=firm_config,
                    firm_risk_rules=firm_risk_rules,
                )
                results.append({
                    "firm_code": rc.firm_code,
                    "status": rc.status,
                    "rule": rc.rule,
                    "reason": rc.reason,
                    "details": rc.details,
                })
            except Exception as exc:
                results.append({
                    "firm_code": firm_code,
                    "status": "REJECTED",
                    "rule": "EXCEPTION",
                    "reason": f"Risk evaluation exception for firm {firm_code}: {exc}",
                    "details": None,
                })
        
        return results
    
    def _get_program_by_id_safe(self, program_id: int) -> Dict[str, Any]:
        """Stage 13E: Safely retrieve program data by ID.
        
        Returns program dict with at least 'id' and 'account_size' fields.
        If lookup fails, returns minimal dict with None account_size.
        """
        try:
            # Try to get program from prop_registry if available
            if hasattr(self, 'prop_registry') and self.prop_registry:
                programs = self.prop_registry.list_programs()
                for prog in programs:
                    if prog.get('id') == program_id:
                        return prog
            
            # Fallback: try direct database query
            if hasattr(self, 'db_url') and self.db_url:
                conn = psycopg2.connect(self.db_url)
                try:
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    cur.execute(
                        """
                        SELECT id, firm_id, name, account_size, currency,
                               max_daily_loss, max_total_loss, profit_target
                        FROM prop_programs
                        WHERE id = %s
                        """,
                        (program_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return dict(row)
                finally:
                    conn.close()
        except Exception as e:
            self.logger.warning("Failed to retrieve program %d: %s", program_id, e)
        
        # Return minimal fallback
        return {"id": program_id, "account_size": None}
    
    def _run_program_sizing_for_task(
        self,
        task_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Stage 13E: run program-aware auto-sizing for each firm/program in task.
        
        Returns list of sizing result dicts.
        """
        firm_codes, routing_meta = get_routing_rules_for_task(task_payload)
        results = []
        
        program_ids = routing_meta.get("program_ids") or []
        user_quantity = routing_meta.get("quantity")
        risk_percent = routing_meta.get("risk_percent")
        
        for firm_code in firm_codes:
            for pid in program_ids:
                try:
                    program = self._get_program_by_id_safe(pid)
                except Exception:
                    program = {"id": pid, "account_size": None}
                
                scaling_rules = get_program_scaling_rules(firm_code, pid)
                
                sr: SizingResult = compute_contract_size_for_program(
                    firm_code=firm_code,
                    program=program,
                    scaling_rules=scaling_rules,
                    entry_price=task_payload.get("entry_price"),
                    stop_loss=task_payload.get("stop_loss"),
                    user_quantity=user_quantity,
                    risk_percent=risk_percent,
                )
                
                results.append({
                    "firm_code": firm_code,
                    "program_id": pid,
                    "status": sr.status,
                    "rule": sr.rule,
                    "reason": sr.reason,
                    "computed_quantity": sr.computed_quantity,
                    "details": sr.details,
                })
        
        return results
    
    def _get_account_metrics_for_program(
        self,
        firm_code: str,
        program_id: int,
    ) -> Dict[str, Any]:
        """
        Stage 13G:
        Retrieve account metrics for a firm/program using AccountStateManager
        with safe environment fallback.
        
        This method must never raise. If no state is available, it returns {}.
        """
        metrics: Dict[str, Any] = {}
        try:
            if self.account_state_manager is not None:
                # 1) Try in-memory state first
                metrics = self.account_state_manager.get_account_state(firm_code, program_id) or {}
                # 2) If nothing in memory, attempt env-based load
                if not metrics:
                    metrics = self.account_state_manager.load_from_env(firm_code, program_id) or {}
        except Exception:
            # Any error must degrade gracefully to {} without crashing router.
            metrics = {}
        return metrics
    
    def _run_account_breach_checks_for_task(
        self,
        task_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Stage 13F:
        Run account-level breach checks for each firm/program combination
        associated with this task.
        
        Returns a list of dicts suitable for logging and filtering.
        """
        firm_codes, routing_meta = get_routing_rules_for_task(task_payload)
        program_ids = routing_meta.get("program_ids") or []
        results: List[Dict[str, Any]] = []
        
        if not firm_codes or not program_ids:
            return results
        
        for firm_code in firm_codes:
            for pid in program_ids:
                try:
                    metrics = self._get_account_metrics_for_program(firm_code, pid)
                    breach_rules = get_account_breach_rules(firm_code, pid)
                    
                    abr: AccountBreachResult = evaluate_account_breach(
                        firm_code=firm_code,
                        program_id=pid,
                        account_metrics=metrics or {},
                        breach_rules=breach_rules,
                    )
                    
                    results.append({
                        "firm_code": abr.firm_code,
                        "program_id": abr.program_id,
                        "status": abr.status,
                        "rule": abr.rule,
                        "reason": abr.reason,
                        "details": abr.details,
                    })
                except Exception as exc:
                    results.append({
                        "firm_code": firm_code,
                        "program_id": pid,
                        "status": "APPROVED",
                        "rule": "EXCEPTION",
                        "reason": f"Account breach evaluation exception for firm {firm_code}, program {pid}: {exc}",
                        "details": None,
                    })
        
        return results
    
    def _execute_connectors_for_task(
        self,
        task_id: int,
        task_payload: Dict[str, Any],
        allowed_firm_codes: Optional[List[str]] = None,
        program_sizing: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute connectors for a task."""
        try:
            firm_codes, routing_meta = get_routing_rules_for_task(task_payload)
            
            if not firm_codes:
                return [{
                    "firm_code": "NONE",
                    "status": "SKIPPED",
                    "reason": "NO_FIRMS_CONFIGURED"
                }]
            
            # Stage 13D: Filter by allowed_firm_codes
            if allowed_firm_codes is not None:
                allowed_set = set(code.upper() for code in allowed_firm_codes if code)
            else:
                allowed_set = None
            
            if self.dry_run:
                return [{
                    "firm_code": firm_code,
                    "status": "SKIPPED",
                    "reason": "GLOBAL_DRY_RUN_ENABLED"
                } for firm_code in firm_codes]
            
            results = []
            
            for firm_code in firm_codes:
                try:
                    # Stage 13D: skip connectors for firms rejected by risk engine
                    if allowed_set is not None and firm_code.upper() not in allowed_set:
                        results.append({
                            "firm_code": firm_code,
                            "status": "SKIPPED",
                            "reason": "RISK_REJECTED",
                            "external_order_id": None,
                            "normalized_order": None,
                        })
                        continue
                    
                    # Stage 13E: Override quantity from program sizing if available
                    firm_routing_meta = routing_meta.copy()
                    if program_sizing:
                        approved_sizing = [
                            r for r in program_sizing
                            if r["firm_code"] == firm_code and r["status"] == "APPROVED"
                        ]
                        if approved_sizing and approved_sizing[0].get("computed_quantity") is not None:
                            firm_routing_meta["quantity"] = approved_sizing[0]["computed_quantity"]
                    
                    normalized_order = self._build_order_payload(task_payload, firm_routing_meta)
                    if not normalized_order:
                        results.append({
                            "firm_code": firm_code,
                            "status": "SKIPPED",
                            "reason": "RISK_REJECTED",
                            "external_order_id": None,
                            "normalized_order": None,
                        })
                        continue
                    
                    connector_cls = CONNECTOR_REGISTRY.get(firm_code)
                    if not connector_cls:
                        results.append({
                            "firm_code": firm_code,
                            "status": "FAILED",
                            "error_message": f"No connector found for {firm_code}"
                        })
                        continue
                    
                    config = get_firm_config(firm_code)
                    if not config.get('enabled', False):
                        results.append({
                            "firm_code": firm_code,
                            "status": "FAILED",
                            "error_message": "CONNECTOR_NOT_CONFIGURED"
                        })
                        continue
                    
                    connector = connector_cls(firm_code, config)
                    
                    max_retries = 2
                    for attempt in range(max_retries + 1):
                        try:
                            result = connector.place_order(normalized_order)
                            
                            if result.status == "RETRY" and attempt < max_retries:
                                self.logger.info("Retrying %s connector (attempt %d/%d)", firm_code, attempt + 1, max_retries)
                                time.sleep(1)
                                continue
                            
                            results.append({
                                "firm_code": firm_code,
                                "status": result.status,
                                "external_order_id": result.external_order_id,
                                "raw_response": result.raw_response,
                                "error_message": result.error_message
                            })
                            break
                        
                        except Exception as connector_error:
                            if attempt == max_retries:
                                results.append({
                                    "firm_code": firm_code,
                                    "status": "FAILED",
                                    "error_message": f"Connector exception: {str(connector_error)}"
                                })
                            else:
                                self.logger.warning("Connector %s attempt %d failed: %s", firm_code, attempt + 1, connector_error)
                
                except Exception as firm_error:
                    results.append({
                        "firm_code": firm_code,
                        "status": "FAILED",
                        "error_message": f"Firm processing error: {str(firm_error)}"
                    })
            
            return results
        
        except Exception as e:
            self.logger.error("Error executing connectors for task %d: %s", task_id, e)
            return [{
                "firm_code": "ALL",
                "status": "FAILED",
                "error_message": f"Connector execution error: {str(e)}"
            }]
    
    def _handle_task(
        self,
        task_id: int,
        trade_id: Optional[str],
        event_type: Optional[str],
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Core routing logic for a single execution task.
        
        In Stage 13B, this is a DRY-RUN:
        - No external HTTP calls are made.
        - We just log the intent and return a simulated result.
        """
        self.logger.info(
            "🚚 [ExecutionRouter] Processing task_id=%s trade_id=%s event_type=%s payload=%s",
            task_id,
            trade_id,
            event_type,
            json.dumps(payload, default=str),
        )
        
        # Stage 13D: run risk checks for this task
        risk_checks = self._run_risk_checks_for_task(payload)
        
        # Stage 13E: program sizing
        program_sizing = self._run_program_sizing_for_task(payload)
        
        # Stage 13H: comprehensive enforcement checks (replaces Stage 13F)
        account_breaches = self._run_comprehensive_enforcement_for_task(payload)
        
        # Determine which firms are allowed to route based on risk + sizing + breach results
        allowed_firm_codes: Optional[List[str]] = None
        if risk_checks:
            allowed_firm_codes = [
                rc["firm_code"]
                for rc in risk_checks
                if rc.get("status") == "APPROVED" and rc.get("firm_code")
            ]
            if not allowed_firm_codes:
                # All requested firms rejected; connectors will be skipped
                allowed_firm_codes = []
        
        # Further filter by program sizing approvals
        if program_sizing:
            sizing_approved_firms = [
                r["firm_code"]
                for r in program_sizing
                if r.get("status") == "APPROVED"
            ]
            if allowed_firm_codes is not None:
                # Intersect with risk-approved firms
                allowed_firm_codes = [
                    fc for fc in allowed_firm_codes
                    if fc in sizing_approved_firms
                ]
            else:
                allowed_firm_codes = sizing_approved_firms
        
        # Further filter by account breach approvals
        if account_breaches:
            approved_by_breach = {
                b["firm_code"]
                for b in account_breaches
                if b.get("status") == "APPROVED" and b.get("firm_code")
            }
            # If no firms appear in account_breaches, leave allowed_firm_codes unchanged
            if approved_by_breach:
                if allowed_firm_codes is None:
                    allowed_firm_codes = list(approved_by_breach)
                else:
                    # Intersect with existing allowed_firm_codes
                    allowed_firm_codes = [
                        code for code in (allowed_firm_codes or [])
                        if code in approved_by_breach
                    ]
        
        # Stage 13C: Execute connectors for this task
        connector_results = self._execute_connectors_for_task(
            task_id=task_id,
            task_payload=payload,
            allowed_firm_codes=allowed_firm_codes,
            program_sizing=program_sizing,
        )
        
        # Placeholder for future real routing logic.
        # In Stage 13B we only simulate success.
        simulated_result = {
            "routed": False,
            "dry_run": self.dry_run,
            "event_type": event_type,
            "trade_id": trade_id,
            "details": "ExecutionRouter dry-run: no external order sent. This is plumbing only.",
            "risk_checks": risk_checks if risk_checks else [],
            "program_sizing": program_sizing if program_sizing else [],
            "account_breaches": account_breaches if account_breaches else [],
            "connector_results": connector_results,
        }
        
        # When we later implement real routing, this method will:
        # - Inspect payload (e.g. firm codes, program ids, quantities)
        # - Call appropriate prop firm connector(s)
        # - Populate result with execution details (order ids, statuses, etc.)
        
        return simulated_result

    def _run_comprehensive_enforcement_for_task(
        self,
        task_payload: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Stage 13H:
        Run comprehensive enforcement checks using unified program metadata.
        
        This replaces the basic account breach checks with full enforcement
        including session, contracts, risk-per-trade, daily loss, and drawdown.
        
        Returns a list of enforcement result dicts.
        """
        firm_codes, routing_meta = get_routing_rules_for_task(task_payload)
        program_ids = routing_meta.get("program_ids") or []
        results: List[Dict[str, Any]] = []
        
        if not firm_codes or not program_ids:
            return results
        
        # Extract order data from payload
        order_data = {
            "entry_price": task_payload.get("entry_price"),
            "stop_loss": task_payload.get("stop_loss"),
            "contracts": task_payload.get("contracts") or task_payload.get("quantity"),
            "session": task_payload.get("session"),
        }
        
        for firm_code in firm_codes:
            for pid in program_ids:
                try:
                    # Get unified program metadata
                    program_metadata = get_unified_program_metadata(firm_code, pid)
                    
                    # Get current account state
                    account_state = self._get_account_metrics_for_program(firm_code, pid)
                    
                    # Run comprehensive enforcement
                    enforcement_result = check_order_enforcement(
                        firm_code=firm_code,
                        program_id=pid,
                        program_metadata=program_metadata,
                        account_state=account_state or {},
                        order_data=order_data,
                    )
                    
                    # Convert to standard result format
                    status = "APPROVED" if enforcement_result["allowed"] else "REJECTED"
                    results.append({
                        "firm_code": firm_code,
                        "program_id": pid,
                        "status": status,
                        "rule": enforcement_result.get("breach_type"),
                        "reason": enforcement_result.get("reason"),
                        "details": enforcement_result,
                    })
                    
                    # Log blocked orders
                    if not enforcement_result["allowed"]:
                        self.logger.warning(
                            f"ORDER BLOCKED: {enforcement_result['reason']} "
                            f"(firm={firm_code}, program={pid}, type={enforcement_result['breach_type']})"
                        )
                        
                except Exception as exc:
                    results.append({
                        "firm_code": firm_code,
                        "program_id": pid,
                        "status": "REJECTED",
                        "rule": "EXCEPTION",
                        "reason": f"Enforcement check exception for firm {firm_code}, program {pid}: {exc}",
                        "details": None,
                    })
                    self.logger.error(
                        f"ORDER BLOCKED: Enforcement exception for {firm_code}/{pid}: {exc}"
                    )
        
        return results

