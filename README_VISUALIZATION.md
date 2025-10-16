# 3D Flood Water Level Visualization

This tool visualizes flood data from KMZ files as 3D extruded polygons with depth-based coloring, creating realistic water-themed visualizations.

## Features

✨ **Depth-Based Coloring**: Automatically color-codes flood areas from light blue (shallow) to dark blue (deep)
📊 **Depth Labels**: Optional labels showing water depth at each polygon centroid
🎬 **360° Animation**: Create rotating animations for presentations
💾 **Export**: Save as high-resolution PNG, PDF, or animated MP4/GIF
🌊 **Realistic Water Theme**: Dark background with glossy water surfaces and gradient effects

## Installation

```bash
# Required dependencies
pip install geopandas matplotlib numpy

# Optional for animation
pip install pillow  # for GIF export
```

## Usage

### Basic Static Plot (Interactive)
```bash
python plot_kmz_flood.py
```

### Save Static Plot Without Showing
```bash
python plot_kmz_flood.py --output out/flood_map.png --no-show
```

### Show Depth Labels
```bash
python plot_kmz_flood.py --show-labels
```

### Create 360° Rotation Animation
```bash
# Save as MP4
python plot_kmz_flood.py --animate --output out/flood_animation.mp4 --no-show

# Save as GIF
python plot_kmz_flood.py --animate --output out/flood_animation.gif --no-show
```

### Use Custom Depth Column
If your KMZ has a specific attribute column with depth values:
```bash
python plot_kmz_flood.py --depth-column "water_level" --show-labels
```

### All Options Combined
```bash
python plot_kmz_flood.py \
  --kmz S1A_20251014_0551.kmz \
  --output out/flood_viz.png \
  --show-labels \
  --depth-column depth \
  --no-show
```

## Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--kmz` | `-k` | Path to KMZ file | `S1A_20251014_0551.kmz` |
| `--output` | `-o` | Output file path (png, pdf, mp4, gif) | None (show only) |
| `--no-show` | - | Don't display interactive window | False |
| `--animate` | - | Create 360° rotation animation | False |
| `--show-labels` | - | Show depth values at polygon centroids | False |
| `--depth-column` | - | Column name containing depth values | Auto-detect |

## Depth Data

The tool handles depth data in three ways:

1. **Specified Column**: Use `--depth-column` to specify the attribute column name
2. **Auto-Detection**: Automatically searches for common column names:
   - `depth`, `DEPTH`, `water_depth`, `Depth`, `flood_depth`
3. **Random Values**: If no depth column found, generates random depths (0.5-3.0m) for demonstration

## Output Formats

- **PNG**: High-resolution raster (default DPI: 200)
- **PDF**: Vector format for print
- **MP4**: Smooth 360° rotation video (requires ffmpeg)
- **GIF**: Animated image (larger file size)

## Examples

### Example 1: Quick Preview
```bash
python plot_kmz_flood.py
```

### Example 2: Publication-Ready Static Image
```bash
python plot_kmz_flood.py \
  --output publication/flood_depth_map.pdf \
  --show-labels \
  --no-show
```

### Example 3: Presentation Animation
```bash
python plot_kmz_flood.py \
  --animate \
  --output presentation/flood_rotation.mp4 \
  --no-show
```

### Example 4: Social Media GIF
```bash
python plot_kmz_flood.py \
  --animate \
  --output social/flood_demo.gif \
  --show-labels \
  --no-show
```

## Visualization Details

### Color Scheme
- **Water Surface**: Gradient from light blue (#1e88e5) to deep blue (#0d47a1)
- **Water Edges**: Light cyan highlights (#64b5f6)
- **Background**: Dark navy theme for contrast
- **Depth Labels**: White text on navy boxes with cyan borders

### 3D Settings
- **View Angle**: Elevation 45°, Azimuth -120°
- **Extrusion Scale**: Depth × 0.05 (visual scale factor)
- **Transparency**: 70% for water surface, 60% for sides

### Animation Settings
- **Rotation**: Full 360° around vertical axis
- **Frame Rate**: 2° per frame (180 total frames)
- **Duration**: ~9 seconds at 20 FPS

## Troubleshooting

### No Output File Created
- Check that the `out/` directory exists or use a different path
- Ensure you have write permissions
- For animations, ensure ffmpeg is installed: `brew install ffmpeg` (macOS)

### Empty/Blank Figure
- Verify the KMZ contains polygon geometries
- Check console output for geometry count
- Try with `--show-labels` to see if data is present

### Depth Column Not Found
- Check your KMZ attributes: open in QGIS or examine with geopandas
- Use `--depth-column` to specify the correct column name
- Tool will use random depths if column not found

### Animation Not Saving
- MP4 requires ffmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Ubuntu)
- Try GIF format instead: `--output file.gif`
- Check console for error messages

## Technical Notes

- **CRS Handling**: Automatically sets EPSG:4326 if CRS is missing
- **Geometry Types**: Supports both Polygon and MultiPolygon
- **Memory**: Large KMZ files may require significant RAM for rendering
- **Performance**: Animation creation can take 30-60 seconds for complex geometries

## Future Enhancements

- [ ] Support for DEM integration (actual elevation data)
- [ ] Custom color palettes
- [ ] Interactive HTML output with plotly
- [ ] Time-series animation from multiple KMZ files
- [ ] Configurable extrusion scale factor

## References

- GISTDA Sphere 3D Layer Documentation: https://sphere.gistda.or.th/docs/js/3d-layer
- Matplotlib 3D Documentation: https://matplotlib.org/stable/tutorials/toolkits/mplot3d.html
- GeoPandas KML Support: https://geopandas.org/en/stable/docs/user_guide/io.html

## License

MIT License - Feel free to use and modify for your projects.
