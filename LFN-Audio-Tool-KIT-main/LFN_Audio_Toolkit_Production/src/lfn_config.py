"""
LFN Audio Toolkit - Project Configuration
==========================================

Shared configuration constants and utilities for the toolkit.
"""
# -*- coding: utf-8 -*-
from pathlib import Path


# Project structure markers - used to identify the project root directory
PROJECT_MARKERS = ['preflight_check.py', 'setup.py', 'README.md', 'requirements.txt']

# Default directories
DEFAULT_LOG_DIR = 'logs'
DEFAULT_OUTPUT_DIR = 'outputs'
DEFAULT_SPECTROGRAM_DIR = 'spectrograms'
DEFAULT_TRENDS_DIR = 'trends'
DEFAULT_RECORDINGS_DIR = 'recordings'


def find_project_root(start_path=None, max_levels=3):
    """
    Find the project root directory by looking for marker files.
    
    Args:
        start_path: Starting directory (defaults to this file's directory)
        max_levels: Maximum number of parent directories to check
    
    Returns:
        Path object pointing to project root, or start_path if not found
    """
    if start_path is None:
        current = Path(__file__).resolve().parent
    else:
        current = Path(start_path).resolve()
    
    # Check current directory and up to max_levels parent directories
    for _ in range(max_levels + 1):
        # Check if any marker files exist in current directory
        if any((current / marker).exists() for marker in PROJECT_MARKERS):
            return current
        
        # Move to parent directory
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    
    # Fallback to original start path
    return Path(start_path).resolve() if start_path else Path(__file__).resolve().parent


# Global project root - calculated once when module is imported
PROJECT_ROOT = find_project_root()
