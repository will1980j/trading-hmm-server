#!/usr/bin/env python3
"""
Phase D.3: Contract Tests for Historical API v1
"""

import pytest
import requests
from datetime import datetime

# Test against local or deployed instance
BASE_URL = "http://localhost:5000"  # Change to Railway URL for production tests

def test_world_endpoint_returns_bias_stack():
    """World endpoint returns correct bias stack for a known timestamp"""
    response = requests.get(f"{BASE_URL}/api/hist/v1/world", params={
        "symbol": "GLBX.MDP3:NQ",
        "ts": "2025-12-02T00:14:00Z",
        "include": "ohlcv,bias,triangles"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "timestamp" in data
    assert "symbol" in data
    assert "ohlcv" in data
    assert "bias" in data
    
    # Verify bias stack
    assert "1m" in data["bias"]
    assert "5m" in data["bias"]
    assert "15m" in data["bias"]
    assert "1h" in data["bias"]
    assert "4h" in data["bias"]
    assert "1d" in data["bias"]
    
    # Verify OHLCV structure
    assert "open" in data["ohlcv"]
    assert "high" in data["ohlcv"]
    assert "low" in data["ohlcv"]
    assert "close" in data["ohlcv"]

def test_dataset_row_count_equals_bars():
    """Dataset endpoint row count equals number of bars in window"""
    # Query a known window
    response = requests.get(f"{BASE_URL}/api/hist/v1/dataset", params={
        "symbol": "GLBX.MDP3:NQ",
        "start": "2025-12-02T00:10:00Z",
        "end": "2025-12-02T00:30:00Z",
        "include": "ohlcv"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Get bars count
    bars_response = requests.get(f"{BASE_URL}/api/hist/v1/bars", params={
        "symbol": "GLBX.MDP3:NQ",
        "start": "2025-12-02T00:10:00Z",
        "end": "2025-12-02T00:30:00Z"
    })
    
    assert bars_response.status_code == 200
    bars_data = bars_response.json()
    
    # Row counts should match
    assert data["count"] == bars_data["count"]
    assert len(data["rows"]) == len(bars_data["bars"])

def test_determinism_hash_identical_across_calls():
    """Determinism gate returns identical hash for repeated calls"""
    params = {
        "symbol": "GLBX.MDP3:NQ",
        "start": "2025-12-02T00:10:00Z",
        "end": "2025-12-02T00:20:00Z",
        "include": "ohlcv,bias"
    }
    
    # Call twice
    response1 = requests.get(f"{BASE_URL}/api/hist/v1/quality/determinism", params=params)
    response2 = requests.get(f"{BASE_URL}/api/hist/v1/quality/determinism", params=params)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    data1 = response1.json()
    data2 = response2.json()
    
    # Hashes must be identical
    assert data1["dataset_hash"] == data2["dataset_hash"]
    assert data1["row_count"] == data2["row_count"]
    assert data1["pass"] == True

def test_alignment_checks_pass_for_known_good_range():
    """Alignment quality gate passes for known good range"""
    response = requests.get(f"{BASE_URL}/api/hist/v1/quality/alignment", params={
        "symbol": "GLBX.MDP3:NQ",
        "start": "2025-12-02T00:10:00Z",
        "end": "2025-12-02T00:30:00Z"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "checks" in data
    assert "pass" in data
    
    # Verify alignment checks
    assert data["checks"]["timestamps_1m_aligned"]["pass"] == True
    assert data["checks"]["bias_timestamps_aligned"]["pass"] == True
    assert data["checks"]["timestamps_1m_aligned"]["misaligned_count"] == 0
    assert data["checks"]["bias_timestamps_aligned"]["misaligned_count"] == 0

def test_coverage_checks_pass_for_known_good_range():
    """Coverage quality gate passes for known good range"""
    response = requests.get(f"{BASE_URL}/api/hist/v1/quality/coverage", params={
        "symbol": "GLBX.MDP3:NQ",
        "start": "2025-12-02T00:10:00Z",
        "end": "2025-12-02T00:30:00Z"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify structure
    assert "checks" in data
    assert "pass" in data
    
    # Verify coverage checks
    assert data["checks"]["bars_1m_present"]["pass"] == True
    assert data["checks"]["bias_rows_present"]["pass"] == True
    assert data["checks"]["bars_1m_present"]["missing_count"] == 0

if __name__ == '__main__':
    # Run tests
    print("Running Phase D.3 Historical API Contract Tests...")
    print("=" * 80)
    
    tests = [
        ("World endpoint bias stack", test_world_endpoint_returns_bias_stack),
        ("Dataset row count", test_dataset_row_count_equals_bars),
        ("Determinism hash", test_determinism_hash_identical_across_calls),
        ("Alignment checks", test_alignment_checks_pass_for_known_good_range),
        ("Coverage checks", test_coverage_checks_pass_for_known_good_range)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    
    exit(0 if failed == 0 else 1)
