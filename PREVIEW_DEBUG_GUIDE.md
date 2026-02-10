# Preview Reset Bug - Debugging Guide

**Date:** 2026-02-10  
**Issue:** After going through the flow, clicking preview jumps back to initial state instead of showing the preview page  
**Status:** 🔧 Debug logging added

---

## Problem Analysis

When you click "Preview & Save" or "Preview Listing", instead of showing the preview page, it resets to the initial upload state.

### Root Cause Identified

The issue is likely caused by **incomplete state persistence**. The original code was saving form data to localStorage but **NOT saving**:
- ✗ `synthesisData` (AI property overview)
- ✗ `individualAnalyses` (per-image AI analysis)
- ✗ `uploadedImages` (image URLs/data)
- ✗ `showPreview` (preview visibility flag)

**Result:** When state is restored (e.g., after component remount or during lifecycle), these critical values are lost, causing the preview to fail and reset to initial state.

---

## Changes Made

### 1. Enhanced State Persistence

**File:** `frontend/src/App.svelte`

**Before:**
```javascript
function saveCurrentState() {
  const state = {
    formData: listingStore.toJSON(),
    schema: formSchema,
    aiMessage,
    currentStep,
    completionPercentage
    // ❌ Missing: synthesisData, individualAnalyses, uploadedImages, showPreview
  };
  localStorage.setItem('mobi_listing_state', JSON.stringify(state));
}
```

**After:**
```javascript
function saveCurrentState() {
  const state = {
    formData: listingStore.toJSON(),
    schema: formSchema,
    aiMessage,
    currentStep,
    completionPercentage,
    synthesisData,           // ✅ Added
    individualAnalyses,      // ✅ Added
    uploadedImages,          // ✅ Added
    showPreview              // ✅ Added
  };
  console.log('💾 Saving state:', state);
  localStorage.setItem('mobi_listing_state', JSON.stringify(state));
}
```

### 2. Enhanced State Loading

**Before:**
```javascript
function loadSavedState() {
  const saved = localStorage.getItem('mobi_listing_state');
  if (saved) {
    const state = JSON.parse(saved);
    listingStore.loadState(state.formData);
    formSchema = state.schema || [];
    aiMessage = state.aiMessage || '';
    currentStep = state.currentStep || 0;
    completionPercentage = state.completionPercentage || 0;
    // ❌ Not restoring images/synthesis/preview state
  }
}
```

**After:**
```javascript
function loadSavedState() {
  const saved = localStorage.getItem('mobi_listing_state');
  if (saved) {
    const state = JSON.parse(saved);
    console.log('📂 Loading saved state:', state);
    listingStore.loadState(state.formData);
    formSchema = state.schema || [];
    aiMessage = state.aiMessage || '';
    currentStep = state.currentStep || 0;
    completionPercentage = state.completionPercentage || 0;
    synthesisData = state.synthesisData || null;        // ✅ Added
    individualAnalyses = state.individualAnalyses || []; // ✅ Added
    uploadedImages = state.uploadedImages || [];        // ✅ Added
    showPreview = state.showPreview || false;           // ✅ Added
    console.log('✅ State loaded successfully');
  }
}
```

### 3. Added Comprehensive Debug Logging

**Console logs added:**

```javascript
// On mount
console.log('🚀 App mounted');

// In handleFormComplete
console.log('=== handleFormComplete called ===');
console.log('listingData:', listingStore.toJSON());
console.log('synthesisData:', synthesisData);
console.log('uploadedImages:', uploadedImages);
console.log('completionPercentage:', completionPercentage);

// Reactive watcher for showPreview
$: {
  if (showPreview) {
    console.log('🔵 showPreview changed to TRUE');
  } else {
    console.log('🔴 showPreview changed to FALSE');
  }
}

// In saveCurrentState
console.log('💾 Saving state:', state);

// In loadSavedState
console.log('📂 Loading saved state:', state);
console.log('✅ State loaded successfully');
```

### 4. Added Validation in handleFormComplete

```javascript
// Verify minimum data requirements
const listingData = listingStore.toJSON();
if (!listingData.property_type) {
  console.error('ERROR: property_type is missing!');
  error = 'Please select a property type before previewing';
  return;
}

if (uploadedImages.length === 0) {
  console.error('ERROR: No images uploaded!');
  error = 'Please upload at least one image before previewing';
  return;
}
```

### 5. Save State After Preview Trigger

```javascript
function handleFormComplete() {
  // ... validation ...
  showPreview = true;
  saveCurrentState(); // ✅ Persist preview state immediately
}
```

---

## How to Debug

### Step 1: Open Browser DevTools

```bash
cd /home/ubuntu/mobi

# Terminal 1: Backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Open browser: http://localhost:5173
# Press F12 to open DevTools → Go to Console tab
```

### Step 2: Go Through the Flow

1. Upload an image
2. Select property type (e.g., "Apartment")
3. Fill some fields
4. Click "Preview & Save"

### Step 3: Watch Console Output

**Expected console output:**

```
🚀 App mounted
📂 Loading saved state: { ... }
✅ State loaded successfully

[After upload]
💾 Saving state: { uploadedImages: [...], synthesisData: {...}, ... }

[After clicking "Preview & Save"]
=== handleFormComplete called ===
listingData: { property_type: "apartment", ... }
synthesisData: { total_rooms: 4, ... }
uploadedImages: ["data:image/png;base64,..."]
individualAnalyses: [{ description: "...", ... }]
completionPercentage: 45
All checks passed, setting showPreview = true
showPreview is now: true
💾 Saving state: { showPreview: true, ... }
🔵 showPreview changed to TRUE
  - listingData: { property_type: "apartment", ... }
  - images: 1
```

**If bug still occurs, you might see:**

```
=== handleFormComplete called ===
listingData: { property_type: "apartment", ... }
synthesisData: null  ⚠️ THIS IS BAD
uploadedImages: []   ⚠️ THIS IS BAD
ERROR: No images uploaded!
```

or

```
🔵 showPreview changed to TRUE
[milliseconds later]
🔴 showPreview changed to FALSE  ⚠️ SOMETHING RESET IT
```

### Step 4: Check localStorage

In DevTools Console, run:
```javascript
JSON.parse(localStorage.getItem('mobi_listing_state'))
```

**Expected output:**
```json
{
  "formData": { "property_type": "apartment", ... },
  "schema": [...],
  "aiMessage": "...",
  "currentStep": 3,
  "completionPercentage": 45,
  "synthesisData": { "total_rooms": 4, ... },
  "individualAnalyses": [...],
  "uploadedImages": ["data:image/png;base64,..."],
  "showPreview": true
}
```

If any of these are `null`, `[]`, or `false` when they shouldn't be, that's the problem.

---

## Possible Issues & Solutions

### Issue 1: Images Not Persisting

**Symptom:** `uploadedImages: []` in console log

**Possible causes:**
- Images not being added to `uploadedImages` array after upload
- handleBatchUpload not being called
- Image data being lost during serialization

**Check:**
```javascript
// In handleBatchUpload
console.log('Images received:', imageUrls);
console.log('uploadedImages before:', uploadedImages);
console.log('uploadedImages after:', [...uploadedImages, ...imageUrls]);
```

### Issue 2: Synthesis Data Missing

**Symptom:** `synthesisData: null` in console log

**Possible causes:**
- API call to `/api/analyze-batch` failing
- Response not being parsed correctly
- synthesisData not being set in handleBatchUpload

**Check network tab:**
- Look for `/api/analyze-batch` request
- Check if response contains `synthesis` object
- Verify response is 200 OK

### Issue 3: showPreview Flipping Back to False

**Symptom:** Preview appears briefly then disappears

**Possible causes:**
- Component remounting
- Error causing reset
- Parent component forcing re-render

**Check console for:**
```
🔵 showPreview changed to TRUE
🔴 showPreview changed to FALSE  ← What triggered this?
```

Look for any error messages or function calls between TRUE and FALSE.

### Issue 4: ListingPreview Component Error

**Symptom:** Preview doesn't render at all, blank screen

**Possible causes:**
- Missing required props
- Error in ListingPreview component
- CSS issue hiding content

**Check:**
1. Browser DevTools → Elements tab
2. Look for `<div class="listing-preview">` element
3. Check if it exists but is hidden (display: none, opacity: 0)
4. Check Console for React/Svelte errors

---

## Common Fixes

### Fix 1: Clear localStorage and Try Again

```javascript
// In browser console
localStorage.removeItem('mobi_listing_state');
// Then refresh page and try flow again
```

### Fix 2: Check Network Errors

- Open Network tab in DevTools
- Filter by "Fetch/XHR"
- Look for failed API calls (red status)
- Click on failed call to see error details

### Fix 3: Check Backend Logs

```bash
# Terminal running backend
# Look for error messages when preview is clicked
# Example: "ERROR: ..." or stack traces
```

---

## If Still Broken

### Collect Debug Info

1. **Console logs** - Copy all console output during the flow
2. **Network tab** - Screenshot of all API calls
3. **localStorage** - Copy `localStorage.getItem('mobi_listing_state')`
4. **Error messages** - Any red text in console
5. **State dump** - Run this in console when bug occurs:

```javascript
{
  listingData: window.listingStore?.toJSON(),
  showPreview: /* inspect in React DevTools */,
  uploadedImages: /* inspect in React DevTools */,
  synthesisData: /* inspect in React DevTools */
}
```

### Share This Info

- Console logs
- localStorage content
- Network request details
- Any error messages

---

## Next Steps

After collecting debug info:

1. **If images missing:** Check `handleBatchUpload` and `MultiImageUpload.svelte`
2. **If synthesis missing:** Check `/api/analyze-batch` endpoint response
3. **If showPreview flips:** Check for component remount or error
4. **If validation fails:** Check minimum requirements logic

---

## Clean Up Debug Logs (Later)

Once bug is fixed, remove console.log statements:

```bash
cd /home/ubuntu/mobi
grep -n "console.log" frontend/src/App.svelte
# Manually remove debug logs or use sed
```

But keep them for now - they're essential for debugging!
