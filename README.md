# UR7e Robot Control

A collection of Python scripts, configuration files and documentation for connecting to, monitoring and controlling Universal Robots UR7e robotic arms using a Mac.

The project uses a direct Ethernet connection between the robot controller and a MacBook, with Python libraries such as `ur-rtde` for communication and control.

This repository is intended to serve two purposes:

- Store the code and resources developed for the robot.
- Provide a step-by-step guide so that the connection and control setup can be reproduced on another computer.

---

# 1. Direct Ethernet Connection: UR7e to Mac

## 1.1 Overview

The first step is to establish a direct Ethernet connection between the Universal Robots UR7e controller and the Mac.

This allows the Mac to communicate with the robot over a local network without requiring an internet connection or an external network router.

The connection is used for:
- Communicating with the robot controller.
- Reading joint positions and TCP coordinates.
- Sending movement commands.
- Running Python scripts through the RTDE interface.
- Integrating external applications, such as computer vision systems.

### Hardware required

- Universal Robots UR7e robotic arm and control box.
- MacBook (tested on a 2020 M1 MacBook Air).
- Ethernet cable.
- USB-C to Ethernet adapter (if the Mac does not have an Ethernet port).

**Tested Ethernet adapter:** AX88179A USB 3.0 to Gigabit Ethernet.

### Network configuration

The following static IP addresses were used for this setup:

| Device | Network interface | IP address |
|---|---|---|
| UR7e robot | Ethernet | `192.168.1.10` |
| MacBook | AX88179A Ethernet (`en8`) | `192.168.1.20` |
| Both devices | Subnet mask | `255.255.255.0` |

The two devices must be on the same subnet so they can communicate directly.

> **Important:** These are the IP addresses used in this project. If you are connecting to a different robot or using a different network, check the existing configuration before assigning addresses. Each device must have a unique IP address.

---

## 1.2 Physical connection

1. Ensure the robot is in a safe state before connecting any equipment.
2. Connect one end of the Ethernet cable to the Ethernet port on the UR control box.
3. Connect the other end to the USB-C Ethernet adapter.
4. Connect the adapter to the Mac.
5. Allow macOS a few seconds to recognise the Ethernet adapter.

The physical connection should look like:

`UR7e Control Box → Ethernet Cable → USB-C Ethernet Adapter → MacBook`

The Mac can remain connected to Wi-Fi. Wi-Fi and the robot's direct Ethernet connection are separate network connections. However, check that macOS is routing traffic to the robot through the Ethernet interface.

---

## 1.3 Configure the robot's IP address

The robot needs a static IP address so that the Mac can consistently connect to it.

On the UR teach pendant:

1. Open the robot's Settings.
2. Navigate to the network configuration settings.
3. Select the Ethernet interface.
4. Configure the IPv4 settings manually.
5. Use the following values:

| Setting | Value |
|---|---|
| IP address | `192.168.1.10` |
| Subnet mask | `255.255.255.0` |
| Default gateway | Leave blank if not required |
| DNS server | Leave blank if not required |

6. Apply the settings and check that the robot displays the correct IP address.

**Note:** The robot's network settings may already be configured. Check the existing settings before changing them.

---

## 1.4 Identify the Mac's Ethernet interface

Before configuring the Mac, identify which network interface corresponds to the USB-C Ethernet adapter.

Open Terminal and run:

```bash
networksetup -listallhardwareports
```

This lists the network hardware recognised by macOS.

Look for an entry similar to:

```text
Hardware Port: AX88179A
Device: en8
Ethernet Address: ...
```

In this setup:

- `AX88179A` is the Ethernet adapter.
- `en8` is the corresponding macOS network interface.

**Important:** Your Mac may assign a different interface name, such as `en5` or `en7`. Always check the output rather than assuming it is `en8`.

You can also list the available network services:

```bash
networksetup -listallnetworkservices
```

---

## 1.5 Configure a static IP address on macOS

The Mac needs a static IP address in the same subnet as the robot.

The robot uses:

```text
192.168.1.10
```

Therefore, the Mac will use:

```text
192.168.1.20
```

### Method A: macOS System Settings (recommended)

1. Open **System Settings**.
2. Select **Network**.
3. Select the USB-C Ethernet adapter (AX88179A).
4. Click **Details**.
5. Open the **TCP/IP** section.
6. Change **Configure IPv4** to **Manually**.
7. Enter the following:

| Setting | Value |
|---|---|
| IP address | `192.168.1.20` |
| Subnet mask | `255.255.255.0` |
| Router | Leave blank |

8. Click **OK** or **Apply** to save the changes.

The Mac should now have a static Ethernet address of `192.168.1.20`.

### Method B: Terminal

If you prefer using Terminal, you can configure the network service using:

```bash
sudo networksetup -setmanual "AX88179A" 192.168.1.20 255.255.255.0
```

Replace `AX88179A` with the exact network service name shown by:

```bash
networksetup -listallnetworkservices
```

You may be prompted to enter your Mac's administrator password.

---

## 1.6 Verify the Mac's Ethernet configuration

Open Terminal and run:

```bash
ifconfig en8
```

Look for an IPv4 address similar to:

```text
inet 192.168.1.20 netmask 0xffffff00 broadcast 192.168.1.255
```

This confirms that the Ethernet interface has the expected IP address.

If you see a different address, or no `inet` entry, the interface may not have been configured correctly.

### Troubleshooting: IP address not appearing

During the initial setup, macOS reported the correct address in Network Settings, but `ifconfig en8` did not show an IPv4 address.

If this happens, you can try manually assigning the address to the interface:

```bash
sudo ifconfig en8 down
sudo ifconfig en8 up
sudo ifconfig en8 inet 192.168.1.20 netmask 255.255.255.0
```

Then check again:

```bash
ifconfig en8
```

**Important:** This `ifconfig` method manually assigns the address to the active interface. It may not persist after disconnecting the adapter or restarting the Mac. Use the macOS Network Settings configuration for the normal, persistent setup.

---

## 1.7 Check the network route

If Wi-Fi is also enabled, check that macOS is sending traffic to the robot through the correct Ethernet interface.

Run:

```bash
route get 192.168.1.10
```

Look for:

```text
interface: en8
```

The interface should match the Ethernet adapter identified earlier.

If the route uses Wi-Fi instead, macOS is not sending the robot traffic through the intended connection. Check the Ethernet IP configuration and network routing before proceeding.

---

## 1.8 Test communication with the robot

Once both devices have their IP addresses configured, test whether they can communicate.

In Terminal, run:

```bash
ping 192.168.1.10
```

A successful connection should produce output similar to:

```text
64 bytes from 192.168.1.10: icmp_seq=0 ttl=64 time=1.208 ms
64 bytes from 192.168.1.10: icmp_seq=1 ttl=64 time=1.150 ms
64 bytes from 192.168.1.10: icmp_seq=2 ttl=64 time=1.180 ms
```

To stop the ping test, press:

```text
Control + C
```

A successful result should show:

```text
5 packets transmitted, 5 packets received, 0.0% packet loss
```

This confirms that the Mac can communicate with the robot over the network.

---

## 1.9 Check the robot communication ports

The UR controller provides several communication interfaces over TCP/IP.

For this project, two particularly important ports are:

| Port | Interface | Purpose |
|---|---|---|
| `29999` | Dashboard Server | Communicating with the robot controller and accessing dashboard commands |
| `30004` | RTDE | Exchanging robot data with external applications |

Check that the ports are reachable from the Mac.

### Test Dashboard Server (29999)

```bash
nc -vz -G 3 192.168.1.10 29999
```

Expected output:

```text
Connection to 192.168.1.10 port 29999 [tcp/*] succeeded!
```

### Test RTDE (30004)

```bash
nc -vz -G 3 192.168.1.10 30004
```

Expected output:

```text
Connection to 192.168.1.10 port 30004 [tcp/*] succeeded!
```

If both connections succeed, the Mac can reach the robot's Dashboard Server and RTDE interfaces.

A successful port test confirms network connectivity to the service. It does not, by itself, confirm that a Python control command will execute successfully.

---

## 1.10 Troubleshooting

| Problem | Possible cause | What to check |
|---|---|---|
| Ethernet adapter not appearing | Adapter not recognised | Reconnect the USB-C adapter and run `networksetup -listallhardwareports` |
| No IPv4 address on `en8` | Static address not applied | Check macOS Network Settings and run `ifconfig en8` |
| Ping fails | Incorrect IP or subnet | Check both devices' IP addresses and subnet masks |
| Ping works but Python cannot connect | Communication service unavailable or disabled | Check the relevant robot service and TCP port |
| Port 29999 fails | Dashboard Server unavailable or disabled | Check the robot's security/service settings |
| Port 30004 fails | RTDE unavailable or disabled | Check RTDE service settings |
| Route uses Wi-Fi | macOS routing issue | Run `route get 192.168.1.10` and check the interface |
| Connection stops after reconnecting | Manually assigned IP may have been lost | Recheck `ifconfig` and configure the address persistently in System Settings |

### Robot service settings

On PolyScope 5, communication interfaces may need to be enabled in the robot's security/service settings.

Check the relevant services for:

- Dashboard Server.
- Real-Time Data Exchange (RTDE).

The exact settings and availability depend on the PolyScope software version and controller configuration.

For this project, the robot was running:

```text
URSoftware 5.25.2.130406
```

The robot was also switched to **Remote Control** mode when preparing for remote control using Python.

---

## 1.11 Successful connection checklist

Before moving on to Python setup, check the following:

- [ ] Ethernet cable connected between the robot and Mac.
- [ ] Mac recognises the USB-C Ethernet adapter.
- [ ] Robot IP address is `192.168.1.10`.
- [ ] Mac Ethernet IP address is `192.168.1.20`.
- [ ] Both devices use subnet mask `255.255.255.0`.
- [ ] `ifconfig en8` shows the correct IPv4 address.
- [ ] `route get 192.168.1.10` uses the Ethernet interface.
- [ ] `ping 192.168.1.10` succeeds.
- [ ] TCP port `29999` is reachable.
- [ ] TCP port `30004` is reachable.

Once these checks pass, the direct Ethernet connection is established and the Mac is ready for the software setup.

---

## References

- [Universal Robots UR7e User Manual](https://www.universal-robots.com/manuals/EN/PDF/SW5_25/user-manual-UR7e-PDF_online/733-466-00_UR7e_User_Manual_en_Global.pdf)
- [Universal Robots: Overview of Client Interfaces](https://www.universal-robots.com/articles/ur/interface-communication/overview-of-client-interfaces/)
- [Universal Robots: RTDE Guide](https://docs.universal-robots.com/tutorials/communication-protocol-tutorials/rtde-guide.html)
- [Universal Robots: Dashboard Server](https://www.universal-robots.com/articles/ur/dashboard-server-e-series-port-29999/)

---

**Safety notice:** This guide covers network connectivity only. Establishing an Ethernet connection does not make the robot safe to move. Before sending movement commands, follow the laboratory's risk assessment, operating procedures and safety requirements. Ensure the workspace is clear and that the robot is under appropriate supervision.
