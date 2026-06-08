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


df["date_only"] = df["date"].dt.date.astype(str)
df["time_only"] = df["date"].dt.strftime("%I:%M %p")


# -----------------------------
# Metric choices for dropdown
# -----------------------------

date = sorted(df["date_only"].dropna().unique())
time = sorted(df["time_only"].dropna().unique())

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
            "Can I Play Outside",
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
            html.Div([
                html.Label(
                    "Select a date:",
                    style={"fontWeight": "bold", "marginBottom": "8px", "display": "block"}
                ),
                dcc.Dropdown(
                    id="date-dropdown",
                    options=[{"label": "All Dates", "value": "ALL"}] + [
                        {"label": d, "value": d} for d in date_only
                    ],
                    value="ALL",
                    clearable=False,
                    style={"width": "250px"}
                )
            ]),

            html.Div([
                html.Label(
                    "Select a time:",
                    style={"fontWeight": "bold", "marginBottom": "8px", "display": "block"}
                ),
                dcc.Dropdown(
                    id="time-dropdown",
                    options=[{"label": "All Times", "value": "ALL"}] + [
                        {"label": t, "value": t} for t in time_only
                    ],
                    value="ALL",
                    clearable=False,
                    style={"width": "250px"}
                )
            ])
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "gap": "20px",
            "marginBottom": "30px",
            "flexWrap": "wrap"
        }),

        # KPI card
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


        #Visual
        html.Div([
            dash_table.DataTable(
                id="weather-table",
                columns=[
                    {"name": "Date", "id": "date_only"},
                    {"name": "Time", "id": "time_only"},
                    {"name": "Temperature (°F)", "id": "temperature_2m"},
                    {"name": "UV Index", "id": "uv_index"},
                    {"name": "Precipitation (in)", "id": "precipitation"},
                    {"name": "Precipitation Probability (%)", "id": "precipitation_probability"},
                    {"name": "Wind Gusts (mph)", "id": "wind_gusts_10m"},
                    {"name": "Wind Speed (mph)", "id": "wind_speed_10m"}
                ],
                data=[],
                page_size=24,
                sort_action="native",
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "10px",
                    "fontFamily": "Arial",
                    "fontSize": "14px"
                },
                style_header={
                    "backgroundColor": "#e9ecef",
                    "fontWeight": "bold"
                },
                style_data={
                    "backgroundColor": "white",
                    "color": "#212529"
                }
            )
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
    Output("weather-table", "data"),
    Output("max-temp-kpi", "children"),
    Input("date-dropdown", "value"),
    Input("time-dropdown", "value")
)

def update_dashboard(selected_date, selected_time):
    filtered_df = df.copy()

    if selected_date != "ALL":
        filtered_df = filtered_df[filtered_df["date_only"] == selected_date]

    if selected_time != "ALL":
        filtered_df = filtered_df[filtered_df["time_only"] == selected_time]

    if filtered_df.empty:
        max_temp = "No data"
    else:
        max_temp = f"{filtered_df['temperature_2m'].max():.1f} °F"

    table_df = filtered_df[[
        "date_only",
        "time_only",
        "temperature_2m",
        "uv_index",
        "precipitation",
        "precipitation_probability",
        "wind_gusts_10m",
        "wind_speed_10m"
    ]].copy()

    return table_df.to_dict("records"), max_temp

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
