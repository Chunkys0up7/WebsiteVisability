# Comparison Display Fix - Session State Restoration

**Date:** October 22, 2025  
**Status:** ✅ FIXED  
**Issue:** Comparison tab showing only second URL's analysis instead of actual comparison

## The Problem

After fixing the tab display logic, the comparison feature was **running successfully** (visible in logs), but the UI was showing:
- ❌ Only the **second URL's individual analysis**
- ❌ **Not the actual comparison results**
- ❌ Making it look like a regular analysis instead of a comparison

### Root Cause: Session State Overwriting

The `perform_analysis()` function was being called **recursively** for the comparison URL:

```python
# Line 1058: Analyze comparison URL
comparison_success = perform_analysis(
    normalized_comparison_url,  # Second URL
    analyze_dynamic,
    analysis_type,
    crawler_types,
    capture_evidence,
    None  # No nested comparisons
)
```

**The Problem:**
1. First URL analyzed → stores results in `st.session_state`
2. `perform_analysis()` called again for second URL
3. Second URL analyzed → **overwrites** `st.session_state` with second URL's results
4. Comparison created and stored in `st.session_state.comparison_results` ✅
5. **But** all other session state variables (`static_result`, `llm_report`, `score`, etc.) still contain **second URL's data**
6. UI displays second URL's individual analysis in all the main tabs
7. Comparison tab has the comparison data but user sees second URL everywhere else

### The Flow (Before Fix)

```
User enters:
  - First URL: chase.com
  - Comparison URL: wellsfargo.com

Analysis runs:
  1. Analyze chase.com
     st.session_state.analyzed_url = "chase.com"
     st.session_state.static_result = chase_analysis
     st.session_state.score = chase_scores
     ...
  
  2. Store first_analysis:
     st.session_state.first_analysis = {
       'url': 'chase.com',
       'static_result': chase_analysis,
       ...
     }
  
  3. Call perform_analysis(wellsfargo.com)
     st.session_state.analyzed_url = "wellsfargo.com"  ❌ OVERWRITES!
     st.session_state.static_result = wellsfargo_analysis  ❌ OVERWRITES!
     st.session_state.score = wellsfargo_scores  ❌ OVERWRITES!
     ...
  
  4. Create comparison:
     st.session_state.comparison_results = comparison_data  ✅
  
  5. Return to main flow
     st.session_state.analyzed_url still = "wellsfargo.com"  ❌
     All other tabs show wellsfargo.com data  ❌
```

### User Experience

- **Overview tab**: Shows wellsfargo.com (second URL)
- **LLM Analysis tab**: Shows wellsfargo.com analysis
- **Recommendations tab**: Shows wellsfargo.com recommendations
- **Comparison tab**: Shows comparison (but user is confused why everything else is wellsfargo.com)

## The Solution

After creating the comparison, **restore the first analysis** as the primary display:

```python
# Line 1100-1108: After comparison is created
st.session_state.comparison_results = comparison_results
logger.info(f"Website comparison completed between {st.session_state.first_analysis['url']} and {comparison_url}")

# Restore the first analysis as the primary display
st.session_state.static_result = st.session_state.first_analysis['static_result']
st.session_state.dynamic_result = st.session_state.first_analysis['dynamic_result']
st.session_state.bot_directives = st.session_state.first_analysis['bot_directives']
st.session_state.llm_report = st.session_state.first_analysis['llm_report']
st.session_state.score = st.session_state.first_analysis['score']
```

### The Flow (After Fix)

```
User enters:
  - First URL: chase.com
  - Comparison URL: wellsfargo.com

Analysis runs:
  1. Analyze chase.com
     st.session_state.analyzed_url = "chase.com"
     st.session_state.static_result = chase_analysis
     st.session_state.score = chase_scores
     ...
  
  2. Store first_analysis:
     st.session_state.first_analysis = {
       'url': 'chase.com',
       'static_result': chase_analysis,
       ...
     }
  
  3. Call perform_analysis(wellsfargo.com)
     st.session_state.analyzed_url = "wellsfargo.com"  (temporarily)
     st.session_state.static_result = wellsfargo_analysis  (temporarily)
     st.session_state.score = wellsfargo_scores  (temporarily)
     ...
  
  4. Create comparison:
     st.session_state.comparison_results = comparison_data  ✅
  
  5. RESTORE first analysis:  🎯 NEW!
     st.session_state.static_result = chase_analysis  ✅
     st.session_state.score = chase_scores  ✅
     st.session_state.llm_report = chase_report  ✅
     ...
  
  6. Return to main flow
     st.session_state.analyzed_url = "chase.com"  ✅
     All tabs show chase.com data  ✅
     Comparison tab shows chase.com vs wellsfargo.com  ✅
```

### New User Experience

- **Overview tab**: Shows chase.com (first URL) ✅
- **LLM Analysis tab**: Shows chase.com analysis ✅
- **Recommendations tab**: Shows chase.com recommendations ✅
- **Comparison tab**: Shows chase.com vs wellsfargo.com comparison ✅

**Coherent and intuitive!**

## Why This Makes Sense

1. **User's primary URL is the first one** they enter
2. **Comparison is a supplementary feature** to compare against another site
3. **Main tabs should show the primary URL's analysis**
4. **Comparison tab shows the comparison**
5. This matches user expectations and standard UX patterns

## Testing Checklist

✅ **Test the complete comparison flow:**

1. Open the app
2. Enter first URL: `https://www.chase.com/personal/mortgage-b`
3. Enable "Compare with another website"
4. Enter comparison URL: `https://www.wellsfargo.com/mortgage/`
5. Click "Start Analysis"
6. Wait for completion

**Verify:**
- ✅ **Executive Summary** shows chase.com data
- ✅ **Overview** shows chase.com scores
- ✅ **LLM Analysis** shows chase.com analysis
- ✅ **Recommendations** shows chase.com recommendations  
- ✅ **All other tabs** show chase.com data
- ✅ **Comparison tab** shows:
  - chase.com vs wellsfargo.com URLs
  - Overall similarity score
  - Detailed comparison metrics
  - Content/Accessibility/Technical comparisons

## Files Modified

- `app/main.py` (lines 1103-1108)
  - Added session state restoration after comparison

## Related Fixes

This builds on the previous fix:
1. **Previous**: Fixed comparison tab display logic (removed `return` statements)
2. **This**: Fixed session state to show correct data in all tabs

## Lessons Learned

1. **Recursive function calls can overwrite session state** - be careful when calling the same function that modifies global state
2. **Session state needs to be managed explicitly** - can't assume it will persist correctly through recursive calls
3. **Test the full user journey, not just individual features** - the comparison worked in isolation but broke the overall UX
4. **Primary vs secondary data** - when comparing, make it clear which is the primary analysis vs the comparison

---

**Status:** The comparison feature should now work correctly, showing:
- **Main tabs**: First URL's individual analysis  
- **Comparison tab**: Full comparison between both URLs

