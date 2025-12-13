"""
Test Hybrid Sync System Status
"""

from hybrid_sync.gap_detector import GapDetector
from hybrid_sync.reconciliation_engine import ReconciliationEngine

print("=" * 80)
print("HYBRID SIGNAL SYNCHRONIZATION SYSTEM - STATUS CHECK")
print("=" * 80)
print()

# Run gap detection
print("🔍 Running gap detection scan...")
detector = GapDetector()
report = detector.run_complete_scan()

print()
print("=" * 80)
print("GAP DETECTION REPORT")
print("=" * 80)
print(f"Total Gaps: {report['total_gaps']}")
print(f"Health Score: {report['health_score']}/100")
print()

if report['total_gaps'] > 0:
    print("Gaps by Type:")
    for gap_type, count in report['gaps_by_type'].items():
        if count > 0:
            print(f"  {gap_type}: {count}")
    
    print()
    print("=" * 80)
    print("SAMPLE GAP DETAILS")
    print("=" * 80)
    
    # Show first gap of each type
    for gap_type, gap_list in report['gap_details'].items():
        if gap_list:
            print(f"\n{gap_type} (showing first):")
            gap = gap_list[0]
            for key, value in gap.items():
                print(f"  {key}: {value}")
else:
    print("✅ No gaps detected - system is healthy!")

print()
print("=" * 80)
print("RECONCILIATION ENGINE TEST")
print("=" * 80)

# Test current price retrieval
engine = ReconciliationEngine()
current_price = engine.get_current_price()
print(f"Current NQ Price: {current_price}")

print()
print("=" * 80)
print("STATUS CHECK COMPLETE")
print("=" * 80)
