from rtde_receive import RTDEReceiveInterface

ROBOT_IP = "192.168.1.10"

try:
    print("Connecting to UR7e RTDE Receive...")

    robot = RTDEReceiveInterface(ROBOT_IP, 10.0)

    print("\nConnection successful!")

    print("Joint positions:", robot.getActualQ())
    print("TCP position:", robot.getActualTCPPose())

    robot.disconnect()

except Exception as e:
    print("Error:", e)