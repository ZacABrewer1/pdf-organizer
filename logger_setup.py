import os
import logging
from datetime import datetime
from typing import Optional

def setup_logger(log_folder: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure the application logger
    
    Args:
        log_folder: Folder to store log files, if None uses current directory
        
    Returns:
        Configured logger
    """
    if log_folder is None:
        log_folder = os.path.join(os.getcwd(), 'logs')
    
    # Create log folder if it doesn't exist
    os.makedirs(log_folder, exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_folder, f"pdf_organizer_{timestamp}.log")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # File handler for detailed logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler for info and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized. Log file: {log_file}")
    return logger
