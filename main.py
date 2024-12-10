import os
import json
import pandas as pd
import logging
import cv2
from pyzbar.pyzbar import decode
from camera.camera_handler import CameraHandler
import signal
import sys

# Setup logging
LOG_FILE = "logs/app.log"
os.makedirs("logs", exist_ok=True)

# Configure logging to write to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),  # Log to file
        logging.StreamHandler()        # Log to console
    ]
)

# Load configuration
CONFIG_PATH = "config/settings.json"
with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

CAMERA_DEVICE_INDEX = config["camera_device_index"]
OUTPUT_FILE = "data/qr_codes.csv"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Global variables to manage resources
camera_handler = None
qr_records = []

def signal_handler(sig, frame):
    """
    Gracefully handle termination signals like Ctrl+C (SIGINT).
    """
    logging.info("Termination signal received. Cleaning up resources...")
    if camera_handler:
        camera_handler.disconnect()
    cv2.destroyAllWindows()
    sys.exit(0)

# Register the signal handler for SIGINT
signal.signal(signal.SIGINT, signal_handler)

def main():
    global camera_handler, qr_records

    # Initialize camera
    camera_handler = CameraHandler(CAMERA_DEVICE_INDEX)

    try:
        # Connect to the camera
        camera_handler.connect()
        logging.info("Connected to the USB camera successfully.")

        while True:
            # Capture a frame
            frame = camera_handler.get_frame()

            # Detect QR codes in the frame
            qr_codes = decode(frame)

            # Draw bounding boxes and display QR codes on the frame
            for qr_code in qr_codes:
                points = qr_code.polygon
                if len(points) == 4:  # Draw a rectangle around the QR code
                    pts = [(point.x, point.y) for point in points]
                    for i in range(4):
                        cv2.line(frame, pts[i], pts[(i + 1) % 4], (0, 255, 0), 2)
                data = qr_code.data.decode("utf-8")
                x, y = qr_code.rect.left, qr_code.rect.top
                cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Log and record the QR code data
                if data not in [record[1] for record in qr_records]:
                    logging.info(f"Detected QR code: {data}")
                    qr_records.append((pd.Timestamp.now().isoformat(), data))

            # Save detected QR codes to CSV
            if qr_records:
                df = pd.DataFrame(qr_records, columns=["Timestamp", "QR Code"])
                df.to_csv(OUTPUT_FILE, index=False)

            # Display the video stream
            cv2.imshow("Real-Time QR Code Detection", frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except EOFError:
        logging.info("EOF signal (Ctrl+D) received. Exiting application...")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        # Cleanup resources
        if camera_handler:
            camera_handler.disconnect()
        logging.info("Camera connection closed.")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
