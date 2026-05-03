# 🧪 Testing Guide - AnkiAI v2.0

Hướng dẫn kiểm tra toàn bộ chức năng của add-on.

---

## Part 1: Installation & Basic Functionality

### Test 1.1: Installation

- [ ] Download AnkiAI add-on
- [ ] Extract to Anki addons21 folder
- [ ] Restart Anki
- [ ] Check: Add-ons > AnkiAI appears in list
- [ ] Status: ✅ / ❌

### Test 1.2: Menu Appearance

- [ ] Open Browser (Ctrl+B)
- [ ] Right-click on a card
- [ ] See: "AnkiAI: Tự động thêm ảnh bằng AI" menu
- [ ] Status: ✅ / ❌

### Test 1.3: First Run Setup

- [ ] Click menu
- [ ] Config dialog appears
- [ ] Can enter OpenAI API key
- [ ] Can select DALL-E or Search mode
- [ ] Can enter (optional) Pexels key
- [ ] Test Connection button works
- [ ] Status: ✅ / ❌

---

## Part 2: Api Integration Testing

### Test 2.1: OpenAI KeyValidation

- [ ] Enter invalid key → Error message
- [ ] Enter valid key → "Connection successful"
- [ ] Status: ✅ / ❌

### Test 2.2: Search Mode - Pexels Provider

- [ ] Set mode: Search
- [ ] Add Pexels API key
- [ ] Select 5 cards
- [ ] Process
- [ ] Check: Images added successfully
- [ ] Time: Should be < 2 min
- [ ] Status: ✅ / ❌

### Test 2.3: Search Mode - Unsplash Fallback

- [ ] Set mode: Search
- [ ] Add Unsplash key (remove Pexels key)
- [ ] Select 5 cards
- [ ] Process
- [ ] Check: Images added (from Unsplash)
- [ ] Status: ✅ / ❌

### Test 2.4: Search Mode - Multiple Providers (Fallback)

- [ ] Config: Set all 3 keys (Pexels, Unsplash, Pixabay)
- [ ] Select 10 cards
- [ ] Process
- [ ] Check: All 10 images added
- [ ] Check logs: Fallback working?
- [ ] Status: ✅ / ❌

### Test 2.5: DALL-E Mode

- [ ] Set mode: DALL-E
- [ ] Select 3 cards (small batch)
- [ ] Process
- [ ] Check: Unique AI-generated images added
- [ ] Time: Should be 5-15 min for 3 cards
- [ ] Status: ✅ / ❌

### Test 2.6: Keyword Caching

- [ ] Config: enable_keyword_cache = true
- [ ] Select 20 cards (same vocabulary repeats 5x)
- [ ] Process (first run)
- [ ] Check: ~20 API calls to OpenAI
- [ ] Select same 20 cards again
- [ ] Process (second run)
- [ ] Check: Cache hit! Only 5 new keywords generated
- [ ] Status: ✅ / ❌

---

## Part 3: Image Quality Testing

### Test 3.1: Mobile Responsive Images

- [ ] Add images using add-on
- [ ] View card on desktop browser
- [ ] Check: Images fit properly, not too big
- [ ] View card on iPad
- [ ] Check: Images scale down, still visible
- [ ] View card in AnkiDroid (mobile)
- [ ] Check: Images display perfectly ✅
- [ ] Status: ✅ / ❌

### Test 3.2: Image Optimization

- [ ] Enable: enable_image_optimization = true
- [ ] Add 10 images
- [ ] Check image file size
- [ ] Average size should be: 500KB-800KB
- [ ] Add 10 images with optimization OFF
- [ ] Average size should be: 1.5MB-2.5MB
- [ ] Compare: WITH optimization should be 60-75% smaller
- [ ] Status: ✅ / ❌

### Test 3.3: Image Loading (Lazy Load)

- [ ] Check HTML source of card
- [ ] Confirm: `loading="lazy"` attribute present
- [ ] Open many cards with images
- [ ] Check: Images load only when visible
- [ ] Performance: Better on slow connections
- [ ] Status: ✅ / ❌

---

## Part 4: Performance Testing

### Test 4.1: Speed Benchmark

**Test Setup**: 100 cards, Search mode, Pexels API

- [ ] Time start
- [ ] Select all 100 cards
- [ ] Process
- [ ] Record time
- [ ] Expected: 2-4 minutes
- [ ] PASS if: < 5 minutes
- [ ] Status: ✅ / ❌ (time: ___ min)

### Test 4.2: Memory Usage

During processing of 100 images:
- [ ] Check memory usage: Should not exceed 200MB
- [ ] PASS if: < 300MB peak
- [ ] Status: ✅ / ❌

### Test 4.3: CPU Usage

During processing of 100 images:
- [ ] Check CPU usage: Should be < 30%
- [ ] PASS if: Anki remains responsive
- [ ] Status: ✅ / ❌

### Test 4.4: Batch Processing

- [ ] Add 500 cards total
- [ ] Process batch 1: 100 cards
- [ ] Wait 5 min
- [ ] Process batch 2: 100 cards
- [ ] ... repeat
- [ ] Total time for 500: Should be ~20-40 minutes
- [ ] Check: No memory leaks
- [ ] Status: ✅ / ❌

---

## Part 5: Error Handling

### Test 5.1: Invalid API Key

- [ ] Enter wrong OpenAI key
- [ ] Select cards
- [ ] Process
- [ ] Expected: Clear error message
- [ ] No crash
- [ ] Status: ✅ / ❌

### Test 5.2: No Internet Connection

- [ ] Disable internet
- [ ] Try to generate images
- [ ] Expected: Timeout error (not hang)
- [ ] Switch back online
- [ ] Works again
- [ ] Status: ✅ / ❌

### Test 5.3: Some Cards Fail

- [ ] Select 10 cards
- [ ] 2 have empty vocabulary field
- [ ] Process
- [ ] Expected: 8 succeed, 2 fail gracefully
- [ ] Error message shows which failed
- [ ] Anki doesn't crash
- [ ] Status: ✅ / ❌

### Test 5.4: Network Timeout

- [ ] Slow internet simulation
- [ ] Process images with timeout=10s
- [ ] Expected: Auto retry 3 times
- [ ] Falls back to next provider
- [ ] Status: ✅ / ❌

---

## Part 6: Configuration Testing

### Test 6.1: Config Persistence

- [ ] Set: image_quality = 70
- [ ] Restart Anki
- [ ] Check: Config remembered = 70
- [ ] Change: image_quality = 95
- [ ] Restart
- [ ] Check: Updated to 95
- [ ] Status: ✅ / ❌

### Test 6.2: Field Selection

- [ ] Create note with custom fields
- [ ] Change vocabulary_field to "Term"
- [ ] Change image_field to "Picture"
- [ ] Process
- [ ] Images added to "Picture" field
- [ ] Status: ✅ / ❌

### Test 6.3: Timeout Settings

- [ ] Set image_download_timeout = 15
- [ ] Process slow connection
- [ ] Expected: Faster failure (good for slow internet)
- [ ] Set image_download_timeout = 30
- [ ] Process again
- [ ] Expected: More time to complete
- [ ] Status: ✅ / ❌

---

## Part 7: Compatibility Testing

### Test 7.1: Different Anki Versions

- [ ] Anki 24.04
- [ ] Anki 24.11 (latest)
- [ ] Expected: Works on both
- [ ] Status: ✅ / ❌

### Test 7.2: Operating Systems

- [ ] macOS 13+
  - [ ] Add-on loads
  - [ ] Images added
  - [ ] Status: ✅ / ❌

- [ ] Windows 10
  - [ ] Add-on loads
  - [ ] Images added
  - [ ] Status: ✅ / ❌

- [ ] Linux (Ubuntu)
  - [ ] Add-on loads
  - [ ] Images added
  - [ ] Status: ✅ / ❌

### Test 7.3: Different Note Types

- [ ] Basic type
- [ ] Cloze type
- [ ] Custom type (3+ fields)
- [ ] All work?: ✅ / ❌

### Test 7.4: AnkiWeb Sync

- [ ] Add images with add-on
- [ ] Sync to AnkiWeb
- [ ] Check: Images sync successfully
- [ ] Download on another computer
- [ ] Check: Images present
- [ ] Status: ✅ / ❌

---

## Part 8: Stress Tests

### Test 8.1: Large Batch

- [ ] Select 500 cards
- [ ] Process in batches of 100
- [ ] Expected: No crashes, all complete
- [ ] Status: ✅ / ❌

### Test 8.2: Rapid Requests

- [ ] Queue 10 batches
- [ ] Process several concurrently
- [ ] Expected: Handled gracefully
- [ ] Status: ✅ / ❌

### Test 8.3: Mixed Field Types

- [ ] Vocabulary: English word
- [ ] Definition: Multiple lines, HTML rich text
- [ ] Image: Multiple existing images
- [ ] Process
- [ ] Expected: Add new image without breaking existing content
- [ ] Status: ✅ / ❌

---

## Part 9: User Experience

### Test 9.1: UI Responsiveness

During 100-image processing:
- [ ] Anki menu still responsive
- [ ] Can click other cards (won't affect processing)
- [ ] Progress bar updates smoothly
- [ ] Status: ✅ / ❌

### Test 9.2: Error Messages

- [ ] Clear and helpful
- [ ] Not too technical
- [ ] Tell user what to do next
- [ ] Status: ✅ / ❌

### Test 9.3: Configuration UI

- [ ] Easy to find (Tools > Add-ons > AnkiAI > Config)
- [ ] Clearly labeled fields
- [ ] Help text available
- [ ] Status: ✅ / ❌

---

## Part 10: Regression Tests (Ensuring nothing broke)

### Test 10.1: v1.0 Config Compatibility

- [ ] Update from v1.0 to v2.0
- [ ] Old config still works
- [ ] No data loss
- [ ] New features enabled by default
- [ ] Status: ✅ / ❌

### Test 10.2: Existing Features

- [ ] DALL-E mode still works
- [ ] Search mode still works
- [ ] Field selection still works
- [ ] Error handling still works
- [ ] Status: ✅ / ❌

---

## Final Checklist

**Basic Functionality**: _____ / 6 passed  
**API Integration**: _____ / 6 passed  
**Image Quality**: _____ / 3 passed  
**Performance**: _____ / 4 passed  
**Error Handling**: _____ / 4 passed  
**Configuration**: _____ / 3 passed  
**Compatibility**: _____ / 4 passed  
**Stress Tests**: _____ / 3 passed  
**User Experience**: _____ / 3 passed  
**Regression**: _____ / 2 passed  

**Total**: _____ / 38 tests passed

---

## Release Criteria

✅ **READY TO RELEASE** if:
- All 38 tests passed
- Performance meets targets (< 5 min for 100 images)
- No crashes in stress tests
- Mobile images display properly

⚠️ **READY WITH WARNINGS** if:
- 35+ tests passed
- Known limitations documented

❌ **NOT READY** if:
- < 35 tests passed
- Crashes detected
- Critical bugs found

---

## Reporting Issues

If test fails:

1. Note test number and name
2. Record expected vs actual result
3. Note system (OS, Anki version)
4. Provide error message if any
5. File issue on GitHub

---

**Tester**: ________________  
**Date**: ________________  
**Anki Version**: ________________  
**OS**: ________________  
**Overall Status**: ✅ / ⚠️ / ❌

---

Thank you for testing AnkiAI v2.0! 🙏
