python3 -m venv ~/venv649
source ~/venv649/bin/activate
pip install --upgrade pip
pip install bleak paho-mqtt
export MQTT_HOST=16.176.183.97
export MQTT_PORT=1883

sudo apt update
sudo apt install python3-pip -y
pip3 install paho-mqtt bleak
python3 -m pip show paho-mqtt
python3 -m pip show bleak
