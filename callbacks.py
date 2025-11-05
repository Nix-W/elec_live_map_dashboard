"""
Callback functions for the Real-Time Electricity Geo Dashboard.
"""
import json
import math
from collections import defaultdict
from datetime import datetime
import dash
from dash import html
from dash.dependencies import Input, Output, State, ALL
import dash_leaflet as dl
import mqtt_client
from utils import (
    _parse_timestamp, _to_float, _color_from_change, _radius_from_demand,
    _build_popup_content, format_power_display, format_demand_display,
    format_emissions_display, format_price_display, format_timestamp_display,
    get_change_color, get_change_symbol, get_emission_change_color,
    get_emission_change_symbol, clean_facility_row_for_display,
    extract_unique_regions, extract_unique_fuel_techs,
    filter_summary_data_by_region, filter_summary_data_by_fuel,
    create_filter_status_message
)
from config import COLORS


def register_callbacks(app):
    """Register all callbacks with the Dash app."""
    
    @app.callback(
        Output("map-data-store", "data"),
        Output("facility-data-store", "data"),
        Output("summary-data-unfiltered", "data"),
        Input("interval", "n_intervals"),
    )
    def refresh_data(_):
        facility_points = defaultdict(lambda: defaultdict(list))
        demand_samples = []

        for point in mqtt_client.latest_points:
            facility_code = str(point.get("facility_code") or "").strip()
            unit_code = str(point.get("unit_code") or "").strip()
            if not facility_code or not unit_code:
                continue

            demand_candidate = (
                point.get("demand")
                or point.get("demand_mw")
                or point.get("demand_nem")
            )
            demand_float = _to_float(demand_candidate)
            if demand_float is not None:
                demand_samples.append(demand_float)

            facility_points[facility_code][unit_code].append(point)

        demand_min = min(demand_samples) if demand_samples else None
        demand_max = max(demand_samples) if demand_samples else None

        facility_records = []
        summary_records = []
        map_payload = {
            "demand_min": demand_min,
            "demand_max": demand_max,
            "facilities": {},
        }

        for facility_id, unit_map in facility_points.items():
            facility_entries = []
            facility_total_power = 0.0
            facility_total_emissions = 0.0
            facility_has_power = False
            facility_has_emissions = False
            unit_records_temp = []

            for unit_code, points in unit_map.items():
                unit_entries = []
                for point in points:
                    timestamp = _parse_timestamp(point.get("timestamp"))
                    unit_entries.append((timestamp, point))
                    facility_entries.append((timestamp, point))

                if not unit_entries:
                    continue

                unit_entries.sort(key=lambda item: item[0] or datetime.min)
                unit_timestamp, unit_point = unit_entries[-1]

                # Calculate current values for this unit
                unit_power = _to_float(unit_point.get("power_mw"))
                unit_emissions = _to_float(unit_point.get("emissions_t"))

                # Add to facility totals
                if unit_power is not None:
                    facility_total_power += unit_power
                    facility_has_power = True

                if unit_emissions is not None:
                    facility_total_emissions += unit_emissions
                    facility_has_emissions = True

                unit_demand = _to_float(
                    unit_point.get("demand")
                    or unit_point.get("demand_mw")
                    or unit_point.get("demand_nem")
                )
                unit_price = _to_float(unit_point.get("price"))

                # Store unit data for later processing after facility changes are calculated
                unit_records_temp.append({
                    "facility_id": facility_id,
                    "unit_code": unit_code,
                    "power_mw": unit_power,
                    "demand_mw": unit_demand,
                    "emissions_t": unit_emissions,
                    "price": unit_price if math.isnan(unit_price) == False else 0,
                    "timestamp": unit_timestamp,
                })

            if not facility_entries:
                continue

            facility_entries.sort(key=lambda item: item[0] or datetime.min)
            latest_timestamp, latest_point = facility_entries[-1]

            # Calculate facility-level changes by comparing current totals with previous totals
            facility_power_change = None
            facility_emission_change = None
            
            # Get previous facility totals by processing previous timestamp data
            if len(facility_entries) > 1:
                # Get unique timestamps and find previous one
                timestamps = sorted(list(set(item[0] for item in facility_entries if item[0])))
                if len(timestamps) > 1:
                    previous_timestamp = timestamps[-2]
                    
                    # Calculate previous facility totals
                    previous_facility_power = 0.0
                    previous_facility_emissions = 0.0
                    previous_has_power = False
                    previous_has_emissions = False
                    
                    for timestamp, point in facility_entries:
                        if timestamp == previous_timestamp:
                            prev_power = _to_float(point.get("power_mw"))
                            prev_emissions = _to_float(point.get("emissions_t"))
                            
                            if prev_power is not None:
                                previous_facility_power += prev_power
                                previous_has_power = True
                            if prev_emissions is not None:
                                previous_facility_emissions += prev_emissions
                                previous_has_emissions = True
                    
                    # Calculate changes
                    if facility_has_power and previous_has_power:
                        facility_power_change = facility_total_power - previous_facility_power
                    if facility_has_emissions and previous_has_emissions:
                        facility_emission_change = facility_total_emissions - previous_facility_emissions

            # Use facility power change for marker color
            power_change = facility_power_change

            marker_color = _color_from_change(power_change)

            lat = _to_float(latest_point.get("lat"))
            lng = _to_float(latest_point.get("lng"))
            if lat is None or lng is None:
                continue

            facility_name = latest_point.get("facility_name") or facility_id
            network_region = latest_point.get("network_region") or ""
            fuel_tech = latest_point.get("fuel_tech") or ""

            demand_value = _to_float(
                latest_point.get("demand")
                or latest_point.get("demand_mw")
                or latest_point.get("demand_nem")
            )

            total_power_display = (
                f"{facility_total_power:.2f}"
                if facility_has_power
                else None
            )

            total_emissions_display = (
                f"{facility_total_emissions:.2f}"
                if facility_has_emissions
                else None
            )

            # Add facility records for each unit
            for unit_record in unit_records_temp:
                facility_records.append({
                    "facility_id": unit_record["facility_id"],
                    "unit_code": unit_record["unit_code"],
                    "power_mw": format_power_display(unit_record['power_mw']),
                    "demand_mw": format_demand_display(unit_record['demand_mw']),
                    "emissions_t": format_emissions_display(unit_record['emissions_t']),
                    "price": format_price_display(unit_record['price']),
                    "timestamp": format_timestamp_display(unit_record['timestamp']),
                    "facility_power_change": facility_power_change,
                    "facility_emission_change": facility_emission_change,
                })

            summary_records.append(
                {
                    "facility_id": facility_id,
                    "facility_code": facility_id,
                    "facility_name": facility_name,
                    "network_region": network_region,
                    "fuel_tech": fuel_tech.replace("_", " ").title(),
                    "total_power_mw": total_power_display if total_power_display is not None else "N/A",
                    "total_emissions_t": total_emissions_display if total_emissions_display is not None else "N/A",
                }
            )

            map_payload["facilities"][facility_id] = {
                "lat": lat,
                "lng": lng,
                "marker_color": marker_color,
                "facility_name": facility_name,
                "facility_code": facility_id,
                "network_region": network_region,
                "fuel_tech": fuel_tech,
                "demand_value": demand_value,
                "power_change": power_change,
                "total_power_display": total_power_display,
                "total_emissions_display": total_emissions_display,
                "latest_timestamp": latest_timestamp.isoformat() if latest_timestamp else None,
            }

        facility_records.sort(key=lambda row: row["unit_code"])
        summary_records.sort(key=lambda row: row["facility_name"])

        return map_payload, facility_records, summary_records


    @app.callback(
        Output("region-filter", "options"),
        Output("fuel-filter", "options"),
        Input("summary-data-unfiltered", "data"),
    )
    def update_filter_options(summary_data):
        region_options = extract_unique_regions(summary_data)
        fuel_options = extract_unique_fuel_techs(summary_data)
        return region_options, fuel_options


    @app.callback(
        Output("summary-table", "data"),
        Output("filter-status", "children"),
        Input("summary-data-unfiltered", "data"),
        Input("region-filter", "value"),
        Input("fuel-filter", "value"),
    )
    def filter_summary_table(summary_data, selected_region, selected_fuel):
        if not summary_data:
            return [], ""
        
        filtered_data = summary_data.copy()
        total_count = len(filtered_data)
        
        # Filter by region
        filtered_data = filter_summary_data_by_region(filtered_data, selected_region)
        
        # Filter by fuel technology
        filtered_data = filter_summary_data_by_fuel(filtered_data, selected_fuel)
        
        filtered_count = len(filtered_data)
        
        # Create status message
        status = create_filter_status_message(
            filtered_count, total_count, selected_region, selected_fuel
        )
        
        return filtered_data, status


    @app.callback(
        Output("region-filter", "value"),
        Output("fuel-filter", "value"),
        Input("clear-filters", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_filters(n_clicks):
        return None, None


    @app.callback(
        Output("map", "children"),
        Input("map-data-store", "data"),
        Input("selected-facility", "data"),
    )
    def render_map(map_data, selected_facility):
        tile_layer = dl.TileLayer()

        if not map_data:
            return [tile_layer]

        demand_min = map_data.get("demand_min")
        demand_max = map_data.get("demand_max")
        facilities = map_data.get("facilities") or {}

        markers = []
        selected_popup = None

        for facility_id, info in facilities.items():
            lat = _to_float(info.get("lat"))
            lng = _to_float(info.get("lng"))
            if lat is None or lng is None:
                continue

            marker_color = info.get("marker_color") or COLORS['no_change']
            demand_value = info.get("demand_value")
            marker_radius = _radius_from_demand(
                demand_value,
                demand_min,
                demand_max,
            )

            facility_name = info.get("facility_name") or facility_id
            facility_type = info.get("fuel_tech") or "Unknown"
            total_power_display = info.get("total_power_display")
            total_emissions_display = info.get("total_emissions_display")

            popup_content = _build_popup_content(
                facility_name,
                facility_type,
                total_power_display,
                total_emissions_display
            )

            is_selected = selected_facility == facility_id
            outline_color = COLORS['selected_outline'] if is_selected else marker_color
            adjusted_radius = marker_radius + (1.5 if is_selected else 0.0)

            markers.append(
                dl.CircleMarker(
                    id={"type": "facility-marker", "facility_id": facility_id},
                    center=[lat, lng],
                    radius=adjusted_radius,
                    color=outline_color,
                    fillColor=marker_color,
                    fillOpacity=0.85 if is_selected else 0.6,
                    weight=4 if is_selected else 2,
                    opacity=1.0 if is_selected else 0.9,
                    n_clicks=0,
                    children=dl.Popup(popup_content),
                )
            )

            if is_selected:
                selected_popup = dl.Popup(
                    id="selected-popup",
                    position=[lat, lng],
                    autoClose=False,
                    closeButton=True,
                    autoPan=True,
                    children=_build_popup_content(
                        facility_name,
                        facility_type,
                        total_power_display,
                        total_emissions_display,
                    ),
                )

        map_children = [tile_layer] + markers
        if selected_popup is not None:
            map_children.append(selected_popup)

        return map_children


    @app.callback(
        Output("selected-facility", "data"),
        Input({"type": "facility-marker", "facility_id": ALL}, "n_clicks"),
        Input("summary-table", "selected_rows"),
        State("summary-table", "data"),
        State("selected-facility", "data"),
    )
    def update_selected_facility(marker_clicks, summary_selected_rows, summary_data, current_selection):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update

        trigger = ctx.triggered[0]
        prop_id = trigger.get("prop_id", "")

        if prop_id == "summary-table.selected_rows":
            if summary_selected_rows is None:
                return dash.no_update

            if not summary_selected_rows:
                if current_selection is None:
                    return dash.no_update
                return None

            index = summary_selected_rows[0]
            if summary_data is None or index >= len(summary_data):
                return dash.no_update

            facility_id = summary_data[index].get("facility_id")
            if not facility_id:
                return dash.no_update

            if facility_id == current_selection:
                return dash.no_update

            return facility_id

        if not marker_clicks:
            return dash.no_update

        if not trigger.get("value"):
            return dash.no_update

        trigger_id_raw = prop_id.split(".")[0]
        try:
            trigger_id = json.loads(trigger_id_raw)
        except json.JSONDecodeError:
            return dash.no_update

        facility_id = trigger_id.get("facility_id")
        if not facility_id:
            return dash.no_update

        if facility_id == current_selection:
            return dash.no_update

        return facility_id


    @app.callback(
        Output("facility-table-container", "style"),
        Output("facility-table", "data"),
        Output("facility-info-display", "children"),
        Input("selected-facility", "data"),
        State("facility-data-store", "data"),
        State("summary-table", "data"),
    )
    def display_facility_details(selected_facility, facility_records, summary_data):
        if not selected_facility or not facility_records:
            return {"display": "none"}, [], ""

        matching_rows = [row for row in facility_records if row.get("facility_id") == selected_facility]
        if not matching_rows:
            return {"display": "none"}, [], ""

        # Get facility summary info
        facility_summary = None
        if summary_data:
            for summary_row in summary_data:
                if summary_row.get("facility_id") == selected_facility:
                    facility_summary = summary_row
                    break

        # Get facility changes from first row (all rows have same facility changes)
        facility_power_change = matching_rows[0].get("facility_power_change")
        facility_emission_change = matching_rows[0].get("facility_emission_change")

        # Create facility info display
        facility_info_display = ""
        if facility_summary:
            facility_name = facility_summary.get("facility_name", "N/A")
            facility_code = facility_summary.get("facility_code", "N/A")
            fuel_tech = facility_summary.get("fuel_tech", "N/A")
            total_power = facility_summary.get("total_power_mw", "N/A")
            total_emissions = facility_summary.get("total_emissions_t", "N/A")

            # Create display elements for changes
            facility_power_change = facility_power_change if facility_power_change is not None else 0
            power_color = get_change_color(facility_power_change)
            power_symbol = get_change_symbol(facility_power_change)
            power_change_display = html.Div([
                html.Strong("Power Change: ", style={"color": "#495057"}),
                html.Span(f"{facility_power_change:+.2f} MW {power_symbol}", 
                            style={"color": power_color, "fontWeight": "bold"})
            ], style={"display": "inline-block"})

            facility_emission_change = facility_emission_change if facility_emission_change is not None else 0
            emission_color = get_emission_change_color(facility_emission_change)
            emission_symbol = get_emission_change_symbol(facility_emission_change)
            emission_change_display = html.Div([
                html.Strong("Emission Change: ", style={"color": "#495057"}),
                html.Span(f"{facility_emission_change:+.2f} t {emission_symbol}", 
                            style={"color": emission_color, "fontWeight": "bold"})
            ], style={"display": "inline-block"})

            facility_info_display = html.Div([
                html.Div([
                    html.H4(facility_name, style={
                        "margin": "0 0 10px 0", 
                        "color": "#2c3e50", 
                        "fontSize": "1.3rem",
                        "fontWeight": "400",
                        "fontFamily": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
                        "letterSpacing": "0.5px"
                    }),
                    html.Div([
                        html.Span(f"Code: {facility_code}", style={"marginRight": "20px", "color": "#6c757d", "fontSize": "0.9rem"}),
                        html.Span(f"Type: {fuel_tech}", style={"color": "#6c757d", "fontSize": "0.9rem"}),
                    ])
                ]),
                html.Div([
                    html.Div([
                        html.Strong("Total Power: ", style={"color": "#495057"}),
                        html.Span(f"{total_power}", style={"color": "#007bff", "fontWeight": "bold"})
                    ], style={"display": "inline-block", "marginRight": "30px"}),
                    power_change_display,
                ], style={"marginTop": "8px"}),
                html.Div([
                    html.Div([
                        html.Strong("Total Emissions: ", style={"color": "#495057"}),
                        html.Span(f"{total_emissions}", style={"color": "#fd7e14", "fontWeight": "bold"})
                    ], style={"display": "inline-block", "marginRight": "30px"}),
                    emission_change_display,
                ], style={"marginTop": "8px"})
            ])

        rows_for_display = []
        for row in matching_rows:
            clean_row = clean_facility_row_for_display(row)
            rows_for_display.append(clean_row)

        rows_for_display.sort(key=lambda row: row.get("unit_code") or "")

        return {"display": "block"}, rows_for_display, facility_info_display


    @app.callback(
        Output("summary-table", "selected_rows"),
        Input("selected-facility", "data"),
        State("summary-table", "data"),
        State("summary-table", "selected_rows"),
        prevent_initial_call=True,
    )
    def sync_summary_table_selection(selected_facility, summary_data, current_selection):
        if not selected_facility or not summary_data:
            return []

        # Find the index of the selected facility
        target_index = None
        for idx, row in enumerate(summary_data):
            if row.get("facility_id") == selected_facility:
                target_index = idx
                break

        if target_index is None:
            return []

        # Only update if the selection is actually different
        if current_selection and len(current_selection) > 0 and current_selection[0] == target_index:
            return dash.no_update

        return [target_index]