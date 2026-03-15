import dash
import pandas as pd
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

# ── app instance ──
app = dash.Dash(__name__)

# ── data ──
df = pd.read_excel('fragile_states_index.xlsx')

# ── gemini ──
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a brutally direct geopolitical military analyst.
No greetings. No filler. No "great question".
Lead with the answer. Use short punchy paragraphs.
Back every claim with specific data from the Fragile States Index scores provided.
Format: verdict first, reasoning second, wildcards last."""

LAYERS = [
    {"label": "Overall Fragility",    "value": "Total"},
    {"label": "Economic Inequality",  "value": "E2: Economic Inequality"},
    {"label": "Security Apparatus",   "value": "C1: Security Apparatus"},
    {"label": "State Legitimacy",     "value": "P1: State Legitimacy"},
    {"label": "Human Rights",         "value": "P3: Human Rights"},
    {"label": "Factionalized Elites", "value": "C2: Factionalized Elites"},
]

colorscales = {
    "Total":                    "Reds",
    "E2: Economic Inequality":  "Plasma",
    "C1: Security Apparatus":   "Inferno",
    "P1: State Legitimacy":     "OrRd",
    "P3: Human Rights":         "YlOrRd",
    "C2: Factionalized Elites": "Hot",
}