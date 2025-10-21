import asyncio
import json
import paho.mqtt.client as mqtt
from bleak import BleakClient, BleakScanner

# MQTT 和 BLE 的基本配置
MQTT_BROKER = "13.211.78.96"  # 我的 EC2 服务器 IP
MQTT_PORT = 1883
TOPIC_SENSOR = "hotel/room1/sensor"  # 传感器数据主题
TOPIC_CMD = "hotel/room1/cmd"        # 控制命令主题

# 和 Arduino 上的一样
BLE_NAME = "cc123"
SERVICE_UUID = "f75cfb20-4bce-4d2a-a9a7-3d9a93e0e2f5"
SENSOR_CHAR_UUID = "f75cfb21-4bce-4d2a-a9a7-3d9a93e0e2f5"
COMMAND_CHAR_UUID = "f75cfb22-4bce-4d2a-a9a7-3d9a93e0e2f5"

# 当 MQTT 成功连接时触发
def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    client.subscribe(TOPIC_CMD)

# 当 MQTT 收到消息时触发
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"[MQTT → BLE] Received command: {payload}")
        asyncio.run_coroutine_threadsafe(send_ble_command(payload), loop)
    except Exception as e:
        print("MQTT message error:", e)

# 创建 MQTT 客户端并连接服务器
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# BLE 部分
ble_client = None  # 全局 BLE 客户端

# 扫描并连接 Arduino 设备
async def connect_ble():
    print("[BLE] Scanning nearby devices...")
    devices = await BleakScanner.discover(timeout=8)
    found_names = [d.name for d in devices if d.name]
    print(f"[BLE] Found devices: {found_names}")

    # 查找目标设备
    device = next((d for d in devices if d.name == BLE_NAME), None)
    if not device:
        print(f"[BLE] '{BLE_NAME}' not found. Make sure Arduino is powered and advertising.")
        return None

    # 连接设备
    print(f"[BLE] Connecting to {BLE_NAME}...")
    client = BleakClient(device, timeout=20)
    await client.connect()
    print(f"[BLE] Connected to {BLE_NAME}")

    # 开启传感器通知
    await client.start_notify(SENSOR_CHAR_UUID, ble_notify_handler)
    return client

# 当 Arduino 发送新的传感器数据时触发
async def ble_notify_handler(sender, data):
    try:
        msg = data.decode("utf-8")
        print(f"[BLE → MQTT] {msg}")
        mqtt_client.publish(TOPIC_SENSOR, msg)
    except Exception as e:
        print("BLE notify error:", e)

# 向 Arduino 发送控制命令
async def send_ble_command(payload: str):
    global ble_client
    if ble_client and ble_client.is_connected:
        await ble_client.write_gatt_char(COMMAND_CHAR_UUID, payload.encode())
        print(f"[BLE] Command sent: {payload}")
    else:
        print("[BLE] Not connected. Command skipped.")

# 主循环，不断保持 BLE 连接
async def main():
    global ble_client
    while True:
        try:
            ble_client = await connect_ble()
            if ble_client:
                while ble_client.is_connected:
                    await asyncio.sleep(1)
            else:
                print("[BLE] Retry in 10 seconds...")
                await asyncio.sleep(10)
        except Exception as e:
            print(f"[BLE] Error: {e}")
            print("[BLE] Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

# 程序主入口
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    mqtt_client.loop_start()

    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n[EXIT] User stopped the program.")
    finally:
        if ble_client and ble_client.is_connected:
            asyncio.run(ble_client.disconnect())
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("[CLEAN EXIT] Disconnected from BLE and MQTT.")
