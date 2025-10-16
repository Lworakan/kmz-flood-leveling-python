# KMZ Flood Leveling - 3D Visualization

Visualize flood polygon data from KMZ files as realistic 3D water levels with animation support.

## Features

- ✨ **Realistic water appearance** - Blue gradients, transparency, and water-themed styling
- 🔄 **360° Animation** - Create rotating MP4/GIF animations
- 💾 **Export options** - Save as static PNG or animated video
- 🎨 **Dark theme** - Better contrast for water visualization

## Requirements

```bash
pip install geopandas matplotlib numpy
# For animation support (optional):
pip install pillow  # for GIF
# or ensure ffmpeg is installed for MP4
```

## Usage

### Basic 3D Plot (Interactive)
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz
```

### Save Static Image
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz --output flood_map.png --no-show
```

### Create Rotating Animation (MP4)
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz --output flood_animation.mp4 --animate --no-show
```

### Create Rotating Animation (GIF)
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz --output flood_animation.gif --animate --no-show
```

## Options

- `--kmz`, `-k`: Path to KMZ file (default: `S1A_20251014_0551.kmz`)
- `--output`, `-o`: Output file path for saving (PNG, PDF, MP4, GIF)
- `--no-show`: Skip displaying the interactive window
- `--animate`: Create a 360° rotation animation (requires --output)

## Design Features

The visualization uses:
- **Water surface**: Bright blue (#1e88e5) with 70% transparency for realistic water appearance
- **Water depth**: Deep blue (#0d47a1) sides showing water volume
- **Water edges**: Light blue (#64b5f6) highlights for wave-like effect
- **Dark background**: Navy theme (#0a1929) for better contrast
- **Grid**: Subtle blue grid lines for depth perception

## Example Output

The script extracts polygon data from KMZ files and renders them as extruded 3D shapes representing flood water levels. The animation rotates the view 360° to show all perspectives.

Visualize flood polygons from KMZ files as extruded 3D shapes without requiring DEM (Digital Elevation Model) data.

## Features

- Extract and parse KML from KMZ files
- Display flood polygons as 3D extruded shapes using Poly3DCollection
- Save static images (PNG, PDF, etc.)
- Create 360° rotation animations (MP4, GIF)
- Customizable output and display options

## Requirements

```bash
pip install geopandas matplotlib numpy
```

For animation support:
```bash
# For MP4 (recommended)
brew install ffmpeg  # macOS
# or: sudo apt-get install ffmpeg  # Linux

# For GIF
pip install pillow
```

## Usage

### Display interactive 3D plot
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz
```

### Save static image without displaying
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz --output out/flood_3d.png --no-show
```

### Create 360° rotation animation (MP4)
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz --output out/flood_rotate.mp4 --animate --no-show
```

### Create 360° rotation animation (GIF)
```bash
python plot_kmz_flood.py --kmz S1A_20251014_0551.kmz --output out/flood_rotate.gif --animate --no-show
```

### All options
```bash
python plot_kmz_flood.py --help
```

## Arguments

- `--kmz, -k`: Path to KMZ file (default: S1A_20251014_0551.kmz)
- `--output, -o`: Save output to file (png, pdf, mp4, gif, etc.)
- `--no-show`: Don't open interactive window
- `--animate, -a`: Create 360° rotation animation

## How it works

1. **Extract KML**: Unzips the KMZ and finds the KML file
2. **Parse polygons**: Reads flood polygon geometries using GeoPandas
3. **Extrude in 3D**: Creates top face and vertical side walls using Poly3DCollection
4. **Render**: Displays or saves as static image or rotating animation

## Notes

- The extrusion height is set to 0.1 relative units (adjustable in code)
- Default view: elevation 45°, azimuth -120°
- Animation uses 2° steps (180 frames total) at 20 fps
- MP4 requires ffmpeg; GIF requires pillow

## Example Output

The visualization shows flood-affected areas as extruded 3D polygons with:
- Top surfaces (blue, semi-transparent)
- Vertical side walls (blue, with edges)
- Proper coordinate labels (Longitude, Latitude, Relative height)
- Equal-aspect 3D axes to avoid distortion
