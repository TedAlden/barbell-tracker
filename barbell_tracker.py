"""
This class is responsible for tracking the barbell using OpenCV and generating
position data.
"""

import cv2

class BarbellTracker:
    def __init__(
            self,
            show_preview=True,
            sample_interval=1,
            show_bar_path=True,
            barbell_height_m=0.45,
            match_threshold=0.3):
        self.show_preview = show_preview
        self.sample_interval = sample_interval
        self.show_bar_path = show_bar_path
        self.barbell_height_m = barbell_height_m
        self.match_threshold = match_threshold
        self.reset()

    def reset(self):
        self.template = None
        self.template_region = None
        self.pixels_per_meter = None
        self.positions = []
        self.timestamps = []
        self.fps = 0
        self.num_frames = 0
        self.current_frame = 0

    def track(self, video_path):
        self.reset()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file.")

        self.fps = int(cap.get(cv2.CAP_PROP_FPS))
        self.num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        ret, frame = cap.read()
        if not ret:
            raise Exception("Could not read first frame.")

        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        self.template_region = self.get_template_selection(frame)
        if self.template_region is None:
            raise Exception("No selection made for barbell plate.")

        x, y, w, h = self.template_region
        if w == 0 or h == 0:
            raise Exception("Invalid template region.")

        self.template = frame[y:y+h, x:x+w].copy()

        self.pixels_per_meter = h / self.barbell_height_m

        if self.show_preview:
            frame_width = frame.shape[1]
            frame_height = frame.shape[0]
            window_width = int(800 * frame_width / frame_height)
            window_height = 800
            cv2.namedWindow("Barbell Tracking", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Barbell Tracking", window_width, window_height)

        # Tracking loop using template matching
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if self.current_frame % self.sample_interval != 0:
                self.current_frame += 1
                continue

            self.current_frame += 1

            position = self.track_frame(frame)

            if position is not None:
                self.positions.append(position)
                self.timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        return self.positions, self.timestamps

    def track_frame(self, frame):
        position = None

        # Use template matching to find the barbell plate
        result = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        x, y, w, h = self.template_region

        if max_val >= self.match_threshold:
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2

            position = (center_x, center_y)

        if self.show_preview:
            # Draw box and center
            cv2.rectangle(frame, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 5)
            cv2.circle(frame, (center_x, center_y), 10, (0, 0, 255), -1)

            # Draw bar path
            if self.show_bar_path and len(self.positions) > 1:
                for i in range(1, len(self.positions)):
                    last_point = (int(self.positions[i-1][0]), int(self.positions[i-1][1]))
                    this_point = (int(self.positions[i][0]), int(self.positions[i][1]))
                    cv2.line(frame, last_point, this_point, (255, 0, 255), 2)

            cv2.putText(frame, f"Frame: {self.current_frame}/{self.num_frames}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            match_text = f"Match: {max_val:.2f}" if position else "No match found"
            cv2.putText(frame, match_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Barbell Tracking", frame)

        return position

    def get_template_selection(self, frame):
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        window_width = int(800 * frame_width / frame_height)
        window_height = 800

        cv2.namedWindow("Select Barbell Plate", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Select Barbell Plate", window_width, window_height)

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
                selection = (
                    min(start_point[0], end_point[0]),
                    min(start_point[1], end_point[1]),
                    abs(end_point[0] - start_point[0]),
                    abs(end_point[1] - start_point[1])
                )
                img_copy = frame.copy()
                cv2.rectangle(
                    img_copy,
                    (selection[0], selection[1]),
                    (selection[0] + selection[2], selection[1] + selection[3]),
                    (0, 255, 0),
                    2
                )
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
