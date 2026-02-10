# How to Run E2E Test with Video Recording

## Test: Property Type Preservation

This test verifies that selecting "apartment" stays selected through multiple "Continue" clicks (doesn't get overwritten by backend null values).

## Prerequisites

**Terminal 1 - Backend:**
```bash
cd /home/ubuntu/mobi/backend
uv run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd /home/ubuntu/mobi/frontend
npm run dev
```

Wait until both are running before running tests!

## Run the Test with Video

**Option 1: Run just the property-type test**
```bash
cd /home/ubuntu/mobi/frontend
npm run test:e2e -- property-type-preservation
```

**Option 2: Run with visible browser (headed mode)**
```bash
npm run test:e2e -- property-type-preservation --headed
```

**Option 3: Run in debug mode (step through)**
```bash
npm run test:e2e -- property-type-preservation --debug
```

## Where to Find the Video

After the test runs, the video will be saved at:

```
/home/ubuntu/mobi/frontend/test-results/
└── property-type-preservation-chromium/
    └── video.webm  ← YOUR VIDEO!
```

**To find it:**
```bash
cd /home/ubuntu/mobi/frontend
find test-results -name "*.webm"
```

**Example output:**
```
test-results/property-type-preservation-should-preserve-property-type-selection-through-multiple-continue-clicks-chromium/video.webm
```

## Download the Video

**If you're SSH'd into the server:**

```bash
# From your local machine (not on server!)
cd ~/Downloads
scp ubuntu@your-server:/home/ubuntu/mobi/frontend/test-results/**/video.webm ./property-type-test.webm
```

**Or use the OpenClaw file browser** if available.

## What the Video Will Show

You'll see the browser:
1. ✅ Upload 2 images
2. ✅ Property overview appears at top
3. ✅ Select "apartment" from dropdown
4. ✅ Click "Continue" → more fields appear
5. ✅ Fill in price, bedrooms
6. ✅ Click "Continue" again → even more fields
7. ✅ Fill in bathrooms, square_feet
8. ✅ Click "Continue" to reach 100%
9. ✅ "Listing Complete!" message appears
10. ✅ Click "Preview Listing" button
11. ✅ Preview page loads (no error!)
12. ✅ Preview shows "apartment" in the listing

**Key moment:** After each "Continue" click, watch the dropdown - it should stay "apartment" and NOT reset to empty!

## Test Output in Console

You'll see:
```
Step 1: Uploading images...
Step 2: Selecting property_type = apartment
✓ property_type selected: apartment
Step 3: Clicking Continue (step 2)...
✓ After Continue click: property_type STILL apartment (not overwritten!)
Step 4: Clicking Continue again (step 3)...
✓ After 2nd Continue: property_type STILL apartment!
Step 5: Clicking Continue to reach 100%...
Step 6: Final check - property_type should STILL be apartment
✓ localStorage confirms: property_type = apartment
Step 7: Clicking Preview Listing...
Step 8: Verifying preview page loaded...
✅ SUCCESS! Preview loaded without property_type error!
✅ Preview page shows property_type = apartment
```

## If Test Fails

If the bug comes back:
- Video will show dropdown resetting to empty after "Continue"
- Console will show: `Expected "apartment", got null`
- Video saved in same location

## Clean Up Videos

Videos can get large. To clean up:
```bash
cd /home/ubuntu/mobi/frontend
rm -rf test-results/
```

## All E2E Tests with Video

To run ALL E2E tests and record videos:
```bash
npm run test:e2e
```

Videos will be in `test-results/` organized by test name.

---

**Quick Command Cheat Sheet:**

```bash
# Run test
cd /home/ubuntu/mobi/frontend && npm run test:e2e -- property-type-preservation

# Find video
find test-results -name "*.webm"

# View video (if on local machine with GUI)
open test-results/**/video.webm  # macOS
xdg-open test-results/**/video.webm  # Linux

# Or just navigate to the folder in file browser
```

Enjoy watching your test run! 🎥
