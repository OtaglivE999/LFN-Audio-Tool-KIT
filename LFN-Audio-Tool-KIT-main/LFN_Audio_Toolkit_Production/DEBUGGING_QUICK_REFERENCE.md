# LFN Audio Toolkit - Quick Debugging Reference

**Version 2.0.0** | One-page reference for troubleshooting

## 🚨 Emergency Diagnostics

```bash
# Run comprehensive diagnostic check
python debug_utils.py --check-all

# Quick health check
python preflight_check.py

# Enable verbose logging
export LFN_DEBUG=1                    # Linux/Mac
set LFN_DEBUG=1                       # Windows
```

## 🔍 Common Issues Quick Fixes

### Audio Devices Not Found
```bash
# List devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Try with specific device
python src/lfn_realtime_monitor.py --device 1
```

### FFmpeg Not Found
```bash
# Check installation
ffmpeg -version

# Install: See TROUBLESHOOTING.md section on FFmpeg
```

### GPU Not Working
```bash
# Check GPU
nvidia-smi
python -c "import cupy as cp; print('CuPy OK')"

# Run without GPU first
python src/lfn_batch_file_analyzer.py path/to/audio  # No --gpu flag
```

### Memory Errors
```bash
# Use block processing
python src/lfn_batch_file_analyzer.py path/to/audio --block-duration 30

# Check available memory
free -h                               # Linux
```

## 📊 Diagnostic Commands

| Command | Purpose |
|---------|---------|
| `python debug_utils.py --check-all` | Full system diagnostic |
| `python debug_utils.py --audio-devices` | List audio devices |
| `python debug_utils.py --gpu-info` | GPU status |
| `python debug_utils.py --test-ffmpeg` | Test FFmpeg |
| `python debug_utils.py --analyze-logs` | Review logs |
| `python preflight_check.py` | Pre-flight check |
| `python run_tests.py` | Run test suite |

## 📝 Log Locations

- **Main logs:** `logs/lfn_*.log`
- **Error logs:** `logs/lfn_*_error.log`
- **Real-time DB:** `src/lfn_live_log.db`
- **Alerts:** `src/alerts_log.json`

## 🔧 Environment Variables

| Variable | Effect |
|----------|--------|
| `LFN_DEBUG=1` | Enable debug mode |
| `LFN_LOG_LEVEL=DEBUG` | Verbose logging |
| `LFN_LOG_FILE=path/to/file.log` | Log to file |
| `FFMPEG_DEBUG=1` | FFmpeg verbose output |

## ⚡ Performance Tuning

```bash
# Enable GPU (10x faster)
python src/lfn_batch_file_analyzer.py path/to/audio --gpu

# Use block processing for large files
python src/lfn_batch_file_analyzer.py path/to/audio --block-duration 30

# Reduce spectrogram resolution (edit source):
# lfn_realtime_monitor.py line 62: SPECTROGRAM_NPERSEG = 1024
```

## 🎯 Error Pattern Quick Guide

| Error Type | Quick Check |
|------------|-------------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `PortAudioError` | Check device permissions/connections |
| `ffmpeg conversion failed` | Install FFmpeg |
| `MemoryError` | Use `--block-duration`, close apps |
| `GPU computation failed` | Check GPU memory, run on CPU |
| `Permission denied` | Check directory permissions |
| `Database is locked` | Kill other instances, remove `.db-journal` |

## 📚 Documentation

- **Full Debugging Guide:** [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **User Guide:** [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

## 🆘 Getting Help

1. Run diagnostics: `python debug_utils.py --check-all`
2. Check documentation above
3. Review error messages carefully
4. Generate system report: `python debug_utils.py --system-report`
5. Create GitHub issue with report

## 💡 Pro Tips

- Always run `preflight_check.py` after installation
- Use virtual environments to avoid conflicts
- Keep logs enabled during troubleshooting
- Test with small files before processing large batches
- Monitor system resources during long operations
- Read the full error message, not just the last line

---

**Need more details?** See [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md) for comprehensive debugging workflows and explanations.
