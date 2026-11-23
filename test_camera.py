"""Live wrist-camera preview + capture of images with the robot pose.

Modes:

  manual (default)  Live video window. Move the robot yourself (freedrive or
                    jog on the pendant). Click the video window, then press
                    SPACE to capture, q or Esc to quit.

  waypoints         Robot moves through joint configurations from a JSON file
                    (list of 6-joint lists in radians, or a previous
                    poses.json), stops, settles, then captures automatically.
                    The video freezes during each move. Press q/Esc in the
                    window between waypoints to stop.

Usage:
  python capture_loop.py --ip 192.168.1.10
  python capture_loop.py --ip 192.168.1.10 --waypoints captures/session_X/poses.json

Needs:  pip install ur_rtde opencv-python
Waypoint mode needs the robot in Remote Control mode on the pendant.
"""
import argparse
import json
import math
import time
from pathlib import Path

import cv2
from rtde_receive import RTDEReceiveInterface

CAM_INDEX = 0
W, H = 2592, 1944
SETTLE_S = 0.5            # wait after the robot stops, before capturing
DRAIN_FRAMES = 6          # discard buffered frames so the saved one is current
MAX_LIN_SPEED = 0.005     # m/s: refuse to capture if the TCP moves faster
MAX_ANG_SPEED = 0.02      # rad/s
REFUSE_WHEN_MOVING = False  # True = refuse to capture while the robot moves
WINDOW = "Wrist camera (SPACE = capture, q = quit)"


def open_camera():
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
    if not cap.isOpened():
        raise SystemExit("Could not open camera. Check CAM_INDEX and camera permission.")
    for _ in range(30):  # warm-up: exposure settles
        cap.read()
    return cap


def sharpness(frame):
    h, w = frame.shape[:2]
    centre = frame[h // 3: 2 * h // 3, w // 3: 2 * w // 3]
    return cv2.Laplacian(cv2.cvtColor(centre, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()


def tcp_speeds(rtde_r):
    v = rtde_r.getActualTCPSpeed()  # vx,vy,vz,wx,wy,wz
    return math.sqrt(sum(x * x for x in v[:3])), math.sqrt(sum(x * x for x in v[3:]))


def show(frame, status):
    h, w = frame.shape[:2]
    view = cv2.resize(frame, (960, int(h * 960 / w)))
    vh, vw = view.shape[:2]
    cv2.line(view, (vw // 2 - 20, vh // 2), (vw // 2 + 20, vh // 2), (0, 255, 0), 1)
    cv2.line(view, (vw // 2, vh // 2 - 20), (vw // 2, vh // 2 + 20), (0, 255, 0), 1)
    cv2.putText(view, status, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow(WINDOW, view)


def grab_fresh(cap):
    for _ in range(DRAIN_FRAMES):
        cap.read()
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Camera read failed")
    return frame


def save_sample(cap, rtde_r, out_dir, records, force=False, frame=None):
    """Save an image and the robot pose.

    If `frame` is given (manual mode), that exact frame from the live feed is
    saved. Otherwise (waypoint mode) wait for the robot to settle and grab a
    fresh frame.
    """
    lin, ang = tcp_speeds(rtde_r)
    moving = lin > MAX_LIN_SPEED or ang > MAX_ANG_SPEED
    if moving and not force:
        if REFUSE_WHEN_MOVING:
            print("Robot still moving, hold still and try again.")
            return False
        print("Warning: robot was moving; image may be blurred or pose slightly off.")
    if frame is None:
        time.sleep(SETTLE_S)
        frame = grab_fresh(cap)
    idx = len(records)
    record = {
        "index": idx,
        "image": f"img_{idx:03d}.png",
        "tcp_pose": list(rtde_r.getActualTCPPose()),  # x,y,z,rx,ry,rz (m, rotvec rad)
        "q": list(rtde_r.getActualQ()),               # joint angles (rad)
        "timestamp": time.time(),
    }
    cv2.imwrite(str(out_dir / record["image"]), frame)
    records.append(record)
    (out_dir / "poses.json").write_text(json.dumps(records, indent=2))
    print(f"[{idx:03d}] saved {record['image']}  sharpness={sharpness(frame):.0f}")
    return True


def load_waypoints(path):
    data = json.loads(Path(path).read_text())
    return [p["q"] if isinstance(p, dict) else p for p in data]


def run_manual(cap, rtde_r, out_dir, records):
    print("Manual mode: click the video window, SPACE = capture, q/Esc = quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Frame read failed")
            break
        lin, ang = tcp_speeds(rtde_r)
        moving = lin > MAX_LIN_SPEED or ang > MAX_ANG_SPEED
        show(frame, f"saved {len(records)}  sharp {sharpness(frame):.0f}  "
                    f"{'MOVING' if moving else 'steady'}")
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord(" "):
            save_sample(cap, rtde_r, out_dir, records, frame=frame)


def run_waypoints(cap, rtde_r, args, out_dir, records):
    from rtde_control import RTDEControlInterface
    rtde_c = RTDEControlInterface(args.ip)
    waypoints = load_waypoints(args.waypoints)
    print(f"{len(waypoints)} waypoints. Keep the e-stop within reach.")
    try:
        for q in waypoints:
            rtde_c.moveJ(q, args.speed, args.accel)  # blocks until the move ends
            time.sleep(SETTLE_S)
            save_sample(cap, rtde_r, out_dir, records, force=True)
            frame = grab_fresh(cap)
            show(frame, f"saved {len(records)}/{len(waypoints)}  (q = stop)")
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                print("Stopped by user.")
                break
    finally:
        rtde_c.stopScript()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", default="192.168.1.10")
    ap.add_argument("--waypoints", help="JSON file of joint configs (rad)")
    ap.add_argument("--speed", type=float, default=0.3, help="rad/s")
    ap.add_argument("--accel", type=float, default=0.3, help="rad/s^2")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out_dir = Path(args.out or f"captures/session_{time.strftime('%Y%m%d_%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving to {out_dir}")

    rtde_r = RTDEReceiveInterface(args.ip)
    cap = open_camera()
    records = []
    try:
        if args.waypoints:
            run_waypoints(cap, rtde_r, args, out_dir, records)
        else:
            run_manual(cap, rtde_r, out_dir, records)
    finally:
        cap.release()
        cv2.destroyAllWindows()
    print(f"Done: {len(records)} samples in {out_dir}")


if __name__ == "__main__":
    main()