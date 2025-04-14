import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from typing import Dict, List, Callable, Any, Optional
import logging

from pdf_utils import PDFProcessor
from file_operations import FileOperator
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class PDFOrganizerGUI:
    """Main GUI for the PDF Organizer application"""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Enhanced PDF Organizer")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.pdf_processor = PDFProcessor()
        self.file_operator = FileOperator()
        
        # Load configuration
        self.config = self.config_manager.load_config()
        self.mapping = self.config_manager.load_mapping()
        
        # Update pattern from config
        if 'patterns' in self.config and self.config['patterns']:
            self.pdf_processor.patterns = self.config['patterns']
        
        # Set operation type from config
        if 'is_move_operation' in self.config:
            self.file_operator.set_operation_type(self.config['is_move_operation'])
        
        # Current folder data
        self.current_folder = tk.StringVar(value="")
        self.preview_data = {}
        self.is_processing = False
        
        # Create GUI elements
        self._create_menu()
        self._create_main_frame()
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Source Folder...", command=self._select_folder)
        file_menu.add_separator()
        
        # Recent folders submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        self._update_recent_menu()
        file_menu.add_cascade(label="Recent Folders", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Configuration menu
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Target Folders...", command=self._edit_target_folders)
        config_menu.add_command(label="Extraction Patterns...", command=self._edit_patterns)
        menubar.add_cascade(label="Configuration", menu=config_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_frame(self):
        """Create the main application frame and widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(folder_frame, text="PDF Source Folder:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(folder_frame, textvariable=self.current_folder, width=50).pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse...", command=self._select_folder).pack(side=tk.LEFT)
        
        # Operation type (move/copy) selection
        operation_frame = ttk.Frame(main_frame)
        operation_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.operation_var = tk.BooleanVar(value=self.config.get('is_move_operation', True))
        ttk.Radiobutton(
            operation_frame, 
            text="Move Files", 
            variable=self.operation_var, 
            value=True,
            command=self._update_operation_type
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            operation_frame, 
            text="Copy Files", 
            variable=self.operation_var, 
            value=False,
            command=self._update_operation_type
        ).pack(side=tk.LEFT)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Preview tab
        preview_frame = ttk.Frame(self.notebook)
        self.notebook.add(preview_frame, text="Preview")
        self._create_preview_tab(preview_frame)
        
        # Report tab
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="Report")
        self._create_report_tab(report_frame)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame, 
            text="Generate Preview", 
            command=self._generate_preview
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.process_button = ttk.Button(
            button_frame, 
            text="Process Files",
            command=self._process_files,
            state=tk.DISABLED
        )
        self.process_button.pack(side=tk.LEFT)
        
        # Status and progress
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(status_frame, mode="determinate", length=200)
        self.progress.pack(side=tk.RIGHT)
    
    def _create_preview_tab(self, parent):
        """Create the preview tab content"""
        # Create a frame for the treeview
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create the treeview with scrollbars
        self.preview_tree = ttk.Treeview(
            tree_frame,
            columns=("Job", "Target Folder", "Status"),
            show="headings"
        )
        
        # Configure columns
        self.preview_tree.heading("Job", text="Job Name")
        self.preview_tree.heading("Target Folder", text="Target Folder")
        self.preview_tree.heading("Status", text="Status")
        
        self.preview_tree.column("Job", width=150)
        self.preview_tree.column("Target Folder", width=300)
        self.preview_tree.column("Status", width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for treeview and scrollbars
        self.preview_tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def _create_report_tab(self, parent):
        """Create the report tab content"""
        # Create text widget with scrollbars
        self.report_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.report_text.config(state=tk.DISABLED)
        
        # Bottom buttons for report actions
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Save Report...", 
            command=self._save_report
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Clear Report", 
            command=self._clear_report
        ).pack(side=tk.LEFT)
    
    def _select_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(
            title="Select PDF Source Folder",
            initialdir=self.current_folder.get() or os.path.expanduser("~")
        )
        
        if folder:
            self.current_folder.set(folder)
            self.config_manager.update_recent_folder(folder)
            self._update_recent_menu()
            self._generate_preview()
    
    def _update_recent_menu(self):
        """Update the recent folders menu"""
        # Clear current items
        self.recent_menu.delete(0, tk.END)
        
        # Add recent folders from config
        recent_folders = self.config.get('recent_folders', [])
        
        if not recent_folders:
            self.recent_menu.add_command(label="(No recent folders)", state=tk.DISABLED)
        else:
            for folder in recent_folders:
                # Create a lambda that captures the current folder value
                self.recent_menu.add_command(
                    label=folder, 
                    command=lambda f=folder: self._select_recent_folder(f)
                )
    
    def _select_recent_folder(self, folder):
        """Select a folder from the recent folders menu"""
        if os.path.exists(folder):
            self.current_folder.set(folder)
            self._generate_preview()
        else:
            messagebox.showerror(
                "Folder Not Found", 
                f"The folder '{folder}' no longer exists."
            )
            # Remove from recent folders
            recent_folders = self.config.get('recent_folders', [])
            if folder in recent_folders:
                recent_folders.remove(folder)
                self.config['recent_folders'] = recent_folders
                self.config_manager.save_config(self.config)
                self._update_recent_menu()
    
    def _update_operation_type(self):
        """Update the operation type based on the radio button selection"""
        is_move = self.operation_var.get()
        self.file_operator.set_operation_type(is_move)
        
        # Update config
        self.config['is_move_operation'] = is_move
        self.config_manager.save_config(self.config)
        
        logger.info(f"Operation type set to {'MOVE' if is_move else 'COPY'}")
    
    def _edit_target_folders(self):
        """Open dialog to edit target folders"""
        target_folders = self.config.get('target_folders', {})
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Target Folders")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog modal
        dialog.focus_set()
        
        # Instructions label
        ttk.Label(
            dialog, 
            text="Configure job names and their target folders:",
            wraplength=480
        ).pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Create frame for entries
        entries_frame = ttk.Frame(dialog)
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable frame for entries
        canvas = tk.Canvas(entries_frame)
        scrollbar = ttk.Scrollbar(entries_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Current entries
        entry_pairs = []
        
        # Add existing target folders
        for job_name, folder_path in target_folders.items():
            self._add_target_folder_entry(scrollable_frame, entry_pairs, job_name, folder_path)
        
        # Add a blank entry if none exist
        if not target_folders:
            self._add_target_folder_entry(scrollable_frame, entry_pairs)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Add Row",
            command=lambda: self._add_target_folder_entry(scrollable_frame, entry_pairs)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="Save",
            command=lambda: self._save_target_folders(dialog, entry_pairs)
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Wait for the dialog to close
        self.root.wait_window(dialog)
    
    def _add_target_folder_entry(self, parent, entry_pairs, job_name="", folder_path=""):
        """Add a row for job name and target folder"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=(0, 5))
        
        job_entry = ttk.Entry(row_frame, width=20)
        job_entry.insert(0, job_name)
        job_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        folder_entry = ttk.Entry(row_frame, width=30)
        folder_entry.insert(0, folder_path)
        folder_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        browse_button = ttk.Button(
            row_frame,
            text="Browse...",
            command=lambda e=folder_entry: self._browse_target_folder(e)
        )
        browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_button = ttk.Button(
            row_frame,
            text="X",
            width=2,
            command=lambda: self._remove_target_folder_entry(row_frame, entry_pairs)
        )
        remove_button.pack(side=tk.LEFT)
        
        entry_pairs.append((job_entry, folder_entry))
    
    def _browse_target_folder(self, entry_widget):
        """Browse for a target folder and update the entry widget"""
        folder = filedialog.askdirectory(
            title="Select Target Folder",
            initialdir=entry_widget.get() or os.path.expanduser("~")
        )
        
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)
    
    def _remove_target_folder_entry(self, row_frame, entry_pairs):
        """Remove a target folder entry row"""
        # Find the entry pair to remove
        to_remove = None
        for i, (job_entry, folder_entry) in enumerate(entry_pairs):
            if job_entry.master == row_frame:
                to_remove = i
                break
        
        if to_remove is not None:
            entry_pairs.pop(to_remove)
            row_frame.destroy()
    
    def _save_target_folders(self, dialog, entry_pairs):
        """Save the target folders configuration"""
        target_folders = {}
        
        for job_entry, folder_entry in entry_pairs:
            job_name = job_entry.get().strip()
            folder_path = folder_entry.get().strip()
            
            if job_name and folder_path:
                target_folders[job_name] = folder_path
        
        # Update target_folders in config
        self.config['target_folders'] = target_folders
        self.config_manager.save_config(self.config)
        
        logger.info(f"Saved {len(target_folders)} target folders")
        
        # Close dialog
        dialog.destroy()
        
        # Regenerate preview if needed
        if self.current_folder.get():
            self._generate_preview()
    
    def _edit_patterns(self):
        """Open dialog to edit extraction patterns"""
        patterns = self.config.get('patterns', [r"Job:\s*(.*)"])
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Extraction Patterns")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Make dialog modal
        dialog.focus_set()
        
        # Instructions label
        ttk.Label(
            dialog, 
            text="Configure regex patterns for extracting job names from PDFs. "
                 "Each pattern should have one capture group for the job name.",
            wraplength=480
        ).pack(fill=tk.X, padx=10, pady=(10, 0))
        
        ttk.Label(
            dialog,
            text="Example: 'Job:\\s*(.*)' will extract 'ABC123' from 'Job: ABC123'",
            wraplength=480
        ).pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # Create frame for entries
        entries_frame = ttk.Frame(dialog)
        entries_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable frame for entries
        canvas = tk.Canvas(entries_frame)
        scrollbar = ttk.Scrollbar(entries_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pattern entries
        pattern_entries = []
        
        # Add existing patterns
        for pattern in patterns:
            self._add_pattern_entry(scrollable_frame, pattern_entries, pattern)
        
        # Add a blank entry if none exist
        if not patterns:
            self._add_pattern_entry(scrollable_frame, pattern_entries)
        
        # Buttons frame
        buttons_frame = ttk.Frame(dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Add Pattern",
            command=lambda: self._add_pattern_entry(scrollable_frame, pattern_entries)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="Save",
            command=lambda: self._save_patterns(dialog, pattern_entries)
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=(0, 5))
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Wait for the dialog to close
        self.root.wait_window(dialog)
    
    def _add_pattern_entry(self, parent, pattern_entries, pattern=""):
        """Add a row for pattern entry"""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=(0, 5))
        
        pattern_entry = ttk.Entry(row_frame, width=50)
        pattern_entry.insert(0, pattern)
        pattern_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        
        remove_button = ttk.Button(
            row_frame,
            text="X",
            width=2,
            command=lambda: self._remove_pattern_entry(row_frame, pattern_entries)
        )
        remove_button.pack(side=tk.LEFT)
        
        pattern_entries.append(pattern_entry)
    
    def _remove_pattern_entry(self, row_frame, pattern_entries):
        """Remove a pattern entry row"""
        # Find the entry to remove
        to_remove = None
        for i, entry in enumerate(pattern_entries):
            if entry.master == row_frame:
                to_remove = i
                break
        
        if to_remove is not None:
            pattern_entries.pop(to_remove)
            row_frame.destroy()
    
    def _save_patterns(self, dialog, pattern_entries):
        """Save the extraction patterns configuration"""
        patterns = []
        
        for entry in pattern_entries:
            pattern = entry.get().strip()
            if pattern:
                patterns.append(pattern)
        
        # Ensure at least one pattern
        if not patterns:
            patterns = [r"Job:\s*(.*)"]
        
        # Update patterns in config
        self.config['patterns'] = patterns
        self.config_manager.save_config(self.config)
        
        # Update pdf processor
        self.pdf_processor.patterns = patterns
        
        logger.info(f"Saved {len(patterns)} extraction patterns")
        
        # Close dialog
        dialog.destroy()
        
        # Regenerate preview if needed
        if self.current_folder.get():
            self._generate_preview()
    
    def _generate_preview(self):
        """Generate a preview of how files will be organized"""
        folder_path = self.current_folder.get()
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showerror(
                "Invalid Folder", 
                "Please select a valid source folder."
            )
            return
        
        # Clear the preview tree
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Disable buttons during processing
        self.process_button.config(state=tk.DISABLED)
        self.status_var.set("Analyzing PDF files...")
        self.root.update()
        
        # Get target folders from config
        target_folders = self.config.get('target_folders', {})
        
        # Create a thread for analysis
        def analyze_thread():
            # Get the mapping data
            self.preview_data = self.pdf_processor.analyze_pdf_folder(
                folder_path, target_folders, self.mapping
            )
            
            # Update GUI on the main thread
            self.root.after(0, self._update_preview_display)
        
        # Start the analysis thread
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def _update_preview_display(self):
        """Update the preview display with analysis results"""
        # Clear current preview
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Add files to process
        for pdf_file, data in self.preview_data['to_process'].items():
            source_path = os.path.join(self.current_folder.get(), pdf_file)
            self.preview_tree.insert(
                "", "end", values=(
                    data['job_text'],
                    data['target_folder'],
                    "New"
                ),
                tags=("new",)
            )
        
        # Add unknown files
        for item in self.preview_data['unknown']:
            self.preview_tree.insert(
                "", "end", values=(
                    item['job_text'],
                    "Unknown - Will Not Process",
                    "Unknown Job"
                ),
                tags=("unknown",)
            )
        
        # Add already mapped files
        for pdf_file, target_folder in self.preview_data['already_mapped'].items():
            self.preview_tree.insert(
                "", "end", values=(
                    "Existing Mapping",
                    target_folder,
                    "Already Mapped"
                ),
                tags=("mapped",)
            )
        
        # Configure tag colors
        self.preview_tree.tag_configure("new", background="#e6ffe6")
        self.preview_tree.tag_configure("unknown", background="#ffe6e6")
        self.preview_tree.tag_configure("mapped", background="#e6e6ff")
        
        # Update status
        total_files = len(self.preview_data['to_process']) + len(self.preview_data['unknown']) + len(self.preview_data['already_mapped'])
        self.status_var.set(f"Found {total_files} PDF files. Ready to process.")
        
        # Enable process button if there are files to process
        if self.preview_data['to_process'] or self.preview_data['already_mapped']:
            self.process_button.config(state=tk.NORMAL)
        else:
            self.process_button.config(state=tk.DISABLED)
    
    def _process_files(self):
        """Process files according to the preview"""
        if self.is_processing:
            return
        
        # Check if there are files to process
        if not self.preview_data['to_process'] and not self.preview_data['already_mapped']:
            messagebox.showinfo("No Files", "No files to process.")
            return
        
        # Confirm processing
        operation_name = "move" if self.file_operator.is_move_operation else "copy"
        if not messagebox.askyesno(
            "Confirm Processing",
            f"Are you sure you want to {operation_name} the files as shown in the preview?"
        ):
            return
        
        # Prepare for processing
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.file_operator.clear_report_data()
        
        # Switch to report tab
        self.notebook.select(1)
        
        # Clear report text
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete(1.0, tk.END)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.report_text.insert(tk.END, f"PDF Organizer Report - {timestamp}\n")
        self.report_text.insert(tk.END, f"Operation: {'MOVE' if self.file_operator.is_move_operation else 'COPY'}\n")
        self.report_text.insert(tk.END, f"Source folder: {self.current_folder.get()}\n\n")
        self.report_text.insert(tk.END, "Processing files...\n\n")
        self.report_text.config(state=tk.DISABLED)
        self.root.update()
        
        # Reset progress bar
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.preview_data['to_process']) + len(self.preview_data['already_mapped'])
        
        # Create file mapping for processing
        file_mapping = {}
        
        # Add new files to process
        for pdf_file, data in self.preview_data['to_process'].items():
            source_path = os.path.join(self.current_folder.get(), pdf_file)
            destination_path = os.path.join(data['target_folder'], pdf_file)
            file_mapping[source_path] = destination_path
            
            # Update mapping dict for future use
            self.mapping[pdf_file] = data['target_folder']
        
        # Add already mapped files
        for pdf_file, target_folder in self.preview_data['already_mapped'].items():
            source_path = os.path.join(self.current_folder.get(), pdf_file)
            destination_path = os.path.join(target_folder, pdf_file)
            file_mapping[source_path] = destination_path
        
        # Function to update progress
        def update_progress(current, total):
            self.progress["value"] = current
            self.status_var.set(f"Processing file {current} of {total}")
            self.root.update()
        
        # Create a thread for processing
        def process_thread():
            success_count, failure_count = self.file_operator.process_files_with_progress(
                file_mapping, update_progress
            )
            
            # Save the updated mapping
            self.config_manager.save_mapping(self.mapping)
            
            # Update GUI on the main thread
            self.root.after(0, lambda: self._finalize_processing(success_count, failure_count))
        
        # Start the processing thread
        threading.Thread(target=process_thread, daemon=True).start()
    
    def _finalize_processing(self, success_count, failure_count):
        """Finalize processing and update the report"""
        # Update report
        self.report_text.config(state=tk.NORMAL)
        self.report_text.insert(tk.END, f"\nProcessing complete!\n")
        self.report_text.insert(tk.END, f"Successfully processed: {success_count} files\n")
        self.report_text.insert(tk.END, f"Failed: {failure_count} files\n\n")
        
        # Add detailed report
        self.report_text.insert(tk.END, "DETAILED REPORT\n")
        self.report_text.insert(tk.END, "-" * 40 + "\n")
        
        for item in self.file_operator.report_data:
            operation = item['operation'].upper()
            status = item['status'].upper()
            source = item['source']
            dest = item['destination']
            
            self.report_text.insert(tk.END, f"Operation: {operation}\n")
            self.report_text.insert(tk.END, f"From: {source}\n")
            self.report_text.insert(tk.END, f"To: {dest}\n")
            self.report_text.insert(tk.END, f"Status: {status}\n")
            
            if status == "ERROR" and 'error' in item:
                self.report_text.insert(tk.END, f"Error: {item['error']}\n")
                
            self.report_text.insert(tk.END, "-" * 40 + "\n")
        
        self.report_text.see(1.0)  # Scroll to the top
        self.report_text.config(state=tk.DISABLED)
        
        # Update status
        self.status_var.set(f"Completed: {success_count} successful, {failure_count} failed")
        self.is_processing = False
        
        # Ask if user wants to generate preview again
        if messagebox.askyesno(
            "Process Complete", 
            "Processing complete. Do you want to generate a new preview?"
        ):
            self.notebook.select(0)  # Switch to preview tab
            self._generate_preview()
    
    def _save_report(self):
        """Save the current report to a file"""
        if not self.report_text.get(1.0, tk.END).strip():
            messagebox.showinfo("Empty Report", "No report data to save.")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=os.path.expanduser("~")
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.report_text.get(1.0, tk.END))
                messagebox.showinfo("Report Saved", f"Report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving report: {e}")
    
    def _clear_report(self):
        """Clear the report text"""
        if messagebox.askyesno("Clear Report", "Are you sure you want to clear the report?"):
            self.report_text.config(state=tk.NORMAL)
            self.report_text.delete(1.0, tk.END)
            self.report_text.config(state=tk.DISABLED)
    
    def _show_about(self):
        """Show about dialog"""
        about_dialog = tk.Toplevel(self.root)
        about_dialog.title("About PDF Organizer")
        about_dialog.geometry("400x300")
        about_dialog.transient(self.root)
        about_dialog.grab_set()
        
        # Make dialog modal
        about_dialog.focus_set()
        
        # Content
        ttk.Label(
            about_dialog,
            text="Enhanced PDF Organizer",
            font=("", 16, "bold")
        ).pack(pady=(20, 5))
        
        ttk.Label(
            about_dialog,
            text="Version 1.0",
            font=("", 10)
        ).pack(pady=(0, 20))
        
        ttk.Label(
            about_dialog,
            text="An application to automatically organize PDF files based on job information.",
            wraplength=350,
            justify=tk.CENTER
        ).pack(pady=(0, 10))
        
        ttk.Label(
            about_dialog,
            text="Features:\n"
                 "• Automatic job text extraction\n"
                 "• Copy or move operations\n"
                 "• Custom extraction patterns\n"
                 "• Preview functionality\n"
                 "• Detailed reporting",
            justify=tk.LEFT
        ).pack(pady=(0, 20))
        
        ttk.Button(
            about_dialog,
            text="OK",
            command=about_dialog.destroy
        ).pack(pady=(0, 20))
        
        # Center the dialog
        about_dialog.update_idletasks()
        width = about_dialog.winfo_width()
        height = about_dialog.winfo_height()
        x = (about_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (about_dialog.winfo_screenheight() // 2) - (height // 2)
        about_dialog.geometry(f'{width}x{height}+{x}+{y}')
