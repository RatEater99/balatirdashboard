from dash import dcc, html
from app import df, LAYERS


def create_layout():
    return html.Div(className="app-shell", children=[

        # ── SIDEBAR ──
        html.Div(className="sidebar", children=[

            html.Div(className="sidebar-top", children=[
                html.Div("GLOBAL RISK INTEL", className="system-tag"),
                html.Div("FRAGILE STATES", className="logo"),
                html.Div("Fund for Peace · 2023 Dataset", className="logo-sub"),
            ]),

            html.Div(className="threat-block", children=[
                html.Div("Global Threat Index", className="threat-label"),
                html.Div(className="threat-bar-wrap", children=[
                    html.Div(className="threat-bar")
                ]),
                html.Div([
                    f"{df['Total'].mean():.0f}",
                    html.Span(" / 120")
                ], className="threat-value"),
            ]),

            html.Div(className="nav-section", children=[
                html.Div("LAYERS", className="nav-heading"),
                html.Div(id="layer-buttons", children=[
                    html.Button(
                        layer["label"],
                        id={"type": "layer-btn", "index": layer["value"]},
                        className="side-btn active" if layer["value"] == "Total" else "side-btn",
                        n_clicks=0
                    )
                    for layer in LAYERS
                ]),
            ]),

            html.Div(className="sidebar-footer", children=[
                html.Div(className="status-row", children=[
                    html.Div(className="status-item", children=[
                        html.Div(className="dot dot-green"),
                        html.Span("Feed Active"),
                    ]),
                    html.Div(className="status-item", children=[
                        html.Div(className="dot dot-red"),
                        html.Span("Alert"),
                    ]),
                ]),
                html.Div("BUILD 2023.4.1 // SENTINEL", className="build-tag"),
            ]),
        ]),

        # ── MAIN ──
        html.Div(className="main", children=[

            # topbar
            html.Div(className="topbar", children=[
                html.Div(className="topbar-section", children=[
                    html.Div("Active Layer", className="tl"),
                    html.Div(id="active-layer-name", children="Overall Fragility", className="tv"),
                ]),
                html.Div(className="topbar-section", children=[
                    html.Div("Most Fragile", className="tl"),
                    html.Div(df.loc[df["Total"].idxmax(), "Country"], className="tv tv-red"),
                ]),
                html.Div(className="topbar-section", children=[
                    html.Div("Most Stable", className="tl"),
                    html.Div(df.loc[df["Total"].idxmin(), "Country"], className="tv tv-green"),
                ]),
                html.Div(className="topbar-section", children=[
                    html.Div("Global Avg", className="tl"),
                    html.Div(f"{df['Total'].mean():.1f}", className="tv tv-amber"),
                ]),
            ]),

            # content
            html.Div(className="content-row", children=[

                # map
                html.Div(className="map-wrap", children=[
                    html.Div(className="map-corner-br"),
                    dcc.Graph(
                        id="map",
                        style={"height": "100%"},
                        config={"displayModeBar": False, "displaylogo": False}
                    )
                ]),

                # war panel
                html.Div(className="war-panel", children=[

                    html.Div(className="panel-header", children=[
                        html.Div("Combat Analysis", className="panel-title"),
                        html.Div("FSI ENGINE", className="panel-badge"),
                    ]),

                    html.Div(className="combatants", children=[
                        html.Div(id="slot-a", className="combatant-slot", children=[
                            html.Div("Country A", className="slot-label"),
                            html.Div("Click to select", className="slot-empty", id="slot-a-text"),
                        ]),
                        html.Div("VS", className="vs-divider"),
                        html.Div(id="slot-b", className="combatant-slot", children=[
                            html.Div("Country B", className="slot-label"),
                            html.Div("Click to select", className="slot-empty", id="slot-b-text"),
                        ]),
                    ]),

                    html.Div(id="selecting-hint", className="selecting-hint",
                             children="", style={"display": "none"}),

                    html.Button(
                        "ANALYZE CONFLICT",
                        id="analyze-btn",
                        className="analyze-btn",
                        disabled=True,
                        n_clicks=0
                    ),
                    dcc.Loading(
                        id="loading-analysis",
                        type="default",
                        children=html.Div(id="intel-output", className="intel-output", children=[
                            html.Div(
                                "Select two countries on the map to begin conflict analysis.",
                                className="intel-placeholder"
                            )
                        ]),
                        custom_spinner=html.Div(className="loading-dots"),
                    ),

                    html.Div(className="chat-bar", children=[
                        html.Span("›_", className="chat-prompt"),
                        dcc.Input(
                            id="chat-input",
                            className="chat-input",
                            placeholder="Ask a follow-up...",
                            debounce=False,
                            n_submit=0,
                        ),
                        html.Button("ASK", id="chat-send", className="chat-send", n_clicks=0),
                    ]),
                ]),
            ]),
        ]),

        # stores
        dcc.Store(id="selected-layer", data="Total"),
        dcc.Store(id="country-a",      data=None),
        dcc.Store(id="country-b",      data=None),
        dcc.Store(id="selecting-slot", data=None),
        dcc.Store(id="chat-history",   data=[]),
    ])