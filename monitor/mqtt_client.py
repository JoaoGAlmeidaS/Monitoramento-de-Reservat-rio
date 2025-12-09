import paho.mqtt.client as mqtt

last_message = ""  # dado recebido mais recente

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker!")
    client.subscribe("esp32/sensor/reservatorio")

def on_message(client, userdata, msg):
    global last_message
    last_message = msg.payload.decode()
    print("Mensagem recebida:", last_message)
    

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()