import matplotlib.pyplot as plt
import numpy as np

from barbell_tracker import BarbellTracker
from scipy.interpolate import interp1d


def print_analysis(positions, timestamps, frame_count):
    velocities = []
    
    for i in range(1, len(positions)):
        dx_meters = positions[i][1] - positions[i-1][1]  # vertical displacement (pixels)
        dt = timestamps[i] - timestamps[i-1]
        v = dx_meters / dt if dt > 0 else 0
        velocities.append(v)
    
    if velocities:
        print(f"Average velocity: {np.mean(velocities):.3f} m/s")
        print(f"Peak velocity: {max(velocities):.3f} m/s")
        print(f"Min velocity: {min(velocities):.3f} m/s")
        print(f"Velocity std dev: {np.std(velocities):.3f} m/s")
        print(f"Total tracking points: {len(positions)}")
        print(f"Tracking success rate: {len(positions)/len(timestamps)*100:.1f}%")
    else:
        print("No velocities calculated. The barbell may not have been detected in the video.")


def main():
    tracker = BarbellTracker()

    positions, timestamps = tracker.track("lift.mp4")

    positions = list(map(lambda pos: (pos[0] / tracker.pixels_per_meter, pos[1] / tracker.pixels_per_meter), positions))

    print_analysis(positions, timestamps, tracker.num_frames)


if __name__ == "__main__":
    main()
