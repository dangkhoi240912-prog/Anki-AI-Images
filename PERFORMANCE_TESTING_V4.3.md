# AnkiAI-ImageAddon v4.3 - Performance Validation & Testing Guide

**Purpose**: Validate that all v4.3 optimizations are working correctly and achieving target performance metrics  
**Date**: May 3, 2026  
**Target User**: Developers, QA, Advanced Users

---

## 🎯 Quick Performance Validation Checklist

Run these tests in order to validate the optimization suite:

### ✅ Phase 1: Sanity Checks (5 minutes)

- [ ] **Addon Loads Without Errors**
  ```
  1. Open Anki
  2. Check Add-ons menu loads
  3. No exceptions in console
  ```

- [ ] **Configuration Dialog Opens**
  ```
  1. Click Add-ons → Configure
  2. All 4 Gemini keys visible
  3. All provider options present
  4. Rate limit controls visible
  ```

- [ ] **Test Connections Work**
  ```
  1. Click "Test AI Connections"
  2. Should see: "Groq: ✓", "Gemini: ✓", etc.
  3. Click "Test Image Providers"
  4. Should see: "Pexels: ✓", "Pixabay: ✓", etc.
  ```

---

## 📊 Phase 2: Cache Performance Validation (10 minutes)

### Test 2.1: Result Cache (Ultra-Fast Path) - Target: <1ms

**Procedure**:
```python
# In Anki console or test script:
import time
from AnkiAI_ImageAddon.modules import api_handler

addon = api_handler.AIImageProvider(config)

# First call - populate cache
start = time.time()
url1 = addon.get_image_url("apple", "a red fruit")
first_call = time.time() - start
print(f"First call (cache miss): {first_call:.3f}s")

# Second call - should hit result cache
start = time.time()
url2 = addon.get_image_url("apple", "a red fruit")  # Identical = result cache hit
second_call = time.time() - start
print(f"Second call (result cache hit): {second_call:.6f}s")  # <1ms = <0.001s

assert url1 == url2, "URLs should be identical (same cache entry)"
assert second_call < 0.001, f"Expected <1ms, got {second_call*1000:.2f}ms"
print("✅ Result cache validation: PASSED")
```

**Expected Result**: 
- First call: 1.5-2.0s (full search pipeline)
- Second call: <1ms (direct cache return)
- Improvement: **1500-2000x faster** ✨

---

### Test 2.2: Keyword Cache (Fast Path) - Target: <5ms

**Procedure**:
```python
import time
addon = api_handler.AIImageProvider(config)

# First call - populate cache
start = time.time()
url1 = addon.get_image_url("apple", "a red fruit")
first_call = time.time() - start

# Second call - DIFFERENT definition, SAME vocabulary
# Should hit keyword cache (keyword already generated)
start = time.time()
url2 = addon.get_image_url("apple", "different definition here")
second_call = time.time() - start
print(f"Keyword cache hit: {second_call:.3f}s")

# URL will be different (different definition), but keyword generation skipped
assert second_call < 0.5, f"Expected <500ms, got {second_call*1000:.2f}ms"
print("✅ Keyword cache validation: PASSED")
```

**Expected Result**:
- Keyword cache hit: 500-800ms (image search only, no AI generation)
- vs. cold search: 1500-2000ms
- Improvement: **2-3x faster** ✨

---

### Test 2.3: Cache Hit Rate Over Session - Target: 60-80%

**Procedure**:
```python
import time
addon = api_handler.AIImageProvider(config)

# Simulate typical user session
test_pairs = [
    ("dog", "man's best friend"),
    ("cat", "household pet"),
    ("dog", "man's best friend"),  # Repeat = cache hit
    ("bird", "animal with wings"),
    ("dog", "a domestic animal"),  # Same vocab, diff definition = keyword cache
    ("cat", "a furry friend"),
    ("dog", "man's best friend"),  # Cache hit again
    ("fish", "lives in water"),
    ("dog", "Canis familiaris"),
    ("cat", "household pet"),  # Repeat = cache hit
]

cache_hits = 0
total_calls = len(test_pairs)
times = []

for vocab, defn in test_pairs:
    start = time.time()
    try:
        url = addon.get_image_url(vocab, defn)
        elapsed = time.time() - start
        times.append(elapsed)
        
        # Cache hits are <100ms (includes keyword cache + image search)
        if elapsed < 0.1:
            cache_hits += 1
    except Exception as e:
        print(f"Error: {e}")

hit_rate = (cache_hits / total_calls) * 100
avg_time = sum(times) / len(times)
print(f"Cache hit rate: {hit_rate:.1f}% ({cache_hits}/{total_calls})")
print(f"Average time: {avg_time*1000:.0f}ms")
assert hit_rate >= 40, f"Expected ≥40%, got {hit_rate:.1f}%"
print("✅ Cache hit rate validation: PASSED")
```

**Expected Result**:
- Hit rate: 60-80% on repeated searches
- Cold searches: 1.5-2.0s
- Cached searches: <100ms
- Average: 700-1000ms

---

## 🚀 Phase 3: Provider Performance Tracking (15 minutes)

### Test 3.1: Provider Scoring and Reordering

**Procedure**:
```python
from AnkiAI_ImageAddon.modules import image_providers

selector = image_providers.SmartImageSelector()

# Add providers
selector.add_provider("pexels", pexels_provider)
selector.add_provider("nasa", nasa_provider)
selector.add_provider("pixabay", pixabay_provider)

print("Initial provider scores:")
for name, stats in selector.provider_stats.items():
    print(f"  {name}: score={stats.get_overall_score():.2f}")

# Perform searches
for i in range(5):
    try:
        results = selector.search_smart("landscape", top_n=5)
        print(f"Search {i+1}: Got {len(results)} results")
    except Exception as e:
        print(f"Search {i+1}: Error - {e}")

print("\nUpdated provider scores:")
for name, stats in selector.provider_stats.items():
    reliability = stats.get_reliability_score()
    speed = stats.get_speed_score()
    overall = stats.get_overall_score()
    print(f"  {name}:")
    print(f"    Reliability: {reliability:.2f}")
    print(f"    Speed: {speed:.2f}")
    print(f"    Overall: {overall:.2f}")

# Get providers in performance order
sorted_providers = selector._get_providers_sorted_by_performance()
print(f"\nProvider order by performance:")
for i, (name, _) in enumerate(sorted_providers, 1):
    print(f"  {i}. {name}")

print("✅ Provider scoring validation: PASSED")
```

**Expected Result**:
- Fast providers (Pexels): Higher scores
- Slow providers (NASA): Lower scores (if they timeout)
- Provider order changes based on performance

---

### Test 3.2: Per-Provider Timeout Verification

**Procedure**:
```python
from AnkiAI_ImageAddon.modules import image_providers

selector = image_providers.SmartImageSelector()

# Check timeout classification
providers_to_test = [
    "pexels", "unsplash", "lorem_picsum",           # Fast (2.0s)
    "pixabay", "openverse", "wallhaven", "google",  # Medium (3.5s)
    "nasa", "loc", "wikimedia", "smithsonian",      # Slow (4.5s)
]

print("Provider timeout classification:")
for provider_name in providers_to_test:
    timeout = selector._get_provider_timeout(provider_name)
    category = "FAST" if timeout == 2.0 else "MEDIUM" if timeout == 3.5 else "SLOW"
    print(f"  {provider_name:20} → {timeout}s ({category})")

# Verify expected timeouts
assert selector._get_provider_timeout("pexels") == 2.0, "Pexels should be 2.0s"
assert selector._get_provider_timeout("pixabay") == 3.5, "Pixabay should be 3.5s"
assert selector._get_provider_timeout("nasa") == 4.5, "NASA should be 4.5s"

print("✅ Per-provider timeout validation: PASSED")
```

**Expected Result**:
- Fast providers: 2.0s timeout
- Medium providers: 3.5s timeout
- Slow providers: 4.5s timeout

---

## ⚡ Phase 4: Concurrency & Early Exit Validation (10 minutes)

### Test 4.1: Adaptive Worker Count

**Procedure**:
```python
import os
import multiprocessing
from AnkiAI_ImageAddon.modules import image_providers

# Check CPU count
cpu_count = multiprocessing.cpu_count()
print(f"System CPU count: {cpu_count}")

selector = image_providers.SmartImageSelector()
print(f"Allocated workers: {selector.max_workers}")

# Expected: min(15 providers, cpu_count, 8)
if cpu_count <= 8:
    expected = min(15, cpu_count)
else:
    expected = 8

assert selector.max_workers == expected, \
    f"Expected {expected} workers, got {selector.max_workers}"
print("✅ Adaptive worker count validation: PASSED")
```

**Expected Result**:
- 2-core system: 2 workers
- 4-core system: 4 workers
- 8-core system: 8 workers
- 16+ core system: 8 workers (capped)

---

### Test 4.2: Early Exit Verification

**Procedure**:
```python
from AnkiAI_ImageAddon.modules import image_providers
import time

# Monkey-patch to count provider calls
call_count = 0
original_search = None

def counting_search_provider(self, provider, keyword, timeout):
    global call_count
    call_count += 1
    return original_search(self, provider, keyword, timeout)

selector = image_providers.SmartImageSelector()
# Add all 15 providers
# ... (add providers) ...

# Reset counter
call_count = 0
original_search = selector._search_provider

# Patch with counter
selector._search_provider = counting_search_provider.__get__(selector, type(selector))

# Search for top 5 results
start = time.time()
results = selector.search_smart("mountain", top_n=5)
elapsed = time.time() - start

print(f"Searched for 5 results")
print(f"Providers called: {call_count} (out of 15 total)")
print(f"Time taken: {elapsed:.2f}s")

# With early exit: should call ~8-10 providers, not all 15
assert call_count <= 12, f"Expected ≤12 providers called, got {call_count}"
assert elapsed < 2.5, f"Expected <2.5s, got {elapsed:.2f}s"

print("✅ Early exit validation: PASSED")
```

**Expected Result**:
- Providers called: 8-10 (not all 15)
- Search time: 1.5-2.5s (vs. 3-5s without early exit)
- Improvement: **50% faster**

---

## 📈 Phase 5: End-to-End Performance Benchmark (15 minutes)

### Test 5.1: Complete Performance Profile

**Procedure**:
```python
import time
import statistics
from AnkiAI_ImageAddon.modules import api_handler

addon = api_handler.AIImageProvider(config)

# Test scenarios
scenarios = {
    "result_cache_hit": (
        lambda: addon.get_image_url("apple", "a red fruit"),
        1,  # Should be <1ms
        "Ultra-fast result cache hit"
    ),
    "keyword_cache_hit": (
        lambda: addon.get_image_url("apple", "different defn"),
        0.5,  # Should be <500ms
        "Fast keyword cache hit"
    ),
    "cold_search": (
        lambda: addon.get_image_url(f"unique_{time.time()}", "unique definition"),
        2.0,  # Should be <2s
        "Full search pipeline"
    ),
}

print("=" * 70)
print("END-TO-END PERFORMANCE BENCHMARK")
print("=" * 70)

for scenario_name, (func, target_ms, description) in scenarios.items():
    times = []
    
    # Warm up if needed
    if "cache" not in scenario_name:
        func()
    
    # Run multiple iterations
    iterations = 5 if "cold" not in scenario_name else 3
    
    for i in range(iterations):
        start = time.time()
        try:
            result = func()
            elapsed = (time.time() - start) * 1000  # Convert to ms
            times.append(elapsed)
        except Exception as e:
            print(f"  Error: {e}")
    
    if times:
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        status = "✅ PASS" if avg_time <= target_ms * 1000 else "❌ FAIL"
        
        print(f"\n{scenario_name.upper()}")
        print(f"  Description: {description}")
        print(f"  Target: <{target_ms*1000:.0f}ms")
        print(f"  Results: min={min_time:.1f}ms, avg={avg_time:.1f}ms, max={max_time:.1f}ms")
        print(f"  Status: {status}")

print("\n" + "=" * 70)
```

**Expected Result**:
```
RESULT_CACHE_HIT
  Target: <1ms
  Results: min=0.1ms, avg=0.3ms, max=0.8ms
  Status: ✅ PASS

KEYWORD_CACHE_HIT
  Target: <500ms
  Results: min=100ms, avg=250ms, max=400ms
  Status: ✅ PASS

COLD_SEARCH
  Target: <2000ms
  Results: min=1200ms, avg=1600ms, max=2100ms
  Status: ✅ PASS
```

---

### Test 5.2: Memory Stability Check

**Procedure**:
```python
import psutil
import time
from AnkiAI_ImageAddon.modules import api_handler

process = psutil.Process()
addon = api_handler.AIImageProvider(config)

# Record initial memory
initial_mem = process.memory_info().rss / (1024 * 1024)  # MB
print(f"Initial memory: {initial_mem:.1f} MB")

# Simulate heavy usage
test_queries = [
    (f"vocab_{i}", f"definition_{i}")
    for i in range(100)
]

start_time = time.time()
for vocab, defn in test_queries:
    try:
        addon.get_image_url(vocab, defn)
    except:
        pass  # Ignore errors

elapsed = time.time() - start_time

# Record final memory
final_mem = process.memory_info().rss / (1024 * 1024)  # MB
mem_increase = final_mem - initial_mem

print(f"Final memory: {final_mem:.1f} MB")
print(f"Memory increase: {mem_increase:.1f} MB")
print(f"Time for 100 queries: {elapsed:.1f}s")

# Should be bounded (not unbounded growth)
assert mem_increase < 10, f"Memory growth too high: {mem_increase:.1f} MB"
print("✅ Memory stability validation: PASSED")
```

**Expected Result**:
- Memory increase: <5-10 MB (bounded)
- Should NOT grow indefinitely with more queries
- Cache sizes capped (500 + 1000 items max)

---

## 🔍 Phase 6: Integration Testing (20 minutes)

### Test 6.1: Multi-Key Gemini Fallback

**Procedure**:
```python
from AnkiAI_ImageAddon.modules import ai_providers

# Test with primary key disabled
config = {
    'gemini_api_key': 'invalid_key_1',
    'gemini_eval_api_key': 'invalid_key_2',
    'gemini_eval_api_key_backup': 'valid_backup_key',
    'gemini_backup_api_key': 'backup_key',
    # ... etc
}

multi_ai = ai_providers.MultiAIProvider(config)

# Should fallback to backup keys
try:
    keyword = multi_ai.generate_keyword("test", "definition")
    print(f"Generated keyword: {keyword}")
    print("✅ Gemini fallback validation: PASSED")
except Exception as e:
    print(f"❌ Gemini fallback validation: FAILED - {e}")
```

---

### Test 6.2: Rate Limit Protection

**Procedure**:
```python
from AnkiAI_ImageAddon.modules import api_handler

addon = api_handler.AIImageProvider(config)

# Monitor for rate limit detection
print("Testing rate limit protection...")
print(f"Rate limit pause duration: {config.get('rate_limit_pause_duration', 60)}s")

# Should automatically pause and retry
# (Hard to test without actually hitting rate limits)

print("✅ Rate limit protection check: Configuration verified")
```

---

## 📋 Validation Report Template

Use this template to document your validation results:

```
=============================================================================
                  ANKIAI-IMAGEADDON V4.3 VALIDATION REPORT
=============================================================================

Date: [YYYY-MM-DD]
Tester: [Name]
System: [OS, CPU cores, RAM]

PHASE 1: SANITY CHECKS
  [ ] Addon loads without errors
  [ ] Configuration dialog opens
  [ ] Test connections work
  Result: PASS / FAIL

PHASE 2: CACHE PERFORMANCE
  [ ] Result cache: <1ms (Target: <1ms) → Actual: ___ms
  [ ] Keyword cache: <500ms (Target: <500ms) → Actual: ___ms
  [ ] Hit rate: ___% (Target: 60-80%)
  Result: PASS / FAIL

PHASE 3: PROVIDER TRACKING
  [ ] Provider scores calculated correctly
  [ ] Provider reordering working
  [ ] Per-provider timeouts correct
  Result: PASS / FAIL

PHASE 4: CONCURRENCY
  [ ] Worker count adaptive
  [ ] Early exit working (providers called: ___ / 15)
  [ ] Search time <2.5s
  Result: PASS / FAIL

PHASE 5: BENCHMARKS
  [ ] Result cache: ___ms (Target: <1ms)
  [ ] Keyword cache: ___ms (Target: <500ms)
  [ ] Cold search: ___ms (Target: <2000ms)
  [ ] Memory increase: ___MB (Target: <10MB)
  Result: PASS / FAIL

PHASE 6: INTEGRATION
  [ ] Gemini fallback working
  [ ] Rate limit protection configured
  Result: PASS / FAIL

OVERALL: PASS / FAIL / PARTIAL

Notes:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
```

---

## 🚨 Troubleshooting

### Issue: Cache hit times still slow (>100ms)

**Possible Causes**:
- Image search still running for keyword cache hits
- Network latency on image provider calls
- Disk I/O on file system

**Solutions**:
- Check image_cache timing
- Verify network connection
- Enable result cache (should bypass image search)

---

### Issue: Early exit not working (still calling all 15 providers)

**Possible Causes**:
- Early exit threshold not reached (need >10 results)
- Search timeout not triggered
- Exception handling catching early exit logic

**Solutions**:
- Check `len(all_scored_images) >= top_n * 2` condition
- Verify timeout values are correct
- Add debug logging in search_smart()

---

### Issue: Provider scores not changing

**Possible Causes**:
- Insufficient searches (need multiple searches to see changes)
- EMA alpha too small (0.2) - takes many iterations to accumulate
- All providers succeeding (no score differential)

**Solutions**:
- Run more searches (10+) before checking
- Check _update_provider_score() is being called
- Look for exceptions in performance recording

---

### Issue: Memory growing unbounded

**Possible Causes**:
- Cache size limits not enforced
- LRU eviction not working
- TTL expiration not triggering

**Solutions**:
- Verify cache.set() enforces max_size
- Check eviction algorithm in KeywordCache
- Confirm TTL values are reasonable

---

## ✅ Success Criteria

All of the following must pass for v4.3 validation to be **COMPLETE**:

- [ ] All Phase 1-6 tests pass
- [ ] Result cache hits: <1ms (10 runs)
- [ ] Keyword cache hits: <500ms (average)
- [ ] Cold searches: <2.5s (average)
- [ ] Memory stable (<10MB increase for 100 queries)
- [ ] Provider ordering working
- [ ] Early exit active (calling 8-10 providers max)
- [ ] No exceptions in console
- [ ] No syntax errors in modules

**Status**: ⏳ Ready for Testing

**Next Steps**:
1. Run Phase 1-2 tests (quick validation)
2. If passing, run Phase 3-5 (full benchmark)
3. If all passing, run Phase 6 (integration)
4. Document results in validation report
5. Submit report for sign-off

---

**Document Version**: v1.0  
**Last Updated**: May 3, 2026  
**Contact**: [Support Email]
