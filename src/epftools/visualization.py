import plotly.express as px
import pandas as pd
import json

def create_choropleth_map(df, location_col, color_col, geojson_path, output_path):
    """
    Create a choropleth map and save it as an HTML file.

    Args:
        df (pd.DataFrame): DataFrame containing the data to plot.
        location_col (str): The name of the column in the DataFrame that contains the location data (e.g., pincodes).
        color_col (str): The name of the column in the DataFrame to use for the color scale.
        geojson_path (str): The path to the GeoJSON file with the map data.
        output_path (str): The path to save the generated HTML file.
    """
    with open(geojson_path) as geofile:
        geojson = json.load(geofile)

    fig = px.choropleth(df, geojson=geojson, color=color_col,
                        locations=location_col, featureidkey=f"properties.{location_col}",
                        projection="mercator"
                       )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html(output_path)
    print(f"Created map: {output_path}")
