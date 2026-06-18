# 🐍 Python SysAdmin Script Library

[![CI](https://github.com/DevOpsDerek/Python_Scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/DevOpsDerek/Python_Scripts/actions/workflows/ci.yml)

A beginner-friendly collection of Python scripts for common system administration tasks.
Each script is standalone, heavily commented, and designed to teach Python concepts through real-world examples.

## 📁 Library Structure

```
sysadmin-scripts/
├── 01_filesystem/          # File & directory operations
├── 02_system_monitoring/   # CPU, memory, disk monitoring
├── 03_process_management/  # Working with running processes
├── 04_network/             # Network utilities & diagnostics
├── 05_log_analysis/        # Parsing and analyzing log files
└── 06_automation/          # Scheduling & automated reporting
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Any Script
```bash
python 01_filesystem/list_files.py
python 02_system_monitoring/system_info.py
# etc.
```

## 📚 Python Concepts Covered

| Category | Key Concepts |
|---|---|
| Filesystem | `os`, `pathlib`, `shutil`, `glob`, generators |
| System Monitoring | `psutil`, dataclasses, formatted output |
| Process Management | `psutil`, signal handling, user input |
| Network | `socket`, `subprocess`, threading, timeouts |
| Log Analysis | File I/O, regex (`re`), `collections.Counter` |
| Automation | `schedule`, `smtplib`, `datetime`, functions |

## 💡 Learning Tips

1. **Read the comments** — every script explains *why*, not just *what*
2. **Run it first**, then modify small pieces to see what changes
3. **Check the "Try This" sections** at the bottom of each script
4. **Python docs**: https://docs.python.org/3/

## ⚙️ Dependencies

See `requirements.txt`. Most scripts use only the Python standard library.
`psutil` is required for system/process monitoring scripts.
`schedule` is required for the automation scripts.
