from django.shortcuts import render
from django.http import JsonResponse
from . import mqtt_client
from .models import SensorData
import json
from datetime import datetime
from django.utils import timezone

# Create your views here.
def monitor_view(request):
    raw = mqtt_client.last_message

    # Default response structure (todos os campos começam como None para não quebrar)
    response = {
        "raw_message": raw,
        "devid": None,
        "volume": None,
        "umidade": None,
        "temperatura": None,
        "profundidade": None,
        "timestamp": None,
        "error": None,
    }

    if not raw or not isinstance(raw, str):
        response["error"] = "Formato Inválido"
        return JsonResponse(response, status=200)

    # Tentar parse como JSON primeiro
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            dados_internos = parsed.get("data", {})

            response['devid'] = parsed.get("devid")

            response['volume'] = dados_internos.get("adc")
            response['umidade'] = dados_internos.get("var0")
            response['temperatura'] = dados_internos.get("var1")
            response['profundidade'] = dados_internos.get("adc")
            response['timestamp'] = dados_internos.get("timestamp")
            return JsonResponse(response, status=200)
    except (json.JSONDecodeError, TypeError):
        pass  # Não é JSON, tentar CSV

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

                response['timestamp'] = timestamp
                response['profundidade'] = float(nivel)
                response['volume'] = float(volume)

                return JsonResponse(response, status=200)
    except Exception:
        pass

    # Se chegou aqui, não é JSON nem CSV válido
    response["error"] = "Formato Inválido"
    return JsonResponse(response, status=200)


def home(request):
    return render(request, "home.html", {
        "mensagem": mqtt_client.last_message
    })


def data_view(request):
    data = list(SensorData.objects.all().order_by('-id').values(
        'id', 'devid', 'volume', 'umidade', 'temperatura', 'profundidade', 'timestamp', 'raw_message', 'created_at'
    ))
    return JsonResponse(data, safe=False)