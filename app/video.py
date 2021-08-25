from aiortc.mediastreams import VideoStreamTrack
import cv2
import sys
from av import VideoFrame


class CameraDevice():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            print('Failed to open default camera. Exiting...')
            sys.exit()
        self.cap.set(3, 640)
        self.cap.set(4, 360)

    def get_latest_frame(self):
        ret, frame = self.cap.read()
        return frame

    def get_jpeg_frame(self):
        encode_param = (cv2.IMWRITE_JPEG_QUALITY, 90)
        frame = self.get_latest_frame()
        ret, encimg = cv2.imencode('.jpg', frame, encode_param)
        return encimg.tostring()


class RTCVideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.camera_device = CameraDevice()
        self.data_bgr = None

    async def recv(self):
        self.data_bgr = self.camera_device.get_latest_frame()
        frame = VideoFrame.from_ndarray(self.data_bgr, format='bgr24')
        pts, time_base = await self.next_timestamp()
        frame.pts = pts
        frame.time_base = time_base
        return frame

