import dash
from dash import html, dcc
import dash_leaflet as dl
from dash.dependencies import Input, Output
import mqtt_client

mqtt_client.start_background_loop()

app = dash.Dash(__name__)
app.title = "Real-Time Electricity Geo Dashboard"

app.layout = html.Div([
    html.H2("🌍 Real-Time Electricity Dashboard", style={"textAlign": "center"}),
    html.P("Streaming facilities' emissions, power, demand, and price", style={"textAlign": "center"}),

    dl.Map(
        id="map",
        # center of Australia
        center=[-25.0, 134.0],
        zoom=4,
        style={'width': '100%', 'height': '70vh'},
        children=[dl.TileLayer()]
    ),
    dcc.Interval(id="interval", interval=1000, n_intervals=0),
])

@app.callback(Output("map", "children"), Input("interval", "n_intervals"))
def update_map(_):
    markers = []
    for point in mqtt_client.latest_points:
        popup = (
            f"Facility: {point.get('facility')}<br>"
            f"Region: {point.get('region_id')} ({point.get('region_code')})<br>"
            f"Emissions: {point.get('emissions_t')} (tonnes)<br>"
            f"Power: {point.get('power_mw')} (MW)<br>"
            f"Demand: {point.get('demand_mw')} (MW)<br>"
            f"Price: ${point.get('price_aud')} ($/MWh)<br>"
            f"Timestamp: {point.get('timestamp')}"
        )
        markers.append(dl.CircleMarker(
            center=[point["lat"], point["lng"]],
            radius=8,
            color="#70B2B2",
            fillColor="#70B2B2",
            fillOpacity=0.2,
            children=dl.Popup(html.Iframe(srcDoc=popup, style={"border": "none", "width": "320px"}))
        ))
    return [dl.TileLayer()] + markers

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=8050)
