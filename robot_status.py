
from rtde_receive import RTDEReceiveInterface
import math
import time

ROBOT_IP = "192.168.1.10"

def main():

    robot = None

    try:
        print("Connecting to UR7e...")

        robot = RTDEReceiveInterface(ROBOT_IP)

        print("Successfully connected!\n")

        while True:

            # Read joint positions
            joints = robot.getActualQ()

            # Read TCP position
            tcp = robot.getActualTCPPose()

            print("\033[2J\033[H", end="")

            print("================================")
            print("       UR7e ROBOT MONITOR")
            print("================================")

            print("\nJOINT POSITIONS")

            for i, angle in enumerate(joints):
                degrees = math.degrees(angle)
                print(f"Joint {i+1}: {degrees:8.2f} degrees")

            print("\nTOOL CENTRE POINT (TCP)")

            print(f"X:  {tcp[0]:.4f} m")
            print(f"Y:  {tcp[1]:.4f} m")
            print(f"Z:  {tcp[2]:.4f} m")

            print("\nTCP ORIENTATION (Rotation vector)")

            print(f"RX: {tcp[3]:.4f}")
            print(f"RY: {tcp[4]:.4f}")
            print(f"RZ: {tcp[5]:.4f}")

            print("\nPress Ctrl+C to stop monitoring")

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

    except Exception as e:
        print("\nError:", e)

    finally:
        if robot is not None:
            robot.disconnect()
            print("Disconnected from robot.")


if __name__ == "__main__":
    main()
