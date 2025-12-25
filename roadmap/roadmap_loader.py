import yaml
import logging
import traceback
from pathlib import Path

logger = logging.getLogger(__name__)

_roadmap_cache = None
_cache_mtime = 0.0
_cache_path = ""
_last_error = None

ROADMAP_V3_PATH = Path(__file__).resolve().parent / "unified_roadmap_v3.yaml"

def _get_file_mtime(filepath):
    try:
        return filepath.stat().st_mtime
    except:
        return 0.0

def get_last_error():
    return _last_error

def _get_fallback_roadmap():
    return {"roadmap_version": "3.0.0-fallback", "phases": [], "feature_flags": {}, "current_data_state": {}, "_fallback": True, "_error": _last_error}

def load_roadmap_v3(force_reload=False):
    global _roadmap_cache, _cache_mtime, _cache_path, _last_error
    current_mtime = _get_file_mtime(ROADMAP_V3_PATH)
    if not force_reload and _roadmap_cache is not None and _cache_mtime == current_mtime:
        return _roadmap_cache
    try:
        if not ROADMAP_V3_PATH.exists():
            _last_error = f"File not found: {ROADMAP_V3_PATH}"
            return _get_fallback_roadmap()
        with open(ROADMAP_V3_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if data is None:
            _last_error = "YAML parsed but returned None"
            return _get_fallback_roadmap()
        _roadmap_cache = data
        _cache_mtime = current_mtime
        _cache_path = str(ROADMAP_V3_PATH)
        _last_error = None
        return data
    except Exception as e:
        _last_error = f"{type(e).__name__}: {e}"
        return _get_fallback_roadmap()

def get_phase_progress(roadmap=None):
    if roadmap is None:
        roadmap = load_roadmap_v3()
    phases = roadmap.get("phases", [])
    feature_flags = roadmap.get("feature_flags", {})
    result = []
    for phase in phases:
        phase_id = phase.get("phase_id", "??")
        name = phase.get("name", "Unknown")
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
            module_list.append({"id": module_id, "title": module_title, "done": module_done, "status": module_status, "tasks_total": task_count, "tasks_done": task_done})
        module_percent = int((completed_modules / total_modules * 100)) if total_modules > 0 else 0
        task_percent = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        result.append({"phase_id": phase_id, "name": name, "status": status, "modules_total": total_modules, "modules_done": completed_modules, "module_percent": module_percent, "tasks_total": total_tasks, "tasks_done": completed_tasks, "task_percent": task_percent, "module_list": module_list, "is_complete": status == "COMPLETE", "is_active": status == "IN_PROGRESS"})
    result.sort(key=lambda x: x["phase_id"])
    return result

def get_overall_progress(roadmap=None):
    phases = get_phase_progress(roadmap)
    total_phases = len(phases)
    completed_phases = sum(1 for p in phases if p["is_complete"])
    active_phase = next((p for p in phases if p["is_active"]), None)
    total_modules = sum(p["modules_total"] for p in phases)
    completed_modules = sum(p["modules_done"] for p in phases)
    total_tasks = sum(p["tasks_total"] for p in phases)
    completed_tasks = sum(p["tasks_done"] for p in phases)
    return {"phases_total": total_phases, "phases_done": completed_phases, "phase_percent": int((completed_phases / total_phases * 100)) if total_phases > 0 else 0, "modules_total": total_modules, "modules_done": completed_modules, "module_percent": int((completed_modules / total_modules * 100)) if total_modules > 0 else 0, "tasks_total": total_tasks, "tasks_done": completed_tasks, "task_percent": int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0, "active_phase": active_phase["phase_id"] if active_phase else None, "active_phase_name": active_phase["name"] if active_phase else "None"}

def get_feature_flags(roadmap=None):
    if roadmap is None:
        roadmap = load_roadmap_v3()
    flags = roadmap.get("feature_flags", {})
    return {k: (v == "ON" or v is True) for k, v in flags.items()}

def get_databento_state(roadmap=None):
    if roadmap is None:
        roadmap = load_roadmap_v3()
    return roadmap.get("current_data_state", {}).get("databento_ohlcv_1m", {})

def get_homepage_roadmap_data():
    try:
        roadmap = load_roadmap_v3()
        is_fallback = roadmap.get("_fallback", False)
        error_msg = roadmap.get("_error")
        return {"version": roadmap.get("roadmap_version", "unknown"), "phases": get_phase_progress(roadmap), "overall": get_overall_progress(roadmap), "feature_flags": get_feature_flags(roadmap), "databento_state": get_databento_state(roadmap), "source_of_truth": roadmap.get("source_of_truth", {}), "_is_fallback": is_fallback, "_error": error_msg}
    except Exception as e:
        return {"version": "error", "phases": [], "overall": {"phases_total": 0, "phases_done": 0, "phase_percent": 0, "modules_total": 0, "modules_done": 0, "module_percent": 0, "tasks_total": 0, "tasks_done": 0, "task_percent": 0, "active_phase": None, "active_phase_name": "Error"}, "feature_flags": {}, "databento_state": {}, "source_of_truth": {}, "_is_fallback": True, "_error": f"{type(e).__name__}: {e}"}

def invalidate_cache():
    global _roadmap_cache, _cache_mtime
    _roadmap_cache = None
    _cache_mtime = 0.0

def get_roadmap_version():
    roadmap = load_roadmap_v3()
    return roadmap.get("roadmap_version", "unknown")

def load_v3_yaml():
    resolved_path = str(ROADMAP_V3_PATH)
    exists = False
    yaml_importable = False
    try:
        import yaml
        yaml_importable = True
    except ImportError as e:
        return (None, f"PyYAML import failed: {e}", resolved_path, False, False)
    try:
        exists = ROADMAP_V3_PATH.exists()
        if not exists:
            return (None, f"File not found: {resolved_path}", resolved_path, False, yaml_importable)
    except Exception as e:
        return (None, f"Path check failed: {type(e).__name__}: {e}", resolved_path, False, yaml_importable)
    try:
        with open(ROADMAP_V3_PATH, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if data is None:
            return (None, "YAML parsed but returned None", resolved_path, True, yaml_importable)
        if not isinstance(data, dict):
            return (None, f"YAML root is not a dict: {type(data)}", resolved_path, True, yaml_importable)
        if "phases" not in data:
            return (None, "YAML missing 'phases' key", resolved_path, True, yaml_importable)
        if not isinstance(data.get("phases"), list):
            return (None, f"'phases' is not a list: {type(data.get('phases'))}", resolved_path, True, yaml_importable)
        return (data, None, resolved_path, True, yaml_importable)
    except yaml.YAMLError as e:
        return (None, f"YAML parse error: {e}", resolved_path, True, yaml_importable)
    except Exception as e:
        return (None, f"{type(e).__name__}: {e}", resolved_path, True, yaml_importable)

def build_v3_snapshot():
    resolved_path = str(ROADMAP_V3_PATH)
    data, error_str, path_str, exists, yaml_importable = load_v3_yaml()
    if error_str:
        return (None, error_str, path_str, exists, yaml_importable)
    try:
        version = data.get("roadmap_version", "unknown")
        phases_raw = data.get("phases", [])
        feature_flags = data.get("feature_flags", {})
        phases_out = []
        for phase in phases_raw:
            phase_id = phase.get("phase_id", "??")
            name = phase.get("name", "Unknown")
            status = phase.get("status", "PLANNED")
            modules = phase.get("modules", [])
            total_tasks = 0
            done_tasks = 0
            module_list = []
            for module in modules:
                module_id = module.get("module_id", "")
                module_title = module.get("title", "")
                module_status = module.get("status", "PLANNED")
                tasks = module.get("tasks", [])
                task_count = len(tasks)
                task_done = sum(1 for t in tasks if t.get("status") == "COMPLETE")
                total_tasks += task_count
                done_tasks += task_done
                module_list.append({"id": module_id, "title": module_title, "status": module_status, "done": module_status == "COMPLETE", "tasks_total": task_count, "tasks_done": task_done})
            if total_tasks > 0:
                percent = int(round(done_tasks / total_tasks * 100))
            else:
                percent = 0 if status != "COMPLETE" else 100
            phases_out.append({"phase_id": phase_id, "name": name, "status": status, "is_complete": status == "COMPLETE", "is_active": status == "IN_PROGRESS", "task_percent": percent, "tasks_total": total_tasks, "tasks_done": done_tasks, "module_list": module_list})
        snapshot = {"roadmap_version": version, "version": version, "phases": phases_out, "source_of_truth": data.get("source_of_truth", {}), "current_data_state": data.get("current_data_state", {}), "feature_flags": {k: (v == "ON" or v is True) for k, v in feature_flags.items()}}
        return (snapshot, None, path_str, exists, yaml_importable)
    except Exception as e:
        error_str = f"{type(e).__name__}: {e}"
        return (None, error_str, resolved_path, exists, yaml_importable)
