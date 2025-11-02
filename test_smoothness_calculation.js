// Test script for equity curve smoothness calculation
// Run this in browser console on Strategy Comparison page

console.log("🧪 Testing Smoothness Calculation Functions...\n");

// Test 1: Perfect linear growth (should score very high)
console.log("Test 1: Perfect Linear Growth");
const perfectResults = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]; // All wins
const perfectSmooth = calculateEquityCurveSmoothness(perfectResults);
console.log("Results:", perfectResults);
console.log("Smoothness Score:", perfectSmooth.smoothnessScore, "/100");
console.log("R-Squared:", perfectSmooth.rSquared);
console.log("Recovery Factor:", perfectSmooth.recoveryFactor);
console.log("Max Consecutive Losses:", perfectSmooth.maxConsecutiveLosses);
console.log("Expected: High score (90+), R² near 1.0, no losses\n");

// Test 2: Alternating wins/losses (should score medium)
console.log("Test 2: Alternating Wins/Losses");
const alternatingResults = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1];
const alternatingSmooth = calculateEquityCurveSmoothness(alternatingResults);
console.log("Results:", alternatingResults);
console.log("Smoothness Score:", alternatingSmooth.smoothnessScore, "/100");
console.log("R-Squared:", alternatingSmooth.rSquared);
console.log("Recovery Factor:", alternatingSmooth.recoveryFactor);
console.log("Max Consecutive Losses:", alternatingSmooth.maxConsecutiveLosses);
console.log("Expected: Medium score (60-75), lower R², max 1 loss streak\n");

// Test 3: Rough equity curve with streaks (should score low)
console.log("Test 3: Rough Curve with Loss Streaks");
const roughResults = [-1, -1, -1, -1, 2, 2, -1, -1, -1, 3];
const roughSmooth = calculateEquityCurveSmoothness(roughResults);
console.log("Results:", roughResults);
console.log("Smoothness Score:", roughSmooth.smoothnessScore, "/100");
console.log("R-Squared:", roughSmooth.rSquared);
console.log("Recovery Factor:", roughSmooth.recoveryFactor);
console.log("Max Consecutive Losses:", roughSmooth.maxConsecutiveLosses);
console.log("Expected: Low score (<60), lower R², max 4 loss streak\n");

// Test 4: Realistic scalping results
console.log("Test 4: Realistic Scalping Results");
const realisticResults = [
    1.5, -1, 0, 1.2, -1, 1.8, 0, -1, 1.3, 1.1,
    -1, 0, 1.4, -1, 1.6, 0, -1, 1.2, 1.5, -1
];
const realisticSmooth = calculateEquityCurveSmoothness(realisticResults);
console.log("Results:", realisticResults);
console.log("Smoothness Score:", realisticSmooth.smoothnessScore, "/100");
console.log("R-Squared:", realisticSmooth.rSquared);
console.log("Recovery Factor:", realisticSmooth.recoveryFactor);
console.log("Max Consecutive Losses:", realisticSmooth.maxConsecutiveLosses);
console.log("Max Drawdown Duration:", realisticSmooth.maxDrawdownDuration);
console.log("Expected: Medium-high score (70-85), good R², manageable streaks\n");

// Test 5: R-Squared calculation
console.log("Test 5: R-Squared Calculation");
const linearCurve = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]; // Perfect line
const rSquaredLinear = calculateRSquared(linearCurve);
console.log("Linear Curve:", linearCurve);
console.log("R-Squared:", rSquaredLinear);
console.log("Expected: 1.0 (perfect linear fit)\n");

const noisyCurve = [0, 1.2, 1.8, 3.1, 3.9, 5.2, 5.8, 7.1, 7.9, 9.2]; // Noisy line
const rSquaredNoisy = calculateRSquared(noisyCurve);
console.log("Noisy Curve:", noisyCurve);
console.log("R-Squared:", rSquaredNoisy);
console.log("Expected: 0.95+ (still very linear)\n");

console.log("✅ All tests complete!");
console.log("\n📊 Interpretation Guide:");
console.log("• Smoothness 90-100: Exceptionally smooth (institutional quality)");
console.log("• Smoothness 75-89: Very smooth (prop firm ready)");
console.log("• Smoothness 60-74: Acceptable (tradeable but bumpy)");
console.log("• Smoothness <60: Rough ride (psychological challenge)");
