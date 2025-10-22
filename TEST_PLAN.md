# Test Plan - Comparison & Scoring Display

**Date:** October 22, 2025  
**Objective:** Verify comparison feature and scoring breakdown display correctly

## Pre-Test Checklist

- [x] All Python processes killed
- [x] Code syntax validated (no errors)
- [x] Linter checks passed
- [x] Code review completed

## Test Scenarios

### Scenario 1: Score Breakdown Display

**Objective:** Verify scoring rationale is visible

**Steps:**
1. Start Streamlit app
2. Navigate to http://localhost:8501
3. Enter URL: `https://www.chase.com/personal/mortgage-b`
4. Click "Start Analysis"
5. Navigate to "Executive Summary" tab
6. Scroll down to "Component Scores" section

**Expected Results:**
- ✅ See "📊 How the total score is calculated" expander for Scraper Friendliness
- ✅ Expander shows:
  - Component contributions (percentages)
  - Final calculation formula
  - Total points breakdown
- ✅ Same for LLM Accessibility score

**Code Location:** Lines 1507-1523 (Scraper), 1563-1579 (LLM)

### Scenario 2: Comparison Feature

**Objective:** Verify website comparison displays correctly

**Steps:**
1. In sidebar, check "Compare with another website"
2. Enter comparison URL: `https://www.wellsfargo.com/mortgage/`
3. Click "Start Analysis"
4. Wait for both analyses to complete
5. Navigate to "Comparison" tab (14th tab in Reports section)

**Expected Results:**
- ✅ See "🔄 Website Comparison" header
- ✅ Debug expander shows:
  - `comparison_enabled: True`
  - `comparison_url: https://www.wellsfargo.com/mortgage/`
  - `comparison_results exists: True`
- ✅ Main display shows:
  - Both URLs being compared
  - Overall Similarity score
  - Score breakdown with methodology
  - Content comparison metrics
  - Accessibility comparison
  - Technical comparison
  - Recommendations

**Code Location:** Lines 2266-2510

### Scenario 3: Session State Verification

**Objective:** Ensure comparison doesn't overwrite first analysis

**Steps:**
1. After comparison analysis completes
2. Navigate to "Executive Summary" tab
3. Check "Last analyzed" URL

**Expected Results:**
- ✅ Should show FIRST URL (chase.com), not second URL
- ✅ Score cards should show first URL's scores
- ✅ Comparison tab should have separate comparison results

**Code Location:** Lines 1101-1127 (Session state restoration)

## Post-Test Actions

- [ ] Document any failures
- [ ] Screenshot evidence of success
- [ ] Update git with any fixes
- [ ] Mark test as PASSED/FAILED

## Known Issues

- **Dynamic analysis**: Expected to show "Unknown error" on Windows Store Python - this is normal and handled gracefully
- **Playwright errors**: asyncio NotImplementedError warnings in terminal - expected, can be ignored

## Success Criteria

ALL three scenarios must PASS for the test to be considered successful.



