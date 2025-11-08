# BE=1 vs No BE MFE Tracking - Too Complex for Current Implementation

## Problem
Tracking two separate MFE values (BE=1 strategy vs No BE strategy) requires tracking two separate "stopped out" states, but we can't add more arrays due to performance constraints.

## Current Issues
- No BE MFE continues updating after original SL is hit because we check `original_sl_hit` only on current bar
- Once price bounces back, the check becomes false again and MFE continues growing
- We need persistent state tracking which requires additional arrays

## Recommendation
Disable BE=1 MFE tracking feature until we can implement proper state management or find a different approach.

The single MFE value (without BE comparison) works correctly and provides valuable information.
