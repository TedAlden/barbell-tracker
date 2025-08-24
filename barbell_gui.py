"""
This class is responsible for creating a GUI using TKinter that implements the
barbell tracker and barbell analyser.
"""

import threading
import os

import tkinter as tk

from tkinter import ttk, filedialog, messagebox
from barbell_tracker import BarbellTracker
from barbell_analyser import BarbellAnalyser


class BarbellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Barbell Velocity Analyzer")
        self.root.geometry("800x600")
        self.tracker = None
        self.analyser = None
        self.setup_ui()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Barbell Velocity Analyzer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Video File", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        self.file_var = tk.StringVar()
        ttk.Label(file_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W)
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50)
        file_entry.grid(row=0, column=1, padx=(10, 10), sticky=(tk.W, tk.E))

        browse_btn = ttk.Button(file_frame, text="Browse", command=self.btn_browse_click)
        browse_btn.grid(row=0, column=2)

        # Analysis settings
        settings_frame = ttk.LabelFrame(main_frame, text="Analysis Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.barbell_height_var = tk.StringVar(value="0.45")
        ttk.Label(settings_frame, text="Barbell Height (meters):").grid(row=0, column=0, sticky=tk.W)
        height_entry = ttk.Entry(settings_frame, textvariable=self.barbell_height_var, width=10)
        height_entry.grid(row=0, column=1, padx=(10, 0))

        self.match_threshold_var = tk.StringVar(value="0.3")
        ttk.Label(settings_frame, text="Match Threshold:").grid(row=1, column=0, sticky=tk.W)
        threshold_entry = ttk.Entry(settings_frame, textvariable=self.match_threshold_var, width=10)
        threshold_entry.grid(row=1, column=1, padx=(10, 0))

        self.sample_interval_var = tk.IntVar(value=1)
        ttk.Label(settings_frame, text="Sample interval (frames):").grid(row=2, column=0, sticky=tk.W)
        sample_interval_entry = ttk.Entry(settings_frame, textvariable=self.sample_interval_var, width=10)
        sample_interval_entry.grid(row=2, column=1, padx=(10, 0))

        self.show_preview_var = tk.BooleanVar(value=True)
        preview_check = ttk.Checkbutton(settings_frame, text="Show Preview", variable=self.show_preview_var)
        preview_check.grid(row=3, column=0, sticky=tk.W)

        self.show_bar_path_var = tk.BooleanVar(value=True)
        preview_check = ttk.Checkbutton(settings_frame, text="Trace Bar Path", variable=self.show_bar_path_var)
        preview_check.grid(row=4, column=0, sticky=tk.W)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        self.analyze_btn = ttk.Button(control_frame, text="Analyze Video", command=self.btn_analyse_click)
        self.analyze_btn.grid(row=0, column=0)

        self.plot_btn = ttk.Button(control_frame, text="Plot Velocity", command=self.btn_plot_click)
        self.plot_btn.grid(row=0, column=1)

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def btn_browse_click(self):
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes
        )
        if filename:
            self.file_var.set(filename)

    def btn_analyse_click(self):
        if not self.file_var.get():
            messagebox.showerror("Error", "Please select a video file first.")
            return

        if not os.path.exists(self.file_var.get()):
            messagebox.showerror("Error", "Selected video file does not exist.")
            return

        # Start analysis in separate thread
        thread = threading.Thread(target=self.analyze_video)
        thread.daemon = True
        thread.start()
        self.sync_progress_bar(thread)
    
    def btn_plot_click(self):
        if self.analyser is not None:
            self.analyser.plot_velocity()

    def analyze_video(self):
        try:
            self.tracker = BarbellTracker(
                show_preview=self.show_preview_var.get(),
                sample_interval=self.sample_interval_var.get(),
                show_bar_path=self.show_bar_path_var.get(),
                barbell_height_m=0.45,
                match_threshold=0.3
            )
            self.root.after(0, lambda: self.on_analysis_start())

            positions, timestamps = self.tracker.track(self.file_var.get())
            self.root.after(0, lambda: self.on_analysis_complete(positions, timestamps))

        except Exception as e:
            self.root.after(0, lambda err=str(e): self.on_analysis_error(err))

    def sync_progress_bar(self, thread):
        if self.tracker:
            self.progress_bar.config(value=self.tracker.current_frame)
            self.progress_bar.config(maximum=self.tracker.num_frames)
        if thread.is_alive():
            self.root.after(100, lambda: self.sync_progress_bar(thread))

    def on_analysis_start(self):
        self.progress_var.set("Analysing video...")
        self.analyze_btn.config(state="disabled")
        self.plot_btn.config(state="disabled")
        self.progress_bar.config(value=0)

    def on_analysis_complete(self, positions, timestamps):
        self.progress_var.set("Analysis complete!")
        self.analyze_btn.config(state="normal")
        self.plot_btn.config(state="normal")

        # Analyse position data
        try:
            positions_m = [self.convert_position_px_to_m(pos) for pos in positions]
            self.analyser = BarbellAnalyser(positions_m, timestamps, self.tracker.num_frames)
            results_string = self.analyser.get_results_string()
        except Exception as e:
            self.on_analysis_error(str(e))

        # Display results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, results_string)

    def on_analysis_error(self, error_msg):
        self.progress_var.set("Analysis failed!")
        self.analyze_btn.config(state="normal")
        self.plot_btn.config(state="normal")
        messagebox.showerror("Analysis Error", f"Error during analysis: {error_msg}")

    def convert_position_px_to_m(self, position_px):
        if self.tracker.pixels_per_meter > 0:
            return (
                position_px[0] / self.tracker.pixels_per_meter,
                position_px[1] / self.tracker.pixels_per_meter
            )
        return 0
