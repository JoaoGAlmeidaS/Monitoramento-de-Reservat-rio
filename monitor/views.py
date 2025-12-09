from django.shortcuts import render
from django.http import JsonResponse
from . import mqtt_client
import json

# Create your views here.
def monitor_view(request):
    raw = mqtt_client.last_message

    # ---------------------------------------------------------------------------------
    # JSON parsing
    # O código abaixo é para ser utilizado caso a String venha no formato JSON
    # 
    #
    # try:
    #     parsed = json.loads(raw) if raw else None
    # except Exception:
    #     parsed = None
    #
    # response = {
    #     "raw_message": raw,
    #     "devid": parsed.get("devid") if isinstance(parsed, dict) else None,
    #     "volume": parsed.get("volume") if isinstance(parsed, dict) else None,
    #     "umidade": parsed.get("umidade") if isinstance(parsed, dict) else None,
    #     "temperatura": parsed.get("temperatura") if isinstance(parsed, dict) else None,
    #     "profundidade": parsed.get("profundidade") if isinstance(parsed, dict) else None,
    #     "timestamp": parsed.get("timestamp") if isinstance(parsed, dict) else None,
    # }
    # ---------------------------------------------------------------------------------

    # Default response structure (todos os campos começam como None para não quebrar)
    response = {
        "raw_message": raw,
        "devid": None,
        "volume": None,
        "umidade": None,
        "temperatura": None,
        "profundidade": None,
        "timestamp": None,
    }

    # Se houver uma mensagem, tentar parse CSV
    if raw and isinstance(raw, str):
        try:
            # Limpa linhas vazias
            lines = [l for l in raw.splitlines() if l.strip()]
            if len(lines) > 0:
                # Suporta dois formatos:
                # 1) Com cabeçalho, duas linhas: header\ndata
                # 2) Apenas linha de dados: devid,volume,umidade,temperatura,profundidade,timestamp
                first = lines[0].strip()

                if ',' in first:
                    # Detecta se a primeira linha é cabeçalho (contém palavras como 'devid' ou 'volume')
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
                    if headers and values:
                        mapped = dict(zip(headers, values))
                        # Atribuir apenas se a chave existir
                        response['devid'] = mapped.get('devid')
                        # Para números, tentar converter para float quando aplicável
                        for key in ('volume', 'umidade', 'temperatura', 'profundidade'):
                            val = mapped.get(key)
                            if val is not None and val != '':
                                try:
                                    # converter para float (mantendo None em erro)
                                    response[key] = float(val)
                                except Exception:
                                    response[key] = val
                        response['timestamp'] = mapped.get('timestamp')

        except Exception:
            # Falha ao parsear CSV — manter raw_message e campos None
            pass

    return JsonResponse(response, status=200)


def home(request):
    return render(request, "home.html", {
        "mensagem": mqtt_client.last_message
    })