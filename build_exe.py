import os
import sys
import PyInstaller.__main__

"""
Builds a standalone executable for the PDF Organizer tool.
This script creates a Windows executable that:
1. Runs without triggering Windows Firewall
2. Includes all necessary dependencies
3. Automatically applies previous mappings
"""

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Configure PyInstaller command line arguments
    pyinstaller_args = [
        'pdf_organizer.py',  # Script to be converted
        '--name=PDF-Organizer', 
        '--onefile',  # Create a single executable file
        '--windowed',  # Do not open console window when running the executable
        '--noconfirm',  # Replace existing build output without confirmation
        '--add-data=generated-icon.png;.',  # Include the icon
        
        # Include key Python packages
        '--hidden-import=tkinter',
        '--hidden-import=PyPDF2',
        '--hidden-import=PIL',
        
        # Specify icon for the executable
        '--icon=generated-icon.png' if os.path.exists('generated-icon.png') else '',
    ]
    
    # Remove empty arguments
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    # Run PyInstaller
    print(f"Building executable with arguments: {pyinstaller_args}")
    PyInstaller.__main__.run(pyinstaller_args)
    
    print(f"\nBuild complete!")
    print("The executable is located in the 'dist' folder.")

if __name__ == "__main__":
    main()