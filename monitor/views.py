from django.shortcuts import render
from django.http import JsonResponse
from . import mqtt_client
from .models import SensorData
import json

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
            response['devid'] = parsed.get("devid")
            response['volume'] = parsed.get("volume")
            response['umidade'] = parsed.get("umidade")
            response['temperatura'] = parsed.get("temperatura")
            response['profundidade'] = parsed.get("profundidade")
            response['timestamp'] = parsed.get("timestamp")
            return JsonResponse(response, status=200)
    except (json.JSONDecodeError, TypeError):
        pass  # Não é JSON, tentar CSV

    # Tentar parse como CSV
    try:
        # Limpa linhas vazias
        lines = [l for l in raw.splitlines() if l.strip()]
        if len(lines) > 0:
            first = lines[0].strip()
            if ',' in first:
                # Detecta se a primeira linha é cabeçalho
                header_lower = first.lower()
                if ('devid' in header_lower) or ('volume' in header_lower) or ('temperatura' in header_lower):
                    # Cabeçalho presente
                    if len(lines) >= 2:
                        headers = [h.strip() for h in first.split(',')]
                        values = [v.strip() for v in lines[1].split(',')]
                    else:
                        headers = []
                        values = []
                else:
                    # Sem cabeçalho — assumimos a ordem conhecida
                    headers = ['devid', 'volume', 'umidade', 'temperatura', 'profundidade', 'timestamp']
                    values = [v.strip() for v in first.split(',')]

                # Mapear valores para o dicionário de resposta
                if headers and values and len(headers) == len(values):
                    mapped = dict(zip(headers, values))
                    response['devid'] = mapped.get('devid')
                    # Para números, tentar converter para float quando aplicável
                    for key in ('volume', 'umidade', 'temperatura', 'profundidade'):
                        val = mapped.get(key)
                        if val is not None and val != '':
                            try:
                                response[key] = float(val)
                            except ValueError:
                                response[key] = val
                    response['timestamp'] = mapped.get('timestamp')
                    return JsonResponse(response, status=200)
    except Exception:
        pass  # Falha ao parsear CSV

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