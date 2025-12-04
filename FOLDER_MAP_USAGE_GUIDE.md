# Folder Map Scanner - Usage Guide

## Overview

The Folder Map Scanner is a comprehensive tool designed to scan and document project structures. It generates detailed JSON files containing complete directory hierarchies, file metadata, and project organization information.

## Features

- ✅ **Recursive Directory Scanning** - Scans directories up to configurable depth
- ✅ **File Metadata Extraction** - Size, modification time, creation time, extensions
- ✅ **Human-Readable Output** - Formatted file sizes and timestamps
- ✅ **Smart Exclusions** - Automatically excludes common development artifacts
- ✅ **JSON Output** - Machine-readable format for easy parsing
- ✅ **Progress Reporting** - Real-time scanning progress
- ✅ **Error Handling** - Graceful handling of permission issues and errors
- ✅ **Cross-Platform** - Works on Windows, Linux, and macOS

## Usage

### Basic Usage

```bash
# Scan current directory with default settings
python folder_map_scanner.py

# Scan specific directory
python folder_map_scanner.py /path/to/project

# Scan with custom output file
python folder_map_scanner.py -o my_project_map.json

# Scan with increased depth
python folder_map_scanner.py -d 5
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `path` | Directory to scan (positional) | Current directory |
| `-o, --output` | Output file name | `folder_map.json` |
| `-d, --depth` | Maximum scan depth | `3` |
| `--include-hidden` | Include hidden files | `false` |

### Examples

```bash
# Example 1: Scan entire project with full depth
python folder_map_scanner.py /home/user/my-project -d 10 -o full_map.json

# Example 2: Scan current directory, include hidden files
python folder_map_scanner.py --include-hidden

# Example 3: Quick scan of top-level structure only
python folder_map_scanner.py -d 1 -o top_level.json

# Example 4: Scan specific project directory
python folder_map_scanner.py C:\Projects\MyApp -o app_structure.json
```

## Output Format

The scanner generates a JSON file with the following structure:

```json
{
  "scan_info": {
    "timestamp": "2025-11-30T16:07:32.943Z",
    "root_path": "/path/to/project",
    "root_name": "project-name",
    "max_depth": 3,
    "excluded_patterns": [".git", ".vscode", ...],
    "scanner_version": "1.0"
  },
  "folder_map": {
    "type": "directory",
    "path": "/path/to/project",
    "files": [
      {
        "name": "file.txt",
        "size": 1024,
        "size_formatted": "1.0 KB",
        "modified": "2025-11-30T16:07:32.943Z",
        "created": "2025-11-30T16:07:32.943Z",
        "extension": ".txt",
        "is_hidden": false
      }
    ],
    "subdirectories": {
      "subdir1": {
        "type": "directory",
        "path": "/path/to/project/subdir1",
        "files": [...],
        "subdirectories": {...}
      }
    }
  }
}
```

## Excluded Patterns

By default, the scanner excludes common development artifacts:

- `.git`, `.svn`, `.hg` - Version control directories
- `__pycache__`, `.venv`, `venv` - Python artifacts
- `.vscode`, `.idea` - IDE configurations
- `node_modules` - Node.js dependencies
- `target`, `build`, `dist` - Build outputs
- `.env`, `.env.local` - Environment files
- `*.log`, `*.tmp`, `*.bak` - Temporary files
- `.DS_Store`, `Thumbs.db` - System files

## Running on Current Project

To scan the current project structure:

```bash
# Basic scan (depth 3)
python folder_map_scanner.py

# Scan with full project depth
python folder_map_scanner.py -d 5 -o project_structure.json

# Include hidden files
python folder_map_scanner.py --include-hidden -o complete_map.json
```

## Sample Output

When run on this project, the scanner will generate output similar to:

```
🔍 File Folder Map Scanner
================================================================================
📁 Folder Map Scanner initialized
   Max Depth: 3
   Excluded Patterns: 15
🚀 Starting scan of: C:\Users\maheshpattar\Desktop\test2
   Root: test2
  📂 Scanning: test2
    📂 Scanning: Backend
      📂 Scanning: backend_app
        🔒 Permission denied: __pycache__
      📂 Scanning: scripts
      📂 Scanning: tests
    📂 Scanning: CbDOC
    📂 Scanning: Doc
    📂 Scanning: documents
    📂 Scanning: Frontend
      📂 Scanning: examples
      📂 Scanning: modules
      📂 Scanning: services
    📂 Scanning: logs
    📂 Scanning: Resumes
  📂 Scanning: .venv
    🔒 Permission denied: Scripts
    🔒 Permission denied: Lib
✅ Folder map saved to: folder_map.json

================================================================================
📊 FOLDER MAP SUMMARY
================================================================================
📅 Scan Time: 2025-11-30T16:07:32.943Z
🏠 Root Project: test2
📁 Root Path: C:\Users\maheshpattar\Desktop\test2
📏 Max Depth: 3
📄 Files Found: 150+
📂 Directories Found: 50+
💾 Total Size: 15.2 MB

================================================================================
🎉 Folder map generation completed successfully!
```

## Integration with Test Suite

The folder map scanner is integrated into the comprehensive test suite:

1. **`test_resume_processing_workflow.py`** - Automatically generates folder maps
2. **`test_runner.py`** - Validates project structure
3. **`folder_map_scanner.py`** - Standalone scanning tool

## Use Cases

### 1. Project Documentation
Generate comprehensive documentation of project structure for onboarding or reference.

### 2. Code Reviews
Quickly understand project organization before reviewing code changes.

### 3. Migration Planning
Analyze project structure before refactoring or migration.

### 4. Backup Verification
Verify complete project structure is backed up.

### 5. Dependency Analysis
Understand project organization and file relationships.

## Tips

1. **Use appropriate depth** - Start with depth 3, increase if needed
2. **Include hidden files** - Use `--include-hidden` for complete analysis
3. **Custom output names** - Use descriptive names for different scans
4. **Combine with other tools** - Use output for further analysis

## Troubleshooting

### Permission Errors
```
🔒 Permission denied: directory_name
```
This is normal for system directories. Use `--include-hidden` to include more files.

### Large Projects
For very large projects, consider:
- Using smaller depth values
- Excluding large directories manually
- Running during off-peak hours

### Output File Issues
Ensure write permissions in the output directory and sufficient disk space.

## Advanced Usage

### Custom Exclusion Patterns
Modify the `exclude_patterns` list in the script to add custom exclusions.

### Programmatic Usage
```python
from folder_map_scanner import FolderMapScanner

scanner = FolderMapScanner(max_depth=5)
result = scanner.generate_map("/path/to/project", "output.json")
scanner.print_summary(result)
```

### Parsing Output
```python
import json

with open('folder_map.json', 'r') as f:
    data = json.load(f)

# Access scan info
scan_time = data['scan_info']['timestamp']
root_path = data['scan_info']['root_path']

# Access folder structure
files = data['folder_map']['files']
subdirs = data['folder_map']['subdirectories']
```

## Performance

- **Small Projects** (< 100 files): < 1 second
- **Medium Projects** (100-1000 files): 1-10 seconds
- **Large Projects** (> 1000 files): 10-60 seconds

Performance depends on:
- Number of files and directories
- Disk speed
- System resources
- Scan depth

## Security Notes

- The scanner only reads file metadata, not file contents
- Exclude sensitive directories using `exclude_patterns`
- Output files may contain file paths - handle appropriately
- Run with minimal required permissions