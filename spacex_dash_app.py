import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# IBM Applied Data Science Capstone - Plotly Dash lab
# Place spacex_launch_dash.csv in the same folder as this script.
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

app = Dash(__name__)

site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site}
    for site in sorted(spacex_df["Launch Site"].dropna().unique())
]

app.layout = html.Div([
    html.H1(
        "SpaceX Launch Records Dashboard",
        style={"textAlign": "center", "color": "#503D36", "fontSize": 40},
    ),

    # TASK 1: Launch-site dropdown
    dcc.Dropdown(
        id="site-dropdown",
        options=site_options,
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True,
    ),
    html.Br(),

    # TASK 2: Success pie chart
    html.Div(dcc.Graph(id="success-pie-chart")),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload range slider
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload],
    ),

    # TASK 4: Payload/success scatter plot
    html.Div(dcc.Graph(id="success-payload-scatter-chart")),
])


@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        successful = spacex_df[spacex_df["class"] == 1]
        return px.pie(
            successful,
            names="Launch Site",
            title="Total Success Launches by Site",
        )

    filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
    counts = (
        filtered_df.groupby("class")
        .size()
        .reset_index(name="count")
    )
    counts["Outcome"] = counts["class"].map({0: "Failure", 1: "Success"})
    return px.pie(
        counts,
        values="count",
        names="Outcome",
        title=f"Success vs. Failure for {entered_site}",
    )


@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"),
     Input("payload-slider", "value")],
)
def get_payload_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ]

    if entered_site != "ALL":
        filtered_df = filtered_df[
            filtered_df["Launch Site"] == entered_site
        ]

    title = (
        "Payload vs. Launch Outcome for All Sites"
        if entered_site == "ALL"
        else f"Payload vs. Launch Outcome for {entered_site}"
    )

    return px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
        labels={"class": "Launch Outcome (0 = Failure, 1 = Success)"},
    )


if __name__ == "__main__":
    app.run(debug=False)
