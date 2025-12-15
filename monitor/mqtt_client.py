import paho.mqtt.client as mqtt
from .models import SensorData
import json

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
            SensorData.objects.create(
                devid=parsed.get("devid"),
                volume=parsed.get("volume"),
                umidade=parsed.get("umidade"),
                temperatura=parsed.get("temperatura"),
                profundidade=parsed.get("profundidade"),
                timestamp=parsed.get("timestamp"),
                raw_message=raw
            )
            print("Salvo JSON no banco")
            return
    except (json.JSONDecodeError, TypeError):
        pass

    # Tentar parse como CSV
    try:
        lines = [l for l in raw.splitlines() if l.strip()]
        if len(lines) > 0:
            first = lines[0].strip()
            if ',' in first:
                header_lower = first.lower()
                if ('devid' in header_lower) or ('volume' in header_lower) or ('temperatura' in header_lower):
                    if len(lines) >= 2:
                        headers = [h.strip() for h in first.split(',')]
                        values = [v.strip() for v in lines[1].split(',')]
                else:
                    headers = ['devid', 'volume', 'umidade', 'temperatura', 'profundidade', 'timestamp']
                    values = [v.strip() for v in first.split(',')]

                if headers and values and len(headers) == len(values):
                    mapped = dict(zip(headers, values))
                    SensorData.objects.create(
                        devid=mapped.get('devid'),
                        volume=float(mapped.get('volume')) if mapped.get('volume') else None,
                        umidade=float(mapped.get('umidade')) if mapped.get('umidade') else None,
                        temperatura=float(mapped.get('temperatura')) if mapped.get('temperatura') else None,
                        profundidade=float(mapped.get('profundidade')) if mapped.get('profundidade') else None,
                        timestamp=mapped.get('timestamp'),
                        raw_message=raw
                    )
                    print("Salvo CSV no banco")
    except Exception as e:
        print("Erro ao salvar:", e)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_start()