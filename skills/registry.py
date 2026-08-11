from skills.weather import WEATHER_SKILL_SCHEMA, obter_previsao_clima

ALL_TOOLS_SCHEMA = [
    WEATHER_SKILL_SCHEMA
]

TOOL_MAPPING = {
    "obter_previsao_clima": obter_previsao_clima,
}
