import cv2
import sys
import asyncio

class CameraDevice():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            print('Failed to open default camera. Exiting...')
            sys.exit()
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    async def get_latest_frame(self):
        ret, frame = self.cap.read()
        await asyncio.sleep(0)
        return self.rotate(frame)

    def rotate(self, frame):
        return frame

    async def get_jpeg_frame(self):
        encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
        frame = await self.get_latest_frame()
        frame, encimg = cv2.imencode('.jpg', frame, encode_param)
        return encimg.tostring()

camera_device = CameraDevice()