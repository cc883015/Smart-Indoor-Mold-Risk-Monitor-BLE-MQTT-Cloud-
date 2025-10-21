当然可以 ✅
下面是你可以直接上传到 **GitHub** 的 `README.md` 文件，
已完全去除所有姓名、学号、课程代码等个人敏感信息，
仅保留 **通用 IoT 工程项目描述（中英文双语版）**。

---

# 🌡️ Smart Indoor Environment Monitor (BLE ↔ MQTT ↔ Cloud)

A 3-tier IoT system that monitors indoor temperature and humidity using **Arduino**, **Raspberry Pi**, and **AWS EC2**, supporting **real-time alerts** and **remote control** via BLE and MQTT.

一个基于 **Arduino**、**树莓派** 和 **AWS EC2** 的三层物联网系统，用于监控室内温湿度，实现 **实时告警** 与 **远程控制**（BLE + MQTT）。

---

## 🧠 Project Overview / 项目概述

This project demonstrates how to combine **BLE (Bluetooth Low Energy)** for local device communication and **MQTT** for cloud-based IoT message exchange.

本项目展示了如何结合 **BLE 蓝牙低功耗通信** 与 **MQTT 云端通信协议**，构建一个完整的环境监控与控制系统。

---

## 🧩 System Architecture / 系统架构

### 🕹️ Tier 1 – Device Layer (Arduino Nano 33 IoT)

| Component    | Function                                      |
| ------------ | --------------------------------------------- |
| DHT11 Sensor | Measure temperature & humidity                |
| RGB LED      | Green = Normal, Red = Alert                   |
| Buzzer       | Beeps when alert triggered                    |
| BLE Service  | `sensorChar` (Notify) & `commandChar` (Write) |

Arduino reads temperature and humidity, determines environment status, and sends data via BLE to the Raspberry Pi. It can also receive remote commands to control the LED and buzzer.

Arduino 采集温湿度，判断环境状态并通过 BLE 发送数据到 Raspberry Pi，同时接收远程命令控制 LED 和蜂鸣器。

---

### 💻 Tier 2 – Network Layer (Raspberry Pi Gateway)

| Component        | Description                                                     |
| ---------------- | --------------------------------------------------------------- |
| **Python Bleak** | Connects to Arduino via BLE and listens for notifications       |
| **paho-mqtt**    | Publishes sensor data to MQTT broker and subscribes to commands |
| **MQTT Topics**  | `iot/room1/sensor` (data)  /  `iot/room1/cmd` (commands)        |

Flow:

1. Receive sensor data from Arduino (BLE Notify)
2. Publish to MQTT topic on AWS EC2
3. Listen for control commands and forward them back to Arduino

流程：

1. 从 Arduino 接收 BLE 通知
2. 发布到 AWS EC2 上的 MQTT 主题
3. 监听云端控制命令并通过 BLE 发送回 Arduino

---

### ☁️ Tier 3 – Cloud Layer (AWS EC2 + MQTT Dashboard)

| Component                     | Function                                      |
| ----------------------------- | --------------------------------------------- |
| AWS EC2 Broker                | Relays messages between devices and dashboard |
| MQTT Client (Dashboard / App) | Visualizes sensor data and sends commands     |

Users can subscribe to `sensor` topics to view real-time temperature and humidity, and publish commands to `cmd` topics to control the device.

用户可通过 Dashboard 订阅 `sensor` 主题查看实时数据，并通过 `cmd` 主题远程控制设备。

---

## ⚙️ How to Run / 运行方法

### 1️⃣ Arduino Setup

Upload the `.ino` sketch to the Arduino Nano 33 IoT.
Open Serial Monitor to confirm “BLE Ready”.

### 2️⃣ Raspberry Pi Setup

Install dependencies:

```bash
sudo apt install python3-pip
pip3 install paho-mqtt bleak asyncio
```

Run the bridge:

```bash
python3 bridge.py
```

Expected output:

```
[BLE] Connected to cc123  
[BLE → MQTT] {"temperature":25.2,"humidity":56.1,"status":"NORMAL"}
```

### 3️⃣ AWS EC2 Broker

Start Mosquitto:

```bash
sudo systemctl start mosquitto
```

Connect using your MQTT client (e.g. MyMQTT, MQTT Explorer):

| Setting         | Value              |
| --------------- | ------------------ |
| Host            | EC2 Public IP      |
| Port            | 1883               |
| Subscribe Topic | `iot/room1/sensor` |
| Publish Topic   | `iot/room1/cmd`    |

---

## 🔄 Communication Flow / 通信流程

### Upstream (数据上传)

```
Arduino → BLE → Raspberry Pi → MQTT → AWS → Dashboard
```

### Downstream (命令下发)

```
Dashboard → MQTT → AWS → Raspberry Pi → BLE → Arduino
```

---

## 📊 Example JSON Data

```json
{
  "temperature": 18.7,
  "humidity": 74.5,
  "status": "ALERT"
}
```

---

## 🌍 Project Significance / 项目意义

* Demonstrates integration of BLE and MQTT in a multi-tier IoT architecture.
* Enables real-time monitoring of environmental conditions and remote control of edge devices.
* Useful for smart homes, hotels, or laboratory environments to prevent mold growth.

展示了 BLE 与 MQTT 在三层 IoT 体系结构中的结合，支持实时监测与远程控制，适用于酒店、实验室或家庭防潮防霉等场景。

---

## 🧰 Technologies Used / 技术栈

* **Hardware:** Arduino Nano 33 IoT, Raspberry Pi 4, DHT11 Sensor
* **Protocols:** BLE, MQTT, JSON
* **Languages:** C++ (Arduino), Python (Raspberry Pi)
* **Cloud:** AWS EC2 (Mosquitto Broker)

---

## 📘 Keywords

`IoT`  `BLE`  `MQTT`  `Raspberry Pi`  `Arduino Nano 33 IoT`
`AWS EC2`  `Smart Environment`  `Sensor Monitoring`  `Python Bleak`  `paho-mqtt`

---

⭐ **Tagline**

> “An IoT bridge connecting Arduino, Raspberry Pi, and the Cloud for real-time environmental monitoring.”

> “一个连接 Arduino、树莓派与云端的物联网网关，用于实时环境监控。”

---

是否希望我帮你在这份 README 中自动生成一张简洁的系统结构图（Mermaid 代码或嵌图形式）以便在 GitHub 渲染？
那样你的仓库会更专业（像一个真正的开源 IoT 项目）。
