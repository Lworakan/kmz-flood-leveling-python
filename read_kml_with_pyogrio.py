# filename: read_kml_with_pyogrio.py

import os
import zipfile
import tempfile
import pyogrio
import geopandas as gpd

KMZ_PATH = "S1A_20251014_0551.kmz"

def extract_kml(kmz_path, td):
    with zipfile.ZipFile(kmz_path) as zf:
        zf.extractall(td)
    for root, _, files in os.walk(td):
        for f in files:
            if f.lower().endswith(".kml"):
                return os.path.join(root, f)
    raise FileNotFoundError("No .kml inside KMZ")

def main():
    if not os.path.exists(KMZ_PATH):
        raise FileNotFoundError(KMZ_PATH)
    with tempfile.TemporaryDirectory() as td:
        kml = extract_kml(KMZ_PATH, td)
        # pyogrio requires GDAL with KML/LIBKML support installed
        try:
            df = pyogrio.read_dataframe(kml, driver="LIBKML")
        except Exception:
            df = pyogrio.read_dataframe(kml, driver="KML")
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
        print(gdf.head())

if __name__ == "__main__":
    main()
