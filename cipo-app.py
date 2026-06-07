import os
import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

DATABASE_URL = "postgresql+psycopg2://postgres.ydhrsjhuuyuepxvnrruh:caniplayoutside2026@aws-1-us-west-2.pooler.supabase.com:5432/postgres"

# -----------------------------
# Connect to PostgreSQL
# -----------------------------
engine = create_engine(DATABASE_URL)

query = """
SELECT
    date,
    uv_index,
    precipitation,
    temperature_2m,
    precipitation_probability,
    wind_gusts_10m,
    wind_speed_10m,
    precipitation_add
FROM hourly_weather_forecast
ORDER BY date;
"""

df = pd.read_sql(query, engine)

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# -----------------------------
# Metric choices for dropdown
# -----------------------------
metric_options = {
    "Temperature (°F)": "temperature_2m",
    "Precipitation (inches)": "precipitation",
    "Precipitation Probability (%)": "precipitation_probability",
    "Wind Gusts (mph)": "wind_gusts_10m",
    "Wind Speed (mph)": "wind_speed_10m",
    "UV Index": "uv_index",
    "Precipitation Add": "precipitation_add"
}

# -----------------------------
# Create Dash app
# -----------------------------
app = Dash(__name__)
app.title = "Can I Play Outside"

# -----------------------------
# App layout
# -----------------------------
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "padding": "20px",
        "backgroundColor": "#f8f9fa"
    },
    children=[

        html.H1(
            "Hourly Weather Forecast Dashboard",
            style={
                "textAlign": "center",
                "marginBottom": "10px",
                "color": "#1f2d3d"
            }
        ),

        html.P(
            "Interactive weather analytics dashboard using Dash + PostgreSQL",
            style={
                "textAlign": "center",
                "color": "#6c757d",
                "marginBottom": "30px"
            }
        ),

        # Filter section
        html.Div([
            html.Label(
                "Select a weather metric:",
                style={"fontWeight": "bold", "marginBottom": "8px", "display": "block"}
            ),
            dcc.Dropdown(
                id="metric-dropdown",
                options=[{"label": label, "value": value} for label, value in metric_options.items()],
                value="temperature_2m",
                clearable=False,
                style={"width": "350px"}
            )
        ], style={"marginBottom": "30px"}),

        # KPI cards
        html.Div([
            html.Div([
                html.H4("Max Temperature", style={"marginBottom": "10px"}),
                html.H2(id="max-temp-kpi", style={"color": "#007bff"})
            ], style={
                "backgroundColor": "white",
                "borderRadius": "10px",
                "padding": "20px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "width": "250px",
                "textAlign": "center"
            }),

            html.Div([
                html.H4("Avg Precip Probability", style={"marginBottom": "10px"}),
                html.H2(id="avg-precip-kpi", style={"color": "#28a745"})
            ], style={
                "backgroundColor": "white",
                "borderRadius": "10px",
                "padding": "20px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "width": "250px",
                "textAlign": "center"
            }),

            html.Div([
                html.H4("Max Wind Speed", style={"marginBottom": "10px"}),
                html.H2(id="max-wind-kpi", style={"color": "#dc3545"})
            ], style={
                "backgroundColor": "white",
                "borderRadius": "10px",
                "padding": "20px",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                "width": "250px",
                "textAlign": "center"
            })
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "gap": "20px",
            "marginBottom": "30px",
            "flexWrap": "wrap"
        }),

        # Charts row 1
        html.Div([
            dcc.Graph(id="metric-line-chart")
        ], style={
            "backgroundColor": "white",
            "borderRadius": "10px",
            "padding": "15px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "marginBottom": "30px"
        }),

        # Charts row 2
        html.Div([
            dcc.Graph(id="precip-bar-chart")
        ], style={
            "backgroundColor": "white",
            "borderRadius": "10px",
            "padding": "15px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"
        })
    ]
)

# -----------------------------
# Callback for interactivity
# -----------------------------
@app.callback(
    Output("metric-line-chart", "figure"),
    Output("precip-bar-chart", "figure"),
    Output("max-temp-kpi", "children"),
    Output("avg-precip-kpi", "children"),
    Output("max-wind-kpi", "children"),
    Input("metric-dropdown", "value")
)
def update_dashboard(selected_metric):
    # Main line chart for selected metric
    line_fig = px.line(
        df,
        x="date",
        y=selected_metric,
        title=f"{selected_metric.replace('_', ' ').title()} Over Time",
        markers=True
    )

    line_fig.update_layout(
        xaxis_title="Date/Time",
        yaxis_title=selected_metric.replace("_", " ").title(),
        template="plotly_white"
    )

    # Bar chart for precipitation probability
    bar_fig = px.bar(
        df,
        x="date",
        y="precipitation_probability",
        title="Precipitation Probability by Hour"
    )

    bar_fig.update_layout(
        xaxis_title="Date/Time",
        yaxis_title="Precipitation Probability (%)",
        template="plotly_white"
    )

    # KPI calculations
    max_temp = f"{df['temperature_2m'].max():.1f} °F"
    avg_precip = f"{df['precipitation_probability'].mean():.1f}%"
    max_wind = f"{df['wind_speed_10m'].max():.1f} mph"

    return line_fig, bar_fig, max_temp, avg_precip, max_wind

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
