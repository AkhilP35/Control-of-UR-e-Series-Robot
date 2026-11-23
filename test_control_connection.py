from rtde_control import RTDEControlInterface

ROBOT_IP = "192.168.1.10"

try:
    print("Connecting to UR7e RTDE Control...")

    robot = RTDEControlInterface(ROBOT_IP)

    print("\nControl connection successful!")

    robot.stopScript()

except Exception as e:
    print("Error:", e)