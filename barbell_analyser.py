"""
This class is responsible for analyzing the position data from the barbell
tracker using NumPy and SciPy, then plotting it using Matplotlib.
"""

import numpy as np
import scipy.signal
import matplotlib.pyplot as plt


class BarbellAnalyser:
    def __init__(
            self,
            positions,
            timestamps,
            num_frames,
            smooth_displacement=True,
            smooth_velocity=True,
            smooth_acceleration=True,
            smooth_window_length=15,
            smooth_polynomial_order=3):
        self.smooth_displacement = smooth_displacement
        self.smooth_velocity = smooth_velocity
        self.smooth_acceleration = smooth_acceleration
        self.smooth_window_length = smooth_window_length
        self.smooth_polynomial_order = smooth_polynomial_order

        self.positions = positions
        self.timestamps = timestamps
        self.num_frames = num_frames

        self.displacements = []
        self.velocities = []  # only Y-velocities
        self.accelerations = []  # only Y-accelerations

    def smooth_1d(self, data):
        return scipy.signal.savgol_filter(
            data,
            window_length=self.smooth_window_length,
            polyorder=self.smooth_polynomial_order
        )

    def calculate_displacements(self):
        # Normalise starting y position and flip y coordinates
        start_height = self.positions[0][1]
        positions_height_normalised = [
            (position[0], -(position[1] - start_height))
            for position in self.positions
        ]

        displacements_x = np.array([p[0] for p in positions_height_normalised])
        displacements_y = np.array([p[1] for p in positions_height_normalised])

        if self.smooth_displacement:
            displacements_x_smoothed = self.smooth_1d(displacements_x)
            displacements_y_smoothed = self.smooth_1d(displacements_y)
            self.displacements = list(zip(displacements_x_smoothed, displacements_y_smoothed))
        else:
            self.displacements = list(zip(displacements_x, displacements_y))

    def calculate_velocities(self):
        displacements_y = np.array([d[1] for d in self.displacements])
        velocities_y = list(np.gradient(displacements_y, self.timestamps))

        if self.smooth_velocity:
            self.velocities = self.smooth_1d(velocities_y)
        else:
            self.velocities = velocities_y

    def calculate_accelerations(self):
        accelerations_y = list(np.gradient(self.velocities, self.timestamps))

        if self.smooth_acceleration:
            self.accelerations = self.smooth_1d(accelerations_y)
        else:
            self.accelerations = accelerations_y

    def get_results(self):
        self.calculate_displacements()
        self.calculate_velocities()
        self.calculate_accelerations()

        results = {}
        results['peak_velocity'] = max(self.velocities) if self.velocities.any() else 0
        results['avg_velocity'] = np.mean(self.velocities) if self.velocities.any() else 0
        results['min_velocity'] = min(self.velocities) if self.velocities.any() else 0
        results['std_velocity'] = np.std(self.velocities) if self.velocities.any() else 0
        results['total_points'] = len(self.displacements)
        results['success_rate'] = len(self.displacements) / self.num_frames if self.num_frames > 0 else 0

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

    def plot_data(self):
        plt.figure(figsize=(9, 6))

        # Plot displacement-time
        displacements_y = np.array([d[1] for d in self.displacements])

        plt.subplot(2, 2, 1)
        plt.plot(self.timestamps, displacements_y)
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
        xs = [pos[0] for pos in self.displacements]
        ys = [pos[1] for pos in self.displacements]
        start_pos = self.displacements[0]
        end_pos = self.displacements[-1]

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
    
    def export_to_tuple(self):
        data = [("frame_number", "timestamp", "x_pos", "y_pos")]
        for i, (t, (x, y)) in enumerate(zip(self.timestamps, self.displacements)):
            data.append((i, t, x, y))

        return tuple(data)
