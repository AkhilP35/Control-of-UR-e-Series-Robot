import socket

ROBOT_IP = "192.168.1.10"
PORT = 29999

try:
    with socket.create_connection((ROBOT_IP, PORT), timeout=5) as robot:

        print("Connected to Dashboard Server")

        greeting = robot.recv(1024).decode()
        print("Robot greeting:", greeting)

        robot.sendall(b"PolyscopeVersion\n")

        response = robot.recv(1024).decode()
        print("PolyScope version:", response)

        robot.sendall(b"robotmode\n")

        response = robot.recv(1024).decode()
        print("Robot mode:", response)

except Exception as e:
    print("Error:", e)