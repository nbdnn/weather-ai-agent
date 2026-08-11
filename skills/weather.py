WEATHER_SKILL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "obter_clima",
        "description": "Função para obter o clima de uma cidade específica.",
        "parameters": {
            "type": "object",
            "properties": {
                "cidade": {
                    "type": "string",
                    "description": "Nome da cidade para a qual deseja obter o clima.",
                }
            },
            "required": ["cidade"],
        },
    },
}


def obter_clima(cidade: str) -> str:
    """
    Função para obter o clima de uma cidade específica.

    Args:
        cidade (str): Nome da cidade para a qual deseja obter o clima.

    Returns:
        str: Descrição do clima atual na cidade.
    """

    # Exemplo conectando em uma API real (ex: OpenWeatherMap)
    # response = requests.get(
    # f"https://api.openweathermap.org/data/2.5/weather?q={cidade}&..."
    # )

    dados_mock = {
        "São Paulo": "25°C e ensolarado",
        "Curitiba": "12°C e chuvoso",
        "Monte Aprazível": "30°C e muito quente",
    }
    return dados_mock.get(cidade, "Clima não disponível para esta cidade.")
