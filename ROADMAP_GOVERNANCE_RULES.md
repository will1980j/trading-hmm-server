# Roadmap Governance Rules

**Effective Date:** 2025-12-28  
**Authority:** Single Source of Truth for System State

---

## Core Principles

### 1. Roadmap is the Single Source of Truth
- All system state is reflected in the roadmap
- Roadmap status overrides all other documentation
- No work is complete until roadmap is updated
- Conflicting information defers to roadmap

### 2. Phase-Based Development
- Work proceeds in sequential phases
- Each phase has clear objectives and success criteria
- No work on Phase N+1 until Phase N is signed off
- Phase dependencies must be respected

### 3. User-Driven Completion
- Only the user can mark phases complete
- Completion requires explicit user approval
- Kiro cannot self-approve phase completion
- User approval is based on real-world validation

---

## Phase Completion Process

### Step 1: Implementation
- Kiro implements phase objectives
- All success criteria must be met
- Verification artifacts must be created
- Known limitations must be documented

### Step 2: Verification
- User reviews implementation
- User tests in real-world scenarios
- User validates against success criteria
- User identifies any issues or gaps

### Step 3: Sign-Off
- User explicitly approves: "Mark Phase [X] complete"
- Kiro updates roadmap-tracker.md
- Kiro updates UNIFIED_ROADMAP.md (if applicable)
- Kiro updates roadmap_state.py (if applicable)

### Step 4: Lock
- Phase decisions are LOCKED
- Later phases cannot violate locked decisions
- Changes to locked decisions require phase re-opening
- User must approve any locked decision changes

---

## Verification Artifacts Required

### For Each Phase:
1. **Success Criteria Document**
   - List of all success criteria
   - Verification status for each criterion
   - Evidence of completion

2. **Implementation Artifacts**
   - Database schemas
   - Scripts and tools
   - Tests and validation
   - Documentation

3. **Locked Decisions Document**
   - Core architectural decisions
   - Constraints for future phases
   - Rationale for each decision
   - Impact of violating decisions

4. **Known Limitations Document**
   - Current constraints
   - Workarounds available
   - Future resolution plans
   - Impact on next phases

---

## Locked Decision Enforcement

### What Gets Locked:
- **Data schemas** - Table structures, column types, constraints
- **Timestamp semantics** - How timestamps are interpreted
- **Validation rules** - Data quality gates and filters
- **API contracts** - Function signatures, return types
- **Conventions** - Naming, formatting, organization

### What Can Change:
- **Performance optimizations** - As long as behavior is identical
- **Bug fixes** - Corrections that don't change core logic
- **Documentation** - Clarifications and improvements
- **Tooling** - New scripts that don't modify locked behavior

### Violation Process:
1. **Identify violation** - Later phase attempts to change locked decision
2. **Halt work** - Stop implementation immediately
3. **Consult user** - Explain violation and request approval
4. **Re-open phase** - If approved, re-open earlier phase
5. **Update roadmap** - Document decision change and rationale

---

## Phase Dependency Rules

### Sequential Execution
- Phase B cannot start until Phase A is complete
- Phase C cannot start until Phase B is complete
- Phase D cannot start until Phase C is complete
- No parallel phase work allowed

### Dependency Validation
- Each phase lists its prerequisites
- Prerequisites must be met before starting
- Missing prerequisites block phase start
- User can override with explicit approval

### Backward Compatibility
- Later phases must respect earlier phase decisions
- Breaking changes require earlier phase re-opening
- Compatibility must be maintained unless explicitly approved
- Migration paths required for breaking changes

---

## Roadmap Update Requirements

### When to Update:
- **Phase completion** - Mark phase as complete with summary
- **Phase start** - Mark phase as in-progress
- **Blocking issues** - Document what's blocking progress
- **Major milestones** - Update progress within phase
- **Locked decisions** - Document new constraints

### What to Update:
- **roadmap-tracker.md** - Current status and recent changes
- **UNIFIED_ROADMAP.md** - High-level roadmap (if applicable)
- **roadmap_state.py** - Programmatic state (if applicable)
- **Phase summary docs** - Detailed completion artifacts

### Update Checklist:
- [ ] Phase status updated (PLANNED/IN-PROGRESS/COMPLETE)
- [ ] Success criteria documented
- [ ] Verification artifacts listed
- [ ] Locked decisions documented
- [ ] Known limitations identified
- [ ] Next phase prerequisites updated
- [ ] Recent changes log updated

---

## Current Roadmap State

### Completed Phases
- **Phase A:** Deterministic Replay Foundation ✅
- **Phase B:** Indicator Parity Modules ✅
- **Phase C:** Triangle Backfill & Parity Testing ✅ (awaiting sign-off)

### Planned Phases
- **Phase D:** Scalable Signal Storage ⏳ (blocked by Phase C sign-off)

### Active Work
- Phase C verification and sign-off
- No new implementation until sign-off

---

## Enforcement

### Kiro's Responsibilities:
1. **Respect phase boundaries** - No work on future phases
2. **Update roadmap** - Keep roadmap current with all work
3. **Document decisions** - Lock decisions as phases complete
4. **Verify prerequisites** - Check dependencies before starting phases
5. **Request approval** - Never self-approve phase completion

### User's Responsibilities:
1. **Review work** - Validate phase completion
2. **Approve phases** - Explicitly sign off on completed work
3. **Validate parity** - Test against real-world scenarios
4. **Approve changes** - Review locked decision violations

---

## Violation Consequences

### If Kiro Violates:
- **Immediate halt** - Stop all work
- **Rollback** - Revert unauthorized changes
- **Explain** - Document what was violated and why
- **Request approval** - Get explicit user approval to proceed

### If User Requests Violation:
- **Explain impact** - Show what will be affected
- **Propose alternatives** - Suggest non-violating approaches
- **Document approval** - Record user's explicit approval
- **Update roadmap** - Reflect decision change

---

## Phase C Locked Decisions

### 1. Timestamp Semantics
- Clean table: ts = bar OPEN time
- Legacy table: ts = bar CLOSE time
- Triangle events: ts = bar OPEN time
- **Cannot be changed without Phase C re-opening**

### 2. Data Hygiene Rules
- OHLC_INTEGRITY, PRICE_LT_1000, DISCONTINUITY_500
- SMALL_RANGE_BIG_GAP_150, FLAT_DISCONTINUITY_50
- No median-based filtering
- **Cannot be changed without Phase C re-opening**

### 3. Databento Symbology
- Internal: GLBX.MDP3:NQ
- Continuous: NQ.v.0 (root.roll_rule.rank)
- Roll rules: c/n/v only
- **Cannot be changed without Phase C re-opening**

### 4. Batch Insert Strategy
- Batch size: 500 rows
- Commit per batch
- Automatic reconnection with 1 retry
- **Cannot be changed without Phase C re-opening**

---

## Sign-Off Status

**Phase C:** ✅ COMPLETE - Awaiting user approval

**User must confirm:** "Mark Phase C complete"

**After sign-off:**
- Phase C decisions are LOCKED
- Phase D work can begin
- Roadmap updated to reflect completion

---

**Governance Status:** ✅ ACTIVE - All rules in effect
