"""
Prop Firm Registry & Seeder (Stage 13 - Option C)

Centralized, data-driven registry for prop trading firms, programs, and rules.

Design goals:
- Normalized schema with firms, programs, and scaling rules.
- Data-driven: seed from Python definitions into DB via upsert (ON CONFLICT DO NOTHING).
- Resilient to change: schema_version + meta JSONB for additional fields.
- Read-only public API for other modules (e.g., prop firm management UI, simulators).
- Future-proof: stubbed external sync (e.g. propfirmmatch.com) for automatic updates.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class PropFirmRegistry:
    """
    Thin wrapper around the DB connection to manage:
    - prop_firms
    - prop_programs
    - prop_scaling_rules
    
    This class does NOT enforce trading logic; it only reads/writes reference data.
    """
    
    def __init__(self, db):
        """
        :param db: instance of database.railway_db.RailwayDB (or compatible)
        """
        self.db = db
    
    # ---------------------------------------------------------------------
    # Schema & Seeding
    # ---------------------------------------------------------------------
    def ensure_schema_and_seed(self) -> None:
        """
        Ensure that the prop_firms, prop_programs, and prop_scaling_rules tables exist,
        then seed them with a curated baseline set of firms/programs/rules.
        
        This method is idempotent and safe to call multiple times.
        """
        try:
            if not self.db or not getattr(self.db, "conn", None):
                logger.warning("PropFirmRegistry.ensure_schema_and_seed: DB not available")
                return
            
            conn = self.db.conn
            conn.rollback()
            cur = conn.cursor()
            
            # NOTE: The actual CREATE TABLE statements are executed in web_server.py
            # inside the global schema initialization block. Here we only verify that
            # the tables exist by attempting trivial queries.
            try:
                cur.execute("SELECT 1 FROM prop_firms LIMIT 1;")
                cur.execute("SELECT 1 FROM prop_programs LIMIT 1;")
                cur.execute("SELECT 1 FROM prop_scaling_rules LIMIT 1;")
            except Exception as e:
                logger.error("PropFirmRegistry.ensure_schema_and_seed: schema not ready: %s", e)
                conn.rollback()
                return
            
            self._seed_firms_and_programs(cur)
            conn.commit()
            logger.info("✅ PropFirmRegistry: baseline firms/programs/scaling rules ensured")
        except Exception as e:
            logger.error("PropFirmRegistry.ensure_schema_and_seed error: %s", e, exc_info=True)
            try:
                self.db.conn.rollback()
            except Exception:
                pass
    
    def _seed_firms_and_programs(self, cur) -> None:
        """
        Insert baseline firms and their core programs (50k/100k/200k) with simple scaling rules.
        Uses INSERT ... ON CONFLICT DO NOTHING for idempotency.
        """
        firms = [
            # code, name, website
            ("FTMO", "FTMO", "https://ftmo.com"),
            ("APEX", "Apex Trader Funding", "https://apextraderfunding.com"),
            ("TOPSTEP", "Topstep", "https://www.topstep.com"),
            ("MFF", "MyFundedFutures", "https://myfundedfutures.com"),
            ("ALPHA", "Alpha Futures", "https://alphafutures.com"),
            ("TOPONE", "Top One Futures", "https://toponefunding.com"),
            ("TRADEIFY", "Tradeify", "https://tradeify.com"),
            ("FUNDINGTICKS", "FundingTicks", "https://fundingticks.com"),
            ("FUNDEDNEXTFUT", "FundedNext Futures", "https://fundednext.com"),
            ("AQUA", "AquaFutures", "https://aquafutures.com"),
            ("TPT", "Take Profit Trader", "https://takeprofittrader.com"),
        ]
        
        # Insert firms
        for code, name, website in firms:
            cur.execute(
                """
                INSERT INTO prop_firms (code, name, website_url, status, schema_version, meta)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
                """,
                (code, name, website, "active", 1, {}),
            )
        
        # Map firm codes to firm_ids
        cur.execute("SELECT id, code FROM prop_firms")
        firm_rows = cur.fetchall()
        firm_id_by_code = {row[1]: row[0] for row in firm_rows}
        
        # Baseline programs (50k, 100k, 200k) for each firm
        # This is intentionally simplified as a starting point and can be enriched later.
        base_programs: List[Dict[str, Any]] = []
        account_sizes = [50000, 100000, 200000]
        
        for code, name, _ in firms:
            firm_id = firm_id_by_code.get(code)
            if not firm_id:
                continue
            for size in account_sizes:
                # Simple generic program naming & baseline metrics.
                program_name = f"{name} {size/1000:.0f}k Evaluation"
                base_programs.append(
                    {
                        "firm_code": code,
                        "firm_id": firm_id,
                        "name": program_name,
                        "account_size": float(size),
                        "currency": "USD",
                        "max_daily_loss": float(size * 0.05),   # 5% daily
                        "max_total_loss": float(size * 0.10),   # 10% total
                        "profit_target": float(size * 0.10),    # 10% target
                        "min_trading_days": 5,
                        "max_trading_days": 30,
                        "payout_split": 0.80,                   # 80% default
                        "scaling_plan": "Grow 25% size every 10% net profit",
                        "meta": {
                            "note": "Baseline generic program. Replace with real rule set via admin or external sync.",
                            "source": "seed_v1",
                        },
                    }
                )
        
        for p in base_programs:
            cur.execute(
                """
                INSERT INTO prop_programs (
                    firm_id, name, account_size, currency,
                    max_daily_loss, max_total_loss,
                    profit_target, min_trading_days, max_trading_days,
                    payout_split, scaling_plan, schema_version, meta
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s)
                ON CONFLICT (firm_id, name, account_size) DO NOTHING
                """,
                (
                    p["firm_id"],
                    p["name"],
                    p["account_size"],
                    p["currency"],
                    p["max_daily_loss"],
                    p["max_total_loss"],
                    p["profit_target"],
                    p["min_trading_days"],
                    p["max_trading_days"],
                    p["payout_split"],
                    p["scaling_plan"],
                    p["meta"],
                ),
            )
        
        # Map program ids for scaling rules
        cur.execute("SELECT id, firm_id, name, account_size FROM prop_programs")
        program_rows = cur.fetchall()
        programs: List[Dict[str, Any]] = []
        for row in program_rows:
            programs.append(
                {
                    "id": row[0],
                    "firm_id": row[1],
                    "name": row[2],
                    "account_size": float(row[3]),
                }
            )
        
        # Simple scaling rules: +25% size after each 10% profit, up to 3 steps
        for prog in programs:
            cur.execute(
                """
                INSERT INTO prop_scaling_rules (
                    firm_id, program_id,
                    step_number, scale_factor,
                    profit_target_multiple,
                    min_days_between_scales,
                    max_equity_drawdown,
                    meta
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (
                    prog["firm_id"],
                    prog["id"],
                    1,
                    1.25,   # 25% increase
                    1.10,   # 10% profit
                    30,     # 30 days
                    0.10,   # 10% max drawdown during step
                    {
                        "note": "Baseline scaling: increase 25% after 10% profit every 30 days, max 1 step. Replace via admin/automation."
                    },
                ),
            )
    
    # ---------------------------------------------------------------------
    # Public Read-Only Accessors
    # ---------------------------------------------------------------------
    def list_firms(self) -> List[Dict[str, Any]]:
        """Return all active prop firms."""
        if not self.db or not getattr(self.db, "conn", None):
            return []
        try:
            cur = self.db.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT id, code, name, website_url, status, schema_version, meta, last_synced_at
                FROM prop_firms
                WHERE status = 'active'
                ORDER BY name ASC
                """
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("PropFirmRegistry.list_firms error: %s", e)
            try:
                self.db.conn.rollback()
            except Exception:
                pass
            return []
    
    def list_programs(self, firm_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return programs, optionally filtered by firm_id."""
        if not self.db or not getattr(self.db, "conn", None):
            return []
        try:
            cur = self.db.conn.cursor(cursor_factory=RealDictCursor)
            if firm_id:
                cur.execute(
                    """
                    SELECT p.id, p.firm_id, f.code as firm_code, f.name as firm_name,
                           p.name, p.account_size, p.currency,
                           p.max_daily_loss, p.max_total_loss,
                           p.profit_target, p.min_trading_days, p.max_trading_days,
                           p.payout_split, p.scaling_plan, p.meta
                    FROM prop_programs p
                    JOIN prop_firms f ON p.firm_id = f.id
                    WHERE p.firm_id = %s
                    ORDER BY p.account_size ASC, p.name ASC
                    """,
                    (firm_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT p.id, p.firm_id, f.code as firm_code, f.name as firm_name,
                           p.name, p.account_size, p.currency,
                           p.max_daily_loss, p.max_total_loss,
                           p.profit_target, p.min_trading_days, p.max_trading_days,
                           p.payout_split, p.scaling_plan, p.meta
                    FROM prop_programs p
                    JOIN prop_firms f ON p.firm_id = f.id
                    ORDER BY f.name ASC, p.account_size ASC
                    """
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("PropFirmRegistry.list_programs error: %s", e)
            try:
                self.db.conn.rollback()
            except Exception:
                pass
            return []
    
    def list_scaling_rules(self, program_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return scaling rules, optionally filtered by program_id."""
        if not self.db or not getattr(self.db, "conn", None):
            return []
        try:
            cur = self.db.conn.cursor(cursor_factory=RealDictCursor)
            if program_id:
                cur.execute(
                    """
                    SELECT r.id, r.program_id, r.step_number, r.scale_factor,
                           r.profit_target_multiple, r.min_days_between_scales,
                           r.max_equity_drawdown, r.meta
                    FROM prop_scaling_rules r
                    WHERE r.program_id = %s
                    ORDER BY r.step_number ASC
                    """,
                    (program_id,),
                )
            else:
                cur.execute(
                    """
                    SELECT r.id, r.program_id, r.step_number, r.scale_factor,
                           r.profit_target_multiple, r.min_days_between_scales,
                           r.max_equity_drawdown, r.meta
                    FROM prop_scaling_rules r
                    ORDER BY r.program_id ASC, r.step_number ASC
                    """
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error("PropFirmRegistry.list_scaling_rules error: %s", e)
            try:
                self.db.conn.rollback()
            except Exception:
                pass
            return []
    
    def list_firms_with_program_summary(self) -> List[Dict[str, Any]]:
        """
        Convenience method to return firms + summary of programs (counts and min/max sizes).
        This is used to back /api/prop-firm/firms while keeping output shape stable.
        """
        firms = self.list_firms()
        if not firms:
            return []
        try:
            cur = self.db.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT firm_id,
                       COUNT(*) as program_count,
                       MIN(account_size) as min_size,
                       MAX(account_size) as max_size
                FROM prop_programs
                GROUP BY firm_id
                """
            )
            stats = {row["firm_id"]: row for row in cur.fetchall()}
            for f in firms:
                s = stats.get(f["id"])
                if s:
                    f["program_count"] = int(s["program_count"])
                    f["min_account_size"] = float(s["min_size"]) if s["min_size"] is not None else None
                    f["max_account_size"] = float(s["max_size"]) if s["max_size"] is not None else None
                else:
                    f["program_count"] = 0
                    f["min_account_size"] = None
                    f["max_account_size"] = None
            return firms
        except Exception as e:
            logger.error("PropFirmRegistry.list_firms_with_program_summary error: %s", e)
            try:
                self.db.conn.rollback()
            except Exception:
                pass
            return firms
    
    # ---------------------------------------------------------------------
    # Placeholder for future external sync (e.g., propfirmmatch.com)
    # ---------------------------------------------------------------------
    def refresh_from_external_sources(self) -> None:
        """
        Placeholder for future integration with external providers (e.g. propfirmmatch.com).
        
        Design idea:
        - Pull remote JSON feed of firms/programs/rules.
        - Compare with local schema_version or hash.
        - Apply non-breaking merges into prop_firms / prop_programs / prop_scaling_rules.
        - Record last_synced_at and source metadata in meta.
        """
        logger.info("PropFirmRegistry.refresh_from_external_sources: not implemented yet")
        # TODO: implement external data sync (propfirmmatch.com) in a future iteration.
        pass
