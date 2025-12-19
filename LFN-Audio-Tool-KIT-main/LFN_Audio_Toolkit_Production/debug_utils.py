#!/usr/bin/env python3
"""
LFN Audio Toolkit - Debug Utilities
====================================

Diagnostic and debugging helper script for troubleshooting toolkit issues.

Usage:
    python debug_utils.py --check-all          # Run all diagnostic checks
    python debug_utils.py --audio-devices      # List audio devices
    python debug_utils.py --gpu-info           # Show GPU information
    python debug_utils.py --test-ffmpeg        # Test FFmpeg installation
    python debug_utils.py --analyze-logs       # Analyze recent log files
    python debug_utils.py --system-report      # Generate full system report
"""
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(title):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {message}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {message}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ{Colors.END} {message}")


def check_python_environment():
    """Check Python version and environment"""
    print_header("Python Environment")
    
    # Python version
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python version: {version_str}")
    else:
        print_error(f"Python version: {version_str} (requires 3.8+)")
    
    # Virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success(f"Virtual environment: {sys.prefix}")
    else:
        print_warning("Not using virtual environment (recommended)")
    
    # Executable location
    print_info(f"Python executable: {sys.executable}")
    
    # Site packages
    import site
    print_info(f"Site packages: {site.getsitepackages()}")


def check_dependencies():
    """Check installed dependencies and versions"""
    print_header("Dependency Check")
    
    dependencies = {
        'Core': [
            'numpy',
            'scipy',
            'pandas',
            'soundfile',
            'sounddevice',
            'matplotlib'
        ],
        'Optional': [
            'cupy',
            'openpyxl',
            'psutil'
        ]
    }
    
    for category, packages in dependencies.items():
        print(f"\n{Colors.BOLD}{category} Dependencies:{Colors.END}")
        for package in packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                print_success(f"{package:.<40} v{version}")
            except ImportError:
                if category == 'Optional':
                    print_warning(f"{package:.<40} Not installed (optional)")
                else:
                    print_error(f"{package:.<40} NOT INSTALLED")


def check_audio_devices():
    """Check available audio devices"""
    print_header("Audio Devices")
    
    try:
        import sounddevice as sd
        
        devices = sd.query_devices()
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        
        print(f"{Colors.BOLD}Default Input Device:{Colors.END} {default_input}")
        print(f"{Colors.BOLD}Default Output Device:{Colors.END} {default_output}\n")
        
        input_devices = []
        output_devices = []
        
        for idx, device in enumerate(devices):
            device_info = f"[{idx}] {device['name']}"
            channels = f"In: {device['max_input_channels']}, Out: {device['max_output_channels']}"
            sample_rate = f"SR: {device['default_samplerate']:.0f} Hz"
            
            if device['max_input_channels'] > 0:
                input_devices.append(idx)
                marker = "→" if idx == default_input else " "
                print(f"{marker} {device_info:.<50} {channels:.<20} {sample_rate}")
            
            if device['max_output_channels'] > 0 and device['max_input_channels'] == 0:
                output_devices.append(idx)
                marker = "←" if idx == default_output else " "
                print(f"{marker} {device_info:.<50} {channels:.<20} {sample_rate}")
        
        print(f"\n{Colors.GREEN}✓{Colors.END} Found {len(input_devices)} input device(s)")
        print(f"{Colors.GREEN}✓{Colors.END} Found {len(output_devices)} output device(s)")
        
        if not input_devices:
            print_warning("No input devices detected. Real-time monitoring will not work.")
        
    except Exception as e:
        print_error(f"Failed to query audio devices: {e}")


def check_gpu():
    """Check GPU availability and configuration"""
    print_header("GPU Acceleration")
    
    # Check NVIDIA GPU
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,driver_version,memory.total,memory.free',
             '--format=csv,noheader'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print_success("NVIDIA GPU detected")
            for line in result.stdout.strip().split('\n'):
                parts = line.split(', ')
                if len(parts) >= 4:
                    print(f"  GPU: {parts[0]}")
                    print(f"  Driver: {parts[1]}")
                    print(f"  Memory: {parts[2]} total, {parts[3]} free")
        else:
            print_warning("nvidia-smi not found or failed")
    
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("nvidia-smi not available (no NVIDIA GPU or driver not installed)")
    
    # Check CuPy
    print()
    try:
        import cupy as cp
        print_success(f"CuPy installed: v{cp.__version__}")
        
        try:
            cuda_version = cp.cuda.runtime.runtimeGetVersion()
            major = cuda_version // 1000
            minor = (cuda_version % 1000) // 10
            print_success(f"CUDA runtime: {major}.{minor}")
            
            # Test GPU computation
            test_array = cp.array([1, 2, 3, 4, 5])
            result = test_array * 2
            print_success("GPU computation test passed")
            
        except Exception as e:
            print_error(f"GPU computation failed: {e}")
    
    except ImportError:
        print_warning("CuPy not installed (GPU acceleration unavailable)")
        print_info("Install with: pip install cupy-cuda11x (or cupy-cuda12x)")


def check_ffmpeg():
    """Check FFmpeg installation and capabilities"""
    print_header("FFmpeg")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Parse version from first line
            first_line = result.stdout.split('\n')[0]
            print_success(f"FFmpeg installed: {first_line}")
            
            # Check for common codecs
            formats_result = subprocess.run(
                ['ffmpeg', '-formats'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            formats = formats_result.stdout
            codecs_to_check = ['wav', 'mp3', 'flac', 'aac', 'm4a', 'ogg']
            
            print(f"\n{Colors.BOLD}Codec Support:{Colors.END}")
            for codec in codecs_to_check:
                if codec in formats.lower():
                    print_success(f"{codec.upper():.<40} Supported")
                else:
                    print_warning(f"{codec.upper():.<40} Not found")
        
        else:
            print_error("FFmpeg found but returned error")
    
    except FileNotFoundError:
        print_error("FFmpeg not found in PATH")
        print_info("Batch file analyzer requires FFmpeg for audio conversion")
        print_info("Install instructions: See TROUBLESHOOTING.md")
    
    except subprocess.TimeoutExpired:
        print_error("FFmpeg check timed out")


def check_filesystem():
    """Check filesystem, permissions, and disk space"""
    print_header("Filesystem & Permissions")
    
    script_dir = Path(__file__).parent.parent
    
    # Required directories
    dirs_to_check = [
        ('Source Directory', script_dir / 'src'),
        ('Output Directory', script_dir / 'outputs'),
        ('Spectrograms', script_dir / 'spectrograms'),
        ('Trends', script_dir / 'trends'),
        ('Logs', script_dir / 'logs'),
    ]
    
    for name, path in dirs_to_check:
        if path.exists():
            writable = os.access(path, os.W_OK)
            if writable:
                print_success(f"{name:.<40} Exists & Writable")
            else:
                print_error(f"{name:.<40} Exists but NOT Writable")
        else:
            print_warning(f"{name:.<40} Does not exist (will be created)")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print_success(f"  Created: {path}")
            except Exception as e:
                print_error(f"  Failed to create: {e}")
    
    # Disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(script_dir)
        
        total_gb = total / (1024**3)
        free_gb = free / (1024**3)
        used_percent = (used / total) * 100
        
        print(f"\n{Colors.BOLD}Disk Space:{Colors.END}")
        print(f"  Total: {total_gb:.2f} GB")
        print(f"  Free: {free_gb:.2f} GB ({100-used_percent:.1f}% available)")
        
        if free_gb < 1:
            print_error("  WARNING: Less than 1 GB free space")
        elif free_gb < 5:
            print_warning("  WARNING: Less than 5 GB free space")
        else:
            print_success("  Sufficient disk space available")
    
    except Exception as e:
        print_error(f"Failed to check disk space: {e}")


def analyze_logs():
    """Analyze recent log files for errors and warnings"""
    print_header("Log Analysis")
    
    script_dir = Path(__file__).parent.parent
    log_dir = script_dir / 'logs'
    
    if not log_dir.exists():
        print_warning("No logs directory found")
        return
    
    log_files = sorted(log_dir.glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not log_files:
        print_warning("No log files found")
        return
    
    print(f"Found {len(log_files)} log file(s)\n")
    
    # Analyze most recent log files
    for log_file in log_files[:5]:  # Last 5 log files
        print(f"{Colors.BOLD}{log_file.name}{Colors.END}")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            errors = [line for line in lines if 'ERROR' in line]
            warnings = [line for line in lines if 'WARNING' in line]
            
            print(f"  Size: {log_file.stat().st_size / 1024:.1f} KB")
            print(f"  Lines: {len(lines)}")
            print(f"  Errors: {len(errors)}")
            print(f"  Warnings: {len(warnings)}")
            
            # Show recent errors
            if errors:
                print(f"\n  {Colors.RED}Recent Errors:{Colors.END}")
                for error in errors[-3:]:  # Last 3 errors
                    print(f"    {error.strip()[:100]}")
            
            # Show recent warnings
            if warnings:
                print(f"\n  {Colors.YELLOW}Recent Warnings:{Colors.END}")
                for warning in warnings[-3:]:  # Last 3 warnings
                    print(f"    {warning.strip()[:100]}")
            
            print()
        
        except Exception as e:
            print_error(f"  Failed to read log: {e}")


def test_audio_recording():
    """Test audio recording functionality"""
    print_header("Audio Recording Test")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        print("Recording 1 second of audio...")
        duration = 1
        sample_rate = 44100
        
        try:
            audio_data = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            
            # Analyze recorded audio
            max_amplitude = np.max(np.abs(audio_data))
            rms = np.sqrt(np.mean(audio_data**2))
            
            print_success("Recording successful")
            print(f"  Max amplitude: {max_amplitude:.4f}")
            print(f"  RMS level: {rms:.4f}")
            
            if max_amplitude < 0.001:
                print_warning("  Very low signal - check microphone input level")
            elif max_amplitude > 0.99:
                print_warning("  Signal may be clipping - reduce input level")
            else:
                print_success("  Signal level looks good")
        
        except Exception as e:
            print_error(f"Recording failed: {e}")
    
    except ImportError:
        print_error("sounddevice not installed")


def generate_system_report():
    """Generate comprehensive system report"""
    print_header("System Report")
    
    import platform
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system': {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': sys.version,
        }
    }
    
    # Try to get additional system info
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        report['system'].update({
            'cpu_count': psutil.cpu_count(logical=True),
            'ram_gb': round(memory.total / (1024**3), 2),
            'ram_available_gb': round(memory.available / (1024**3), 2),
            'disk_total_gb': round(disk.total / (1024**3), 2),
            'disk_free_gb': round(disk.free / (1024**3), 2)
        })
    except ImportError:
        pass
    
    # Save report
    script_dir = Path(__file__).parent.parent
    report_path = script_dir / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print_success(f"Report saved to: {report_path}")
        print(f"\n{Colors.BOLD}Report Contents:{Colors.END}")
        print(json.dumps(report, indent=2))
    
    except Exception as e:
        print_error(f"Failed to save report: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='LFN Audio Toolkit Debug Utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--check-all', action='store_true',
                        help='Run all diagnostic checks')
    parser.add_argument('--python', action='store_true',
                        help='Check Python environment')
    parser.add_argument('--dependencies', action='store_true',
                        help='Check installed dependencies')
    parser.add_argument('--audio-devices', action='store_true',
                        help='List audio devices')
    parser.add_argument('--gpu-info', action='store_true',
                        help='Show GPU information')
    parser.add_argument('--test-ffmpeg', action='store_true',
                        help='Test FFmpeg installation')
    parser.add_argument('--filesystem', action='store_true',
                        help='Check filesystem and permissions')
    parser.add_argument('--analyze-logs', action='store_true',
                        help='Analyze recent log files')
    parser.add_argument('--test-recording', action='store_true',
                        help='Test audio recording')
    parser.add_argument('--system-report', action='store_true',
                        help='Generate full system report')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    print(f"\n{Colors.BOLD}LFN Audio Toolkit - Debug Utilities{Colors.END}")
    print(f"Version 2.0.0\n")
    
    # Run requested checks
    if args.check_all or args.python:
        check_python_environment()
    
    if args.check_all or args.dependencies:
        check_dependencies()
    
    if args.check_all or args.audio_devices:
        check_audio_devices()
    
    if args.check_all or args.gpu_info:
        check_gpu()
    
    if args.check_all or args.test_ffmpeg:
        check_ffmpeg()
    
    if args.check_all or args.filesystem:
        check_filesystem()
    
    if args.analyze_logs:
        analyze_logs()
    
    if args.test_recording:
        test_audio_recording()
    
    if args.system_report:
        generate_system_report()
    
    print(f"\n{Colors.BOLD}Debug utilities complete!{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
