# LFN Audio Toolkit - Debugging Guide

**Version:** 2.0.0  
**Last Updated:** December 19, 2025

This comprehensive guide covers debugging strategies, logging practices, and solutions for ambiguous behaviors in the LFN Audio Toolkit.

## Table of Contents

1. [Quick Debug Checklist](#quick-debug-checklist)
2. [Enabling Debug Mode](#enabling-debug-mode)
3. [Logging System](#logging-system)
4. [Debugging Workflows](#debugging-workflows)
5. [Interpreting Error Messages](#interpreting-error-messages)
6. [Common Debugging Scenarios](#common-debugging-scenarios)
7. [Ambiguous Behaviors & Edge Cases](#ambiguous-behaviors--edge-cases)
8. [Advanced Debugging Techniques](#advanced-debugging-techniques)
9. [Performance Debugging](#performance-debugging)
10. [Known Limitations](#known-limitations)

---

## Quick Debug Checklist

When encountering issues, run through this checklist first:

- [ ] **Run pre-flight check**: `python preflight_check.py`
- [ ] **Check Python version**: `python --version` (must be 3.8+)
- [ ] **Verify dependencies**: `pip list | grep -E "numpy|scipy|soundfile|sounddevice"`
- [ ] **Test audio devices**: `python -c "import sounddevice as sd; print(sd.query_devices())"`
- [ ] **Check disk space**: Ensure sufficient space for output files
- [ ] **Review recent changes**: Check if issue started after updates
- [ ] **Check file permissions**: Verify read/write access to directories
- [ ] **Review console output**: Look for warnings and error messages
- [ ] **Check log files**: Review any generated log files in the project directory

---

## Enabling Debug Mode

### Environment Variables

Set these environment variables to enable verbose debugging:

```bash
# Enable debug mode (all modules)
export LFN_DEBUG=1

# Enable verbose logging
export LFN_LOG_LEVEL=DEBUG

# Log to file instead of console
export LFN_LOG_FILE=/path/to/debug.log

# Enable FFmpeg debug output
export FFMPEG_DEBUG=1
```

**Windows (Command Prompt):**
```cmd
set LFN_DEBUG=1
set LFN_LOG_LEVEL=DEBUG
set LFN_LOG_FILE=C:\path\to\debug.log
```

**Windows (PowerShell):**
```powershell
$env:LFN_DEBUG=1
$env:LFN_LOG_LEVEL="DEBUG"
$env:LFN_LOG_FILE="C:\path\to\debug.log"
```

### Command-Line Debug Options

Most toolkit scripts support debug flags:

```bash
# Run with verbose output
python src/lfn_batch_file_analyzer.py path/to/audio --verbose

# Enable step-by-step debugging output
python src/lfn_realtime_monitor.py --debug

# Combine with other options
python src/lfn_batch_file_analyzer.py path/to/audio --gpu --verbose
```

---

## Logging System

### Log Levels

The toolkit uses the following log levels:

| Level | Purpose | When to Use |
|-------|---------|-------------|
| **DEBUG** | Detailed diagnostic information | Development, troubleshooting complex issues |
| **INFO** | General informational messages | Normal operation tracking |
| **WARNING** | Warning messages for non-critical issues | Recoverable errors, deprecations |
| **ERROR** | Error messages for failures | Failed operations, exceptions |
| **CRITICAL** | Critical errors causing shutdown | Fatal errors, system failures |

### Log File Locations

Default log file locations:

```
LFN_Audio_Toolkit_Production/
├── logs/
│   ├── lfn_debug.log              # Main debug log (all levels)
│   ├── lfn_error.log              # Error-only log
│   └── lfn_performance.log        # Performance metrics
├── src/
│   ├── lfn_live_log.db            # Real-time monitoring database
│   └── alerts_log.json            # Alert history (JSON format)
└── outputs/
    └── analysis_report_YYYYMMDD.log  # Analysis session logs
```

### Reading Log Files

**View recent errors:**
```bash
# Last 50 lines
tail -n 50 logs/lfn_error.log

# Follow in real-time
tail -f logs/lfn_debug.log

# Search for specific errors
grep -i "error" logs/lfn_debug.log
grep -i "gpu" logs/lfn_debug.log
```

**Windows PowerShell:**
```powershell
# Last 50 lines
Get-Content logs\lfn_error.log -Tail 50

# Follow in real-time
Get-Content logs\lfn_debug.log -Wait

# Search for specific errors
Select-String -Path logs\lfn_debug.log -Pattern "error" -CaseSensitive:$false
```

### Structured Logging Format

Logs follow this format:
```
[TIMESTAMP] [LEVEL] [MODULE] [FUNCTION] - MESSAGE
2025-12-19 10:30:45,123 INFO lfn_batch_file_analyzer analyze_audio_file - Processing file: audio.wav
2025-12-19 10:30:46,789 DEBUG lfn_batch_file_analyzer compute_spectrogram - FFT window size: 4096
2025-12-19 10:30:47,456 WARNING lfn_batch_file_analyzer detect_peaks - Low prominence peak detected at 45Hz
```

---

## Debugging Workflows

### Workflow 1: Batch Analysis Not Working

**Step 1: Verify input files**
```bash
# Check if files exist and are readable
ls -lh path/to/audio/

# Verify file formats
file path/to/audio/*.wav
```

**Step 2: Test with a single file**
```bash
python src/lfn_batch_file_analyzer.py path/to/single/file.wav --verbose
```

**Step 3: Check FFmpeg availability**
```bash
ffmpeg -version

# If not found, install FFmpeg
# See TROUBLESHOOTING.md for installation instructions
```

**Step 4: Test audio file conversion**
```bash
ffmpeg -i input.mp3 -ar 44100 -ac 1 test_output.wav
```

**Step 5: Check output directory permissions**
```bash
# Create output directories manually
mkdir -p outputs/spectrograms outputs/trends

# Check permissions
ls -la outputs/
```

### Workflow 2: Real-Time Monitoring Crashes

**Step 1: List audio devices**
```python
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**Step 2: Test default device**
```python
python -c "import sounddevice as sd; import numpy as np; sd.rec(44100, duration=1, samplerate=44100, channels=1); print('Recording test successful')"
```

**Step 3: Try with specific device**
```bash
python src/lfn_realtime_monitor.py --device 1
```

**Step 4: Check for device conflicts**
```bash
# Close other audio applications
# On Linux, check with:
lsof /dev/snd/*

# On Windows, check Task Manager → Processes
# Look for: Audacity, OBS, Skype, etc.
```

**Step 5: Reduce buffer size to avoid overflows**
```bash
python src/lfn_realtime_monitor.py --duration 5
```

### Workflow 3: GPU Acceleration Issues

**Step 1: Verify CUDA installation**
```bash
nvidia-smi

# Check CUDA version
nvcc --version
```

**Step 2: Test CuPy installation**
```python
python -c "import cupy as cp; print('CuPy version:', cp.__version__); print('CUDA version:', cp.cuda.runtime.runtimeGetVersion())"
```

**Step 3: Test GPU computation**
```python
python -c "import cupy as cp; x = cp.array([1, 2, 3]); print('GPU test:', x * 2)"
```

**Step 4: Check GPU memory**
```bash
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
```

**Step 5: Run without GPU first**
```bash
# Verify analysis works on CPU
python src/lfn_batch_file_analyzer.py path/to/audio

# Then try with GPU
python src/lfn_batch_file_analyzer.py path/to/audio --gpu
```

---

## Interpreting Error Messages

### Common Error Patterns

#### 1. Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'soundfile'
```

**Meaning:** Required Python package not installed.

**Solution:**
```bash
pip install soundfile
# Or reinstall all dependencies
pip install -r requirements.txt
```

**Debug Steps:**
1. Check which Python interpreter is running: `which python` or `where python`
2. Verify pip is installing to correct location: `pip show soundfile`
3. Check if virtual environment is activated

---

#### 2. Audio Device Errors

**Error:**
```
PortAudioError: Device unavailable
OSError: [Errno -9996] Invalid input device
```

**Meaning:** Selected audio device not accessible or doesn't exist.

**Debug Steps:**
1. List all devices: `python -c "import sounddevice as sd; print(sd.query_devices())"`
2. Check device permissions (especially on macOS/Linux)
3. Verify microphone is connected and not in use by another application
4. Try default device: Don't specify `--device` parameter

---

#### 3. FFmpeg Conversion Errors

**Error:**
```
❌ ffmpeg conversion failed: [Errno 2] No such file or directory: 'ffmpeg'
```

**Meaning:** FFmpeg is not installed or not in system PATH.

**Debug Steps:**
1. Test FFmpeg: `ffmpeg -version`
2. Check PATH: `echo $PATH` (Linux/Mac) or `echo %PATH%` (Windows)
3. Install FFmpeg (see TROUBLESHOOTING.md)
4. Specify full path to FFmpeg in code if necessary

---

#### 4. Memory Errors

**Error:**
```
MemoryError: Unable to allocate array
numpy.core._exceptions._ArrayMemoryError
```

**Meaning:** Insufficient RAM for operation.

**Debug Steps:**
1. Check available memory: `free -h` (Linux) or Task Manager (Windows)
2. Close other applications
3. Process files in smaller chunks: `--block-duration 30`
4. Use segmented recording for long sessions
5. Monitor memory during operation: `watch -n 1 free -h`

---

#### 5. GPU Errors

**Error:**
```
⚠️ GPU computation failed, falling back to CPU: Out of memory
cupy.cuda.memory.OutOfMemoryError
```

**Meaning:** GPU memory exhausted.

**Debug Steps:**
1. Check GPU memory: `nvidia-smi`
2. Reduce batch size or chunk size
3. Close other GPU applications (browsers, games)
4. Restart GPU driver: `sudo systemctl restart nvidia-persistenced`
5. Fall back to CPU if issue persists

---

#### 6. File Format Errors

**Error:**
```
RuntimeError: Error opening 'file.mp3': Format not recognised.
```

**Meaning:** Audio file format not supported or file is corrupted.

**Debug Steps:**
1. Check file integrity: `file audio.mp3`
2. Try opening in media player
3. Convert to WAV manually: `ffmpeg -i input.mp3 output.wav`
4. Check for zero-byte files: `ls -lh file.mp3`
5. Verify file extension matches actual format

---

#### 7. Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'outputs/spectrogram.png'
```

**Meaning:** No write permission to output directory.

**Debug Steps:**
1. Check directory permissions: `ls -la outputs/`
2. Create directory if missing: `mkdir -p outputs/spectrograms`
3. Change permissions if needed: `chmod -R 755 outputs/`
4. Run as appropriate user (avoid root/admin when possible)

---

#### 8. Unicode/Encoding Errors (Windows)

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '🎵'
```

**Meaning:** Console encoding issue on Windows.

**Solution:** This is automatically handled in the toolkit scripts. If you still see this:
```cmd
chcp 65001
set PYTHONIOENCODING=utf-8
```

---

## Common Debugging Scenarios

### Scenario 1: "Analysis completes but no spectrograms generated"

**Possible Causes:**
- Output directory doesn't exist
- No write permissions
- Matplotlib backend issue
- Disk full

**Debugging Steps:**
1. Check if directory exists: `ls outputs/spectrograms/`
2. Create if missing: `mkdir -p outputs/spectrograms`
3. Test matplotlib:
   ```python
   python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.savefig('test.png'); print('Success')"
   ```
4. Check disk space: `df -h .`
5. Verify file actually saved: `ls -lh spectrograms/`

---

### Scenario 2: "GPU acceleration doesn't speed up processing"

**Possible Causes:**
- Small dataset (GPU overhead > speedup)
- Data transfer bottleneck
- GPU not being used despite flag
- Incorrect CuPy version

**Debugging Steps:**
1. Verify GPU actually in use:
   ```bash
   # In one terminal:
   watch -n 1 nvidia-smi
   
   # In another terminal:
   python src/lfn_batch_file_analyzer.py path/to/audio --gpu
   ```
2. Check for CPU fallback messages in output
3. Test with larger dataset
4. Monitor GPU utilization percentage
5. Compare timing with and without `--gpu`

---

### Scenario 3: "Real-time monitor shows incorrect frequency values"

**Possible Causes:**
- Sample rate mismatch
- Microphone frequency response not flat
- Background noise interference
- Calibration needed

**Debugging Steps:**
1. Check actual sample rate:
   ```python
   python -c "import sounddevice as sd; print(sd.query_devices()[0]['default_samplerate'])"
   ```
2. Verify microphone specifications (especially for LFN and ultrasonic)
3. Test in quiet environment
4. Use calibrated measurement microphone (e.g., Dayton EMM-6)
5. Apply calibration file if available

---

### Scenario 4: "Database locked errors in real-time monitor"

**Possible Causes:**
- Multiple instances running
- Previous crash left lock file
- Network drive issues (if on network storage)

**Debugging Steps:**
1. Check for running instances:
   ```bash
   ps aux | grep lfn_realtime_monitor
   ```
2. Kill other instances: `kill <PID>`
3. Remove lock file:
   ```bash
   rm src/lfn_live_log.db-journal
   ```
4. Move database to local disk if on network drive
5. Restart with clean database: `rm src/lfn_live_log.db`

---

### Scenario 5: "Files processing very slowly"

**Possible Causes:**
- Large file size
- Low system resources
- Hard disk (not SSD)
- Background processes

**Debugging Steps:**
1. Monitor resource usage:
   ```bash
   htop  # Linux
   # Or Task Manager on Windows
   ```
2. Check file size: `ls -lh file.wav`
3. Enable block processing: `--block-duration 30`
4. Close unnecessary applications
5. Move files to faster storage (SSD)
6. Consider upgrading hardware for large-scale processing

---

## Ambiguous Behaviors & Edge Cases

### 1. Peak Detection in Noisy Environments

**Behavior:** Multiple peaks detected in same frequency range, values fluctuating.

**Explanation:** 
- Noise floor varies across time
- Prominence threshold may be too low
- Multiple simultaneous sound sources

**Best Practice:**
- Increase prominence threshold in code
- Use longer averaging windows
- Apply noise reduction preprocessing
- Record in controlled environment

**Code Location:** `src/lfn_batch_file_analyzer.py`, function `detect_peaks_in_range`

---

### 2. GPU Fallback Without Clear Warning

**Behavior:** Script runs but doesn't use GPU despite `--gpu` flag.

**Explanation:**
- CuPy import failed silently
- GPU out of memory (automatic fallback)
- CUDA version mismatch

**Detection:**
- Look for initialization message: "🚀 GPU acceleration enabled" vs "💻 Running on CPU"
- Check for fallback warning: "⚠️ GPU computation failed, falling back to CPU"
- Monitor GPU usage with `nvidia-smi`

**Best Practice:**
- Always check startup messages
- Test GPU before processing large batches
- Monitor GPU memory during processing

---

### 3. Spectrogram Time Resolution Inconsistency

**Behavior:** Spectrogram time axis doesn't match audio duration exactly.

**Explanation:**
- Window overlap causes edge effects
- FFT window size affects time resolution
- Time bins are discrete, not continuous

**Expected Behavior:**
- Slight mismatch (< 1 second) is normal
- More noticeable with larger FFT window sizes

**Configuration:**
```python
# In lfn_batch_file_analyzer.py, line ~63
NPERSEG = 4096  # Larger = better freq resolution, worse time resolution
NOVERLAP = 2048  # Larger = smoother spectrogram
```

---

### 4. Different Results Between Runs

**Behavior:** Slight variations in peak frequencies or dB levels between runs on same file.

**Explanation:**
- Floating-point arithmetic precision
- Different random seeds in numpy operations
- System load affecting timing

**Expected Variance:**
- Frequency: ±0.5 Hz
- dB level: ±0.1 dB

**Mitigation:**
- Average multiple runs for critical measurements
- Use deterministic operations where possible
- Control for system load

---

### 5. Alert Threshold Behavior

**Behavior:** Alert triggers at unexpected times or doesn't trigger when expected.

**Explanation:**
- Thresholds are dB SPL (Sound Pressure Level), not dBFS
- Peak detection uses prominence filtering
- Time-varying signals may cross threshold intermittently

**Configuration:**
```python
# Default thresholds (can be adjusted)
LFN_ALERT_THRESHOLD = -20.0    # dB
HF_ALERT_THRESHOLD = -30.0      # dB
```

**Best Practice:**
- Adjust thresholds based on your environment
- Use alert history to tune sensitivity
- Consider peak vs average behavior

---

### 6. File Conversion Artifacts

**Behavior:** Analyzed results differ between original file and converted WAV.

**Explanation:**
- Lossy compression artifacts (MP3, AAC)
- Sample rate conversion interpolation
- Bit depth changes

**Best Practice:**
- Use WAV or FLAC formats when possible
- Avoid multiple conversion steps
- Document original format in analysis notes
- Use highest quality settings for conversion

---

### 7. Real-Time vs Batch Analysis Differences

**Behavior:** Real-time monitoring shows different values than batch analysis of same recording.

**Explanation:**
- Different averaging windows
- Real-time uses shorter FFT windows
- Batch uses block processing
- Timestamp alignment differences

**Expected Differences:**
- ±2-3 Hz in peak frequencies
- ±1-2 dB in levels

**Mitigation:**
- Use consistent parameters when comparing
- Document analysis method used
- Prefer batch analysis for archival/reference measurements

---

## Advanced Debugging Techniques

### Using Python Debugger (pdb)

Add breakpoints in source code:

```python
import pdb

def analyze_audio_file(file_path):
    # Set breakpoint here
    pdb.set_trace()
    
    # Code execution will pause here
    audio_data, sr = sf.read(file_path)
    # ...
```

**Common pdb commands:**
- `n` (next): Execute next line
- `s` (step): Step into function
- `c` (continue): Continue execution
- `p variable`: Print variable value
- `l` (list): Show current code context
- `q` (quit): Exit debugger

### Using IPython for Interactive Debugging

```python
# Add this where you want to debug
from IPython import embed
embed()
```

Then you can interactively explore variables and run commands.

### Profiling Performance

**Using cProfile:**
```bash
python -m cProfile -o profile.stats src/lfn_batch_file_analyzer.py path/to/audio
python -m pstats profile.stats
# Then in pstats:
# >>> sort time
# >>> stats 20
```

**Using line_profiler for line-by-line profiling:**
```bash
pip install line_profiler

# Add @profile decorator to function of interest
# Then run:
kernprof -l -v src/lfn_batch_file_analyzer.py path/to/audio
```

### Memory Profiling

```bash
pip install memory_profiler

# Add @profile decorator to function
# Then run:
python -m memory_profiler src/lfn_batch_file_analyzer.py path/to/audio
```

### Network and I/O Debugging

Monitor disk I/O:
```bash
# Linux
iotop -o

# Windows
resmon.exe  # Resource Monitor
```

Monitor file operations:
```bash
# Linux
strace -e trace=open,read,write python src/lfn_batch_file_analyzer.py path/to/audio

# macOS
dtruss -f python src/lfn_batch_file_analyzer.py path/to/audio
```

---

## Performance Debugging

### Identifying Bottlenecks

**1. CPU-Bound Operations:**
- FFT computations
- Peak detection algorithms
- Data preprocessing

**Signs:**
- High CPU usage (near 100%)
- Single core saturated
- GPU idle

**Solutions:**
- Enable GPU acceleration (`--gpu`)
- Reduce FFT window size
- Use block processing

---

**2. I/O-Bound Operations:**
- Reading large audio files
- Writing spectrograms
- Database operations

**Signs:**
- Low CPU usage
- High disk usage
- Slow progress with small files

**Solutions:**
- Use SSD storage
- Reduce output file sizes
- Batch database writes
- Enable file caching

---

**3. Memory-Bound Operations:**
- Loading entire files into memory
- Spectrogram computation
- Long recordings

**Signs:**
- Increasing memory usage
- System swapping
- MemoryError exceptions

**Solutions:**
- Use `--block-duration` flag
- Close other applications
- Increase system RAM
- Use memory-mapped files

---

### Benchmarking

**Time specific operations:**
```python
import time

start = time.time()
# ... operation to benchmark ...
elapsed = time.time() - start
print(f"Operation took {elapsed:.2f} seconds")
```

**Compare processing modes:**
```bash
# Benchmark CPU mode
time python src/lfn_batch_file_analyzer.py path/to/audio

# Benchmark GPU mode
time python src/lfn_batch_file_analyzer.py path/to/audio --gpu
```

---

## Known Limitations

### Hardware Limitations

1. **Microphone Frequency Response**
   - Most consumer microphones don't capture below 20 Hz
   - Ultrasonic response typically rolls off above 20 kHz
   - **Solution:** Use measurement microphone (e.g., Dayton EMM-6, UMIK-1)

2. **Sound Card Limitations**
   - Typical sound cards: 20 Hz - 20 kHz
   - Sample rate limits maximum frequency (Nyquist: fs/2)
   - **Solution:** Use high-quality audio interface with extended range

3. **GPU Memory**
   - Large spectrograms may exceed GPU memory
   - Automatic fallback to CPU
   - **Solution:** Use block processing or reduce resolution

### Software Limitations

1. **Sample Rate Constraints**
   - Maximum frequency detectable: sample_rate / 2
   - 44100 Hz → max 22050 Hz
   - 48000 Hz → max 24000 Hz (required for full ultrasonic range)

2. **Time-Frequency Resolution Trade-off**
   - Larger FFT window → better frequency resolution, worse time resolution
   - Smaller FFT window → better time resolution, worse frequency resolution
   - Cannot have both simultaneously (Heisenberg uncertainty principle)

3. **Peak Detection Accuracy**
   - Frequency bin width limits precision: Δf = sample_rate / NPERSEG
   - For 48 kHz, 4096 NPERSEG: Δf ≈ 11.7 Hz
   - Interpolation can improve, but has limits

4. **Real-Time Processing Latency**
   - Minimum latency ~100ms for analysis
   - Database writes add overhead
   - Cannot achieve sub-10ms latency

### File Format Limitations

1. **Lossy Compression**
   - MP3, AAC lose high-frequency content
   - Not suitable for ultrasonic analysis
   - **Solution:** Use WAV or FLAC

2. **File Size**
   - Very large files (>2 GB) may be slow
   - Memory constraints for full-file processing
   - **Solution:** Use `--block-duration`

3. **Metadata**
   - Not all formats preserve recording metadata
   - Calibration data may be lost
   - **Solution:** Keep original files, document settings

---

## Getting Further Help

### Information to Provide When Reporting Issues

When seeking help, provide:

1. **System Information:**
   ```bash
   python preflight_check.py > system_info.txt
   ```

2. **Error Messages:**
   - Full error traceback
   - Relevant log file excerpts
   - Console output

3. **Reproduction Steps:**
   - Exact command used
   - File formats and sizes
   - Expected vs actual behavior

4. **Environment:**
   - Python version: `python --version`
   - Package versions: `pip list`
   - OS and version
   - GPU info (if relevant): `nvidia-smi`

5. **Attempts to Resolve:**
   - What you've already tried
   - Results of diagnostic commands
   - Changes that made it better/worse

### Support Channels

- **Documentation:** Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
- **GitHub Issues:** [https://github.com/OtaglivE999/LFN-Audio-Tool-KIT/issues](https://github.com/OtaglivE999/LFN-Audio-Tool-KIT/issues)
- **Discussions:** For questions and general help
- **Stack Overflow:** Tag with `lfn-audio-toolkit`

---

## Appendix: Debugging Configuration Reference

### Environment Variables

| Variable | Purpose | Values | Default |
|----------|---------|--------|---------|
| `LFN_DEBUG` | Enable debug mode | 0, 1 | 0 |
| `LFN_LOG_LEVEL` | Logging verbosity | DEBUG, INFO, WARNING, ERROR | INFO |
| `LFN_LOG_FILE` | Log file path | File path | None (console) |
| `FFMPEG_DEBUG` | FFmpeg verbose output | 0, 1 | 0 |
| `CUDA_VISIBLE_DEVICES` | GPU selection | 0,1,2... | All GPUs |

### Configuration Files

Currently, configuration is hardcoded in source files. Future versions may support:
- `config/logging.conf` - Logging configuration
- `config/thresholds.json` - Alert thresholds
- `config/devices.json` - Audio device preferences

### Diagnostic Commands Summary

```bash
# System health
python preflight_check.py
python run_tests.py
python src/lfn_health_assessment.py

# Audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Dependencies
pip list | grep -E "numpy|scipy|soundfile|sounddevice|cupy"

# GPU
nvidia-smi
python -c "import cupy as cp; print(cp.cuda.runtime.runtimeGetVersion())"

# FFmpeg
ffmpeg -version
ffmpeg -formats

# Disk space
df -h .

# Memory
free -h

# Processes
ps aux | grep python
```

---

**For troubleshooting installation and common runtime issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

**For usage instructions, see [USER_GUIDE.md](docs/USER_GUIDE.md)**

**For contributing and development, see [CONTRIBUTING.md](CONTRIBUTING.md)**
