# Contributing to LFN Audio Toolkit

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs
1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/lfn-audio-toolkit/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Error messages/logs

### Suggesting Features
1. Check existing [Feature Requests](https://github.com/yourusername/lfn-audio-toolkit/issues?q=label%3Aenhancement)
2. Create a new issue with:
   - Clear use case description
   - Expected benefits
   - Proposed implementation (optional)

### Code Contributions

#### Setup Development Environment
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/lfn-audio-toolkit.git
cd lfn-audio-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

#### Making Changes
1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards:
   - Follow PEP 8 style guide
   - Add docstrings to functions and classes
   - Include type hints where appropriate
   - Write clear, descriptive commit messages

3. Test your changes:
   ```bash
   python src/lfn_health_assessment.py
   # Run relevant analysis scripts to verify
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request:
   - Provide clear description of changes
   - Reference any related issues
   - Include screenshots if UI changes
   - Ensure all tests pass

## 📝 Coding Standards

### Python Style
- Follow PEP 8
- Use meaningful variable names
- Maximum line length: 100 characters
- Use f-strings for formatting

### Documentation
- Add docstrings to all functions:
  ```python
  def analyze_audio(file_path: str, use_gpu: bool = False) -> dict:
      """
      Analyze audio file for LFN and ultrasonic content.
      
      Args:
          file_path: Path to audio file
          use_gpu: Enable GPU acceleration
          
      Returns:
          Dictionary with analysis results
          
      Raises:
          FileNotFoundError: If audio file doesn't exist
      """
  ```

### Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line: brief summary (50 chars or less)
- Blank line, then detailed description if needed

Examples:
```
Add GPU acceleration support for batch processing

Implement CuPy-based FFT computation to speed up batch
analysis by 10x on CUDA-enabled systems.
```

## 🧪 Testing

### Manual Testing
- Test on multiple audio file formats (WAV, FLAC, MP3)
- Verify output files are generated correctly
- Check error handling with invalid inputs

### Performance Testing
- Profile memory usage with large files
- Benchmark processing speed improvements
- Test GPU vs CPU performance

## 📚 Documentation

When adding new features:
- Update README.md
- Add examples to docs/
- Update command-line help text
- Include usage examples

## 🐛 Debugging

> **Important**: Always aim to fix the root cause, not just the symptom. See our comprehensive [DEBUGGING.md](DEBUGGING.md) guide for detailed methodology.

### Debugging Workflow for Contributors

When fixing bugs or investigating issues:

1. **Reproduce the Issue**
   - Create a minimal test case that consistently reproduces the problem
   - Document exact steps, environment, and conditions

2. **Identify Root Cause**
   - Use the "Five Whys" technique to drill down to the fundamental issue
   - Don't stop at the first error—ask why it occurred
   - See [Root Cause vs Symptom Analysis](DEBUGGING.md#root-cause-vs-symptom-analysis)

3. **Implement Proper Fix**
   - Address the underlying problem, not just the visible symptom
   - Consider edge cases and future implications
   - Add defensive programming where appropriate

4. **Validate Thoroughly**
   - Test the fix with the original reproduction case
   - Test edge cases and boundary conditions
   - Ensure no regression in existing functionality

5. **Add Prevention Measures**
   - Add tests to prevent future regression
   - Improve error messages if applicable
   - Document the root cause for future reference

### Useful Debug Commands
```bash
# Check audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test GPU availability
python -c "import cupy; print(cupy.cuda.runtime.runtimeGetVersion())"

# Verify dependencies
pip list | grep -E "soundfile|numpy|scipy|pandas"

# Run preflight diagnostics
python preflight_check.py

# Run health assessment
python src/lfn_health_assessment.py
```

### Debugging Best Practices

**DO:**
- ✅ Use logging instead of print statements for debugging
- ✅ Write tests that reproduce the bug
- ✅ Document the root cause in commit messages
- ✅ Fix related issues while you're in the code
- ✅ Add clear error messages that guide users to solutions

**DON'T:**
- ❌ Apply quick fixes without understanding the root cause
- ❌ Use broad try-except blocks that hide real issues
- ❌ Leave debugging code in production
- ❌ Ignore edge cases "that probably won't happen"
- ❌ Add arbitrary waits/sleeps to "fix" timing issues

### Example: Good vs Bad Fix

**Bad (Symptom Fix):**
```python
# Just catches the error without fixing the underlying issue
try:
    data = load_entire_file(large_file)
except MemoryError:
    print("File too large")
    return None  # User still can't process their file!
```

**Good (Root Cause Fix):**
```python
# Addresses the fundamental limitation
def load_file_in_chunks(file_path, chunk_size_mb=100):
    """
    Load large files in chunks to avoid memory errors.
    Root cause: Loading entire file exceeds available RAM.
    """
    # Implementation that streams data in manageable chunks
    pass
```

For comprehensive debugging methodology, see [DEBUGGING.md](DEBUGGING.md).

## 📋 Pull Request Checklist

Before submitting:
- [ ] Code follows style guidelines
- [ ] **Root cause addressed** (not just symptom fixed)
- [ ] Added/updated documentation
- [ ] Added/updated tests
- [ ] Tested on multiple scenarios
- [ ] No breaking changes (or documented)
- [ ] Commit messages are clear and explain the "why"
- [ ] Branch is up to date with main
- [ ] Reviewed [DEBUGGING.md](DEBUGGING.md) for best practices

## 🏆 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Credited in documentation

## ❓ Questions

- Open a [Discussion](https://github.com/yourusername/lfn-audio-toolkit/discussions)
- Email: support@example.com

## 📜 Code of Conduct

Be respectful and inclusive. We're all here to learn and improve the project together.

Thank you for contributing! 🎉
