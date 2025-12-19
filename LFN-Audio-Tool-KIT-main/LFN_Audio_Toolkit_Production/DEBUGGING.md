# LFN Audio Toolkit - Debugging Guide

## 🎯 Philosophy: Fix the Root Cause, Not Just the Symptom

This guide emphasizes **identifying and resolving fundamental issues** rather than applying quick fixes that mask symptoms. When you encounter a problem, always ask: "Why is this happening?" until you reach the underlying cause.

---

## Table of Contents

- [Debugging Methodology](#debugging-methodology)
- [Root Cause vs Symptom Analysis](#root-cause-vs-symptom-analysis)
- [Systematic Debugging Workflow](#systematic-debugging-workflow)
- [Diagnostic Tools and Logging](#diagnostic-tools-and-logging)
- [Unknown Resolution Process](#unknown-resolution-process)
- [Common Pitfalls and How to Avoid Them](#common-pitfalls-and-how-to-avoid-them)
- [Debugging by Component](#debugging-by-component)
- [Performance Debugging](#performance-debugging)
- [Memory Debugging](#memory-debugging)
- [Development Environment Setup](#development-environment-setup)
- [Code Review for Root Causes](#code-review-for-root-causes)

---

## Debugging Methodology

### The Five Whys Technique

When encountering an issue, ask "why" at least 5 times to drill down to the root cause:

**Example:**
1. **Problem**: Script crashes with "MemoryError"
2. **Why?** Not enough memory to allocate array
3. **Why?** Loading entire 2-hour audio file into memory at once
4. **Why?** No block processing implementation for large files
5. **Why?** Original design assumed short audio clips
6. **Root Cause**: Architecture doesn't support streaming/chunked processing

**Symptom Fix** ❌: Add a try-except to catch MemoryError  
**Root Cause Fix** ✅: Implement block-by-block processing for large files

---

### Scientific Method for Debugging

1. **Observe**: Document the exact behavior, not assumptions
2. **Hypothesize**: Form testable theories about the root cause
3. **Experiment**: Create minimal reproducible test cases
4. **Analyze**: Examine results objectively
5. **Conclude**: Verify the root cause is addressed
6. **Prevent**: Add safeguards to prevent recurrence

---

## Root Cause vs Symptom Analysis

### Identifying Symptoms vs Root Causes

| Symptom (Surface Issue) | Root Cause (Fundamental Issue) |
|-------------------------|-------------------------------|
| "Script fails with PermissionError" | Incorrect file permissions from previous privileged install |
| "FFmpeg not found error" | FFmpeg not in system PATH variable |
| "GPU acceleration doesn't work" | Mismatched CUDA version between driver and CuPy |
| "Unicode errors on Windows" | Console encoding not set to UTF-8 |
| "Database locked error" | Multiple processes accessing SQLite without proper locking |
| "Spectrograms not generated" | Matplotlib backend incompatible with headless environment |

### Analysis Framework

For each issue, fill out this framework:

```
SYMPTOM:
  What: [Observable behavior]
  When: [Conditions under which it occurs]
  Where: [Which component/function]

IMMEDIATE CAUSE:
  What failed: [Direct technical failure]
  
ROOT CAUSE:
  Why it failed: [Fundamental reason]
  Contributing factors: [Environment, design, assumptions]
  
SOLUTION (ROOT CAUSE):
  Fix: [Address fundamental issue]
  Validation: [How to verify fix works]
  Prevention: [How to prevent recurrence]
```

---

## Systematic Debugging Workflow

### Step 1: Reproduce the Issue

**Goal**: Create a minimal, consistent reproduction case

```bash
# Document exact steps
echo "Reproduction Steps:" > debug_notes.txt
echo "1. Command: python src/lfn_batch_file_analyzer.py test.wav" >> debug_notes.txt
echo "2. Environment: Python 3.9, Windows 10" >> debug_notes.txt
echo "3. Result: MemoryError at line 142" >> debug_notes.txt
```

**Questions to answer:**
- Does it happen every time or intermittently?
- What are the minimal conditions needed to trigger it?
- Can you reproduce it with a simple test case?

---

### Step 2: Gather Diagnostic Information

**System Information:**
```bash
# Capture environment details
python --version > debug_env.txt
pip list >> debug_env.txt
python -c "import sys; print(f'Platform: {sys.platform}')" >> debug_env.txt
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().total / 1e9:.1f} GB')" >> debug_env.txt
```

**Application State:**
```bash
# Run preflight check
python preflight_check.py > preflight_output.txt 2>&1

# Check health
python src/lfn_health_assessment.py > health_output.txt 2>&1
```

**Error Logs:**
```python
# Enable verbose logging in your script
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

---

### Step 3: Form and Test Hypotheses

**Create Isolated Tests:**

```python
# test_hypothesis.py - Minimal reproduction
import numpy as np
import soundfile as sf

# Hypothesis: Memory error occurs with large arrays
def test_large_array_allocation():
    """Test if system can allocate expected array size"""
    try:
        # Calculate expected size
        sample_rate = 44100
        duration_hours = 2
        samples = sample_rate * duration_hours * 3600
        expected_gb = samples * 4 / 1e9  # 4 bytes per float32
        
        print(f"Attempting to allocate {expected_gb:.2f} GB")
        audio = np.zeros(samples, dtype=np.float32)
        print("✅ Allocation successful")
        return True
    except MemoryError as e:
        print(f"❌ MemoryError: {e}")
        print(f"Root cause: Insufficient RAM for {expected_gb:.2f} GB allocation")
        return False

if __name__ == "__main__":
    test_large_array_allocation()
```

---

### Step 4: Trace Execution

**Add Strategic Print Statements:**

```python
def analyze_audio_file(file_path, use_gpu=False):
    print(f"[DEBUG] Starting analysis: {file_path}")
    print(f"[DEBUG] File size: {os.path.getsize(file_path) / 1e6:.2f} MB")
    
    # Load audio
    print(f"[DEBUG] Loading audio...")
    audio, sr = sf.read(file_path)
    print(f"[DEBUG] Loaded: {len(audio)} samples at {sr} Hz")
    print(f"[DEBUG] Duration: {len(audio) / sr:.2f} seconds")
    print(f"[DEBUG] Memory usage: {audio.nbytes / 1e6:.2f} MB")
    
    # Process
    print(f"[DEBUG] Computing spectrogram...")
    freqs, times, Sxx = compute_spectrogram(audio, sr, use_gpu)
    print(f"[DEBUG] Spectrogram shape: {Sxx.shape}")
    print(f"[DEBUG] Spectrogram memory: {Sxx.nbytes / 1e6:.2f} MB")
    
    return {"frequencies": freqs, "times": times, "spectrogram": Sxx}
```

**Use Python Debugger (pdb):**

```python
import pdb

def problematic_function(data):
    # Set breakpoint
    pdb.set_trace()
    
    # Inspect variables interactively
    result = complex_operation(data)
    return result

# Or use breakpoint() in Python 3.7+
def another_function(data):
    breakpoint()  # Cleaner syntax
    result = process(data)
    return result
```

**Interactive Debugging Commands:**
- `l` (list) - Show current code location
- `n` (next) - Execute next line
- `s` (step) - Step into function
- `c` (continue) - Continue execution
- `p variable` - Print variable value
- `pp variable` - Pretty-print variable
- `w` (where) - Show call stack
- `u` (up) - Go up call stack
- `d` (down) - Go down call stack

---

### Step 5: Implement Root Cause Fix

**Bad Example (Symptom Fix):**
```python
# ❌ Masks the real problem
try:
    audio, sr = sf.read(large_file)
    analyze(audio)
except MemoryError:
    print("Not enough memory. Try a smaller file.")
    return None  # User still can't process their file!
```

**Good Example (Root Cause Fix):**
```python
# ✅ Addresses fundamental limitation
def analyze_large_file_in_blocks(file_path, block_duration=30):
    """
    Process large files in manageable chunks to avoid memory issues.
    Root cause: Loading entire file into memory exceeds available RAM.
    Solution: Stream processing in fixed-size blocks.
    """
    info = sf.info(file_path)
    sr = info.samplerate
    total_duration = info.frames / sr
    
    results = []
    for start_time in range(0, int(total_duration), block_duration):
        # Load only one block at a time
        start_frame = int(start_time * sr)
        frames_to_read = int(block_duration * sr)
        
        audio_block, _ = sf.read(
            file_path, 
            start=start_frame, 
            frames=frames_to_read
        )
        
        # Process block
        block_result = analyze(audio_block, sr)
        results.append(block_result)
        
        # Memory is freed after each iteration
        del audio_block
    
    return aggregate_results(results)
```

---

### Step 6: Validate the Fix

**Validation Checklist:**
- [ ] Original issue is resolved
- [ ] No new issues introduced
- [ ] Fix works across different platforms (Windows, macOS, Linux)
- [ ] Fix works with edge cases (empty files, very large files, corrupted files)
- [ ] Performance impact is acceptable
- [ ] Error messages are clear and actionable

**Create Regression Test:**
```python
def test_large_file_processing():
    """Ensure large files can be processed without MemoryError"""
    # Create synthetic large file
    duration_hours = 3
    sample_rate = 44100
    test_file = "test_large.wav"
    
    # Generate test data in chunks to avoid memory issues during test setup
    with sf.SoundFile(test_file, 'w', sample_rate, 1) as f:
        chunk_size = sample_rate * 60  # 1 minute chunks
        for _ in range(duration_hours * 60):
            chunk = np.random.randn(chunk_size).astype(np.float32) * 0.1
            f.write(chunk)
    
    # Test that analysis completes without MemoryError
    try:
        result = analyze_large_file_in_blocks(test_file, block_duration=30)
        assert result is not None
        print("✅ Large file processing test passed")
        return True
    except MemoryError:
        print("❌ Large file processing test failed - MemoryError still occurs")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
```

---

## Diagnostic Tools and Logging

### Built-in Diagnostic Scripts

**1. Preflight Check**
```bash
python preflight_check.py
```
Validates:
- Python version
- Required packages
- FFmpeg installation
- Audio device availability
- File permissions

**2. Health Assessment**
```bash
python src/lfn_health_assessment.py
```
Checks:
- System resources (CPU, RAM, disk space)
- GPU availability
- Configuration validity
- Database connectivity

---

### Custom Logging Configuration

**Application-Wide Logging:**

```python
# logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level=logging.INFO, log_file='lfn_toolkit.log'):
    """
    Configure application-wide logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-20s | %(message)s',
        handlers=[
            logging.FileHandler(log_dir / log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set third-party library log levels
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# Usage in application scripts
if __name__ == "__main__":
    logger = setup_logging(log_level=logging.DEBUG)
    logger.info("Application started")
```

**Performance Profiling:**

```python
import cProfile
import pstats
from pstats import SortKey

def profile_function(func):
    """Decorator to profile function execution"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats(SortKey.CUMULATIVE)
        stats.print_stats(20)  # Top 20 time consumers
        
        return result
    return wrapper

# Usage
@profile_function
def analyze_batch(directory):
    # Your code here
    pass
```

**Memory Profiling:**

```python
import tracemalloc
import gc

def memory_snapshot(label=""):
    """Take a memory snapshot for debugging"""
    gc.collect()  # Force garbage collection
    current, peak = tracemalloc.get_traced_memory()
    print(f"[MEMORY {label}] Current: {current / 1e6:.2f} MB | Peak: {peak / 1e6:.2f} MB")

# Usage
tracemalloc.start()

memory_snapshot("Start")
audio, sr = load_large_file()
memory_snapshot("After load")
result = analyze(audio)
memory_snapshot("After analysis")
del audio
gc.collect()
memory_snapshot("After cleanup")

tracemalloc.stop()
```

---

### System-Level Diagnostics

**Windows PowerShell:**
```powershell
# Check Python environment
python --version
pip list

# Check system resources
Get-ComputerInfo | Select-Object OsTotalVisibleMemorySize, OsFreePhysicalMemory
Get-PSDrive C | Select-Object Used,Free

# Check running processes
Get-Process python | Select-Object Id, CPU, WorkingSet, Path

# Check audio devices
Get-WmiObject Win32_SoundDevice | Select-Object Name, Status
```

**Linux/macOS:**
```bash
# System information
uname -a
python3 --version
pip3 list

# Memory usage
free -h  # Linux
vm_stat  # macOS

# Disk space
df -h

# Check audio
arecord -l  # Linux
system_profiler SPAudioDataType  # macOS

# Check CUDA (if using GPU)
nvidia-smi
nvcc --version

# Monitor process
top -p $(pgrep -f "python.*lfn_")
```

---

## Unknown Resolution Process

When encountering completely unknown issues:

### 1. Isolate the Problem

**Binary Search Approach:**
```bash
# Disable features one by one to narrow down the issue

# Test 1: Run with minimal features
python src/lfn_batch_file_analyzer.py test.wav --export-formats csv

# Test 2: Disable GPU
python src/lfn_batch_file_analyzer.py test.wav --no-gpu

# Test 3: Use simple audio file
python src/lfn_batch_file_analyzer.py simple_test.wav

# Test 4: Check each component independently
python -c "import numpy; print(numpy.__version__)"
python -c "import scipy; print(scipy.__version__)"
python -c "import soundfile; print(soundfile.__version__)"
```

### 2. Search for Similar Issues

**Check GitHub Issues:**
```bash
# Search repository issues
# Look for similar error messages, stack traces, or symptoms
```

**Search Stack Overflow:**
- Copy the exact error message
- Search for the specific function that failed
- Look for version-specific issues

**Check Package Documentation:**
- Verify you're using the API correctly
- Check for breaking changes in recent versions
- Review examples and best practices

### 3. Create Minimal Reproducible Example (MRE)

```python
# minimal_repro.py
"""
Minimal example demonstrating the unknown issue.
Environment:
- Python 3.9.5
- NumPy 1.21.0
- Windows 10

Issue: [Description]
Expected: [Expected behavior]
Actual: [Actual behavior]
"""
import numpy as np

# Minimal code that reproduces the issue
def reproduce_issue():
    data = np.array([1, 2, 3])
    # ... minimal steps to trigger issue
    pass

if __name__ == "__main__":
    reproduce_issue()
```

### 4. Bisect to Find Regression

If something that worked before is now broken:

```bash
# Use git bisect to find the breaking commit
git bisect start
git bisect bad  # Current broken state
git bisect good v1.0.0  # Last known good version

# Git will checkout commits for you to test
python src/lfn_batch_file_analyzer.py test.wav
git bisect good  # or "git bisect bad"

# Continue until the breaking commit is found
git bisect reset  # When done
```

### 5. Consult the Community

**When asking for help, provide:**

1. **Environment details:**
   ```
   - OS: Windows 10 Pro 21H2
   - Python: 3.9.5
   - LFN Toolkit: 2.0.0
   - Key packages: numpy==1.21.0, scipy==1.7.0, soundfile==0.10.3
   ```

2. **Exact error message:**
   ```
   Full stack trace with line numbers
   ```

3. **Minimal reproduction steps:**
   ```
   1. Install package
   2. Run command: python src/lfn_batch_file_analyzer.py test.wav
   3. Error occurs at line 142
   ```

4. **What you've tried:**
   ```
   - Reinstalled dependencies
   - Tested on different audio files
   - Checked FFmpeg installation
   - Results: ...
   ```

---

## Common Pitfalls and How to Avoid Them

### 1. Path Issues on Windows

**Pitfall:** Hardcoded forward slashes or backslashes
```python
# ❌ Platform-specific
path = "C:\\Users\\Name\\file.wav"  # Fails on Unix
path = "C:/Users/Name/file.wav"     # Works but not portable
```

**Root Cause Fix:**
```python
# ✅ Use pathlib for cross-platform compatibility
from pathlib import Path

path = Path.home() / "Desktop" / "file.wav"
# Works on all platforms
```

---

### 2. Encoding Issues

**Pitfall:** Assuming default encoding
```python
# ❌ Uses system default encoding (varies by platform)
with open('results.txt', 'w') as f:
    f.write(data)
```

**Root Cause Fix:**
```python
# ✅ Explicitly specify UTF-8
with open('results.txt', 'w', encoding='utf-8') as f:
    f.write(data)
```

---

### 3. Floating Point Comparisons

**Pitfall:** Direct equality check
```python
# ❌ Can fail due to floating point precision
if frequency == 50.0:
    print("Found 50 Hz")
```

**Root Cause Fix:**
```python
# ✅ Use tolerance-based comparison
import numpy as np

if np.isclose(frequency, 50.0, atol=0.1):
    print("Found ~50 Hz")
```

---

### 4. Resource Leaks

**Pitfall:** Not closing file handles
```python
# ❌ File may remain locked
file = open('data.txt')
data = file.read()
# Forgot to close!
```

**Root Cause Fix:**
```python
# ✅ Use context manager
with open('data.txt', 'r') as file:
    data = file.read()
# Automatically closed
```

---

### 5. Mutable Default Arguments

**Pitfall:** Using mutable defaults
```python
# ❌ Shared state between calls
def analyze_files(files, results=[]):
    results.append(analyze(files))
    return results
```

**Root Cause Fix:**
```python
# ✅ Use None and create new instance
def analyze_files(files, results=None):
    if results is None:
        results = []
    results.append(analyze(files))
    return results
```

---

### 6. Silent Failures

**Pitfall:** Catching all exceptions without logging
```python
# ❌ Hides real issues
try:
    process_audio(file)
except:
    pass  # What went wrong?
```

**Root Cause Fix:**
```python
# ✅ Log exceptions and handle specific errors
import logging

try:
    process_audio(file)
except FileNotFoundError as e:
    logging.error(f"Audio file not found: {file}", exc_info=True)
    raise
except MemoryError as e:
    logging.error(f"Insufficient memory to process {file}", exc_info=True)
    # Try alternative approach
    process_audio_in_chunks(file)
except Exception as e:
    logging.error(f"Unexpected error processing {file}: {e}", exc_info=True)
    raise
```

---

## Debugging by Component

### Audio Input/Recording Issues

**Diagnostic Steps:**
1. List available devices:
   ```python
   import sounddevice as sd
   print(sd.query_devices())
   ```

2. Test device access:
   ```python
   import sounddevice as sd
   import numpy as np
   
   def test_audio_input(device_id=None):
       try:
           print("Recording 2 seconds...")
           recording = sd.rec(
               int(2 * 44100), 
               samplerate=44100, 
               channels=1,
               device=device_id
           )
           sd.wait()
           print(f"✅ Recording successful: {recording.shape}")
           return True
       except Exception as e:
           print(f"❌ Recording failed: {e}")
           return False
   ```

3. Check permissions:
   - Windows: Settings → Privacy → Microphone
   - macOS: System Preferences → Security & Privacy → Microphone
   - Linux: `groups | grep audio`

---

### FFmpeg Conversion Issues

**Diagnostic Steps:**
1. Verify FFmpeg installation:
   ```bash
   ffmpeg -version
   which ffmpeg  # Unix
   where ffmpeg  # Windows
   ```

2. Test conversion manually:
   ```bash
   ffmpeg -i input.mp3 -ar 44100 -ac 1 output.wav
   ```

3. Check supported formats:
   ```bash
   ffmpeg -formats | grep -i mp3
   ffmpeg -codecs | grep -i aac
   ```

**Root Cause Analysis:**
- **Issue**: FFmpeg not found
- **Root Cause**: FFmpeg not in system PATH
- **Solution**: Add FFmpeg to PATH or specify full path in code

---

### GPU Acceleration Issues

**Diagnostic Steps:**
1. Check GPU availability:
   ```python
   try:
       import cupy as cp
       print(f"✅ CuPy version: {cp.__version__}")
       print(f"✅ CUDA version: {cp.cuda.runtime.runtimeGetVersion()}")
       print(f"✅ Device: {cp.cuda.Device(0).name.decode()}")
       
       # Test computation
       a = cp.array([1, 2, 3])
       b = cp.array([4, 5, 6])
       c = a + b
       print(f"✅ GPU computation successful: {cp.asnumpy(c)}")
   except ImportError:
       print("❌ CuPy not installed")
   except Exception as e:
       print(f"❌ GPU error: {e}")
   ```

2. Check CUDA version compatibility:
   ```bash
   nvidia-smi  # Check driver CUDA version
   python -c "import cupy; print(cupy.cuda.runtime.runtimeGetVersion())"
   ```

**Root Cause Analysis:**
- **Issue**: GPU fallback to CPU despite CuPy installed
- **Root Cause**: CUDA version mismatch between driver and CuPy
- **Solution**: Install CuPy version matching CUDA toolkit version

---

### Database Lock Issues

**Diagnostic Steps:**
1. Check for existing connections:
   ```bash
   # Windows
   tasklist | findstr python
   
   # Unix
   ps aux | grep python
   ```

2. Increase timeout:
   ```python
   import sqlite3
   
   conn = sqlite3.connect('lfn_live_log.db')
   conn.execute("PRAGMA busy_timeout = 30000")  # 30 seconds
   ```

**Root Cause Analysis:**
- **Issue**: Database locked error
- **Root Cause**: Multiple processes accessing SQLite without proper synchronization
- **Solution**: Implement proper locking or use connection pooling

---

## Performance Debugging

### Profiling Methodology

**1. Identify Bottlenecks:**
```python
import cProfile
import pstats

# Profile execution
profiler = cProfile.Profile()
profiler.enable()

# Your code
analyze_audio_files(directory)

profiler.disable()

# Analyze results
stats = pstats.Stats(profiler)
stats.strip_dirs()
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions

# Look for:
# - Functions with high cumulative time
# - Functions called many times
# - Unexpected bottlenecks
```

**2. Measure Memory Usage:**
```python
import tracemalloc

tracemalloc.start()

# Your code
result = process_large_file()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("[ Top 10 memory consumers ]")
for stat in top_stats[:10]:
    print(stat)
```

**3. Optimize Based on Data:**
- If I/O bound: Consider async operations, caching
- If CPU bound: Vectorize operations, use GPU
- If memory bound: Process in chunks, use memory-mapped files

---

## Memory Debugging

### Memory Leak Detection

```python
import gc
import sys

def find_memory_leaks():
    """Track object creation to find leaks"""
    
    # Baseline
    gc.collect()
    before_count = len(gc.get_objects())
    
    # Run operation that might leak
    for i in range(100):
        problematic_function()
    
    # Check growth
    gc.collect()
    after_count = len(gc.get_objects())
    
    leaked = after_count - before_count
    print(f"Object count increased by: {leaked}")
    
    if leaked > 1000:  # Threshold
        print("⚠️ Possible memory leak detected")
        
        # Find large objects
        all_objects = gc.get_objects()
        by_type = {}
        for obj in all_objects:
            obj_type = type(obj).__name__
            obj_size = sys.getsizeof(obj)
            by_type[obj_type] = by_type.get(obj_type, 0) + obj_size
        
        print("\nLargest types:")
        for obj_type, size in sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {obj_type}: {size / 1e6:.2f} MB")
```

---

## Development Environment Setup

### Recommended Setup for Debugging

**1. Virtual Environment:**
```bash
# Create isolated environment
python -m venv venv_debug
source venv_debug/bin/activate  # Unix
venv_debug\Scripts\activate     # Windows

# Install in editable mode
pip install -e .

# Install development tools
pip install pytest pytest-cov ipython ipdb
```

**2. IDE Configuration:**

**VS Code (launch.json):**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Batch Analyzer",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/lfn_batch_file_analyzer.py",
            "args": ["test_audio.wav"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Debug Real-time Monitor",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/lfn_realtime_monitor.py",
            "args": ["--device", "0"],
            "console": "integratedTerminal"
        }
    ]
}
```

**PyCharm:**
- Set breakpoints in gutter
- Use "Debug" configuration
- Enable "Attach to Process" for running scripts

---

## Code Review for Root Causes

### Review Checklist

When reviewing code changes, ensure they address root causes:

- [ ] **Error Handling**: Does the fix handle the underlying issue or just catch the exception?
- [ ] **Resource Management**: Are resources properly acquired and released?
- [ ] **Edge Cases**: Does the fix work for all input variations?
- [ ] **Platform Independence**: Does it work on Windows, macOS, and Linux?
- [ ] **Scalability**: Will it work with larger inputs?
- [ ] **Documentation**: Is the root cause and fix documented?
- [ ] **Tests**: Are there tests to prevent regression?
- [ ] **Logging**: Are diagnostic messages clear and actionable?

### Red Flags (Symptom Fixes)

Watch out for these patterns that often indicate symptom fixes:

```python
# 🚩 Catching all exceptions without handling root cause
try:
    risky_operation()
except:
    pass

# 🚩 Adding sleep/wait without understanding timing issue
time.sleep(5)  # "Fixes" race condition by luck

# 🚩 Ignoring warnings
import warnings
warnings.filterwarnings('ignore')

# 🚩 Arbitrary retry without fixing underlying issue
for _ in range(10):
    try:
        unreliable_operation()
        break
    except:
        continue

# 🚩 Hardcoded workarounds
if filename == "problematic.wav":
    use_alternative_method()  # Why only this file?
```

---

## Best Practices Summary

1. **Always ask "Why?"** - Drill down to root causes
2. **Document your findings** - Help others learn from issues
3. **Create reproducible tests** - Prevent regressions
4. **Use logging strategically** - Make debugging easier
5. **Profile before optimizing** - Focus on actual bottlenecks
6. **Test edge cases** - Empty inputs, huge inputs, invalid inputs
7. **Keep it simple** - Complex fixes often indicate wrong approach
8. **Learn from patterns** - Similar issues often have related root causes

---

## Additional Resources

### External Documentation
- [Python Debugging with pdb](https://docs.python.org/3/library/pdb.html)
- [NumPy Debugging Guide](https://numpy.org/doc/stable/user/troubleshooting-importerror.html)
- [SciPy Performance Tips](https://scipy-cookbook.readthedocs.io/items/PerformancePython.html)
- [CuPy User Guide](https://docs.cupy.dev/en/stable/user_guide/)

### Internal Documentation
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Symptom-based quick fixes
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [USER_GUIDE.md](docs/USER_GUIDE.md) - Application usage
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment procedures

---

**Remember**: The goal is not just to make the error go away, but to **understand why it occurred** and **prevent it from happening again**. A proper fix addresses the fundamental issue, not just its visible symptoms.

**Last Updated**: December 2025  
**Version**: 1.0.0
