
from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface
import time

ROBOT_IP = "192.168.1.10"

# Conservative test movement
SPEED = 0.5          # rad/s
ACCELERATION = 0.1    # rad/s²
MOVEMENT = 0.2       # radians (approximately 0.57 degrees)

receive = None
control = None

try:
    print("Connecting to UR7e...")

    # Connect to robot feedback at 10 Hz
    receive = RTDEReceiveInterface(ROBOT_IP, 10.0)

    # Connect to robot control
    control = RTDEControlInterface(ROBOT_IP)

    print("Successfully connected!")

    # Read current joint positions
    current_joints = receive.getActualQ()

    print("\nCurrent joint positions:")
    for i, joint in enumerate(current_joints):
        print(f"Joint {i + 1}: {joint:.6f} rad")

    # Create a target with a tiny change to joint 6
    target_joints = current_joints.copy()
    target_joints[0] += MOVEMENT

    print("\nProposed movement:")
    print("Joint 6:", MOVEMENT, "radians")
    print("Speed:", SPEED, "rad/s")
    print("Acceleration:", ACCELERATION, "rad/s²")

    confirmation = input(
        "\nCheck the robot and its surroundings. "
        "Type MOVE to execute this movement: "
    )

    if confirmation == "MOVE":
        print("\nExecuting movement...")

        result = control.moveJ(
            target_joints,
            SPEED,
            ACCELERATION
        )

        print("Movement command completed:", result)

        print("\nNew joint positions:")
        print(receive.getActualQ())

    else:
        print("Movement cancelled.")

except Exception as e:
    print("\nError:", e)

finally:
    if control is not None:
        try:
            control.stopScript()
        except Exception as e:
            print("Control cleanup:", e)

    if receive is not None:
        try:
            receive.disconnect()
        except Exception:
            pass

    print("\nDisconnected from UR7e.")