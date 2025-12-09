from django.shortcuts import render
from django.http import JsonResponse
from . import mqtt_client
import json

# Create your views here.
def monitor_view(request):
    raw = mqtt_client.last_message
    parsed = None
    try:
        parsed = json.loads(raw) if raw else None
    except Exception:
        parsed = None

    response = {
        "raw_message": raw,
        "devid": parsed.get("devid") if isinstance(parsed, dict) else None,
        "volume": parsed.get("volume") if isinstance(parsed, dict) else None,
        "umidade": parsed.get("umidade") if isinstance(parsed, dict) else None,
        "temperatura": parsed.get("temperatura") if isinstance(parsed, dict) else None,
        "profundidade": parsed.get("profundidade") if isinstance(parsed, dict) else None,
        "timestamp": parsed.get("timestamp") if isinstance(parsed, dict) else None,
    }

    return JsonResponse(response, status=200)


def home(request):
    return render(request, "home.html", {
        "mensagem": mqtt_client.last_message
    })