"""
Roadmap V3 Loader and Progress Tracker

Loads the unified roadmap YAML (v3) and computes progress metrics.
Includes in-memory caching with file modification time checking.
"""

import os
import yaml
import logging
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Cache configuration
_roadmap_cache = None
_cache_mtime = 0.0
_cache_path = ""
_last_error = None

ROADMAP_V3_PATH = Path(__file__).resolve().parent / "unified_roadmap_v3.yaml"


def _get_file_mtime(filepath):
    """Get file modification time, return 0 if file doesn't exist."""
    try:
        return filepath.stat().st_mtime
    except (OSError, FileNotFoundError):
        return 0.0


def get_last_error():
    """Return the last error encountered during roadmap loading."""
    return _last_error


def _get_fallback_roadmap():
    """Return a minimal fallback roadmap if loading fails."""
    return {
        "roadmap_version": "3.0.0-fallback",
        "phases": [],
        "feature_flags": {},
        "current_data_state": {},
        "_fallback": True,
        "_error": _last_error
    }

def load_roadmap_v3(force_reload=False):
    """Load the V3 roadmap YAML with caching."""
    global _roadmap_cache, _cache_mtime, _cache_path, _last_error
    
    current_mtime = _get_file_mtime(ROADMAP_V3_PATH)
    
    if (not force_reload 
        and _roadmap_cache is not None 
        and _cache_mtime == current_mtime
        and _cache_path == str(ROADMAP_V3_PATH)):
        return _roadmap_cache
    
    try:
        logger.info(f"[ROADMAP] Attempting to load: {ROADMAP_V3_PATH}")
        
        if not ROADMAP_V3_PATH.exists():
            _last_error = f"File not found: {ROADMAP_V3_PATH}"
            logger.error(f"[ROADMAP] {_last_error}")
            return _get_fallback_roadmap()
        
        with open(ROADMAP_V3_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            _last_error = "YAML file parsed but returned None"
            logger.error(f"[ROADMAP] {_last_error}")
            return _get_fallback_roadmap()
        
        _roadmap_cache = data
        _cache_mtime = current_mtime
        _cache_path = str(ROADMAP_V3_PATH)
        _last_error = None
        
        phase_count = len(data.get("phases", []))
        logger.info(f"[ROADMAP] Loaded successfully: {phase_count} phases")
        return data
        
    except Exception as e:
        _last_error = f"{type(e).__name__}: {e}"
        logger.error(f"[ROADMAP] Unexpected error: {_last_error}")
        return _get_fallback_roadmap()


def load_v3_yaml():
    """Load the V3 roadmap YAML file with comprehensive error capture."""
    resolved_path = str(ROADMAP_V3_PATH)
    exists = False
    yaml_importable = True
    
    try:
        exists = ROADMAP_V3_PATH.exists()
        if not exists:
            return (None, f"File not found: {resolved_path}", resolved_path, False, yaml_importable)
    except Exception as e:
        return (None, f"Path check failed: {e}", resolved_path, False, yaml_importable)
    
    try:
        with open(ROADMAP_V3_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            return (None, "YAML file parsed but returned None", resolved_path, True, yaml_importable)
        
        if not isinstance(data, dict):
            return (None, f"YAML root is not a dict: {type(data)}", resolved_path, True, yaml_importable)
        
        if "phases" not in data:
            return (None, "YAML missing 'phases' key", resolved_path, True, yaml_importable)
        
        return (data, None, resolved_path, True, yaml_importable)
        
    except yaml.YAMLError as e:
        return (None, f"YAML parse error: {e}", resolved_path, True, yaml_importable)
    except Exception as e:
        return (None, f"{type(e).__name__}: {e}", resolved_path, True, yaml_importable)


def build_v3_snapshot():
    """
    Build V3 roadmap snapshot with comprehensive error capture.
    Returns tuple: (snapshot_dict, error_str, path_str, exists, yaml_importable)
    """
    resolved_path = str(ROADMAP_V3_PATH)
    
    data, error_str, path_str, exists, yaml_importable = load_v3_yaml()
    
    if error_str:
        return (None, error_str, path_str, exists, yaml_importable)
    
    try:
        version = data.get("roadmap_version", "unknown")
        phases_raw = data.get("phases", [])
        feature_flags = data.get("feature_flags", {})
        
        # Overall counters
        overall_phases_done = 0
        overall_modules_total = 0
        overall_modules_done = 0
        overall_tasks_total = 0
        overall_tasks_done = 0
        
        phases_out = []
        for phase in phases_raw:
            phase_id = phase.get("phase_id", "??")
            name = phase.get("name", "Unknown Phase")
            objective = phase.get("objective", "")
            status = phase.get("status", "PLANNED")
            modules = phase.get("modules", [])
            
            total_tasks = 0
            done_tasks = 0
            modules_total = len(modules)
            modules_done = 0
            
            module_list = []
            for module in modules:
                module_id = module.get("module_id", "")
                module_title = module.get("title", "")
                module_status = module.get("status", "PLANNED")
                module_description = module.get("description", "")
                tasks = module.get("tasks", [])
                
                task_count = len(tasks)
                task_done = sum(1 for t in tasks if t.get("status") == "COMPLETE")
                total_tasks += task_count
                done_tasks += task_done
                
                module_done = module_status == "COMPLETE"
                if module_done:
                    modules_done += 1
                
                module_list.append({
                    "id": module_id,
                    "title": module_title,
                    "status": module_status,
                    "done": module_done,
                    "tasks_total": task_count,
                    "tasks_done": task_done,
                    "description": module_description
                })
            
            # Calculate percentages
            if modules_total > 0:
                module_percent = int(round(modules_done / modules_total * 100))
            else:
                module_percent = 100 if status == "COMPLETE" else 0
            
            if total_tasks > 0:
                task_percent = int(round(done_tasks / total_tasks * 100))
            else:
                task_percent = 100 if status == "COMPLETE" else 0
            
            is_complete = status == "COMPLETE"
            if is_complete:
                overall_phases_done += 1
            
            overall_modules_total += modules_total
            overall_modules_done += modules_done
            overall_tasks_total += total_tasks
            overall_tasks_done += done_tasks
            
            phases_out.append({
                "phase_id": phase_id,
                "name": name,
                "objective": objective,
                "status": status,
                "description": phase.get("description", ""),
                "deliverables": phase.get("deliverables", []),
                "rules": phase.get("rules", []),
                "_debug": "deliverables_enabled",
                "is_complete": is_complete,
                "is_active": status == "IN_PROGRESS",
                "modules_total": modules_total,
                "modules_done": modules_done,
                "module_percent": module_percent,
                "task_percent": task_percent,
                "tasks_total": total_tasks,
                "tasks_done": done_tasks,
                "module_list": module_list
            })
        
        # Build overall progress dict
        if len(phases_out) > 0:
            overall_phase_percent = int(round(overall_phases_done / len(phases_out) * 100))
        else:
            overall_phase_percent = 0
        
        if overall_modules_total > 0:
            overall_module_percent = int(round(overall_modules_done / overall_modules_total * 100))
        else:
            overall_module_percent = 0
        
        if overall_tasks_total > 0:
            overall_task_percent = int(round(overall_tasks_done / overall_tasks_total * 100))
        else:
            overall_task_percent = 0
        
        overall = {
            "phases_total": len(phases_out),
            "phases_done": overall_phases_done,
            "phase_percent": overall_phase_percent,
            "modules_total": overall_modules_total,
            "modules_done": overall_modules_done,
            "module_percent": overall_module_percent,
            "tasks_total": overall_tasks_total,
            "tasks_done": overall_tasks_done,
            "task_percent": overall_task_percent
        }
        
        snapshot = {
            "roadmap_version": version,
            "version": version,
            "phases": phases_out,
            "overall": overall,
            "source_of_truth": data.get("source_of_truth", {}),
            "current_data_state": data.get("current_data_state", {}),
            "feature_flags": {
                k: (v == "ON" or v is True) 
                for k, v in feature_flags.items()
            },
            "_is_fallback": False
        }
        
        return (snapshot, None, path_str, exists, yaml_importable)
        
    except Exception as e:
        error_str = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        logger.exception("[ROADMAP_V3_BUILD_SNAPSHOT_ERROR]")
        return (None, error_str, resolved_path, exists, yaml_importable)


def get_phase_progress(roadmap=None):
    """Compute progress for each phase."""
    if roadmap is None:
        roadmap = load_roadmap_v3()
    
    phases = roadmap.get("phases", [])
    
    result = []
    for phase in phases:
        phase_id = phase.get("phase_id", "??")
        name = phase.get("name", "Unknown Phase")
        objective = phase.get("objective", "")
        status = phase.get("status", "PLANNED")
        modules = phase.get("modules", [])
        
        total_modules = len(modules)
        completed_modules = 0
        total_tasks = 0
        completed_tasks = 0
        
        module_list = []
        for module in modules:
            module_id = module.get("module_id", "")
            module_title = module.get("title", "")
            module_status = module.get("status", "PLANNED")
            tasks = module.get("tasks", [])
            
            module_done = module_status == "COMPLETE"
            if module_done:
                completed_modules += 1
            
            task_count = len(tasks)
            task_done = sum(1 for t in tasks if t.get("status") == "COMPLETE")
            total_tasks += task_count
            completed_tasks += task_done
            
            module_list.append({
                "id": module_id,
                "title": module_title,
                "done": module_done,
                "status": module_status,
                "tasks_total": task_count,
                "tasks_done": task_done,
                "description": module.get("description", "")
            })
        
        module_percent = int((completed_modules / total_modules * 100)) if total_modules > 0 else 0
        task_percent = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        
        result.append({
            "phase_id": phase_id,
            "name": name,
            "objective": objective,
            "status": status,
            "modules_total": total_modules,
            "modules_done": completed_modules,
            "module_percent": module_percent,
            "tasks_total": total_tasks,
            "tasks_done": completed_tasks,
            "task_percent": task_percent,
            "module_list": module_list,
            "is_complete": status == "COMPLETE",
            "is_active": status == "IN_PROGRESS"
        })
    
    result.sort(key=lambda x: x["phase_id"])
    return result


def get_overall_progress(roadmap=None):
    """Get overall roadmap progress summary."""
    phases = get_phase_progress(roadmap)
    
    total_phases = len(phases)
    completed_phases = sum(1 for p in phases if p["is_complete"])
    active_phase = next((p for p in phases if p["is_active"]), None)
    
    total_modules = sum(p["modules_total"] for p in phases)
    completed_modules = sum(p["modules_done"] for p in phases)
    
    total_tasks = sum(p["tasks_total"] for p in phases)
    completed_tasks = sum(p["tasks_done"] for p in phases)
    
    return {
        "phases_total": total_phases,
        "phases_done": completed_phases,
        "phase_percent": int((completed_phases / total_phases * 100)) if total_phases > 0 else 0,
        "modules_total": total_modules,
        "modules_done": completed_modules,
        "module_percent": int((completed_modules / total_modules * 100)) if total_modules > 0 else 0,
        "tasks_total": total_tasks,
        "tasks_done": completed_tasks,
        "task_percent": int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0,
        "active_phase": active_phase["phase_id"] if active_phase else None,
        "active_phase_name": active_phase["name"] if active_phase else "None"
    }


def get_homepage_roadmap_data():
    """Build complete roadmap data for homepage rendering."""
    try:
        roadmap = load_roadmap_v3()
        
        is_fallback = roadmap.get("_fallback", False)
        error_msg = roadmap.get("_error")
        
        return {
            "version": roadmap.get("roadmap_version", "unknown"),
            "phases": get_phase_progress(roadmap),
            "overall": get_overall_progress(roadmap),
            "feature_flags": {},
            "databento_state": {},
            "source_of_truth": roadmap.get("source_of_truth", {}),
            "_is_fallback": is_fallback,
            "_error": error_msg
        }
    except Exception as e:
        logger.error(f"[ROADMAP] get_homepage_roadmap_data failed: {e}")
        return {
            "version": "error",
            "phases": [],
            "overall": {
                "phases_total": 0, "phases_done": 0, "phase_percent": 0,
                "modules_total": 0, "modules_done": 0, "module_percent": 0,
                "tasks_total": 0, "tasks_done": 0, "task_percent": 0,
                "active_phase": None, "active_phase_name": "Error"
            },
            "feature_flags": {},
            "databento_state": {},
            "source_of_truth": {},
            "_is_fallback": True,
            "_error": f"{type(e).__name__}: {e}"
        }


def invalidate_cache():
    """Force cache invalidation."""
    global _roadmap_cache, _cache_mtime
    _roadmap_cache = None
    _cache_mtime = 0.0


def get_roadmap_version():
    """Get the current roadmap version."""
    roadmap = load_roadmap_v3()
    return roadmap.get("roadmap_version", "unknown")

# Force git detection - 2025-01-02
