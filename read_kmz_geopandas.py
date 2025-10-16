# filename: kmz_to_geojson.py

import os
import json
import zipfile
import tempfile
import geopandas as gpd

KMZ_PATH = "S1A_20251014_0551.kmz"
OUT_GEOJSON = "S1A_20251014_0551.geojson"

def extract_kml_from_kmz(kmz_path: str, tmpdir: str) -> str:
    if not os.path.exists(kmz_path):
        raise FileNotFoundError(f"Not found: {kmz_path}")
    with zipfile.ZipFile(kmz_path) as zf:
        zf.extractall(tmpdir)
    # find first kml
    for root, _, files in os.walk(tmpdir):
        for f in files:
            if f.lower().endswith(".kml"):
                return os.path.join(root, f)
    raise FileNotFoundError("No .kml inside KMZ")

def read_kml_to_gdf(kml_path: str) -> gpd.GeoDataFrame:
    # Try LIBKML first, then KML (depends on GDAL build)
    try:
        gdf = gpd.read_file(kml_path, driver="LIBKML")
    except Exception:
        gdf = gpd.read_file(kml_path, driver="KML")
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    else:
        gdf = gdf.to_crs(epsg=4326)
    # Optional: clean small invalid geometries
    gdf["geometry"] = gdf["geometry"].buffer(0)
    gdf = gdf[gdf.geometry.is_valid]
    return gdf

def export_geojson(gdf: gpd.GeoDataFrame, out_path: str):
    # Ensure FeatureCollection with EPSG:4326 coordinates
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"Wrote GeoJSON: {out_path} ({len(gdf)} features)")

def main():
    with tempfile.TemporaryDirectory() as td:
        kml_path = extract_kml_from_kmz(KMZ_PATH, td)
        gdf = read_kml_to_gdf(kml_path)
    export_geojson(gdf, OUT_GEOJSON)

if __name__ == "__main__":
    main()
