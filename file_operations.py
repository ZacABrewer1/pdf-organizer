import os
import shutil
import logging
from typing import Dict, List, Callable, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class FileOperator:
    """Handles file operations like copying and moving"""
    
    def __init__(self, is_move_operation: bool = True):
        """
        Initialize with operation type
        
        Args:
            is_move_operation: If True, moves files; if False, copies files
        """
        self.is_move_operation = is_move_operation
        self.report_data = []
    
    def set_operation_type(self, is_move: bool):
        """
        Set the operation type (move or copy)
        
        Args:
            is_move: If True, set to move operation; if False, set to copy operation
        """
        self.is_move_operation = is_move
    
    def process_file(self, source_path: str, destination_path: str) -> bool:
        """
        Process a single file (copy or move)
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if successful, False otherwise
        """
        operation_name = "move" if self.is_move_operation else "copy"
        try:
            # Create target directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Perform the operation
            if self.is_move_operation:
                shutil.move(source_path, destination_path)
            else:
                shutil.copy2(source_path, destination_path)
                
            logger.info(f"Successfully {operation_name}d '{source_path}' to '{destination_path}'")
            
            # Record the operation for reporting
            self.report_data.append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation_name,
                'source': source_path,
                'destination': destination_path,
                'status': 'success'
            })
            
            return True
            
        except FileNotFoundError as e:
            error_msg = f"Error: Source file or target folder not found: {e}"
            logger.error(error_msg)
            self.report_data.append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation_name,
                'source': source_path,
                'destination': destination_path,
                'status': 'error',
                'error': error_msg
            })
            return False
            
        except shutil.Error as e:
            error_msg = f"Error {operation_name}ing '{source_path}': {e}"
            logger.error(error_msg)
            self.report_data.append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation_name,
                'source': source_path,
                'destination': destination_path,
                'status': 'error',
                'error': error_msg
            })
            return False
            
        except Exception as e:
            error_msg = f"Unexpected error {operation_name}ing '{source_path}': {e}"
            logger.error(error_msg)
            self.report_data.append({
                'timestamp': datetime.now().isoformat(),
                'operation': operation_name,
                'source': source_path,
                'destination': destination_path,
                'status': 'error',
                'error': error_msg
            })
            return False
    
    def process_files_with_progress(self, file_mapping: Dict[str, str], 
                                  progress_callback: Callable[[int, int], None] = None) -> Tuple[int, int]:
        """
        Process multiple files with progress tracking
        
        Args:
            file_mapping: Dictionary mapping source files to destination paths
            progress_callback: Function to call with progress updates
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        total_files = len(file_mapping)
        success_count = 0
        failure_count = 0
        
        for idx, (source_file, destination) in enumerate(file_mapping.items()):
            success = self.process_file(source_file, destination)
            
            if success:
                success_count += 1
            else:
                failure_count += 1
                
            if progress_callback:
                progress_callback(idx + 1, total_files)
        
        return success_count, failure_count
    
    def generate_report(self, output_path: str) -> str:
        """
        Generate a detailed report of file operations
        
        Args:
            output_path: Directory to save the report
            
        Returns:
            Path to the generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"pdf_organizer_report_{timestamp}.txt"
        report_path = os.path.join(output_path, report_filename)
        
        operation_type = "move" if self.is_move_operation else "copy"
        
        with open(report_path, 'w') as f:
            f.write(f"PDF Organizer Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Operation Type: {operation_type.upper()}\n")
            f.write("="*80 + "\n\n")
            
            # Summary section
            success_count = sum(1 for item in self.report_data if item['status'] == 'success')
            error_count = sum(1 for item in self.report_data if item['status'] == 'error')
            
            f.write(f"SUMMARY\n")
            f.write(f"Total operations: {len(self.report_data)}\n")
            f.write(f"Successful: {success_count}\n")
            f.write(f"Failed: {error_count}\n")
            f.write("\n" + "="*80 + "\n\n")
            
            # Detailed operations
            f.write("DETAILED OPERATIONS\n")
            for item in self.report_data:
                f.write(f"Time: {item['timestamp']}\n")
                f.write(f"Operation: {item['operation'].upper()}\n")
                f.write(f"Source: {item['source']}\n")
                f.write(f"Destination: {item['destination']}\n")
                f.write(f"Status: {item['status'].upper()}\n")
                
                if item['status'] == 'error' and 'error' in item:
                    f.write(f"Error details: {item['error']}\n")
                    
                f.write("-"*40 + "\n")
        
        logger.info(f"Report generated at {report_path}")
        return report_path
    
    def clear_report_data(self):
        """Clear report data for a new operation"""
        self.report_data = []
