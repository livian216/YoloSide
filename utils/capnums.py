import cv2


class Camera:
    def __init__(self, cam_preset_num=5):
        self.cam_preset_num = cam_preset_num

    def get_cam_num(self):
        cnt = 0
        devices = []
        for device in range(0, self.cam_preset_num):
            stream = cv2.VideoCapture(device, cv2.CAP_DSHOW)
            opened = stream.isOpened()
            if not opened:
                stream.release()
                print(f"[capnums] device {device}: not opened", flush=True)
                continue
            # Use read() instead of grab() — more reliable:
            # some virtual/fake devices pass grab() but fail to
            # retrieve an actual frame.
            grabbed, frame = stream.read()
            stream.release()
            if not grabbed or frame is None:
                print(f"[capnums] device {device}: opened={opened} grabbed={grabbed} frame={'None' if frame is None else f'shape={frame.shape}'} → SKIP", flush=True)
                continue
            cnt = cnt + 1
            devices.append(device)
            print(f"[capnums] device {device}: opened={opened} frame_shape={frame.shape} → ACCEPT", flush=True)
        print(f"[capnums] total: {cnt} camera(s): {devices}", flush=True)
        return cnt, devices


if __name__ == '__main__':
    cam = Camera()
    cam_num, devices = cam.get_cam_num()
    print(cam_num, devices)
