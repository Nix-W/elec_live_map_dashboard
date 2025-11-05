"""
Utility functions for data processing and transformations.
"""
import math
from datetime import datetime
from dash import html
from config import COLORS, BASE_MARKER_RADIUS, MAX_MARKER_RADIUS


def _parse_timestamp(ts_value):
    """Parse timestamp value and return datetime object."""
    if not ts_value:
        return None
    try:
        return datetime.fromisoformat(str(ts_value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _to_float(value):
    """Convert value to float, return None if conversion fails."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _color_from_change(change):
    """Return marker color based on change value."""
    if change is None:
        return COLORS['unknown']
    elif change > 0:
        return COLORS['increase']
    elif change < 0:
        return COLORS['decrease']
    return COLORS['no_change']


def _radius_from_demand(demand_value, demand_min, demand_max):
    """Calculate marker radius based on demand value and range."""
    demand_float = _to_float(demand_value)
    if demand_float is None or demand_min is None or demand_max is None:
        return BASE_MARKER_RADIUS

    if demand_max <= demand_min:
        return BASE_MARKER_RADIUS

    normalized = (demand_float - demand_min) / (demand_max - demand_min)
    normalized = max(0.0, min(1.0, normalized))
    return BASE_MARKER_RADIUS + normalized * (MAX_MARKER_RADIUS - BASE_MARKER_RADIUS)


def _build_popup_content(facility_name, facility_type=None, total_power=None, total_emissions=None):
    """Build popup content for map markers."""
    title = f"{facility_name} [{facility_type.replace('_', ' ').title()}]"
    subtitle = ''
    if total_power is not None:
        subtitle = f"{total_power} MW"
    if total_emissions is not None:
        subtitle += f" · {total_emissions} t Emissions"

    return html.Div(
        [
            html.H3(
                title,
                style={"fontSize": "0.85rem", "marginBottom": "4px"},
            ),
            html.Div(subtitle, style={"fontSize": "0.8rem"}),
        ],
        style={"minWidth": "110px", "textAlign": "center"},
    )


def format_power_display(power_value):
    """Format power value for display."""
    if power_value is not None:
        return f"{power_value:.2f}"
    return "N/A"


def format_demand_display(demand_value):
    """Format demand value for display."""
    if demand_value is not None:
        return f"{demand_value:.2f}"
    return "N/A"


def format_emissions_display(emissions_value):
    """Format emissions value for display."""
    if emissions_value is not None:
        return f"{emissions_value:.2f}"
    return "N/A"


def format_price_display(price_value):
    """Format price value for display."""
    if price_value is not None and not math.isnan(price_value):
        return f"${price_value:.2f}"
    return "N/A"


def format_timestamp_display(timestamp):
    """Format timestamp for display."""
    if timestamp:
        return timestamp.isoformat()
    return "Unknown"


def get_change_color(change_value):
    """Get color for change value display."""
    if change_value > 0:
        return "#28a745"  # green
    elif change_value < 0:
        return "#dc3545"  # red
    else:
        return "#6c757d"  # grey


def get_change_symbol(change_value):
    """Get symbol for change value display."""
    if change_value > 0:
        return "↗"
    elif change_value < 0:
        return "↘"
    else:
        return "→"


def get_emission_change_color(change_value):
    """Get color for emission change (opposite of power change - decrease is good)."""
    if change_value < 0:
        return "#28a745"  # green for decrease
    elif change_value > 0:
        return "#dc3545"  # red for increase
    else:
        return "#6c757d"  # grey for no change


def get_emission_change_symbol(change_value):
    """Get symbol for emission change display."""
    if change_value < 0:
        return "↘"
    elif change_value > 0:
        return "↗"
    else:
        return "→"


def clean_facility_row_for_display(row):
    """Clean facility row data for display by removing internal fields."""
    row_copy = row.copy()
    row_copy.pop("facility_id", None)
    row_copy.pop("facility_power_change", None)
    row_copy.pop("facility_emission_change", None)
    return row_copy


def extract_unique_regions(summary_data):
    """Extract unique network regions from summary data."""
    if not summary_data:
        return []
    
    regions = sorted(list(set(
        row.get("network_region", "").strip() 
        for row in summary_data 
        if row.get("network_region", "").strip()
    )))
    
    return [{"label": region, "value": region} for region in regions]


def extract_unique_fuel_techs(summary_data):
    """Extract unique fuel technologies from summary data."""
    if not summary_data:
        return []
    
    fuel_techs = sorted(list(set(
        row.get("fuel_tech", "").strip() 
        for row in summary_data 
        if row.get("fuel_tech", "").strip()
    )))
    
    return [{"label": fuel, "value": fuel} for fuel in fuel_techs]


def filter_summary_data_by_region(data, selected_region):
    """Filter summary data by selected region."""
    if not selected_region:
        return data
    return [row for row in data if row.get("network_region") == selected_region]


def filter_summary_data_by_fuel(data, selected_fuel):
    """Filter summary data by selected fuel technology."""
    if not selected_fuel:
        return data
    return [row for row in data if row.get("fuel_tech") == selected_fuel]


def create_filter_status_message(filtered_count, total_count, selected_region, selected_fuel):
    """Create status message for applied filters."""
    if selected_region or selected_fuel:
        filters_applied = []
        if selected_region:
            filters_applied.append(f"Region: {selected_region}")
        if selected_fuel:
            filters_applied.append(f"Fuel: {selected_fuel}")
        filter_text = " | ".join(filters_applied)
        return f"Showing {filtered_count} of {total_count} facilities ({filter_text})"
    else:
        return f"Showing all {total_count} facilities"