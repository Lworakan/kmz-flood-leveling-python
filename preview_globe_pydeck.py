# filename: preview_globe_pydeck.py

import json
import pydeck as pdk

GEOJSON_PATH = "S1A_20251014_0551.geojson"

def main():
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    layer = pdk.Layer(
        "GeoJsonLayer",
        data,
        stroked=True,
        filled=True,
        get_fill_color=[31, 119, 180, 80],
        get_line_color=[31, 119, 180, 180],
        line_width_min_pixels=1,
        pickable=True,
    )

    # Globe effect via Mapbox raster or the GlobeView if available
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=15.87, longitude=100.99, zoom=4, bearing=0, pitch=30),
        map_style=None,  # set your own basemap if needed
        views=[pdk.View(type="MapView")],  # for Globe, use appropriate Sphere API in your stack
        tooltip={"text": "{name}"},
    )

    # Save to HTML for quick check
    r.to_html("preview_flood_globe.html", open_browser=False)
    print("Wrote preview_flood_globe.html")

if __name__ == "__main__":
    main()
