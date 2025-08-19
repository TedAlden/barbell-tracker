import cv2
import numpy as np

class BarbellTracker:
    def __init__(self):
        self.template = None
        self.template_region = None
        self.pixels_per_meter = None
        self.barbell_height_m = 0.45
        self.match_threshold = 0.3
        self.positions = []
        self.timestamps = []
        self.fps = 0
        self.num_frames = 0

    def track(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Video FPS: {self.fps}")
        
        self.num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total frames: {self.num_frames}")

        # Read first frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read first frame")
            return

        self.template_region = self.get_template_selection(frame)
        if self.template_region is None:
            print("Error: No selection made for barbell plate.")
            return

        x, y, w, h = self.template_region
        self.template = frame[y:y+h, x:x+w].copy()
        
        self.pixels_per_meter = h / self.barbell_height_m

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
            result = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
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
            cv2.putText(frame, f"Frame: {frame_count}/{self.num_frames}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Barbell Tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
        cap.release()
        cv2.destroyAllWindows()

        return positions, timestamps

    def get_template_selection(self, frame):
        cv2.namedWindow("Select Barbell Plate", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Select Barbell Plate", 800, 600)
        
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
        
        # Set mouse callback for selection
        cv2.setMouseCallback("Select Barbell Plate", mouse_callback)
        cv2.imshow("Select Barbell Plate", frame)
        
        # Wait for user selection
        while selection is None:
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                cv2.destroyWindow("Select Barbell Plate")
                return None
        
        cv2.destroyWindow("Select Barbell Plate")
        
        return selection    
