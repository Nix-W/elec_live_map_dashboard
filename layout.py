"""
Layout components for the Real-Time Electricity Geo Dashboard.
"""
from dash import html, dcc, dash_table
import dash_leaflet as dl
from config import (
    TABLE_COLUMNS, SUMMARY_COLUMNS, MAP_CENTER, MAP_ZOOM, MAP_TILE_URL, 
    MAP_ATTRIBUTION, UPDATE_INTERVAL, APP_TITLE, MAIN_TITLE_STYLE, MAP_STYLE,
    SUMMARY_CONTAINER_STYLE, SECTION_TITLE_STYLE, FILTER_LABEL_STYLE,
    FILTER_DROPDOWN_STYLE, CLEAR_FILTERS_BUTTON_STYLE, FILTER_STATUS_STYLE,
    TABLE_HEADER_STYLE, TABLE_CELL_STYLE, TABLE_SELECTED_ROW_STYLE,
    FACILITY_TABLE_HEADER_STYLE, FACILITY_TABLE_CELL_STYLE, 
    FACILITY_DETAILS_TITLE_STYLE, FACILITY_CHANGES_DISPLAY_STYLE,
    MAIN_CONTAINER_STYLE
)


def create_map_component():
    """Create the map component with base layers."""
    return dl.Map(
        id="map",
        center=MAP_CENTER,
        zoom=MAP_ZOOM,
        style=MAP_STYLE,
        children=[
            dl.TileLayer(
                url=MAP_TILE_URL,
                attribution=MAP_ATTRIBUTION
            )
        ]
    )


def create_filter_controls():
    """Create the filter control components."""
    return html.Div([
        html.Div([
            html.Label("Network Region:", style=FILTER_LABEL_STYLE),
            dcc.Dropdown(
                id="region-filter",
                placeholder="All Regions",
                clearable=True,
                style=FILTER_DROPDOWN_STYLE,
                optionHeight=30
            )
        ], style={"width": "36%", "display": "inline-block", "marginRight": "4%"}),
        
        html.Div([
            html.Label("Fuel Technology:", style=FILTER_LABEL_STYLE),
            dcc.Dropdown(
                id="fuel-filter",
                placeholder="All Technologies",
                clearable=True,
                style=FILTER_DROPDOWN_STYLE,
                optionHeight=30
            )
        ], style={"width": "36%", "display": "inline-block", "marginRight": "4%"}),
        
        html.Button(
            "Clear Filters", 
            id="clear-filters", 
            style=CLEAR_FILTERS_BUTTON_STYLE
        ),
        
        html.Div(
            id="filter-status", 
            style=FILTER_STATUS_STYLE
        )
    ], style={
        "marginBottom": "15px", 
        "backgroundColor": "#f8f9fa", 
        "borderRadius": "8px"
    })


def create_summary_table():
    """Create the summary table component."""
    return html.Div(
        id="summary-table-wrapper",
        style={"overflowY": "auto", "maxHeight": "calc(65vh - 140px)"},
        children=[
            dash_table.DataTable(
                id="summary-table",
                columns=SUMMARY_COLUMNS,
                data=[],
                sort_action="native",
                row_selectable="single",
                selected_rows=[],
                style_table={"overflowY": "auto"},
                style_header=TABLE_HEADER_STYLE,
                style_cell=TABLE_CELL_STYLE,
                style_data_conditional=TABLE_SELECTED_ROW_STYLE,
            ),
        ],
    )


def create_summary_container():
    """Create the complete summary container with filters and table."""
    return html.Div(
        id="summary-table-container",
        style=SUMMARY_CONTAINER_STYLE,
        children=[
            html.H3("Facility Summary", style=SECTION_TITLE_STYLE),
            create_filter_controls(),
            create_summary_table(),
        ],
    )


def create_facility_table():
    """Create the facility details table."""
    return dash_table.DataTable(
        id="facility-table",
        columns=TABLE_COLUMNS,
        data=[],
        sort_action="native",
        style_table={"maxHeight": "320px", "overflowY": "auto"},
        style_header=FACILITY_TABLE_HEADER_STYLE,
        style_cell=FACILITY_TABLE_CELL_STYLE,
    )


def create_facility_details_container():
    """Create the facility details container."""
    return html.Div(
        id="facility-table-container",
        children=[
            html.H3("Facility Details", style=FACILITY_DETAILS_TITLE_STYLE),
            html.Div(
                id="facility-changes-display",
                style=FACILITY_CHANGES_DISPLAY_STYLE,
                children=[
                    html.Div(id="facility-info-display"),
                ]
            ),
            create_facility_table(),
        ],
        style={"display": "none"},
    )


def create_data_stores():
    """Create data storage components."""
    return [
        dcc.Store(id="map-data-store", data={}),
        dcc.Store(id="facility-data-store", data=[]),
        dcc.Store(id="selected-facility", data=None),
        dcc.Store(id="summary-data-unfiltered", data=[]),
    ]


def create_interval_component():
    """Create the interval component for auto-refresh."""
    return dcc.Interval(
        id="interval", 
        interval=UPDATE_INTERVAL, 
        n_intervals=0
    )


def create_main_layout():
    """Create the complete main layout."""
    return html.Div([
        html.H1(f"🇦🇺 {APP_TITLE}", style=MAIN_TITLE_STYLE),
        
        html.Div([
            create_map_component(),
            create_summary_container(),
        ], style={"display": "flex", "justifyContent": "space-around"}),
        
        create_facility_details_container(),
        
        *create_data_stores(),
        create_interval_component(),
    ], style=MAIN_CONTAINER_STYLE)