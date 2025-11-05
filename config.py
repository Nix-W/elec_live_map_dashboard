"""
Configuration constants and settings for the Real-Time Electricity Geo Dashboard.
"""

# Table column definitions
TABLE_COLUMNS = [
    {"name": "Unit Code", "id": "unit_code"},
    {"name": "Power (MW)", "id": "power_mw"},
    {"name": "Demand (MW)", "id": "demand_mw"},
    {"name": "Emissions (t)", "id": "emissions_t"},
    {"name": "Price ($/MWh)", "id": "price"},
    {"name": "Timestamp", "id": "timestamp"},
]

SUMMARY_COLUMNS = [
    {"name": "Facility", "id": "facility_name"},
    {"name": "Network Region", "id": "network_region"},
    {"name": "Fuel Tech", "id": "fuel_tech"},
    {"name": "Total Power (MW)", "id": "total_power_mw"},
    {"name": "Total Emissions (t)", "id": "total_emissions_t"},
]

# Map configuration
MAP_CENTER = [-25.0, 134.0]  # Center of Australia
MAP_ZOOM = 4
MAP_TILE_URL = "https://cartodb-basemaps-{s}.global.ssl.fastly.net/rastertiles/voyager/{z}/{x}/{y}.png"
MAP_ATTRIBUTION = '&copy; <a href="https://carto.com/attributions">CARTO</a>'

# Marker configuration
BASE_MARKER_RADIUS = 7.0
MAX_MARKER_RADIUS = 10.0

# Fuel type color scheme for markers
FUEL_TYPE_COLORS = {
    'black_coal': "#2c3e50",        # dark grey/black for coal
    'brown_coal': "#8b4513",        # brown for brown coal
    'gas_ccgt': "#3498db",          # blue for gas combined cycle
    'gas_ocgt': "#5dade2",          # light blue for gas open cycle
    'gas_steam': "#85c1e9",         # pale blue for gas steam
    'hydro': "#1abc9c",             # teal for hydro
    'wind': "#27ae60",              # green for wind
    'solar': "#f39c12",             # orange for solar
    'battery': "#9b59b6",           # purple for battery
    'biomass': "#16a085",           # dark teal for biomass
    'landfill_gas': "#a569bd",      # light purple for landfill gas
    'waste_coal_mine': "#34495e",   # dark grey for waste coal
    'default': "#95a5a6"            # light grey for unknown fuel types
}

# Update interval (milliseconds)
UPDATE_INTERVAL = 3 * 1000  # 3 seconds

# App configuration
APP_TITLE = "Real-Time Electricity Geo Dashboard"
APP_HOST = '127.0.0.1'
APP_PORT = 8050

# Style configurations
MAIN_TITLE_STYLE = {
    "textAlign": "center", 
    "color": "#2c3e50", 
    "fontWeight": "300", 
    "fontSize": "2.5rem",
    "marginBottom": "30px",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "letterSpacing": "1px"
}

MAP_STYLE = {
    'width': '50%', 
    'height': '65vh',
    'borderRadius': '12px',
    'border': '2px solid #bdc3c7',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
    'overflow': 'hidden'
}

SUMMARY_CONTAINER_STYLE = {
    'width': '50%', 
    'height': '65vh', 
    "margin": "0 16px"
}

SECTION_TITLE_STYLE = {
    "marginTop": "0", 
    "marginBottom": "12px", 
    "color": "#34495e", 
    "fontWeight": "400",
    "fontSize": "1.4rem",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "borderBottom": "2px solid #34495e",
}

FILTER_LABEL_STYLE = {
    "fontSize": "0.8rem", 
    "fontWeight": "500", 
    "color": "#34495e"
}

FILTER_DROPDOWN_STYLE = {
    "fontSize": "0.8rem",
    "marginTop": "5px"
}

CLEAR_FILTERS_BUTTON_STYLE = {
    "backgroundColor": "#e74c3c",
    "color": "white",
    "border": "none",
    "padding": "8px 16px",
    "borderRadius": "4px",
    "fontSize": "0.8rem",
    "cursor": "pointer",
    "transform": "translateY(30px)"
}

FILTER_STATUS_STYLE = {
    "fontSize": "0.8rem",
    "color": "#7f8c8d",
    "marginTop": "8px"
}

TABLE_HEADER_STYLE = {
    "backgroundColor": "#34495e", 
    "color": "white",
    "fontWeight": "500",
    "fontSize": "0.7rem",
    "textAlign": "center",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "letterSpacing": "0.5px",
    "textTransform": "uppercase",
    "border": "none"
}

TABLE_CELL_STYLE = {
    "padding": "12px 8px",
    "textAlign": "left",
    "whiteSpace": "normal",
    "minWidth": "70px",
    "maxWidth": "90px",
    "wordBreak": "break-word",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "fontSize": "0.75rem",
    "border": "1px solid #dee2e6",
    "backgroundColor": "white"
}

FACILITY_TABLE_HEADER_STYLE = {
    "backgroundColor": "#2c3e50", 
    "color": "white",
    "fontWeight": "500",
    "fontSize": "0.7rem",
    "textAlign": "center",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "letterSpacing": "0.5px",
    "textTransform": "uppercase",
    "border": "none"
}

FACILITY_TABLE_CELL_STYLE = {
    "padding": "12px 8px",
    "textAlign": "left",
    "whiteSpace": "normal",
    "minWidth": "70px",
    "wordBreak": "break-word",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "fontSize": "0.75rem",
    "border": "1px solid #dee2e6",
    "backgroundColor": "white"
}

FACILITY_DETAILS_TITLE_STYLE = {
    "marginTop": "20px", 
    "marginBottom": "16px",
    "color": "#34495e", 
    "fontWeight": "400",
    "fontSize": "1.4rem",
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "borderBottom": "2px solid #2c3e50",
    "paddingBottom": "8px"
}

FACILITY_CHANGES_DISPLAY_STYLE = {
    "margin": "15px 0", 
    "padding": "20px", 
    "backgroundColor": "white", 
    "borderRadius": "10px", 
    "border": "1px solid #34495e",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
}

MAIN_CONTAINER_STYLE = {
    "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "fontSize": "14px",
    "padding": "20px",
    "backgroundColor": "#f8f9fa",
    "minHeight": "100vh"
}

TABLE_SELECTED_ROW_STYLE = [
    {
        "if": {"state": "selected"},
        "backgroundColor": "#e3f2fd",
        "color": "#1976d2",
        "fontWeight": "500"
    }
]