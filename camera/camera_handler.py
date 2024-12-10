import cv2

class CameraHandler:
    def __init__(self, device_index):
        self.device_index = device_index
        self.capture = None

    def connect(self):
        self.capture = cv2.VideoCapture(self.device_index)
        if not self.capture.isOpened():
            raise Exception(f"Failed to connect to USB camera with device index: {self.device_index}")

    def get_frame(self):
        if self.capture is None or not self.capture.isOpened():
            raise Exception("Camera connection is not open.")
        ret, frame = self.capture.read()
        if not ret:
            raise Exception("Failed to capture frame from USB camera.")
        return frame

    def disconnect(self):
        if self.capture is not None:
            self.capture.release()

