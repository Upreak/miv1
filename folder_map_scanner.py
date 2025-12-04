#!/usr/bin/env python3
"""
File Folder Map Scanner

A standalone tool to scan and create a comprehensive file folder map of any project.
Generates detailed documentation of the project structure with file metadata.

Features:
- Recursive directory scanning
- File metadata extraction (size, modification time)
- JSON output for easy parsing
- Configurable scan depth
- Excludes common development artifacts
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class FolderMapScanner:
    """Comprehensive folder map scanner for project documentation"""
    
    def __init__(self, max_depth: int = 3, exclude_patterns: Optional[list] = None):
        self.max_depth = max_depth
        self.exclude_patterns = exclude_patterns or [
            '.git', '.svn', '.hg', '__pycache__', '.vscode', '.idea',
            'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
            '.env', '.env.local', '*.log', '*.tmp', '*.bak'
        ]
        
        print(f"Folder Map Scanner initialized")
        print(f"   Max Depth: {max_depth}")
        print(f"   Excluded Patterns: {len(self.exclude_patterns)}")
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from scanning"""
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern.startswith('.'):
                # Directory or file extension
                if path.name.startswith('.') or path.suffix == pattern:
                    return True
            elif pattern in path_str:
                return True
        return False
    
    def scan_directory(self, path: Path, current_depth: int = 0) -> Dict[str, Any]:
        """Recursively scan directory structure"""
        if current_depth >= self.max_depth:
            return {
                "type": "directory",
                "path": str(path),
                "files": [],
                "subdirectories": [],
                "note": "Scan depth limit reached"
            }
        
        structure = {
            "type": "directory",
            "path": str(path),
            "files": [],
            "subdirectories": {}
        }
        
        try:
            if path.exists() and path.is_dir():
                print(f"  {'  ' * current_depth}Scanning: {path.name}")
                
                for item in sorted(path.iterdir()):
                    if self.should_exclude(item):
                        continue
                    
                    if item.is_file():
                        try:
                            file_info = self.get_file_info(item)
                            structure["files"].append(file_info)
                        except Exception as e:
                            print(f"    Warning: Could not read file {item.name}: {e}")
                    
                    elif item.is_dir():
                        try:
                            subdir_structure = self.scan_directory(item, current_depth + 1)
                            structure["subdirectories"][item.name] = subdir_structure
                        except Exception as e:
                            print(f"    Warning: Could not scan directory {item.name}: {e}")
            
        except PermissionError:
            print(f"  {'  ' * current_depth}Permission denied: {path.name}")
            structure["error"] = "Permission denied"
        except Exception as e:
            print(f"  {'  ' * current_depth}Error scanning {path.name}: {e}")
            structure["error"] = str(e)
        
        return structure
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            stat = file_path.stat()
            return {
                "name": file_path.name,
                "size": stat.st_size,
                "size_formatted": self.format_file_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "extension": file_path.suffix.lower(),
                "is_hidden": file_path.name.startswith('.')
            }
        except Exception as e:
            return {
                "name": file_path.name,
                "error": str(e)
            }
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def generate_map(self, root_path: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate complete folder map"""
        root_path = Path(root_path).resolve()
        
        if not root_path.exists():
            print(f"❌ Error: Path does not exist: {root_path}")
            return {}
        
        print(f"Starting scan of: {root_path}")
        print(f"   Root: {root_path.name}")
        
        # Generate timestamp
        scan_info = {
            "scan_info": {
                "timestamp": datetime.now().isoformat(),
                "root_path": str(root_path),
                "root_name": root_path.name,
                "max_depth": self.max_depth,
                "excluded_patterns": self.exclude_patterns,
                "scanner_version": "1.0"
            }
        }
        
        # Scan the directory
        folder_map = self.scan_directory(root_path)
        
        # Combine scan info with folder map
        result = {**scan_info, "folder_map": folder_map}
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Folder map saved to: {output_path}")
        
        return result
    
    def print_summary(self, folder_map: Dict[str, Any]):
        """Print a summary of the folder structure"""
        if not folder_map:
            print("❌ No folder map to summarize")
            return
        
        scan_info = folder_map.get("scan_info", {})
        folder_data = folder_map.get("folder_map", {})
        
        print("\n" + "=" * 80)
        print("FOLDER MAP SUMMARY")
        print("=" * 80)
        
        print(f"Scan Time: {scan_info.get('timestamp', 'Unknown')}")
        print(f"Root Project: {scan_info.get('root_name', 'Unknown')}")
        print(f"Root Path: {scan_info.get('root_path', 'Unknown')}")
        print(f"Max Depth: {scan_info.get('max_depth', 'Unknown')}")
        
        # Count files and directories
        file_count, dir_count = self.count_items(folder_data)
        total_size = self.calculate_total_size(folder_data)
        
        print(f"Files Found: {file_count:,}")
        print(f"Directories Found: {dir_count:,}")
        print(f"Total Size: {self.format_file_size(total_size)}")
        
        print("\n" + "=" * 80)
    
    def count_items(self, folder_data: Dict[str, Any]) -> tuple:
        """Count files and directories recursively"""
        file_count = len(folder_data.get("files", []))
        dir_count = len(folder_data.get("subdirectories", {}))
        
        subdirectories = folder_data.get("subdirectories", {})
        if isinstance(subdirectories, dict):
            for subdir_name, subdir_data in subdirectories.items():
                if isinstance(subdir_data, dict):
                    sub_files, sub_dirs = self.count_items(subdir_data)
                    file_count += sub_files
                    dir_count += sub_dirs
        
        return file_count, dir_count
    
    def calculate_total_size(self, folder_data: Dict[str, Any]) -> int:
        """Calculate total size of all files"""
        total_size = 0
        
        for file_info in folder_data.get("files", []):
            if "size" in file_info:
                total_size += file_info["size"]
        
        subdirectories = folder_data.get("subdirectories", {})
        if isinstance(subdirectories, dict):
            for subdir_name, subdir_data in subdirectories.items():
                if isinstance(subdir_data, dict):
                    total_size += self.calculate_total_size(subdir_data)
        
        return total_size


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="File Folder Map Scanner - Generate comprehensive project structure documentation"
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to scan (default: current directory)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="folder_map.json",
        help="Output file name (default: folder_map.json)"
    )
    
    parser.add_argument(
        "-d", "--depth",
        type=int,
        default=3,
        help="Maximum scan depth (default: 3)"
    )
    
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories"
    )
    
    args = parser.parse_args()
    
    print("File Folder Map Scanner")
    print("=" * 80)
    
    # Configure exclusions
    exclude_patterns = [
        '.git', '.svn', '.hg', '__pycache__', '.vscode', '.idea',
        'node_modules', 'target', 'build', 'dist', '.venv', 'venv',
        '.env', '.env.local', '*.log', '*.tmp', '*.bak'
    ]
    
    if not args.include_hidden:
        exclude_patterns.extend(['.gitignore', '.env', '.DS_Store', 'Thumbs.db'])
    
    # Create scanner
    scanner = FolderMapScanner(
        max_depth=args.depth,
        exclude_patterns=exclude_patterns
    )
    
    # Generate map
    try:
        folder_map = scanner.generate_map(args.path, args.output)
        
        # Print summary
        scanner.print_summary(folder_map)
        
        print("Folder map generation completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError during scan: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()