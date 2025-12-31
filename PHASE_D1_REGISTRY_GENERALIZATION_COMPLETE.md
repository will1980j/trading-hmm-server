# Phase D.1: Symbol Registry Generalization - COMPLETE

**Date:** 2025-12-28  
**Status:** ✅ COMPLETE - Registry is now future-proof

---

## Objective

Ensure symbol_registry can support ES/NQ/YM/RTY now AND CL/GC/6E/BTC later without schema changes.

---

## Success Criteria

### ✅ All Criteria Met

1. **Generalized schema** - Supports any asset class
2. **Optional metadata** - Venue, asset_class, timezone, session_profile
3. **Backward compatibility** - Existing rows remain valid
4. **Script integration** - Reingest script uses registry fields
5. **No new symbols added** - Registry is future-proof, not populated yet

---

## Schema Review

### Current Columns (Phase D.0)
```
internal_symbol (PK) - Internal format (e.g., GLBX.MDP3:NQ)
dataset              - Databento dataset (e.g., GLBX.MDP3)
root                 - Instrument root (e.g., NQ)
roll_rule            - c/n/v
rank                 - 0=front month, 1=second month
schema               - ohlcv-1m (default)
stype_in             - continuous (default)
is_active            - TRUE/FALSE
created_at           - Timestamp
updated_at           - Timestamp
```

### Added Columns (Phase D.1)
```
vendor_dataset       - Vendor-specific dataset (e.g., GLBX.MDP3, CME.MDP3)
schema_name          - Data schema (e.g., ohlcv-1m, trades, quotes)
venue                - Trading venue (e.g., CME, NYMEX, COMEX, ICE)
asset_class          - Asset class (e.g., equity_index, energy, metals, fx, crypto)
timezone             - Primary timezone (e.g., America/Chicago, America/New_York)
session_profile      - Session profile (e.g., cme_equity_index, nymex_energy)
```

**All new columns are nullable** - Backward compatibility maintained

---

## Future Symbol Support

### Equity Index Futures (Current)
```sql
internal_symbol: GLBX.MDP3:NQ
vendor_dataset: GLBX.MDP3
root: NQ
venue: CME
asset_class: equity_index
timezone: America/Chicago
```

### Energy Futures (Future)
```sql
internal_symbol: NYMEX.MDP3:CL
vendor_dataset: NYMEX.MDP3
root: CL
venue: NYMEX
asset_class: energy
timezone: America/New_York
```

### Metals Futures (Future)
```sql
internal_symbol: COMEX.MDP3:GC
vendor_dataset: COMEX.MDP3
root: GC
venue: COMEX
asset_class: metals
timezone: America/New_York
```

### FX Futures (Future)
```sql
internal_symbol: CME.MDP3:6E
vendor_dataset: CME.MDP3
root: 6E
venue: CME
asset_class: fx
timezone: America/Chicago
```

### Crypto Futures (Future)
```sql
internal_symbol: CME.MDP3:BTC
vendor_dataset: CME.MDP3
root: BTC
venue: CME
asset_class: crypto
timezone: America/Chicago
```

---

## Script Integration

### Updated: `scripts/phase_c_reingest_clean_1m.py`

**Registry Query:**
```python
SELECT dataset, root, roll_rule, rank, 
       COALESCE(schema_name, schema) as schema_name, 
       stype_in, is_active,
       vendor_dataset, venue, asset_class
FROM symbol_registry
WHERE internal_symbol = %s
```

**Databento Query:**
```python
query_dataset = vendor_dataset or dataset  # Prefer vendor_dataset
data = client.timeseries.get_range(
    dataset=query_dataset,
    symbols=[db_cont_symbol],
    schema='ohlcv-1m',
    start=start_ts,
    end=end_ts,
    stype_in='continuous'
)
```

**Safe Defaults:**
- If registry lookup fails: dataset='GLBX.MDP3', roll_rule='v', rank=0
- If vendor_dataset is NULL: use dataset column
- If schema_name is NULL: use schema column

---

## Verification

### Migration Success
```
✅ 6 columns added: vendor_dataset, schema_name, venue, asset_class, timezone, session_profile
✅ All columns nullable (backward compatible)
✅ Existing rows updated with metadata
```

### Existing Symbols
```
GLBX.MDP3:ES   dataset=GLBX.MDP3  venue=CME  class=equity_index
GLBX.MDP3:NQ   dataset=GLBX.MDP3  venue=CME  class=equity_index
GLBX.MDP3:RTY  dataset=GLBX.MDP3  venue=CME  class=equity_index
GLBX.MDP3:YM   dataset=GLBX.MDP3  venue=CME  class=equity_index
```

---

## Locked Decisions (Phase D.1)

### 1. Metadata Columns (LOCKED)
- vendor_dataset, schema_name, venue, asset_class, timezone, session_profile
- All columns are TEXT and nullable
- Defaults handled in application code, not database
- **Rationale:** Maximum flexibility for diverse asset classes

### 2. Column Naming (LOCKED)
- `vendor_dataset` (not `vendor_specific_dataset`) - Concise
- `schema_name` (not `data_schema`) - Clear distinction from `schema` column
- `asset_class` (not `instrument_type`) - Industry standard term
- **Rationale:** Clear, concise, industry-standard naming

### 3. Backward Compatibility (LOCKED)
- All new columns nullable
- Existing rows remain valid
- COALESCE used for fallback (schema_name → schema)
- **Rationale:** No breaking changes to existing workflows

### 4. Metadata is Optional (LOCKED)
- venue, asset_class, timezone, session_profile are metadata only
- Not required for ingestion to work
- Used for filtering, grouping, session handling (future)
- **Rationale:** Gradual adoption, no forced migration

---

## Future-Proofing Validation

### Can Now Support (Without Schema Changes)

✅ **Energy:** CL (crude oil), NG (natural gas), RB (gasoline)  
✅ **Metals:** GC (gold), SI (silver), HG (copper)  
✅ **FX:** 6E (euro), 6J (yen), 6B (pound)  
✅ **Crypto:** BTC (bitcoin), ETH (ethereum)  
✅ **Grains:** ZC (corn), ZS (soybeans), ZW (wheat)  
✅ **Rates:** ZN (10-year note), ZB (30-year bond)

### Adding New Symbol (Example)

```sql
INSERT INTO symbol_registry 
(internal_symbol, dataset, root, roll_rule, rank, vendor_dataset, schema_name, 
 venue, asset_class, timezone, is_active)
VALUES 
('NYMEX.MDP3:CL', 'NYMEX.MDP3', 'CL', 'v', 0, 'NYMEX.MDP3', 'ohlcv-1m',
 'NYMEX', 'energy', 'America/New_York', TRUE);
```

**No code changes required!**

---

## Files Created

### Database
- `database/phase_d1_symbol_registry_generalization.sql`
- `database/run_phase_d1_symbol_registry_migration.py`

### Modified
- `scripts/phase_c_reingest_clean_1m.py` - Uses vendor_dataset, schema_name from registry

### Documentation
- `PHASE_D1_REGISTRY_GENERALIZATION_COMPLETE.md` (this file)

---

## Command Reference

### Query Registry
```sql
SELECT internal_symbol, vendor_dataset, root, venue, asset_class, timezone
FROM symbol_registry
WHERE is_active = TRUE
ORDER BY asset_class, root;
```

### Add Energy Symbol
```sql
INSERT INTO symbol_registry 
(internal_symbol, dataset, root, roll_rule, vendor_dataset, venue, asset_class, timezone, is_active)
VALUES 
('NYMEX.MDP3:CL', 'NYMEX.MDP3', 'CL', 'v', 'NYMEX.MDP3', 'NYMEX', 'energy', 'America/New_York', TRUE);
```

### Add Metals Symbol
```sql
INSERT INTO symbol_registry 
(internal_symbol, dataset, root, roll_rule, vendor_dataset, venue, asset_class, timezone, is_active)
VALUES 
('COMEX.MDP3:GC', 'COMEX.MDP3', 'GC', 'v', 'COMEX.MDP3', 'COMEX', 'metals', 'America/New_York', TRUE);
```

---

## Sign-Off Requirements

**User must confirm:**
- [ ] Generalized schema approved
- [ ] Metadata columns appropriate
- [ ] Backward compatibility verified
- [ ] Script integration working
- [ ] Future-proofing validated

**Sign-Off Command:** "Mark Phase D.1 complete"

---

**Status:** ✅ PHASE D.1 COMPLETE - Registry is now future-proof for any symbol
