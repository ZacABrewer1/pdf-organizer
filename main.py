import os
import sys
import tkinter as tk
from tkinter import ttk
import logging

from logger_setup import setup_logger
from gui import PDFOrganizerGUI

def main():
    """Main application entry point"""
    # Set up logging
    if getattr(sys, 'frozen', False):
        # If running as compiled executable
        application_path = os.path.dirname(sys.executable)
    else:
        # If running as script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    log_folder = os.path.join(application_path, 'logs')
    config_folder = os.path.join(application_path, 'config')
    
    # Ensure folders exist
    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(config_folder, exist_ok=True)
    
    # Set up logger
    logger = setup_logger(log_folder)
    logger.info("Application starting")
    
    # Create root window with a theme
    root = tk.Tk()
    
    # Try to set a theme if available
    try:
        style = ttk.Style()
        # Try Windows theme first, fall back to clam or default
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
    except Exception as e:
        logger.warning(f"Could not set theme: {e}")
    
    # Create and run the application
    app = PDFOrganizerGUI(root)
    
    # Set icon if available
    try:
        if sys.platform.startswith('win'):
            root.iconbitmap(os.path.join(application_path, 'pdf_organizer.ico'))
    except Exception as e:
        logger.warning(f"Could not set application icon: {e}")
    
    # Run the main loop
    try:
        root.mainloop()
    except Exception as e:
        logger.critical(f"Unhandled exception in main loop: {e}", exc_info=True)
    finally:
        logger.info("Application shutting down")

if __name__ == "__main__":
    main()