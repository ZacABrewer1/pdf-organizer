# Enhanced PDF Organizer

An advanced PDF organizing tool that automatically applies previous mappings and offers preview, copy/move options, custom patterns, and detailed reporting.

## Features

- **Automatic Job Recognition**: Extracts job information from PDF content using configurable patterns
- **Smart Mapping**: Remembers previous file mappings for consistent organization
- **Preview Mode**: See where files will go before making changes
- **Copy or Move**: Choose whether to copy or move files to destination folders
- **Customizable Patterns**: Configure the pattern used to extract job information
- **Detailed Reports**: Generate comprehensive reports of each operation
- **Recent Folders**: Quick access to previously used folders
- **Error Handling**: Robust error handling with detailed logging

## Requirements

- Python 3.6 or higher
- Required packages: PyPDF2, Pillow (PIL)

## Installation

### Option 1: Run from Source Code

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install PyPDF2 pillow
   ```
3. Run the application:
   ```
   python pdf_organizer.py
   ```

### Option 2: Build Windows Executable

To create a standalone Windows executable that doesn't trigger firewall warnings:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   python build_exe.py
   ```

3. The executable will be created in the `dist` folder

## Usage

1. **Select Source Folder**: Choose the folder containing PDF files to organize
2. **Configure Target Folders**: Set up job names and their corresponding target folders
3. **Preview**: Generate a preview of how files will be organized
4. **Process**: Process the files according to the preview
5. **View Reports**: Check the report tab for details on the operations performed

## Configuration

### Target Folders

Configure the mapping between job names and target folders:

1. Go to Configuration → Target Folders
2. Enter job names and corresponding folder paths
3. Use the "Browse" button to select folders

### Extraction Patterns

Configure how job information is extracted from PDFs:

1. Go to Configuration → Extraction Patterns
2. Enter regex patterns to match job information
3. Default pattern is `Job:\s*(.*)` which extracts text after "Job:"

## Building Windows Executable Without Firewall Alerts

The included `build_exe.py` script is specially configured to create a Windows executable that:

1. Operates locally without network connectivity
2. Doesn't trigger Windows Firewall alerts
3. Includes all necessary dependencies
4. Maintains configuration and mapping between sessions

To build:

```
python build_exe.py
```

### Tips for Avoiding Firewall Alerts

- Run the executable from a consistent location
- Don't place the executable in restricted folders (Program Files, Windows folder)
- The first time you run it, Windows might still ask for permission - allow it once
- Configuration will be stored in the same folder as the executable

## Troubleshooting

- **Files not processed**: Ensure you have proper permissions for both source and target folders
- **Job not detected**: Check the extraction patterns and make sure the PDF contains the expected text
- **Can't open PDF**: Ensure the PDF is not corrupted or password-protected

## License

This project is licensed under the MIT License - see the LICENSE file for details.