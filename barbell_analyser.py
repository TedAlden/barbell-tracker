"""
This class is responsible for analyzing the position data from the barbell
tracker using NumPy.
"""

import numpy as np

class BarbellAnalyser:
    def __init__(self, positions, timestamps, num_frames):
        self.positions = positions
        self.timestamps = timestamps
        self.num_frames = num_frames
        self.velocities = []

    def calculate_velocities(self):
        for i in range(1, len(self.positions)):
            dx = self.positions[i][1] - self.positions[i-1][1]
            dt = self.timestamps[i] - self.timestamps[i-1]
            v = dx / dt if dt > 0 else 0
            self.velocities.append(v)

    def get_results(self):
        self.calculate_velocities()
        results = {}
        results['peak_velocity'] = max(self.velocities) if self.velocities else 0
        results['avg_velocity'] = np.mean(self.velocities) if self.velocities else 0
        results['min_velocity'] = min(self.velocities) if self.velocities else 0
        results['std_velocity'] = np.std(self.velocities) if self.velocities else 0
        results['total_points'] = len(self.positions)
        results['success_rate'] = len(self.positions) / self.num_frames if self.num_frames > 0 else 0

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
