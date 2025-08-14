import time
import random
import streamlit as st

# NOTE: This is a stub. In MCP-enabled IDE, replace impl with MCP tool call, e.g. weather.get(city)

@st.cache_data(ttl=1800)
def get_weather(city: str) -> dict:
    """Fetch weather context for a city.
    Returns a dict like {summary, temp_c, precip_mm, condition, city, fetched_at}.
    This stub generates plausible data; replace with MCP call.
    """
    try:
        # Replace this block with MCP call; e.g.:
        # payload = mcp_call("weather.get", {"city": city})
        # return {**payload, "city": city, "fetched_at": int(time.time())}
        random.seed(hash(city) % 10_000)
        cond = random.choice(["sunny", "cloudy", "rain", "snow", "windy"])  # basic conditions
        temp = round(random.uniform(-2, 30), 1)
        precip = 0.0 if cond in {"sunny", "windy", "cloudy"} else round(random.uniform(0.2, 8.0), 1)
        return {
            "summary": f"{cond}, {temp}°C, {precip} mm",
            "temp_c": temp,
            "precip_mm": precip,
            "condition": cond,
            "city": city,
            "fetched_at": int(time.time()),
        }
    except Exception:
        return {}


def weather_prompt(level: str, wx: dict) -> str:
    if not wx:
        return ""
    city = wx.get("city", "your city")
    cond = wx.get("condition", "current weather")
    t = wx.get("temp_c")
    p = wx.get("precip_mm")
    if level in {"A2", "B1"}:
        return (
            f"Describe your daily routine in {city} when it is {cond}. "
            f"Mention how {t}°C and {p} mm of precipitation affect transport, clothing, and plans."
        )
    return (
        f"Analyze the impact of current weather in {city} ({cond}, {t}°C, {p} mm) on transport, safety, and urban planning. "
        "Use specific numbers and realistic examples."
    )
