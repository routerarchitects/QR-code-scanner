import cv2
from pyzbar.pyzbar import decode

class QRCodeReader:
    @staticmethod
    def detect_qr_code(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        qr_codes = decode(gray)
        results = [qr.data.decode("utf-8") for qr in qr_codes]
        return results

