import os
import sys
import logging
import traceback
from tkinter import Tk, messagebox
from PIL import Image, ImageTk

from logger_setup import setup_logger
from gui import PDFOrganizerGUI

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    except Exception:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def run_pdf_organizer():
    """
    Main entry point for the PDF organizer application.
    This is the main function when running as pyinstaller executable.
    """
    # If running as executable, set the proper paths
    if getattr(sys, 'frozen', False):
        # Get the executable's directory
        executable_dir = os.path.dirname(sys.executable)
        
        # Set up application paths
        log_folder = os.path.join(executable_dir, 'logs')
        config_folder = os.path.join(executable_dir, 'config')
        
        # Set working directory to executable directory to ensure
        # relative paths work correctly (reduces firewall issues)
        os.chdir(executable_dir)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_folder = os.path.join(script_dir, 'logs')
        config_folder = os.path.join(script_dir, 'config')
    
    # Ensure directories exist
    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(config_folder, exist_ok=True)
    
    # Initialize logger
    logger = setup_logger(log_folder)
    logger.info("Starting PDF Organizer application")
    
    try:
        # Create and configure the main window
        root = Tk()
        root.title("Enhanced PDF Organizer")
        
        # Center the window on screen
        window_width = 900
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Try to set application icon
        try:
            icon_path = resource_path('generated-icon.png')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon_image)
                root.iconphoto(True, photo)
                logger.info(f"Set application icon from {icon_path}")
        except Exception as e:
            logger.warning(f"Could not set application icon: {e}")
        
        # Initialize the GUI
        app = PDFOrganizerGUI(root)
        
        # Start the main loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Critical error in application: {e}"
        logger.critical(error_msg, exc_info=True)
        
        # Show error dialog if we have a GUI
        try:
            if 'root' in locals() and root:
                messagebox.showerror("Error", f"An error occurred:\n\n{e}\n\nPlease check the logs for details.")
        except:
            pass
            
        # Print traceback to console
        traceback.print_exc()
    finally:
        logger.info("Application terminated")

if __name__ == "__main__":
    run_pdf_organizer()
