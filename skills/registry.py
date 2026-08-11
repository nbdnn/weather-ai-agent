from skills.weather import WEATHER_SKILL_SCHEMA, obter_clima

ALL_TOOLS_SCHEMA = [
    WEATHER_SKILL_SCHEMA
]

TOOL_MAPPING = {
    "obter_clima": obter_clima,
}
