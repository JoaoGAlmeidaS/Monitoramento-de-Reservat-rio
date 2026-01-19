import paho.mqtt.client as mqtt
from .models import SensorData
import json
from datetime import datetime
from django.utils import timezone

last_message = ""  # dado recebido mais recente

def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker!")
    client.subscribe("esp32/sensor/reservatorio")

def on_message(client, userdata, msg):
    global last_message
    last_message = msg.payload.decode()
    print("Mensagem recebida:", last_message)

    # Tentar salvar no banco se for válido
    save_to_db(last_message)

def save_to_db(raw):
    if not raw or not isinstance(raw, str):
        return

    # Tentar parse como JSON primeiro
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            dados_internos = parsed.get("data", {})

            SensorData.objects.create(
                devid=parsed.get("devid"),

                volume=dados_internos.get("adc"),
                umidade=dados_internos.get("var0"),
                temperatura=float(dados_internos.get("var1")),
                profundidade=dados_internos.get("adc"),
                timestamp=dados_internos.get("timestamp"),
                raw_message=raw
            )
            print("Salvo JSON no banco")
            return
    except (json.JSONDecodeError, TypeError):
        pass

    # Tentar parse como CSV
    try:
        first = raw.strip()

        if ';' in first:
            parts = [p.strip() for p in first.split(';')]

            if len(parts) == 3:
                unix_ts, nivel, volume = parts

                timestamp = timezone.make_aware(
                    datetime.fromtimestamp(int(unix_ts)),
                    timezone.get_current_timezone()
                )

                SensorData.objects.create(
                    devid=None,
                    volume= float(volume),
                    umidade= None,
                    temperatura= None,
                    profundidade= float(nivel),
                    timestamp= timestamp,
                    raw_message= raw
                )
                print("Salvo CSV no banco")
                return
    except Exception as e:
        print("Erro ao salvar CSV:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()