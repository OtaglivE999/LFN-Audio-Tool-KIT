# LFN Audio Toolkit - Troubleshooting Guide

This guide covers common issues and their solutions when using the LFN Audio Toolkit.

> **Note**: This guide provides quick solutions for common symptoms. For in-depth debugging methodology and root cause analysis, see [DEBUGGING.md](DEBUGGING.md).

## Table of Contents

- [Installation Issues](#installation-issues)
- [Audio Device Issues](#audio-device-issues)
- [FFmpeg Issues](#ffmpeg-issues)
- [GPU Acceleration Issues](#gpu-acceleration-issues)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [Output File Issues](#output-file-issues)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Problem: `pip install` fails with permission errors

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Root Cause:**
Python packages are trying to install into system directories (e.g., `/usr/local/lib/python3.x/`) where your user account lacks write permissions. This commonly occurs when Python was installed system-wide or when using a Python installation that was previously managed with sudo/administrator privileges.

**Solutions:**

**Option 1:** Install for current user only (recommended)
```bash
pip install --user -r requirements.txt
```

**Option 2:** Use virtual environment (best practice)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option 3:** Run as administrator (Windows only, not recommended)
```bash
# Right-click Command Prompt -> Run as Administrator
pip install -r requirements.txt
```

**Prevention:**
Always use virtual environments (`python -m venv venv`) for project-specific dependencies. This isolates packages and prevents permission conflicts.

---

### Problem: `ModuleNotFoundError` after installation

**Symptoms:**
```python
ModuleNotFoundError: No module named 'soundfile'
```

**Root Cause:**
The Python interpreter running your script is different from the Python environment where packages were installed. This happens when you have multiple Python installations (system Python, Anaconda, virtual environments) and pip installs to one while your script runs with another.

**Solutions:**

1. **Verify installation:**
```bash
pip list | grep soundfile  # Linux/Mac
pip list | findstr soundfile  # Windows
```

2. **Reinstall the missing package:**
```bash
pip install --upgrade soundfile
```

3. **Check Python version mismatch:**
```bash
# Ensure you're using the same Python version
python --version
pip --version
```

4. **Use the correct pip for your Python:**
```bash
python -m pip install soundfile
```

**Prevention:**
- Use `python -m pip` instead of just `pip` to ensure packages install to the correct Python
- Activate your virtual environment before installing packages
- Use `which python` (Unix) or `where python` (Windows) to verify which Python is active

---

### Problem: `setup.py` fails during installation

**Symptoms:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Root Cause:**
Some Python packages (like `soundfile` or `numpy` when building from source) require C/C++ compilation during installation. Windows doesn't include a C compiler by default, unlike Linux and macOS. The package is trying to compile native extensions but can't find the necessary build tools.

**Solutions:**

**Windows:**
1. Install Microsoft C++ Build Tools:
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++"

**Alternative:** Use precompiled wheels
```bash
pip install --only-binary :all: -r requirements.txt
```

**Prevention:**
Install precompiled binary packages (wheels) when available to avoid compilation requirements.

---

## Audio Device Issues

### Problem: No audio input devices detected

**Symptoms:**
```
Error: Device has no input channels
No audio input devices available
```

**Solutions:**

1. **List available devices:**
```python
import sounddevice as sd
print(sd.query_devices())
```

2. **Check system audio settings:**
   - **Windows:** Settings → System → Sound → Input
   - **macOS:** System Preferences → Sound → Input
   - **Linux:** `arecord -l` or PulseAudio Volume Control

3. **Ensure microphone is not muted:**
   - Check physical mute button
   - Check system volume mixer
   - Verify app has microphone permissions

4. **Select specific device:**
```bash
python src/lfn_realtime_monitor.py --device 1
```

**Prevention:**
- Ensure microphone is connected before running the application
- Grant microphone permissions when prompted by the OS
- Test audio device with system utilities before using the toolkit

---

### Problem: Audio device access denied

**Symptoms:**
```
PortAudioError: Device unavailable
PermissionError: [Errno 13] Permission denied
```

**Root Cause:**
Modern operating systems require explicit user permission for applications to access microphones (privacy protection). The application hasn't been granted these permissions, or on Linux, the user account isn't in the `audio` group which controls audio device access.

**Solutions:**

**Windows:**
- Settings → Privacy → Microphone → Allow apps to access microphone

**macOS:**
- System Preferences → Security & Privacy → Privacy → Microphone
- Add Terminal/IDE to allowed apps

**Linux:**
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Log out and back in
```

**Prevention:**
Grant microphone permissions when first prompted by the OS. On Linux, ensure your user is in the audio group during initial setup.

---

### Problem: Audio buffer overflow warnings

**Symptoms:**
```
[WARN] Audio buffer overflow detected
```

**Root Cause:**
The system cannot process audio data fast enough to keep up with the incoming audio stream. Data is arriving faster than it can be consumed, causing the input buffer to fill up and overflow. This indicates insufficient CPU resources, inefficient processing algorithms, or conflicts with other applications using the audio subsystem.

**Solutions:**

1. **Increase buffer size:** Reduce sample rate or increase blocksize
2. **Close other audio applications**
3. **Check CPU usage** - ensure system isn't overloaded
4. **Disable real-time effects** in audio drivers

**Prevention:**
- Monitor CPU usage before starting real-time analysis
- Close unnecessary applications
- Use GPU acceleration if available
- Adjust buffer size based on your system's performance

---

## FFmpeg Issues

### Problem: `ffmpeg` not found

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
ffmpeg conversion failed
```

**Root Cause:**
The FFmpeg executable is either not installed on the system, or it's installed but not in any directory listed in the system's PATH environment variable. When the toolkit tries to run `ffmpeg`, the operating system cannot locate the executable.

**Solutions:**

1. **Install FFmpeg:**

   **Windows (Chocolatey):**
   ```bash
   choco install ffmpeg
   ```

   **Windows (Manual):**
   - Download from: https://ffmpeg.org/download.html
   - Extract to C:\ffmpeg
   - Add to PATH: System Properties → Environment Variables → Path → Add `C:\ffmpeg\bin`

   **macOS:**
   ```bash
   brew install ffmpeg
   ```

   **Linux (Debian/Ubuntu):**
   ```bash
   sudo apt update && sudo apt install ffmpeg
   ```

2. **Verify installation:**
```bash
ffmpeg -version
```

3. **Specify FFmpeg path manually:**
```python
# In lfn_batch_file_analyzer.py, line 54:
command = ["C:\\path\\to\\ffmpeg.exe", "-y", "-i", input_path, ...]
```

**Prevention:**
Install FFmpeg and add it to PATH during initial setup. Verify with `ffmpeg -version` before running the toolkit.

---

### Problem: Audio conversion fails

**Symptoms:**
```
❌ ffmpeg conversion failed: CalledProcessError
```

**Root Cause:**
The audio file may be corrupted, in an unsupported format, protected by DRM, or the FFmpeg installation may lack necessary codecs. FFmpeg might also fail if there are file path issues (spaces, special characters) or insufficient disk space for the output file.

**Solutions:**

1. **Check file format support:**
```bash
ffmpeg -formats | grep mp3
```

2. **Manually test conversion:**
```bash
ffmpeg -i input.mp3 -ar 44100 -ac 1 output.wav
```

3. **Check file corruption:**
   - Try opening file in media player
   - Verify file isn't 0 bytes

4. **Use WAV files directly** to bypass conversion

**Prevention:**
- Test FFmpeg with sample files before processing important audio
- Verify file integrity before conversion
- Ensure adequate disk space
- Avoid file paths with spaces or special characters

---

## GPU Acceleration Issues

### Problem: CuPy installation fails

**Symptoms:**
```
ERROR: Could not find a version that satisfies the requirement cupy-cuda11x
```

**Root Cause:**
There's a version mismatch between the installed CUDA toolkit/driver and the CuPy package you're trying to install. CuPy packages are built for specific CUDA versions (e.g., cupy-cuda11x for CUDA 11.x, cupy-cuda12x for CUDA 12.x), and you must install the matching version. Alternatively, you may not have an NVIDIA GPU or CUDA drivers installed at all.

**Solutions:**

1. **Check CUDA version:**
```bash
nvidia-smi
# Look for "CUDA Version: X.X"
```

2. **Install matching CuPy version:**
```bash
# For CUDA 11.x
pip install cupy-cuda11x

# For CUDA 12.x
pip install cupy-cuda12x
```

3. **If no NVIDIA GPU:** Skip GPU installation (toolkit works without it)

**Prevention:**
Check CUDA version with `nvidia-smi` before installing CuPy, and install the matching cupy-cudaXXx package.

---

### Problem: GPU falls back to CPU despite CuPy installed

**Symptoms:**
```
⚠️ GPU computation failed, falling back to CPU
[CPU] Running on CPU
```

**Root Cause:**
While CuPy is installed, the GPU is unavailable for computation. Common causes include: GPU memory exhausted by other applications, CUDA driver version mismatch, GPU being used by another process, outdated NVIDIA drivers, or the CuPy installation not matching the installed CUDA runtime version.

**Solutions:**

1. **Verify CUDA installation:**
```python
import cupy as cp
print(cp.cuda.runtime.runtimeGetVersion())
```

2. **Check GPU memory:**
```bash
nvidia-smi
# Look for available memory
```

3. **Close other GPU applications** (games, CUDA apps, browsers with hardware acceleration)

4. **Update NVIDIA drivers:**
   - Download latest from: https://www.nvidia.com/drivers

**Prevention:**
- Monitor GPU memory usage before starting analysis
- Ensure CuPy version matches CUDA version
- Keep NVIDIA drivers up to date
- Close GPU-intensive applications before running analysis

---

## Runtime Errors

### Problem: `MemoryError` during long recordings

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Root Cause:**
The application is trying to load an entire long audio file into RAM at once, which exceeds available system memory. Audio files grow linearly with duration (e.g., a 2-hour recording at 44.1kHz mono requires ~1.2GB). The system doesn't have enough contiguous free RAM to allocate this array, leading to MemoryError.

**Solutions:**

1. **Use segmented recording:**
```python
from src.long_duration_recorder import LongDurationRecorder
recorder = LongDurationRecorder(segment_duration=1800)  # 30-min segments
recorder.record_long_session(8.0, "output")
```

2. **Reduce sample rate:**
```bash
python src/lfn_realtime_monitor.py --sample-rate 44100
```

3. **Close other applications** to free RAM

4. **Monitor memory usage:**
```python
import psutil
print(f"Available RAM: {psutil.virtual_memory().available / 1024**3:.2f} GB")
```

**Prevention:**
Use the `long_duration_recorder.py` module for recordings longer than 30 minutes, which automatically segments recordings to prevent memory issues.

---

### Problem: Database locked errors

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Root Cause:**
SQLite databases allow only one write operation at a time. Another process or thread is currently holding a write lock on the database file. This commonly occurs when multiple instances of the real-time monitor are running simultaneously, or when the previous instance didn't shut down cleanly, leaving a stale lock.

**Solutions:**

1. **Close other instances** of the real-time monitor
2. **Delete lock file:**
```bash
rm lfn_live_log.db-journal
```
3. **Increase timeout:**
```python
# In lfn_realtime_monitor.py:
conn.execute("PRAGMA busy_timeout = 30000")  # 30 seconds
```

**Prevention:**
Only run one instance of the real-time monitor at a time. Ensure proper shutdown with Ctrl+C to release database locks cleanly.

---

### Problem: UTF-8 encoding errors on Windows

**Symptoms:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Root Cause:**
Windows console (cmd.exe) defaults to legacy encodings like cp1252 or cp437 instead of UTF-8. When Python tries to print Unicode characters (emojis, special symbols) that don't exist in these legacy encodings, it fails. This is a Windows-specific issue due to backward compatibility with old console applications.

**Solutions:**

1. **Set environment variable:**
```bash
set PYTHONIOENCODING=utf-8
```

2. **Already handled in scripts** - UTF-8 encoding is forced at lines 9-15 in each script

3. **Use Windows Terminal** instead of cmd.exe

**Prevention:**
Use Windows Terminal (available in Windows 10+) which defaults to UTF-8, or set PYTHONIOENCODING=utf-8 permanently in system environment variables.

---

## Performance Issues

### Problem: Real-time monitoring is slow/laggy

**Symptoms:**
- Analysis takes >5 seconds per interval
- Spectrograms delayed
- Console output slow

**Root Cause:**
The system cannot process audio analysis fast enough in real-time. This is typically due to CPU-intensive spectrogram computation, insufficient CPU resources, or inefficient algorithms running on the CPU when GPU acceleration could provide 10x speedup. High spectrogram resolution also increases computation time quadratically.

**Solutions:**

1. **Enable GPU acceleration:**
```bash
python src/lfn_realtime_monitor.py --gpu
```

2. **Reduce spectrogram resolution:**
```python
# In lfn_realtime_monitor.py, line 62:
SPECTROGRAM_NPERSEG = 1024  # Was 2048
```

3. **Increase duration interval:**
```python
# In lfn_realtime_monitor.py, line 50:
DURATION_SEC = 10  # Was 5
```

4. **Disable trend plots** if not needed

5. **Close resource-heavy applications**

---

### Problem: Batch processing is very slow

**Symptoms:**
- Processing 100 files takes hours
- High CPU/memory usage

**Solutions:**

1. **Enable GPU acceleration:**
```bash
python src/lfn_batch_file_analyzer.py "path" --gpu
```

2. **Use block processing for large files:**
```bash
python src/lfn_batch_file_analyzer.py "path" --block-duration 30
```

3. **Disable trend tracking:**
```bash
python src/lfn_batch_file_analyzer.py "path" --no-trends
```

4. **Process in smaller batches**

---

## Output File Issues

### Problem: Spectrograms not generated

**Symptoms:**
- No PNG files in `spectrograms/` folder
- "Spectrogram: None" in results

**Solutions:**

1. **Check directory permissions:**
```bash
# Windows
icacls spectrograms
# Linux/Mac
ls -la spectrograms/
```

2. **Manually create directory:**
```bash
mkdir -p outputs/spectrograms
```

3. **Check disk space:**
```bash
df -h .  # Linux/Mac
dir     # Windows
```

4. **Verify matplotlib backend:**
```python
import matplotlib
print(matplotlib.get_backend())
# Should be 'Agg' for non-interactive
```

---

### Problem: Excel export fails

**Symptoms:**
```
⚠️ Excel export failed: ...
```

**Solutions:**

1. **Verify openpyxl installed:**
```bash
pip install --upgrade openpyxl
```

2. **Close Excel** if file is open

3. **Check write permissions** in output directory

4. **Use CSV instead:**
```bash
python src/lfn_batch_file_analyzer.py "path" --export-formats csv
```

---

### Problem: Output files have incorrect paths on Windows

**Symptoms:**
```
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

**Solutions:**

1. **Use raw strings or forward slashes:**
```python
path = r"C:\Users\Name\Desktop\audio"  # Raw string
# Or
path = "C:/Users/Name/Desktop/audio"   # Forward slashes work on Windows
```

2. **Avoid paths >260 characters** (Windows limitation)
   - Use shorter folder names
   - Place toolkit closer to C:\

3. **Use pathlib:**
```python
from pathlib import Path
path = Path("C:/Users/Name/Desktop/audio")
```

---

## Platform-Specific Issues

### Windows: "Python not recognized" error

**Solutions:**

1. **Add Python to PATH:**
   - Reinstall Python with "Add to PATH" checked
   - Or manually: System Properties → Environment Variables → Path → Add Python directory

2. **Use Python launcher:**
```bash
py script.py  # Instead of python script.py
```

3. **Use full path:**
```bash
C:\Python39\python.exe script.py
```

---

### macOS: "command not found: python"

**Solutions:**

1. **Use python3:**
```bash
python3 src/lfn_batch_file_analyzer.py "path"
```

2. **Create alias:**
```bash
echo "alias python=python3" >> ~/.zshrc
source ~/.zshrc
```

3. **Install Python from python.org** (not just Xcode tools)

---

### Linux: PortAudio errors

**Symptoms:**
```
OSError: PortAudio library not found
ImportError: libportaudio.so.2: cannot open shared object file
```

**Solutions:**

1. **Install PortAudio:**
```bash
# Debian/Ubuntu
sudo apt install portaudio19-dev python3-pyaudio

# Fedora
sudo dnf install portaudio-devel

# Arch
sudo pacman -S portaudio
```

2. **Reinstall sounddevice:**
```bash
pip uninstall sounddevice
pip install --no-cache-dir sounddevice
```

---

## Still Having Issues?

If your problem isn't covered here:

1. **Run the pre-flight check:**
```bash
python preflight_check.py
```

2. **Run the test suite:**
```bash
python run_tests.py
```

3. **Check logs:** Look for error messages and stack traces

4. **Gather system information:**
```bash
python --version
pip list
# GPU info (if applicable):
nvidia-smi
```

5. **Create an issue on GitHub** with:
   - Full error message and traceback
   - System information (OS, Python version)
   - Steps to reproduce
   - Output of `preflight_check.py`

---

## Quick Diagnostics

Run these commands to diagnose common issues:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Check FFmpeg
ffmpeg -version

# Check audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Check GPU
python -c "import cupy as cp; print(cp.cuda.runtime.runtimeGetVersion())"

# Run full diagnostic
python preflight_check.py
```

---

## Emergency Fixes

### Complete reinstall:

```bash
# 1. Remove virtual environment (if using)
rm -rf venv/  # Linux/Mac
rmdir /s venv  # Windows

# 2. Clear pip cache
pip cache purge

# 3. Reinstall everything
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verify installation
python preflight_check.py
```

---

## Performance Tuning Checklist

- [ ] GPU acceleration enabled (`--gpu` flag)
- [ ] FFmpeg installed and in PATH
- [ ] Sufficient RAM available (4GB+ free)
- [ ] SSD storage (faster than HDD)
- [ ] Close unnecessary applications
- [ ] Use appropriate sample rates (44100 or 48000 Hz)
- [ ] Disable antivirus real-time scanning for output folders
- [ ] Use batch processing for multiple files
- [ ] Enable segmented recording for long sessions

---

**Last Updated:** December 10, 2025
**Toolkit Version:** 2.0.0
