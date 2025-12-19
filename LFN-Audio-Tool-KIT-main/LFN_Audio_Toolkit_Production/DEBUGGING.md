# LFN Audio Toolkit - Debugging Guide

## Overview

This guide provides a systematic approach to debugging issues in the LFN Audio Toolkit. The philosophy is simple: **Fix the root cause, not just the symptom**. When resolving unknowns, ensure every proposed solution addresses the fundamental issue, not just its surface effect.

---

## Table of Contents

1. [Debugging Methodology](#debugging-methodology)
2. [Root Cause Analysis Process](#root-cause-analysis-process)
3. [Debugging Tools and Techniques](#debugging-tools-and-techniques)
4. [Common Root Causes](#common-root-causes)
5. [Systematic Problem Resolution](#systematic-problem-resolution)
6. [Unknown Issues Resolution](#unknown-issues-resolution)
7. [Debugging Workflow](#debugging-workflow)
8. [Advanced Debugging](#advanced-debugging)
9. [Prevention Strategies](#prevention-strategies)

---

## Debugging Methodology

### Core Principles

1. **Understand Before Acting**
   - Don't jump to solutions
   - Gather all relevant information first
   - Reproduce the issue reliably

2. **Question Everything**
   - Don't assume the obvious cause is the real cause
   - Verify your assumptions with evidence
   - Consider multiple hypotheses

3. **Fix Root Causes, Not Symptoms**
   - Symptoms are surface-level manifestations
   - Root causes are fundamental issues
   - Addressing symptoms leads to recurring problems

4. **Document Your Process**
   - Record observations and attempts
   - Track what worked and what didn't
   - Share findings to help others

### The 5 Whys Technique

Ask "why" five times to drill down to the root cause:

**Example:**
```
Problem: Real-time monitoring crashes after 2 minutes
Why? → Memory allocation fails
Why? → Audio buffer keeps growing
Why? → Old buffers aren't being released
Why? → Garbage collection isn't running
Why? → Circular references prevent cleanup
Root Cause: Circular references in audio callback handler
```

**Fix the root cause:** Restructure callback to avoid circular references
**Don't just fix the symptom:** Don't just increase memory limits

---

## Root Cause Analysis Process

### Step 1: Define the Problem Precisely

**Bad:** "The program doesn't work"
**Good:** "Real-time monitor crashes with MemoryError after exactly 2 minutes when GPU acceleration is enabled on CUDA 11.8"

Include:
- **What** is happening (or not happening)?
- **When** does it occur (always, sometimes, under what conditions)?
- **Where** in the code/workflow does it happen?
- **How** can it be reproduced consistently?

### Step 2: Gather Information

```bash
# System information
python --version
pip list
uname -a  # Linux/Mac
systeminfo  # Windows

# Application logs
python preflight_check.py > diagnostic.log 2>&1

# Runtime information
python -c "import sys; print(sys.path)"
python -c "import numpy; print(numpy.__version__, numpy.__file__)"

# Audio device state
python -c "import sounddevice as sd; print(sd.query_devices())"

# GPU state (if applicable)
nvidia-smi
python -c "import cupy; print(cupy.cuda.runtime.runtimeGetVersion())"
```

### Step 3: Form Hypotheses

Based on gathered information, create testable hypotheses:

1. **Hypothesis 1:** Memory leak in audio callback
   - **Test:** Monitor memory usage over time
   - **Expected:** Memory grows linearly with time

2. **Hypothesis 2:** GPU memory exhaustion
   - **Test:** Run without GPU flag
   - **Expected:** Problem disappears

3. **Hypothesis 3:** Audio driver issue
   - **Test:** Try different audio device
   - **Expected:** Different behavior

### Step 4: Test Hypotheses Systematically

Test one variable at a time:

```python
# Create minimal reproducible example
import sounddevice as sd
import time

def test_audio_memory():
    """Test if audio callback leaks memory"""
    import psutil
    process = psutil.Process()
    
    def callback(indata, frames, time_info, status):
        pass  # Minimal callback
    
    stream = sd.InputStream(callback=callback)
    stream.start()
    
    initial_memory = process.memory_info().rss / 1024 / 1024
    print(f"Initial memory: {initial_memory:.2f} MB")
    
    for i in range(12):  # Run for 2 minutes (10s intervals)
        time.sleep(10)
        current_memory = process.memory_info().rss / 1024 / 1024
        print(f"After {(i+1)*10}s: {current_memory:.2f} MB (Δ {current_memory - initial_memory:.2f} MB)")
    
    stream.stop()

test_audio_memory()
```

### Step 5: Identify Root Cause

Compare test results against hypotheses:
- Which hypothesis best explains all observed behavior?
- Are there any contradictions that suggest a different root cause?
- Can you explain why the problem occurs mechanistically?

### Step 6: Verify the Fix

After implementing a fix:

```bash
# Run comprehensive tests
python run_tests.py

# Verify the specific issue is resolved
python test_specific_issue.py

# Check for regressions
python src/lfn_realtime_monitor.py --duration 300  # Run longer than failure point

# Monitor resource usage
watch -n 1 'ps aux | grep python'  # Linux/Mac
```

---

## Debugging Tools and Techniques

### 1. Python Debugger (pdb)

**Interactive debugging:**

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

**Common pdb commands:**
```
n (next)         - Execute next line
s (step)         - Step into function
c (continue)     - Continue execution
p variable       - Print variable value
pp variable      - Pretty-print variable
l (list)         - Show current code context
w (where)        - Show stack trace
q (quit)         - Exit debugger
```

**Example debugging session:**

```python
# In src/lfn_batch_file_analyzer.py
def analyze_audio_file(file_path, use_gpu=False):
    import pdb; pdb.set_trace()  # Debugger will stop here
    
    data, sample_rate = sf.read(file_path)
    # Now you can inspect variables:
    # (Pdb) p file_path
    # (Pdb) p data.shape
    # (Pdb) p sample_rate
```

### 2. Logging for Diagnosis

**Add strategic logging:**

```python
import logging

# Configure at module start
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use throughout code
def process_audio(data):
    logger.debug(f"Processing audio: shape={data.shape}, dtype={data.dtype}")
    logger.debug(f"Memory usage: {get_memory_usage()} MB")
    
    try:
        result = fft_analysis(data)
        logger.info("FFT analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"FFT analysis failed: {e}", exc_info=True)
        raise
```

### 3. Memory Profiling

**Diagnose memory issues:**

```python
from memory_profiler import profile

@profile
def analyze_large_file(file_path):
    """Memory usage will be logged line-by-line"""
    data, sr = sf.read(file_path)
    fft_result = np.fft.rfft(data)
    return fft_result

# Run with:
# python -m memory_profiler src/lfn_batch_file_analyzer.py
```

**Track memory over time:**

```python
import psutil
import tracemalloc

def monitor_memory(func):
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        process = psutil.Process()
        
        mem_before = process.memory_info().rss / 1024 / 1024
        result = func(*args, **kwargs)
        mem_after = process.memory_info().rss / 1024 / 1024
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Memory: {mem_before:.1f} MB → {mem_after:.1f} MB")
        print(f"Peak increase: {peak / 1024 / 1024:.1f} MB")
        
        return result
    return wrapper

@monitor_memory
def analyze_batch(files):
    # Your code here
    pass
```

### 4. Performance Profiling

**Identify bottlenecks:**

```python
import cProfile
import pstats

# Profile code execution
cProfile.run('analyze_audio_file("test.wav")', 'profile_stats')

# Analyze results
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

**Line-by-line profiling:**

```python
from line_profiler import LineProfiler

def analyze_audio(data):
    # Your code here
    pass

# Profile specific function
profiler = LineProfiler()
profiler.add_function(analyze_audio)
profiler.run('analyze_audio(test_data)')
profiler.print_stats()
```

### 5. Network/System Call Tracing

**Linux: strace**
```bash
# Trace system calls
strace -o trace.log python src/lfn_realtime_monitor.py

# Filter for file operations
strace -e trace=open,read,write python script.py

# See time spent in syscalls
strace -c python script.py
```

**Windows: Process Monitor**
- Download Sysinternals Process Monitor
- Filter by process name: python.exe
- Monitor file, registry, and network operations

### 6. Audio-Specific Debugging

**Verify audio data integrity:**

```python
def validate_audio_data(data, sample_rate):
    """Debug audio data issues"""
    print(f"Shape: {data.shape}")
    print(f"Dtype: {data.dtype}")
    print(f"Range: [{data.min():.6f}, {data.max():.6f}]")
    print(f"Mean: {data.mean():.6f}")
    print(f"Std: {data.std():.6f}")
    print(f"Sample rate: {sample_rate} Hz")
    
    # Check for common issues
    if data.max() > 1.0 or data.min() < -1.0:
        print("⚠️  WARNING: Audio data exceeds [-1, 1] range")
    
    if np.isnan(data).any():
        print("⚠️  WARNING: NaN values detected")
    
    if np.isinf(data).any():
        print("⚠️  WARNING: Inf values detected")
    
    if data.std() < 0.001:
        print("⚠️  WARNING: Very low signal variance (possible silence)")
```

**Test audio device:**

```python
import sounddevice as sd
import numpy as np

def test_audio_device(device_id=None):
    """Test audio input device"""
    try:
        # Query device info
        if device_id is not None:
            device = sd.query_devices(device_id)
            print(f"Device: {device['name']}")
            print(f"Channels: {device['max_input_channels']}")
            print(f"Sample rate: {device['default_samplerate']}")
        
        # Test recording
        print("\nRecording 2 seconds...")
        recording = sd.rec(
            int(2 * 48000),
            samplerate=48000,
            channels=1,
            device=device_id,
            dtype='float32'
        )
        sd.wait()
        
        print(f"Recorded: {recording.shape}")
        print(f"Level: {np.abs(recording).max():.4f}")
        
        if np.abs(recording).max() < 0.001:
            print("⚠️  WARNING: Very low signal - check microphone")
        else:
            print("✓ Audio device working correctly")
            
    except Exception as e:
        print(f"❌ Error testing audio device: {e}")
```

---

## Common Root Causes

### Category 1: Environment Issues

| Symptom | Apparent Cause | Root Cause | Fix |
|---------|---------------|------------|-----|
| Import errors | Package not installed | Wrong Python environment active | Activate correct venv |
| FFmpeg not found | FFmpeg missing | PATH not configured | Add FFmpeg to PATH |
| Permission denied | No permissions | Running without required privileges | Fix file/directory permissions |
| Module version conflict | Wrong version | Multiple Python installations | Use virtual environment |

### Category 2: Resource Issues

| Symptom | Apparent Cause | Root Cause | Fix |
|---------|---------------|------------|-----|
| MemoryError | Not enough RAM | Memory leak in callback | Fix circular references |
| Slow performance | Slow CPU | Not using GPU | Enable GPU flag + install CuPy |
| Disk full error | No space | Spectrograms accumulating | Implement cleanup routine |
| Process hangs | Frozen | Waiting for locked resource | Fix resource acquisition order |

### Category 3: Configuration Issues

| Symptom | Apparent Cause | Root Cause | Fix |
|---------|---------------|------------|-----|
| Audio quality poor | Bad device | Wrong sample rate | Match device default rate |
| Inaccurate results | Algorithm issue | Incorrect FFT parameters | Validate FFT window size |
| Missing output | Files not created | Wrong output path | Use absolute paths |
| Encoding errors | Unicode issue | Wrong terminal encoding | Set PYTHONIOENCODING=utf-8 |

### Category 4: Logic Errors

| Symptom | Apparent Cause | Root Cause | Fix |
|---------|---------------|------------|-----|
| Wrong peak detection | Bug in algorithm | Frequency bins miscalculated | Fix frequency mapping |
| Intermittent failures | Random bug | Race condition | Add proper synchronization |
| Inconsistent results | Non-deterministic | Uninitialized variables | Initialize all variables |
| Silent failures | No error | Exception caught and ignored | Remove catch-all except blocks |

---

## Systematic Problem Resolution

### Problem: Unknown Error with No Clear Cause

**Wrong Approach (Fixing Symptoms):**
1. See error message
2. Google the error
3. Try random solutions from Stack Overflow
4. Apply workaround that masks the issue
5. Move on (problem recurs later)

**Right Approach (Finding Root Cause):**

#### Step 1: Reproduce Reliably
```bash
# Create minimal test case
python -c "from src.lfn_realtime_monitor import *; test_specific_function()"

# Note exact conditions:
# - OS: Ubuntu 22.04
# - Python: 3.10.12
# - Package versions: numpy 1.24.3, sounddevice 0.4.6
# - Audio device: USB Microphone (ID 3)
# - GPU: None
```

#### Step 2: Isolate Variables

Test each component independently:

```python
# Test 1: Can we import?
python -c "import sounddevice; print('OK')"

# Test 2: Can we query devices?
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test 3: Can we open stream?
python -c "import sounddevice as sd; s = sd.InputStream(); s.start(); s.stop()"

# Test 4: Can we record?
python -c "import sounddevice as sd; import numpy as np; sd.rec(480, 48000, 1, dtype='float32'); sd.wait(); print('OK')"
```

Identify at which point failure occurs.

#### Step 3: Add Instrumentation

```python
# In the failing function, add detailed logging
def problematic_function(data):
    print(f"[DEBUG] Entered function with data shape: {data.shape}")
    print(f"[DEBUG] Data type: {data.dtype}")
    
    try:
        print(f"[DEBUG] About to process...")
        result = process_data(data)
        print(f"[DEBUG] Processing succeeded, result shape: {result.shape}")
        return result
    except Exception as e:
        print(f"[ERROR] Failed at processing step")
        print(f"[ERROR] Exception type: {type(e).__name__}")
        print(f"[ERROR] Exception message: {e}")
        import traceback
        traceback.print_exc()
        raise
```

#### Step 4: Analyze Failure Mode

```python
# Understand what state leads to failure
def analyze_failure(data):
    """Determine what about this data causes failure"""
    checks = {
        'is_empty': len(data) == 0,
        'has_nan': np.isnan(data).any(),
        'has_inf': np.isinf(data).any(),
        'wrong_dtype': data.dtype != np.float32,
        'wrong_shape': len(data.shape) != 1,
        'out_of_range': (data.max() > 1.0) or (data.min() < -1.0),
    }
    
    print("Data validation:")
    for check, result in checks.items():
        print(f"  {check}: {'❌ FAIL' if result else '✓ PASS'}")
    
    return any(checks.values())
```

#### Step 5: Trace Back to Root Cause

```python
# Use stack trace to understand call chain
def trace_call_stack():
    """Print call stack to understand context"""
    import traceback
    print("\nCall stack:")
    for line in traceback.format_stack()[:-1]:
        print(line.strip())
```

#### Step 6: Formulate Root Cause Hypothesis

**Example Analysis:**

Observations:
- Error occurs only with USB audio device
- Error occurs after exactly 2 minutes
- Error is MemoryError
- Memory grows linearly at 10 MB/minute

Hypothesis: Audio buffers are not being released, causing memory accumulation.

Verification:
```python
# Check if buffers are accumulating
import gc
print(f"Tracked objects: {len(gc.get_objects())}")
# Run for 1 minute
# Check again
print(f"Tracked objects: {len(gc.get_objects())}")
# If number grows significantly, we have a leak
```

Root Cause: Circular reference between audio stream and callback prevents garbage collection.

#### Step 7: Implement Fundamental Fix

**Wrong (Symptom Fix):**
```python
# Just increase memory limit (doesn't fix leak)
import resource
resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, -1))
```

**Right (Root Cause Fix):**
```python
# Break circular reference
class AudioMonitor:
    def __init__(self):
        self.stream = None
        self.callback_ref = None  # Avoid circular ref
    
    def start(self):
        # Use weak reference to avoid circular dependency
        import weakref
        weak_self = weakref.ref(self)
        
        def callback(indata, frames, time_info, status):
            strong_self = weak_self()
            if strong_self is not None:
                strong_self.process_audio(indata)
        
        self.stream = sd.InputStream(callback=callback)
        self.stream.start()
```

---

## Unknown Issues Resolution

### Framework for Resolving Unknowns

When encountering an issue you've never seen before:

#### 1. Categorize the Unknown

**Type A: Known pattern, unknown details**
- You recognize the error type
- Need to identify specific cause
- Example: "KeyError" but don't know which key

**Type B: Unknown pattern, familiar domain**
- Haven't seen this specific error
- Understand the domain (audio processing, file I/O, etc.)
- Example: New PortAudio error code

**Type C: Completely unknown**
- Unfamiliar error in unfamiliar domain
- Need to learn domain concepts first
- Example: CUDA internal error with GPU you've never debugged

#### 2. Information Gathering Strategy

**For Type A:**
```python
# Add extensive logging at the point of failure
try:
    value = dictionary[key]
except KeyError as e:
    print(f"Key not found: {e}")
    print(f"Available keys: {list(dictionary.keys())}")
    print(f"Dictionary size: {len(dictionary)}")
    raise
```

**For Type B:**
```bash
# Research the specific error
# 1. Check official documentation
python -c "import sounddevice; help(sounddevice.InputStream)"

# 2. Check source code
pip show sounddevice  # Find installation location
cat /path/to/sounddevice/__init__.py

# 3. Search issues in project repository
# Visit: https://github.com/spatialaudio/python-sounddevice/issues

# 4. Enable verbose logging
export SD_DEBUG=1  # Some packages have debug modes
```

**For Type C:**
```bash
# Learn the domain first
# 1. Read documentation
# 2. Find examples and tutorials  
# 3. Build minimal working example
# 4. Compare with failing code

# For GPU/CUDA issues:
# Check CUDA documentation
nvcc --version
nvidia-smi -q  # Detailed GPU info

# Test CUDA independently
python -c "import cupy; a = cupy.array([1,2,3]); print(a)"
```

#### 3. Binary Search Debugging

When you don't know where the problem is:

```python
# Divide code into sections and test each
def complex_analysis(data):
    # Section 1: Data validation
    print("Checkpoint 1")
    validated_data = validate(data)
    
    # Section 2: Preprocessing
    print("Checkpoint 2")
    preprocessed = preprocess(validated_data)
    
    # Section 3: FFT analysis
    print("Checkpoint 3")
    fft_result = compute_fft(preprocessed)
    
    # Section 4: Peak detection
    print("Checkpoint 4")
    peaks = detect_peaks(fft_result)
    
    # Section 5: Formatting
    print("Checkpoint 5")
    return format_results(peaks)

# Run and see which checkpoint is the last printed
# Problem is between last successful checkpoint and next one
```

#### 4. Differential Analysis

Compare working vs. non-working scenarios:

```python
def compare_scenarios():
    """Find what's different between working and failing cases"""
    
    # Working case
    print("=" * 50)
    print("WORKING CASE")
    print("=" * 50)
    working_file = "working.wav"
    working_data, working_sr = sf.read(working_file)
    print(f"Shape: {working_data.shape}")
    print(f"Sample rate: {working_sr}")
    print(f"Data range: [{working_data.min()}, {working_data.max()}]")
    print(f"File size: {os.path.getsize(working_file)} bytes")
    
    # Failing case
    print("\n" + "=" * 50)
    print("FAILING CASE")
    print("=" * 50)
    failing_file = "failing.wav"
    failing_data, failing_sr = sf.read(failing_file)
    print(f"Shape: {failing_data.shape}")
    print(f"Sample rate: {failing_sr}")
    print(f"Data range: [{failing_data.min()}, {failing_data.max()}]")
    print(f"File size: {os.path.getsize(failing_file)} bytes")
    
    # Compare
    print("\n" + "=" * 50)
    print("DIFFERENCES")
    print("=" * 50)
    if working_data.shape != failing_data.shape:
        print(f"❌ Shape differs: {working_data.shape} vs {failing_data.shape}")
    if working_sr != failing_sr:
        print(f"❌ Sample rate differs: {working_sr} vs {failing_sr}")
```

#### 5. Asking for Help Effectively

When you need external help, provide:

```text
Title: MemoryError in lfn_realtime_monitor after 120 seconds with USB device

Environment:
- OS: Ubuntu 22.04 LTS
- Python: 3.10.12
- Toolkit version: 2.0.0
- Package versions:
  - sounddevice: 0.4.6
  - numpy: 1.24.3
  - scipy: 1.11.1

Issue:
Real-time monitor crashes with MemoryError after exactly 2 minutes when using
USB audio device (Blue Yeti). Built-in microphone works fine.

Reproduction:
```bash
python src/lfn_realtime_monitor.py --device 3 --duration 180
```

Observations:
1. Memory grows at 10 MB/minute (monitored with htop)
2. Crash occurs at 2min ± 5sec
3. Error traceback shows failure in numpy.fft.rfft
4. Does not occur with built-in microphone (device 0)
5. Does not occur with --duration 60 (stops before crash)

Investigation:
- Checked audio buffer sizes: 480 samples @ 48kHz = 10ms blocks
- Monitored gc.get_objects(): grows from 50k to 200k objects
- Added memory profiling: see attached memory_profile.txt
- Tested with minimal callback: still crashes
- Hypothesis: circular reference in callback prevents GC

Attempted fixes:
1. Added explicit del statements: no effect
2. Called gc.collect() manually: temporary relief only
3. Used weakref for callback: resolved issue!

Question: Is using weakref the correct approach, or should the architecture
be changed? See code snippet below:

[code snippet]
```

---

## Debugging Workflow

### Standard Debugging Process

```
┌─────────────────────────────────────────────────────────┐
│ 1. Observe Problem                                      │
│    - What is the symptom?                              │
│    - When does it occur?                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Gather Information                                   │
│    - System state                                       │
│    - Error messages                                     │
│    - Logs and traces                                    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Reproduce Reliably                                   │
│    - Create minimal test case                           │
│    - Document exact steps                               │
│    - Verify consistency                                 │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Form Hypotheses                                      │
│    - What could cause this?                             │
│    - List possible root causes                          │
│    - Prioritize by likelihood                           │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Test Hypotheses                                      │
│    - Design tests for each hypothesis                   │
│    - Test one variable at a time                        │
│    - Record results                                     │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Identify Root Cause                                  │
│    - Which hypothesis explains all evidence?            │
│    - Can you prove the mechanism?                       │
│    - Are there contradictions?                          │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 7. Implement Fix                                        │
│    - Fix the root cause, not the symptom               │
│    - Consider side effects                              │
│    - Add tests to prevent regression                    │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 8. Verify Fix                                           │
│    - Test the original failure case                     │
│    - Run full test suite                                │
│    - Monitor for regressions                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│ 9. Document                                             │
│    - What was the root cause?                           │
│    - How was it fixed?                                  │
│    - Update troubleshooting guide                       │
└─────────────────────────────────────────────────────────┘
```

### Quick Debug Checklist

Before deep debugging, verify basics:

```bash
# ✓ Environment check
python --version  # 3.8+?
which python      # Correct Python?
pip list          # All packages installed?

# ✓ File check
ls -la input.wav  # File exists?
file input.wav    # Correct format?
head -c 100 input.wav | hexdump -C  # Not corrupted?

# ✓ Permissions check
ls -la output/    # Directory writable?
touch output/test.txt && rm output/test.txt  # Can create files?

# ✓ Resources check
df -h .           # Enough disk space?
free -h           # Enough memory?
top               # CPU usage normal?

# ✓ Dependencies check
python preflight_check.py  # All systems go?
```

---

## Advanced Debugging

### Debugging Race Conditions

Race conditions are hard to reproduce and debug:

```python
import threading
import time

# Add debugging to find race conditions
class DebugLock:
    """Wrapper to debug lock acquisition"""
    def __init__(self, name):
        self.lock = threading.Lock()
        self.name = name
    
    def acquire(self):
        caller = threading.current_thread().name
        print(f"[{time.time():.3f}] {caller} acquiring {self.name}")
        result = self.lock.acquire()
        print(f"[{time.time():.3f}] {caller} acquired {self.name}")
        return result
    
    def release(self):
        caller = threading.current_thread().name
        print(f"[{time.time():.3f}] {caller} releasing {self.name}")
        self.lock.release()
        print(f"[{time.time():.3f}] {caller} released {self.name}")

# Use in code
data_lock = DebugLock("data_lock")
```

### Debugging Callback Hell

Audio callbacks are tricky:

```python
# Track callback execution
class CallbackTracer:
    def __init__(self):
        self.call_count = 0
        self.last_call_time = None
        self.exceptions = []
    
    def trace(self, func):
        def wrapper(*args, **kwargs):
            self.call_count += 1
            current_time = time.time()
            
            if self.last_call_time:
                interval = current_time - self.last_call_time
                if interval > 0.015:  # Expected: 10ms, allow 50% margin
                    print(f"⚠️  Long interval: {interval*1000:.1f}ms")
            
            self.last_call_time = current_time
            
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.exceptions.append((self.call_count, e))
                print(f"❌ Exception in callback #{self.call_count}: {e}")
                raise
        
        return wrapper

# Usage
tracer = CallbackTracer()

@tracer.trace
def audio_callback(indata, frames, time_info, status):
    # Your callback code
    pass
```

### Debugging Memory Corruption

Rare but severe:

```python
import sys

# Check reference counts
def check_refcounts(obj, expected):
    actual = sys.getrefcount(obj) - 1  # Subtract getrefcount's ref
    if actual != expected:
        print(f"⚠️  Unexpected refcount: {actual} (expected {expected})")
        import gc
        referrers = gc.get_referrers(obj)
        print(f"   Referrers: {len(referrers)}")
        for i, ref in enumerate(referrers[:5]):
            print(f"   [{i}] {type(ref)}")

# Check for corruption
def validate_array(arr, name):
    """Validate numpy array hasn't been corrupted"""
    try:
        # Check basic properties
        shape = arr.shape
        dtype = arr.dtype
        size = arr.size
        
        # Check data access
        _ = arr[0]
        _ = arr[-1]
        _ = arr.sum()
        
        print(f"✓ {name} validated: {shape} {dtype}")
    except Exception as e:
        print(f"❌ {name} corrupted: {e}")
        raise
```

---

## Prevention Strategies

### 1. Design for Debuggability

```python
class AudioAnalyzer:
    """Design with debugging in mind"""
    
    def __init__(self, debug=False):
        self.debug = debug
        self.metrics = {
            'calls': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def _log(self, level, message):
        """Centralized logging"""
        if self.debug or level == 'error':
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] [{level.upper()}] {message}")
        
        if level == 'error':
            self.metrics['errors'] += 1
        elif level == 'warning':
            self.metrics['warnings'] += 1
    
    def analyze(self, data):
        """Main analysis with debug support"""
        self.metrics['calls'] += 1
        self._log('info', f"Starting analysis (call #{self.metrics['calls']})")
        
        # Validate input
        if not self._validate_input(data):
            self._log('error', "Invalid input data")
            return None
        
        try:
            result = self._do_analysis(data)
            self._log('info', "Analysis completed successfully")
            return result
        except Exception as e:
            self._log('error', f"Analysis failed: {e}")
            raise
    
    def _validate_input(self, data):
        """Validate and log issues"""
        if data is None:
            self._log('error', "Data is None")
            return False
        
        if len(data) == 0:
            self._log('warning', "Data is empty")
            return False
        
        if np.isnan(data).any():
            self._log('warning', "Data contains NaN")
            return False
        
        return True
    
    def get_metrics(self):
        """Return debugging metrics"""
        return self.metrics.copy()
```

### 2. Add Assertions

```python
def process_audio(data, sample_rate):
    """Process with runtime checks"""
    
    # Preconditions
    assert data is not None, "Data cannot be None"
    assert len(data) > 0, "Data cannot be empty"
    assert sample_rate > 0, f"Invalid sample rate: {sample_rate}"
    assert data.dtype == np.float32, f"Expected float32, got {data.dtype}"
    
    # Process
    result = do_processing(data, sample_rate)
    
    # Postconditions
    assert result is not None, "Processing returned None"
    assert len(result) > 0, "Processing returned empty result"
    assert not np.isnan(result).any(), "Result contains NaN"
    
    return result
```

### 3. Add Health Checks

```python
def health_check():
    """Periodic system health verification"""
    issues = []
    
    # Check 1: Memory usage
    import psutil
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        issues.append(f"High memory usage: {mem.percent}%")
    
    # Check 2: Disk space
    disk = psutil.disk_usage('.')
    if disk.percent > 95:
        issues.append(f"Low disk space: {disk.free / 1024**3:.1f} GB free")
    
    # Check 3: Audio device
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if not any(d['max_input_channels'] > 0 for d in devices):
            issues.append("No audio input devices available")
    except Exception as e:
        issues.append(f"Audio device check failed: {e}")
    
    # Check 4: Output directories
    for dir_path in ['outputs', 'outputs/spectrograms']:
        if not os.path.isdir(dir_path):
            issues.append(f"Missing directory: {dir_path}")
        elif not os.access(dir_path, os.W_OK):
            issues.append(f"Cannot write to: {dir_path}")
    
    return issues

# Run periodically
if __name__ == '__main__':
    issues = health_check()
    if issues:
        print("⚠️  Health check warnings:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All health checks passed")
```

### 4. Build Testing Into Development

```python
# Test as you code
def new_feature(data):
    """New feature with built-in tests"""
    
    # Inline test
    if __name__ == '__main__':
        # Test 1: Normal case
        test_data = np.random.randn(1000).astype(np.float32)
        result = new_feature(test_data)
        assert result is not None
        print("✓ Test 1 passed")
        
        # Test 2: Edge case - empty
        try:
            new_feature(np.array([]))
            print("✗ Test 2 failed: should have raised ValueError")
        except ValueError:
            print("✓ Test 2 passed")
        
        # Test 3: Edge case - NaN
        test_data_nan = np.array([1.0, np.nan, 3.0], dtype=np.float32)
        result_nan = new_feature(test_data_nan)
        assert not np.isnan(result_nan).any()
        print("✓ Test 3 passed")
```

---

## Final Checklist

Before concluding debugging:

- [ ] Root cause identified and understood
- [ ] Fix addresses root cause, not just symptom
- [ ] Fix tested with original failure case
- [ ] Fix tested with edge cases
- [ ] Full test suite passes
- [ ] No performance regressions
- [ ] Documentation updated
- [ ] Added tests to prevent regression
- [ ] Committed with clear explanation

---

## See Also

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and quick fixes
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [preflight_check.py](preflight_check.py) - Automated diagnostics
- [run_tests.py](run_tests.py) - Test suite

---

**Remember:** The goal isn't just to make the error go away. The goal is to understand why it happened and ensure it never happens again.

**Last Updated:** December 19, 2025  
**Version:** 1.0.0
