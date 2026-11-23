
import socket
from pathlib import Path
import time

# Robot connection
HOST = "192.168.1.10" # The UR IP address
PORT = 30002 # UR secondary client

# Location of your existing Robotiq script
SCRIPT_PATH = Path("/Volumes/SSD/UR7e_Control/scripts/gripper.script")


def send_gripper_command(position, speed=50, force=50):

    # Check input values
    if not 0 <= position <= 100:
        raise ValueError("Position must be between 0 and 100")

    if not 0 <= speed <= 100:
        raise ValueError("Speed must be between 0 and 100")

    if not 0 <= force <= 100:
        raise ValueError("Force must be between 0 and 100")

    # Read your existing Robotiq function library
    script = SCRIPT_PATH.read_text()

    # Replace the hardcoded movement command with our Python inputs
    old_command = "rq_move_and_wait(58)"

    new_command = f"""
    rq_set_speed_norm({speed})
    rq_set_force_norm({force})
    rq_move_and_wait_norm({position})
    """

    if script.count(old_command) != 1:
        raise ValueError("Could not find the expected movement command in gripper.script")

    script = script.replace(old_command, new_command.strip())

    # Call the outer gripper function after its definition
    script = script.rstrip() + "\ngripper()\n"

    # Send the URScript to the robot
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        s.connect((HOST, PORT))
        s.sendall(script.encode("utf-8"))

    print(f"Gripper command sent: position={position}%, speed={speed}%, force={force}%")


def open_gripper(speed=50, force=50):
    send_gripper_command(0, speed, force)


def close_gripper(speed=50, force=50):
    send_gripper_command(100, speed, force)


def move_gripper(position, speed=50, force=50):
    send_gripper_command(position, speed, force)


if __name__ == "__main__":

    print("Robotiq Hand-E Python Controller")

    open_gripper()
