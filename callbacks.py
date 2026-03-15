import dash
from dash import Input, Output, State, ctx
import plotly.graph_objects as go
from app import app, df, client, LAYERS, colorscales, SYSTEM_PROMPT


@app.callback(
    Output("selected-layer", "data"),
    [Input({"type": "layer-btn", "index": layer["value"]}, "n_clicks") for layer in LAYERS],
    prevent_initial_call=True
)
def update_selected(*args):
    return ctx.triggered_id["index"]


@app.callback(
    Output("map", "figure"),
    Output("active-layer-name", "children"),
    *[Output({"type": "layer-btn", "index": layer["value"]}, "className") for layer in LAYERS],
    Input("selected-layer", "data")
)
def update_map(selected_layer):
    fig = go.Figure(go.Choropleth(
        locations=df["Country"],
        locationmode="country names",
        z=df[selected_layer],
        colorscale=colorscales[selected_layer],
        autocolorscale=False,
        marker=dict(line=dict(color="rgba(0,0,0,0)", width=0)),
        hovertemplate="<b>%{location}</b><br>Score: %{z:.1f}<extra></extra>"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            showframe=False, showcoastlines=False,
            showland=True,  landcolor="#1a1d26",
            showocean=True, oceancolor="#060709",
            showlakes=False, showcountries=False,
            bgcolor="#060709",
        ),
        paper_bgcolor="#060709",
        plot_bgcolor="#060709",
        font=dict(color="#5a6480", family="IBM Plex Mono"),
        coloraxis_colorbar=dict(
            thickness=6, len=0.4, x=1.01,
            tickfont=dict(size=9, color="#5a6480", family="IBM Plex Mono"),
            outlinewidth=0, bgcolor="rgba(0,0,0,0)",
        )
    )
    active_label = next(l["label"] for l in LAYERS if l["value"] == selected_layer)
    btn_classes  = [
        "side-btn active" if l["value"] == selected_layer else "side-btn"
        for l in LAYERS
    ]
    return fig, active_label, *btn_classes


@app.callback(
    Output("selecting-slot", "data"),
    Output("slot-a",         "className"),
    Output("slot-b",         "className"),
    Output("selecting-hint", "children"),
    Output("selecting-hint", "style"),
    Input("slot-a",  "n_clicks"),
    Input("slot-b",  "n_clicks"),
    State("selecting-slot", "data"),
    prevent_initial_call=True
)
def toggle_selecting(a_clicks, b_clicks, current):
    triggered = ctx.triggered_id
    new_slot   = None if current == ("a" if triggered == "slot-a" else "b") else ("a" if triggered == "slot-a" else "b")
    slot_a_cls = "combatant-slot selecting" if new_slot == "a" else "combatant-slot"
    slot_b_cls = "combatant-slot selecting" if new_slot == "b" else "combatant-slot"
    hint       = f"→ CLICK A COUNTRY ON THE MAP FOR SLOT {new_slot.upper()}" if new_slot else ""
    hint_style = {"display": "block"} if new_slot else {"display": "none"}
    return new_slot, slot_a_cls, slot_b_cls, hint, hint_style


@app.callback(
    Output("country-a",      "data"),
    Output("country-b",      "data"),
    Output("selecting-slot", "data",    allow_duplicate=True),
    Output("slot-a-text",    "children"),
    Output("slot-b-text",    "children"),
    Output("slot-a-text",    "className"),
    Output("slot-b-text",    "className"),
    Output("slot-a",         "className", allow_duplicate=True),
    Output("slot-b",         "className", allow_duplicate=True),
    Output("selecting-hint", "style",   allow_duplicate=True),
    Output("analyze-btn",    "disabled"),
    Input("map", "clickData"),
    State("selecting-slot",  "data"),
    State("country-a",       "data"),
    State("country-b",       "data"),
    prevent_initial_call=True
)
def assign_country(clickData, slot, country_a, country_b):
    if not clickData or not slot:
        raise dash.exceptions.PreventUpdate
    country = clickData["points"][0]["location"]
    if slot == "a":
        country_a = country
    else:
        country_b = country
    a_text   = country_a if country_a else "Click to select"
    b_text   = country_b if country_b else "Click to select"
    a_cls    = "slot-country" if country_a else "slot-empty"
    b_cls    = "slot-country" if country_b else "slot-empty"
    both_set = country_a is not None and country_b is not None
    return (
        country_a, country_b, None,
        a_text, b_text, a_cls, b_cls,
        "combatant-slot", "combatant-slot",
        {"display": "none"}, not both_set
    )


def get_scores(country):
    row = df[df["Country"] == country]
    if row.empty:
        return {}
    return {
        "Total":        float(row["Total"].values[0]),
        "Security":     float(row["C1: Security Apparatus"].values[0]),
        "Legitimacy":   float(row["P1: State Legitimacy"].values[0]),
        "Economy":      float(row["E1: Economy"].values[0]),
        "Human Rights": float(row["P3: Human Rights"].values[0]),
        "Elites":       float(row["C2: Factionalized Elites"].values[0]),
    }


def build_prompt(history, new_message=None):
    """Flatten chat history into a single string for the API."""
    full = SYSTEM_PROMPT + "\n\n"
    for msg in history:
        role = "ANALYST" if msg["role"] == "model" else "USER"
        full += f"{role}: {msg['content']}\n\n"
    if new_message:
        full += f"USER: {new_message}"
    return full


@app.callback(
    Output("intel-output", "children"),
    Output("chat-history", "data"),
    Output("chat-input",   "value"),
    Input("analyze-btn",   "n_clicks"),
    Input("chat-send",     "n_clicks"),
    Input("chat-input",    "n_submit"),
    State("country-a",     "data"),
    State("country-b",     "data"),
    State("chat-input",    "value"),
    State("chat-history",  "data"),
    prevent_initial_call=True
)
def run_analysis(analyze_clicks, send_clicks, n_submit, country_a, country_b, user_msg, history):
    triggered = ctx.triggered_id

    # ── initial conflict analysis ──
    if triggered == "analyze-btn":
        if not country_a or not country_b:
            raise dash.exceptions.PreventUpdate

        a_scores = get_scores(country_a)
        b_scores = get_scores(country_b)

        prompt = f"""{SYSTEM_PROMPT}

Conflict analysis: {country_a} vs {country_b}

{country_a} FSI scores: {a_scores}
{country_b} FSI scores: {b_scores}

Who wins and why? Consider state capacity, security apparatus, internal cohesion, economic resilience.
Be direct. No fluff. Lead with the verdict."""

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        reply = response.text

        new_history = [
            {"role": "user",  "content": f"Analyze {country_a} vs {country_b}"},
            {"role": "model", "content": reply},
        ]
        return reply, new_history, ""

    # ── follow-up chat ──
    elif triggered in ("chat-send", "chat-input") and user_msg:
        if not history:
            raise dash.exceptions.PreventUpdate

        full_prompt = build_prompt(history, user_msg)

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=full_prompt
        )
        reply = response.text

        history.append({"role": "user",  "content": user_msg})
        history.append({"role": "model", "content": reply})

        # build readable transcript (skip first exchange which is the system prompt turn)
        transcript = history[1]["content"]  # first model reply
        for msg in history[2:]:
            if msg["role"] == "user":
                transcript += f"\n\n▸ {msg['content']}\n\n"
            else:
                transcript += msg["content"]

        return transcript, history, ""

    raise dash.exceptions.PreventUpdate