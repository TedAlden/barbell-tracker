"""
This class is responsible for analyzing the position data from the barbell
tracker using NumPy and SciPy, then plotting it using Matplotlib.
"""

import numpy as np
import scipy.signal
import matplotlib.pyplot as plt


class BarbellAnalyser:
    def __init__(self, positions, timestamps, num_frames):
        self.positions_xy_raw = positions
        self.timestamps = timestamps
        self.num_frames = num_frames

        self.positions_xy_normalised = []
        self.positions_y_smoothed = []
        self.velocities = []
        self.accelerations = []

    def preprocess_data(self):
        # Normalise starting y position and flip y coordinates
        start_height = self.positions_xy_raw[0][1]
        self.positions_xy_normalised = [
            (position[0], -(position[1] - start_height))
            for position in self.positions_xy_raw
        ]

        # Use savgol filter to smooth y position
        positions_y = np.array([p[1] for p in self.positions_xy_normalised])
        self.positions_y_smoothed = scipy.signal.savgol_filter(positions_y, window_length=15, polyorder=3)

    def calculate_velocities(self):
        # Use second-order central differences to calculate velocity
        self.velocities = list(np.gradient(self.positions_y_smoothed, self.timestamps))

    def calculate_accelerations(self):
        # Use second-order central differences to calculate velocity
        self.accelerations = list(np.gradient(self.velocities, self.timestamps))

    def get_results(self):
        self.preprocess_data()
        self.calculate_velocities()
        self.calculate_accelerations()
        results = {}
        results['peak_velocity'] = max(self.velocities) if self.velocities else 0
        results['avg_velocity'] = np.mean(self.velocities) if self.velocities else 0
        results['min_velocity'] = min(self.velocities) if self.velocities else 0
        results['std_velocity'] = np.std(self.velocities) if self.velocities else 0
        results['total_points'] = len(self.positions_xy_raw)
        results['success_rate'] = len(self.positions_xy_raw) / self.num_frames if self.num_frames > 0 else 0

        return results

    def get_results_string(self):
        results = self.get_results()

        results_string = f"Barbell Lift Velocity Analysis Results\n"
        results_string += f"{'='*50}\n"
        results_string += f"Peak Velocity: {results['peak_velocity']:.3f} m/s\n"
        results_string += f"Average Velocity: {results['avg_velocity']:.3f} m/s\n"
        results_string += f"Minimum Velocity: {results['min_velocity']:.3f} m/s\n"
        results_string += f"Standard Deviation: {results['std_velocity']:.3f} m/s\n"
        results_string += f"Total Points: {results['total_points']}\n"
        results_string += f"Success Rate: {results['success_rate']:.1f}%\n"
        results_string += f"{'='*50}\n"

        return results_string

    def plot_velocity(self):
        plt.figure(figsize=(9, 6))

        # Plot displacement-time
        plt.subplot(2, 2, 1)
        plt.plot(self.timestamps, self.positions_y_smoothed)
        plt.xlabel("Time (s)")
        plt.ylabel("Barbell Vertical Displacement (m)")
        plt.title("Barbell Vertical Displacement Over Time")
        plt.grid()

        # Plot velocity-time
        plt.subplot(2, 2, 2)
        plt.plot(self.timestamps, self.velocities)
        plt.xlabel("Time (s)")
        plt.ylabel("Barbell Vertical Velocity (m/s)")
        plt.title("Barbell Vertical Velocity Over Time")
        plt.grid()

        # Plot acceleration-time
        plt.subplot(2, 2, 3)
        plt.plot(self.timestamps, self.accelerations)
        plt.xlabel("Time (s)")
        plt.ylabel("Barbell Vertical Acceleration (m/s²)")
        plt.title("Barbell Vertical Acceleration Over Time")
        plt.grid()

        # Plot bar path
        xs = [pos[0] for pos in self.positions_xy_normalised]
        ys = [pos[1] for pos in self.positions_xy_normalised]
        start_pos = self.positions_xy_normalised[0]
        end_pos = self.positions_xy_normalised[-1]

        plt.subplot(2, 2, 4)
        plt.plot(xs, ys)
        plt.xlabel("Barbell Horizontal Displacement (m)")
        plt.ylabel("Barbell Vertical Displacement (m)")
        plt.title("Barbell Path")
        plt.text(start_pos[0], start_pos[1], "Start", fontsize=10, verticalalignment='center')
        plt.text(end_pos[0], end_pos[1], "End", fontsize=10, verticalalignment='center')
        plt.grid()

        plt.tight_layout()
        plt.show()
