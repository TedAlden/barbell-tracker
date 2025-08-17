import cv2
import numpy as np

def track_barbell():
    BARBELL_HEIGHT_M = 0.45  # Height of the barbell in meters
    
    # Load video
    video_path = "lift.mp4"
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video FPS: {fps}")
    
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames: {num_frames}")

    # Read first frame
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read first frame")
        return

    # Use frame aspect ratio to set window size
    frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    window_width = int(1000 * frame_width / frame_height)
    window_height = 1000

    # Create window for selecting the plate on the barbell
    print("Please select the barbell plate by drawing a rectangle around it.")
    cv2.namedWindow("Select Barbell Plate", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Select Barbell Plate", window_width, window_height)

    # Initialize selection variables
    selection = None
    drawing = False
    start_point = None
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal selection, drawing, start_point
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_copy = frame.copy()
                cv2.rectangle(img_copy, start_point, (x, y), (0, 255, 0), 2)
                cv2.imshow("Select Barbell Plate", img_copy)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)
            selection = (min(start_point[0], end_point[0]), 
                        min(start_point[1], end_point[1]),
                        abs(end_point[0] - start_point[0]),
                        abs(end_point[1] - start_point[1]))
            img_copy = frame.copy()
            cv2.rectangle(img_copy, (selection[0], selection[1]), 
                         (selection[0] + selection[2], selection[1] + selection[3]), 
                         (0, 255, 0), 2)
            cv2.imshow("Select Barbell Plate", img_copy)
    
    cv2.setMouseCallback("Select Barbell Plate", mouse_callback)
    cv2.imshow("Select Barbell Plate", frame)
    
    # Wait for user selection
    while selection is None:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cap.release()
            cv2.destroyAllWindows()
            return
    
    cv2.destroyWindow("Select Barbell Plate")
    
    # Extract template from selected region
    x, y, w, h = selection
    template = frame[y:y+h, x:x+w]
    
    # Calculate pixels per meter conversion
    pixels_per_meter = h / BARBELL_HEIGHT_M
    print(f"Template size: {w}x{h} pixels")
    print(f"Barbell height: {BARBELL_HEIGHT_M} meters")
    print(f"Pixels per meter: {pixels_per_meter:.2f}")
    
    # Store positions and timestamps
    positions = []
    timestamps = []
    
    # Reset video to beginning
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    # Tracking loop using template matching
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Use template matching to find the barbell
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Match threshold
        if max_val > 0.3:
            # Get the center of the matched region
            cx = max_loc[0] + w // 2
            cy = max_loc[1] + h // 2
            
            # Draw box and center
            cv2.rectangle(frame, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            
            # Save position and timestamp
            positions.append((cx, cy))
            timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)  # seconds
            
            # Display match confidence
            cv2.putText(frame, f"Match: {max_val:.2f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            # No good match found
            cv2.putText(frame, "No match found", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display frame number
        cv2.putText(frame, f"Frame: {frame_count}/{num_frames}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Barbell Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Calculate velocity in m/s
    velocities = []
    for i in range(1, len(positions)):
        # Calculate displacement in pixels
        dx_pixels = positions[i][1] - positions[i-1][1]  # vertical displacement (pixels)
        
        # Convert to meters
        dx_meters = dx_pixels / pixels_per_meter
        
        # Calculate time difference
        dt = timestamps[i] - timestamps[i-1]
        
        # Calculate velocity in m/s
        v = dx_meters / dt if dt > 0 else 0
        velocities.append(v)
    
    if velocities:
        print(f"Average velocity: {np.mean(velocities):.3f} m/s")
        print(f"Peak velocity: {max(velocities):.3f} m/s")
        print(f"Min velocity: {min(velocities):.3f} m/s")
        print(f"Velocity std dev: {np.std(velocities):.3f} m/s")
        print(f"Total tracking points: {len(positions)}")
        print(f"Tracking success rate: {len(positions)/frame_count*100:.1f}%")
    else:
        print("No velocities calculated. The barbell may not have been detected in the video.")


if __name__ == "__main__":
    track_barbell()
