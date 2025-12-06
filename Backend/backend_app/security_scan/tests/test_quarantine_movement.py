"""
Test for quarantine movement functionality.

Testing Parameters:
- Test: Quarantine movement
- Expected Behavior: No race conditions, unique IDs
"""

import pytest
import tempfile
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

from ...security_scan.quarantine_manager import FileQuarantineManager
from ...security_scan.config import SecurityScanConfig


class TestQuarantineMovement:
    """Test suite for quarantine file movement operations."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config = SecurityScanConfig()
        self.config.quarantine_base_path = self.temp_dir
        self.config.ensure_folder_structure()
        
        # Create test file content
        self.test_content = b"Test file content for quarantine movement."
        self.test_filename = "test_file.txt"
    
    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_folder_structure_creation(self):
        """Test that quarantine folder structure is created correctly."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        quarantine_manager.ensure_folder_structure()
        
        # Verify all folders exist
        expected_folders = [
            self.temp_dir,
            os.path.join(self.temp_dir, "incoming"),
            os.path.join(self.temp_dir, "scanning"),
            os.path.join(self.temp_dir, "clean"),
            os.path.join(self.temp_dir, "infected"),
            os.path.join(self.temp_dir, "logs")
        ]
        
        for folder in expected_folders:
            assert os.path.exists(folder), f"Folder {folder} should exist"
            assert os.path.isdir(folder), f"{folder} should be a directory"
    
    def test_move_to_incoming_unique_naming(self):
        """Test that incoming files get unique names."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create multiple files with same name
        paths = []
        for i in range(3):
            path = quarantine_manager.move_to_incoming(
                self.test_content, 
                self.test_filename
            )
            paths.append(path)
        
        # Verify all paths are unique
        unique_paths = set(paths)
        assert len(unique_paths) == 3, "All paths should be unique"
        
        # Verify all files exist in incoming folder
        incoming_files = os.listdir(os.path.join(self.temp_dir, "incoming"))
        assert len(incoming_files) == 3
        
        # Verify each path contains timestamp and original filename
        for path in paths:
            filename = os.path.basename(path)
            assert "incoming_" in filename
            assert self.test_filename in filename
            assert os.path.exists(path)
    
    def test_move_to_scanning(self):
        """Test moving file from any location to scanning folder."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create file in incoming
        incoming_path = quarantine_manager.move_to_incoming(
            self.test_content, 
            self.test_filename
        )
        
        # Move to scanning
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        
        # Verify file moved correctly
        assert os.path.exists(scanning_path)
        assert not os.path.exists(incoming_path)  # Original should be gone
        
        # Verify file is in scanning folder
        filename = os.path.basename(scanning_path)
        assert "scanning_" in filename
        assert self.test_filename in filename
        
        # Verify content preserved
        with open(scanning_path, 'rb') as f:
            content = f.read()
            assert content == self.test_content
    
    def test_mark_as_safe(self):
        """Test marking file as safe and moving to clean folder."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create file in scanning
        incoming_path = quarantine_manager.move_to_incoming(
            self.test_content, 
            self.test_filename
        )
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        
        # Mark as safe
        clean_path = quarantine_manager.mark_as_safe(scanning_path)
        
        # Verify file moved correctly
        assert os.path.exists(clean_path)
        assert not os.path.exists(scanning_path)  # Original should be gone
        
        # Verify file is in clean folder
        filename = os.path.basename(clean_path)
        assert "clean_" in filename
        assert self.test_filename in filename
        
        # Verify content preserved
        with open(clean_path, 'rb') as f:
            content = f.read()
            assert content == self.test_content
    
    def test_mark_as_infected(self):
        """Test marking file as infected and moving to infected folder."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create file in scanning
        incoming_path = quarantine_manager.move_to_incoming(
            self.test_content, 
            self.test_filename
        )
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        
        # Mark as infected
        infected_path = quarantine_manager.mark_as_infected(scanning_path)
        
        # Verify file moved correctly
        assert os.path.exists(infected_path)
        assert not os.path.exists(scanning_path)  # Original should be gone
        
        # Verify file is in infected folder
        filename = os.path.basename(infected_path)
        assert "infected_" in filename
        assert self.test_filename in filename
        
        # Verify content preserved
        with open(infected_path, 'rb') as f:
            content = f.read()
            assert content == self.test_content
    
    def test_concurrent_file_movements(self):
        """Test concurrent file movements to ensure no race conditions."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        def process_file(file_id):
            """Process a single file through the quarantine pipeline."""
            content = f"Content for file {file_id}".encode()
            filename = f"file_{file_id}.txt"
            
            try:
                # Move to incoming
                incoming_path = quarantine_manager.move_to_incoming(content, filename)
                
                # Move to scanning
                scanning_path = quarantine_manager.move_to_scanning(incoming_path)
                
                # Randomly mark as safe or infected
                if file_id % 2 == 0:
                    final_path = quarantine_manager.mark_as_safe(scanning_path)
                    expected_prefix = "clean_"
                else:
                    final_path = quarantine_manager.mark_as_infected(scanning_path)
                    expected_prefix = "infected_"
                
                # Verify final state
                assert os.path.exists(final_path)
                assert expected_prefix in os.path.basename(final_path)
                
                return final_path
                
            except Exception as e:
                return f"Error processing file {file_id}: {str(e)}"
        
        # Process multiple files concurrently
        num_files = 10
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_file, i) for i in range(num_files)]
            results = [future.result() for future in futures]
        
        # Verify all operations completed successfully
        success_count = sum(1 for result in results if isinstance(result, str) and result.startswith(self.temp_dir))
        assert success_count == num_files, f"Expected {num_files} successful operations, got {success_count}"
        
        # Verify folder contents
        incoming_files = os.listdir(os.path.join(self.temp_dir, "incoming"))
        scanning_files = os.listdir(os.path.join(self.temp_dir, "scanning"))
        
        assert len(incoming_files) == 0, "Incoming folder should be empty"
        assert len(scanning_files) == 0, "Scanning folder should be empty"
        
        # Verify files are in correct final locations
        clean_files = os.listdir(os.path.join(self.temp_dir, "clean"))
        infected_files = os.listdir(os.path.join(self.temp_dir, "infected"))
        
        assert len(clean_files) == 5, "Should have 5 files in clean folder"
        assert len(infected_files) == 5, "Should have 5 files in infected folder"
    
    def test_get_log_path(self):
        """Test getting the log path from quarantine manager."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        log_path = quarantine_manager.get_log_path()
        
        expected_log_path = os.path.join(self.temp_dir, "logs")
        assert log_path == expected_log_path
        assert os.path.exists(log_path)
        assert os.path.isdir(log_path)
    
    def test_file_movement_error_handling(self):
        """Test error handling during file movements."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Test moving non-existent file
        non_existent_path = os.path.join(self.temp_dir, "non_existent.txt")
        
        try:
            quarantine_manager.move_to_scanning(non_existent_path)
            assert False, "Should have raised an exception for non-existent file"
        except Exception:
            pass  # Expected behavior
    
    def test_large_file_movement(self):
        """Test movement of large files."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create large file content (1MB)
        large_content = b"x" * (1024 * 1024)
        large_filename = "large_file.txt"
        
        # Move through quarantine pipeline
        incoming_path = quarantine_manager.move_to_incoming(large_content, large_filename)
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        clean_path = quarantine_manager.mark_as_safe(scanning_path)
        
        # Verify file size is preserved
        assert os.path.getsize(clean_path) == len(large_content)
        
        # Verify content is preserved
        with open(clean_path, 'rb') as f:
            content = f.read()
            assert content == large_content
    
    def test_special_characters_in_filename(self):
        """Test handling of special characters in filenames."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        special_filenames = [
            "file with spaces.txt",
            "file-with-dashes.txt",
            "file_with_underscores.txt",
            "file.with.dots.txt",
            "file(1).txt",
            "файл.txt",  # Unicode characters
        ]
        
        for filename in special_filenames:
            content = f"Content for {filename}".encode()
            
            # Move through quarantine pipeline
            incoming_path = quarantine_manager.move_to_incoming(content, filename)
            scanning_path = quarantine_manager.move_to_scanning(incoming_path)
            clean_path = quarantine_manager.mark_as_safe(scanning_path)
            
            # Verify file exists and content preserved
            assert os.path.exists(clean_path)
            
            with open(clean_path, 'rb') as f:
                file_content = f.read()
                assert file_content == content
    
    def test_folder_permissions(self):
        """Test that quarantine folders have appropriate permissions."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        quarantine_manager.ensure_folder_structure()
        
        # Test that we can write to all folders
        test_content = b"Test write permission"
        
        # Test incoming folder
        incoming_path = quarantine_manager.move_to_incoming(test_content, "test.txt")
        assert os.path.exists(incoming_path)
        
        # Test scanning folder
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        assert os.path.exists(scanning_path)
        
        # Test clean folder
        clean_path = quarantine_manager.mark_as_safe(scanning_path)
        assert os.path.exists(clean_path)
        
        # Test infected folder
        incoming_path2 = quarantine_manager.move_to_incoming(test_content, "test2.txt")
        scanning_path2 = quarantine_manager.move_to_scanning(incoming_path2)
        infected_path = quarantine_manager.mark_as_infected(scanning_path2)
        assert os.path.exists(infected_path)