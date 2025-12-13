"""
Test SIGNAL_CREATED Reconciliation (Tier 0)
"""

from hybrid_sync.signal_created_reconciler import SignalCreatedReconciler
from hybrid_sync.gap_detector import GapDetector

print("=" * 80)
print("SIGNAL_CREATED RECONCILIATION TEST (TIER 0)")
print("=" * 80)
print()

# Step 1: Check current gaps
print("STEP 1: Detecting current gaps...")
detector = GapDetector()
gap_report = detector.run_complete_scan()

print(f"Total gaps before reconciliation: {gap_report['total_gaps']}")
print(f"Health score before: {gap_report['health_score']}/100")
print()

# Show gap breakdown
print("Gaps by type:")
for gap_type, count in gap_report['gaps_by_type'].items():
    if count > 0:
        print(f"  {gap_type}: {count}")

print()
print("=" * 80)
print("STEP 2: Running SIGNAL_CREATED reconciliation...")
print("=" * 80)
print()

# Step 2: Run SIGNAL_CREATED reconciliation
reconciler = SignalCreatedReconciler()

# Get signals that can be filled from SIGNAL_CREATED
signals_with_gaps = reconciler.get_all_signals_with_gaps()
print(f"Signals with gaps fillable from SIGNAL_CREATED: {len(signals_with_gaps)}")

if signals_with_gaps:
    print(f"\nSample trade_ids:")
    for trade_id in signals_with_gaps[:5]:
        print(f"  {trade_id}")
    
    # Run reconciliation
    print()
    results = reconciler.reconcile_all_from_signal_created()
    
    print()
    print("=" * 80)
    print("RECONCILIATION RESULTS")
    print("=" * 80)
    print(f"Signals attempted: {results['signals_attempted']}")
    print(f"HTF alignment filled: {results['htf_filled']}")
    print(f"Metadata filled: {results['metadata_filled']}")
    print(f"Confirmation time filled: {results['confirmation_filled']}")
    print(f"Total fields filled: {results['total_filled']}")
    
    # Step 3: Check gaps after reconciliation
    print()
    print("=" * 80)
    print("STEP 3: Checking gaps after reconciliation...")
    print("=" * 80)
    print()
    
    gap_report_after = detector.run_complete_scan()
    
    print(f"Total gaps after reconciliation: {gap_report_after['total_gaps']}")
    print(f"Health score after: {gap_report_after['health_score']}/100")
    print()
    
    # Show improvement
    gaps_eliminated = gap_report['total_gaps'] - gap_report_after['total_gaps']
    health_improvement = gap_report_after['health_score'] - gap_report['health_score']
    
    print("=" * 80)
    print("IMPROVEMENT SUMMARY")
    print("=" * 80)
    print(f"Gaps eliminated: {gaps_eliminated}")
    print(f"Health score improvement: +{health_improvement} points")
    print()
    
    if gaps_eliminated > 0:
        print("✅ SIGNAL_CREATED reconciliation successfully filled gaps!")
    else:
        print("⚠️ No gaps were eliminated (may need other reconciliation tiers)")
else:
    print("\n✅ No signals need SIGNAL_CREATED reconciliation")

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
