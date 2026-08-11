import os
from collections import defaultdict

import requests

WEATHER_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "obter_previsao_clima",
        "description": (
            "Obtém a previsão do tempo para os próximos dias em uma cidade, "
            "incluindo temperatura mínima e máxima, velocidade do vento, "
            "umidade relativa do ar e probabilidade de chuva."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "cidade": {
                    "type": "string",
                    "description": (
                        "Nome da cidade para a qual deseja consultar o clima. "
                        "Exemplos: São Paulo, Curitiba, Paris, Nova York."
                    ),
                }
            },
            "required": ["cidade"],
        },
    },
}


def obter_previsao_clima(cidade: str) -> str:
    """
    Função para obter o clima de uma cidade específica.

    Args:
        cidade (str): Nome da cidade para a qual deseja obter o clima.

    Returns:
        str: Descrição do clima atual na cidade.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "Erro de configuração: A chave OPENWEATHER_API_KEY não foi encontrada no arquivo .env."

    try:
        # ETAPA 1: Converter o nome da cidade em coordenadas geográficas (lon e lat)

        geo_url = (
            f"http://api.openweathermap.org/geo/1.0/direct"
            f"?q={cidade}&limit=1&appid={api_key}"
        )

        geo_response = requests.get(geo_url, timeout=5)
        geo_data = geo_response.json()

        if not geo_data:
            return f"Não foi possível encontrar as coordenadas geográficas para '{cidade}'."

        lat = geo_data[0].get("lat")
        lon = geo_data[0].get("lon")
        nome_oficial = geo_data[0].get("name")
        pais = geo_data[0].get("country", None)

        # ETAPA 2: Buscar clima usando lat e lon
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pt_br"
        )

        weather_response = requests.get(weather_url, timeout=5)
        weather_response.raise_for_status()
        data = weather_response.json()

        # Processamento e agrupamento das medições por dia (AAAA-MM-DD)
        medicoes_por_dia = defaultdict(list)
        for item in data["list"]:
            data_str = item["dt_txt"].split(" ")[0]
            medicoes_por_dia[data_str].append(item)

        resumo_clima = [
            f"Previsão meteorológica detalhada para {nome_oficial} ({pais}):"
        ]

        for data_dia, medicoes in list(medicoes_por_dia.items())[:3]:

            temps = [
                m["main"]["temp"]
                for m in medicoes
                if isinstance(m.get("main"), dict) and m["main"].get("temp") is not None
            ]
            umidades = [
                m["main"]["humidity"]
                for m in medicoes
                if isinstance(m.get("main"), dict) and m["main"].get("humidity") is not None
            ]
            ventos = [
                m["wind"]["speed"] * 3.6
                for m in medicoes
                if isinstance(m.get("wind"), dict) and m["wind"].get("speed") is not None
            ]
            chances_chuva = [
                m["pop"] * 100
                for m in medicoes
                if m.get("pop") is not None
            ]

            temp_min = min(temps) if temps else None
            temp_max = max(temps) if temps else None
            umidade_media = (sum(umidades) / len(umidades)) if umidades else None
            vento_max = max(ventos) if ventos else None
            chance_chuva_max = max(chances_chuva) if chances_chuva else None

            if temp_min is not None and temp_max is not None:
                temp_texto = f"Mínima de {temp_min:.1f}°C e Máxima de {temp_max:.1f}°C"
            elif temp_min is not None:
                temp_texto = f"Mínima de {temp_min:.1f}°C"
            elif temp_max is not None:
                temp_texto = f"Máxima de {temp_max:.1f}°C"
            else:
                temp_texto = "Indisponível"

            chuva_texto = (
                f"{chance_chuva_max:.0f}%" if chance_chuva_max is not None else "Indisponível"
            )
            umidade_texto = (
                f"{umidade_media:.0f}%" if umidade_media is not None else "Indisponível"
            )
            vento_texto = (
                f"{vento_max:.1f} km/h" if vento_max is not None else "Indisponível"
            )

            # Busca a descrição da condição
            condicao = "Sem descrição"
            if medicoes and isinstance(medicoes[len(medicoes) // 2].get("weather"), list):
                weather_list = medicoes[len(medicoes) // 2]["weather"]
                if weather_list and isinstance(weather_list[0], dict):
                    condicao = weather_list[0].get("description", "Sem descrição")

            resumo_clima.append(
                f"- Data {data_dia}: {condicao.capitalize()}.\n"
                f"  - Temperatura: {temp_texto}\n"
                f"  - Probabilidade de chuva: {chuva_texto}\n"
                f"  - Umidade média: {umidade_texto}\n"
                f"  - Vento máximo: {vento_texto}"
            )

        return "\n".join(resumo_clima)

    except requests.exceptions.RequestException as e:
        return f"Erro de comunicação com o serviço OpenWeatherMap: {e!s}"
    except (KeyError, IndexError, ValueError) as e:
        return f"Erro ao processar dados de clima retornados pela API: {e!s}"