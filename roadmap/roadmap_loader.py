'''Roadmap V3 Loader'''
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
_roadmap_cache = None
_cache_mtime = 0.0
ROADMAP_V3_PATH = Path(__file__).parent / 'unified_roadmap_v3.yaml'

def load_roadmap_v3(force_reload=False):
    global _roadmap_cache, _cache_mtime
    try:
        mtime = ROADMAP_V3_PATH.stat().st_mtime
    except:
        mtime = 0
    if not force_reload and _roadmap_cache and _cache_mtime == mtime:
        return _roadmap_cache
    try:
        with open(ROADMAP_V3_PATH, 'r', encoding='utf-8') as f:
            _roadmap_cache = yaml.safe_load(f)
        _cache_mtime = mtime
        return _roadmap_cache
    except Exception as e:
        logger.error(f'Error loading roadmap: {e}')
        return {'roadmap_version': 'fallback', 'phases': [], 'feature_flags': {}}

def get_phase_progress(roadmap=None):
    if roadmap is None:
        roadmap = load_roadmap_v3()
    phases = roadmap.get('phases', [])
    flags = roadmap.get('feature_flags', {})
    result = []
    for p in phases:
        mods = p.get('modules', [])
        mod_list = []
        done_count = 0
        for m in mods:
            is_done = m.get('status') == 'COMPLETE'
            if is_done:
                done_count += 1
            flag = m.get('feature_flag', '')
            flag_on = flags.get(flag, False)
            if isinstance(flag_on, str):
                flag_on = flag_on == 'ON'
            mod_list.append({
                'id': m.get('module_id', ''),
                'title': m.get('title', ''),
                'done': is_done,
                'flag_enabled': flag_on if flag else True,
                'acceptance_criteria': m.get('acceptance_criteria', [])[:2]
            })
        pct = int(done_count / len(mods) * 100) if mods else 0
        result.append({
            'phase_id': p.get('phase_id', '?'),
            'name': p.get('name', ''),
            'objective': p.get('objective', ''),
            'modules_total': len(mods),
            'modules_done': done_count,
            'module_percent': pct,
            'module_list': mod_list,
            'is_complete': p.get('status') == 'COMPLETE',
            'is_active': p.get('status') == 'IN_PROGRESS'
        })
    return sorted(result, key=lambda x: x['phase_id'])

def get_overall_progress(roadmap=None):
    phases = get_phase_progress(roadmap)
    total = len(phases)
    done = sum(1 for p in phases if p['is_complete'])
    active = next((p for p in phases if p['is_active']), None)
    mods_total = sum(p['modules_total'] for p in phases)
    mods_done = sum(p['modules_done'] for p in phases)
    return {
        'phases_total': total,
        'phases_done': done,
        'phase_percent': int(done / total * 100) if total else 0,
        'modules_total': mods_total,
        'modules_done': mods_done,
        'module_percent': int(mods_done / mods_total * 100) if mods_total else 0,
        'active_phase': active['phase_id'] if active else None,
        'active_phase_name': active['name'] if active else 'None'
    }

def get_feature_flags(roadmap=None):
    if roadmap is None:
        roadmap = load_roadmap_v3()
    flags = roadmap.get('feature_flags', {})
    return {k: (v == 'ON' or v is True) for k, v in flags.items()}

def get_homepage_roadmap_data():
    roadmap = load_roadmap_v3()
    return {
        'version': roadmap.get('roadmap_version', 'unknown'),
        'phases': get_phase_progress(roadmap),
        'overall': get_overall_progress(roadmap),
        'feature_flags': get_feature_flags(roadmap)
    }
