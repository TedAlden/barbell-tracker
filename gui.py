import threading
import os

import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt

from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from barbell_tracker import BarbellTracker


class BarbellAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Barbell Velocity Analyzer")
        self.root.geometry("800x600")
        
        self.tracker = BarbellTracker()
        self.video_path = None
        self.results = {}
        
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
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2)
        
        # Analysis settings
        settings_frame = ttk.LabelFrame(main_frame, text="Analysis Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.barbell_height_var = tk.StringVar(value="0.45")
        ttk.Label(settings_frame, text="Barbell Height (meters):").grid(row=0, column=0, sticky=tk.W)
        height_entry = ttk.Entry(settings_frame, textvariable=self.barbell_height_var, width=10)
        height_entry.grid(row=0, column=1, padx=(10, 10))
        
        self.match_threshold_var = tk.StringVar(value="0.3")
        ttk.Label(settings_frame, text="Match Threshold:").grid(row=1, column=0, sticky=tk.W)
        threshold_entry = ttk.Entry(settings_frame, textvariable=self.match_threshold_var, width=10)
        threshold_entry.grid(row=1, column=1, padx=(10, 0))
        
        # TODO
        # self.show_preview_var = tk.BooleanVar(value=True)
        # preview_check = ttk.Checkbutton(settings_frame, text="Show Preview During Analysis", variable=self.show_preview_var)
        # preview_check.grid(row=2, column=0, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.analyze_btn = ttk.Button(control_frame, text="Analyze Video", command=self.start_analysis)
        self.analyze_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create text widget for results
        self.results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    def browse_file(self):
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes
        )
        if filename:
            self.video_path = filename
            self.file_var.set(filename)
    
    def start_analysis(self):
        if not self.video_path:
            messagebox.showerror("Error", "Please select a video file first.")
            return
            
        if not os.path.exists(self.video_path):
            messagebox.showerror("Error", "Selected video file does not exist.")
            return
            
        # Disable buttons during analysis
        self.progress_bar.config(value=0)
        self.analyze_btn.config(state="disabled")
        self.progress_var.set("Loading video...")
        
        # Start analysis in separate thread
        thread = threading.Thread(target=self.analyze_video)
        thread.daemon = True
        thread.start()

        self.sync_progress_bar(thread)
        
    def analyze_video(self):
        try:
            self.tracker = BarbellTracker()
            self.root.after(0, lambda: self.progress_var.set("Loading video..."))
            
            # Configure tracker
            try:
                barbell_height = float(self.barbell_height_var.get())
                match_threshold = float(self.match_threshold_var.get())
                self.tracker.barbell_height_m = barbell_height
                self.tracker.match_threshold = match_threshold
            except ValueError:
                messagebox.showwarning("Warning", "Invalid template settings. Using defaults.")
            
            # Analyze video
            self.root.after(0, lambda: self.progress_var.set("Analyzing video..."))
            positions, timestamps = self.tracker.track(self.video_path)
            results = self.analyse_raw_data(positions, timestamps)

            # Update UI with results
            self.root.after(0, lambda: self.analysis_complete(results))

        except Exception as e:
            self.root.after(0, lambda err=str(e): self.analysis_error(err))

    def sync_progress_bar(self, thread):    
        self.progress_bar.config(value=self.tracker.current_frame)
        self.progress_bar.config(maximum=self.tracker.num_frames)

        if thread.is_alive():
            self.root.after(100, lambda: self.sync_progress_bar(thread))

    def analyse_raw_data(self, positions, timestamps):
        velocities = []

        positions = list(map(lambda pos: (
            pos[0] / self.tracker.pixels_per_meter,
            pos[1] / self.tracker.pixels_per_meter
        ), positions))

        for i in range(1, len(positions)):
            dx_meters = positions[i][1] - positions[i-1][1]
            dt = timestamps[i] - timestamps[i-1]
            v = dx_meters / dt if dt > 0 else 0
            velocities.append(v)

        results = {}
        results['peak_velocity'] = max(velocities) if velocities else 0
        results['avg_velocity'] = np.mean(velocities) if velocities else 0
        results['min_velocity'] = min(velocities) if velocities else 0
        results['std_velocity'] = np.std(velocities) if velocities else 0
        results['total_points'] = len(positions)
        results['success_rate'] = len(positions) / self.tracker.num_frames
        return results

    def analysis_complete(self, results):
        self.progress_var.set("Analysis complete!")
        
        # Re-enable buttons
        self.analyze_btn.config(state="normal")
        
        # Display results
        self.display_results(results)
        
    def analysis_error(self, error_msg):
        self.progress_var.set("Analysis failed!")
        self.analyze_btn.config(state="normal")
        messagebox.showerror("Analysis Error", f"Error during analysis: {error_msg}")

    def display_results(self, results):
        self.results_text.delete(1.0, tk.END)

        results_text = f"Barbell Lift Velocity Analysis Results\n"
        results_text += f"{'='*50}\n"
        results_text += f"Peak Velocity: {results['peak_velocity']:.3f} m/s\n"
        results_text += f"Average Velocity: {results['avg_velocity']:.3f} m/s\n"
        results_text += f"Minimum Velocity: {results['min_velocity']:.3f} m/s\n"
        results_text += f"Standard Deviation: {results['std_velocity']:.3f} m/s\n"
        results_text += f"Total Points: {results['total_points']}\n"
        results_text += f"Success Rate: {results['success_rate']:.1f}%\n"
        results_text += f"{'='*50}\n"

        self.results_text.insert(1.0, results_text)

def main():
    root = tk.Tk()
    app = BarbellAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
