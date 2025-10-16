"""Plot KMZ flood polygons as extruded 3D-like shapes (no DEM).

This script can extract a KML from a KMZ and plot polygons with a small
extrusion to give 3D perception. Use --output to save the figure to a file
and --no-show to skip displaying the interactive window.
"""

import os
import zipfile
import tempfile
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
import geopandas as gpd

KMZ_PATH = "S1A_20251014_0551.kmz"


def extract_kml(kmz_path, td):
    with zipfile.ZipFile(kmz_path) as zf:
        zf.extractall(td)
    for f in os.listdir(td):
        if f.lower().endswith(".kml"):
            return os.path.join(td, f)
    raise FileNotFoundError("No .kml inside KMZ")


def read_polygons(kml_path):
    try:
        gdf = gpd.read_file(kml_path, driver="LIBKML")
    except Exception:
        gdf = gpd.read_file(kml_path)
    gdf = gdf[gdf.geometry.notnull()]
    gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
    return gdf


def _set_axes_equal(ax):
    """Make 3D axes have equal scale.

    This is a helper to avoid distorted-looking extrusions.
    """
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


def plot_extruded_3d(gdf, outpath: str | None = None, show: bool = True, animate: bool = False, 
                     show_depth_labels: bool = False, depth_column: str = None):
    """Plot the GeoDataFrame polygons with a small extrusion and depth-based coloring.

    Args:
        gdf: GeoDataFrame with Polygon or MultiPolygon geometries.
        outpath: if provided, save the figure to this path.
        show: if True, call plt.show(); otherwise close the figure.
        animate: if True, create a rotating animation instead of static plot.
        show_depth_labels: if True, add text labels showing depth at polygon centroids.
        depth_column: name of the column in gdf containing depth values (in meters).
                      If None, will try 'depth', 'DEPTH', 'water_depth', or generate random depths.
    """
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")
    
    # Set dark background for better water contrast
    ax.set_facecolor('#0a1929')
    fig.patch.set_facecolor('#0f2537')
    
    ax.set_title("Flood Water Level Visualization", fontsize=16, color='white', pad=20)

    # base z for all polygons
    base_z = 0.0
    extrude_h = 0.15  # water depth height

    if gdf is None or len(gdf) == 0:
        print("Warning: GeoDataFrame is empty — saving/plotting an empty figure.")

    # Extract or generate depth values
    if depth_column and depth_column in gdf.columns:
        depths = gdf[depth_column].values
    else:
        # Try common depth column names
        for col in ['depth', 'DEPTH', 'water_depth', 'Depth', 'flood_depth']:
            if col in gdf.columns:
                depths = gdf[col].values
                print(f"Using depth column: {col}")
                break
        else:
            # Generate random depths for demonstration (0.5 to 3.0 meters)
            depths = np.random.uniform(0.5, 3.0, len(gdf))
            print("No depth column found - using random depths (0.5-3.0m) for visualization")
    
    # Normalize depths for color mapping (0=light blue, 1=dark blue)
    min_depth = np.min(depths)
    max_depth = np.max(depths)
    if max_depth > min_depth:
        normalized_depths = (depths - min_depth) / (max_depth - min_depth)
    else:
        normalized_depths = np.ones_like(depths) * 0.5
    
    print(f"Depth range: {min_depth:.2f}m to {max_depth:.2f}m")

    # track min/max for axis limits
    xs = []
    ys = []

    # Water color palette - realistic flood water colors with depth variation
    
    for idx, geom in enumerate(gdf.geometry):
        if geom.geom_type == "Polygon":
            polys = [geom]
        else:
            polys = list(geom.geoms)

        # Get depth and color for this feature
        depth = depths[idx]
        norm_depth = normalized_depths[idx]
        
        # Color mapping: light blue (shallow) to dark blue (deep)
        # Using a gradient from cyan/light blue to navy/dark blue
        water_color = plt.cm.Blues(0.4 + norm_depth * 0.6)  # 0.4 to 1.0 range in Blues colormap
        water_rgba = tuple(water_color[:3]) + (0.7,)
        side_rgba = tuple(c * 0.7 for c in water_color[:3]) + (0.6,)
        edge_color = tuple(c * 1.2 if c * 1.2 <= 1 else 1 for c in water_color[:3])
        
        for poly in polys:
            exterior = poly.exterior
            coords = list(exterior.coords)
            # separate x and y arrays for limits
            x = [c[0] for c in coords]
            y = [c[1] for c in coords]
            xs.extend(x)
            ys.extend(y)

            # Use actual depth to set extrusion height
            actual_extrude_h = depth * 0.05  # scale depth to reasonable visual height
            
            # create top and bottom faces as 3D polygons
            top = [(xi, yi, base_z + actual_extrude_h) for xi, yi in zip(x, y)]
            bottom = [(xi, yi, base_z) for xi, yi in zip(x, y)]

            # Add water surface (top face) with depth-based color
            poly_top = Poly3DCollection([top], facecolor=water_rgba, alpha=0.7, linewidths=0.8)
            poly_top.set_edgecolor(edge_color)
            ax.add_collection3d(poly_top)

            # Add bottom face (submerged ground) - darker
            poly_bottom = Poly3DCollection([bottom], facecolor='#1a1a1a', alpha=0.3, linewidths=0)
            ax.add_collection3d(poly_bottom)

            # add side walls as quads between consecutive vertices (water depth)
            side_quads = []
            n = len(coords)
            for i in range(n - 1):
                x0, y0 = coords[i][0], coords[i][1]
                x1, y1 = coords[i + 1][0], coords[i + 1][1]
                quad = [
                    (x0, y0, base_z),
                    (x1, y1, base_z),
                    (x1, y1, base_z + actual_extrude_h),
                    (x0, y0, base_z + actual_extrude_h),
                ]
                side_quads.append(quad)

            # Water sides with depth-based gradient
            poly_sides = Poly3DCollection(side_quads, facecolor=side_rgba, alpha=0.6, linewidths=0.3)
            poly_sides.set_edgecolor(edge_color)
            ax.add_collection3d(poly_sides)
            
            # Add depth label at centroid if requested
            if show_depth_labels:
                centroid = poly.centroid
                ax.text(centroid.x, centroid.y, base_z + actual_extrude_h + 0.02, 
                       f'{depth:.1f}m', fontsize=9, color='white', weight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='navy', alpha=0.8, edgecolor='cyan'),
                       ha='center', va='bottom')

    # Style axis labels with water theme
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_zlabel("Water Depth (m)")
    
    # Customize tick colors
    ax.tick_params(colors='white', labelsize=9)
    
    # Grid styling for water effect
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('#1e3a5f')
    ax.yaxis.pane.set_edgecolor('#1e3a5f')
    ax.zaxis.pane.set_edgecolor('#1e3a5f')
    ax.grid(True, linestyle='--', alpha=0.3, color='#4a90e2')

    # set limits based on data with a small margin
    if xs and ys:
        margin = 0.01 * max(max(xs) - min(xs), max(ys) - min(ys)) if len(xs) > 1 and len(ys) > 1 else 0.001
        ax.set_xlim(min(xs) - margin, max(xs) + margin)
        ax.set_ylim(min(ys) - margin, max(ys) + margin)
        ax.set_zlim(-0.02, max_depth * 0.06)  # Scale z-axis based on max depth

    _set_axes_equal(ax)
    ax.view_init(elev=45, azim=-120)
    plt.tight_layout()

    if animate:
        # Create 360° rotation animation
        print("Creating 360° rotation animation...")
        
        def update(frame):
            ax.view_init(elev=45, azim=frame)
            return ax,

        frames = np.arange(0, 360, 2)  # 2-degree steps = 180 frames
        anim = animation.FuncAnimation(fig, update, frames=frames, interval=50, blit=False)

        if outpath:
            outpath = Path(outpath)
            outpath.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine format from extension
            ext = outpath.suffix.lower()
            if ext == '.gif':
                print(f"Saving animation as GIF to: {outpath.absolute()}")
                anim.save(outpath, writer='pillow', fps=20, dpi=100)
            else:
                # Default to MP4
                if ext != '.mp4':
                    outpath = outpath.with_suffix('.mp4')
                print(f"Saving animation as MP4 to: {outpath.absolute()}")
                anim.save(outpath, writer='ffmpeg', fps=20, dpi=100)
            print(f"✓ Animation saved successfully!")

        if show:
            print("Displaying animated figure...")
            plt.show()
        else:
            print("Skipping interactive display (--no-show)")
            plt.close(fig)
    else:
        # Static image
        if outpath:
            outpath = Path(outpath)
            outpath.parent.mkdir(parents=True, exist_ok=True)
            print(f"Saving figure to: {outpath.absolute()}")
            fig.savefig(outpath, dpi=200, bbox_inches="tight")
            print(f"✓ Saved figure to: {outpath.absolute()}")

        if show:
            print("Displaying interactive figure...")
            plt.show()
        else:
            print("Skipping interactive display (--no-show)")
            plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Plot KMZ flood polygons with a quick 3D extrusion (no DEM).")
    parser.add_argument("--kmz", "-k", default=KMZ_PATH, help="Path to KMZ file (default: %(default)s)")
    parser.add_argument("--output", "-o", default=None, help="If provided, save the figure to this file path (png, pdf, mp4, gif, etc.)")
    parser.add_argument("--no-show", action="store_true", help="Do not open the interactive window after plotting")
    parser.add_argument("--animate", "-a", action="store_true", help="Create a 360° rotation animation (MP4 or GIF)")
    args = parser.parse_args()

    print(f"🔧 Arguments parsed:")
    print(f"   KMZ: {args.kmz}")
    print(f"   Output: {args.output}")
    print(f"   No-show: {args.no_show}")
    print(f"   Animate: {args.animate}")
    print()

    if not os.path.exists(args.kmz):
        raise FileNotFoundError(f"KMZ not found: {args.kmz}")
    with tempfile.TemporaryDirectory() as td:
        kml = extract_kml(args.kmz, td)
        gdf = read_polygons(kml)

    print(f"📊 Loaded {len(gdf)} flood polygons from KMZ")
    plot_extruded_3d(gdf, outpath=args.output, show=not args.no_show, animate=args.animate)


if __name__ == "__main__":
    main()
