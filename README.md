# Micromouse Adversarial Maze Generator

An interactive web application for generating, visualizing, and exporting maze designs optimized for adversarial pathfinding scenarios. Built with Flask and a web-based GUI.

## Overview

This application allows you to:
- **Create mazes** interactively on a canvas by drawing walls
- **Visualize maze structures** in real-time
- **Generate maze data** in CSV format compatible with Micromouse competition standards
- **Load and edit** existing maze files
- **Test maze layouts** with pathfinding algorithms
- **Export mazes** for use in simulations or competitions

## Project Structure

```
Micromouse/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── README.md             # This file
├── generator_true.py       # maze generator
└── *.csv                 # Maze data files
```

## Prerequisites

- **Python 3.7+**
- **pip** (Python package manager)
- A modern web browser (Chrome, Firefox, Edge, Safari)

## Installation

### 1. Clone or navigate to the project directory

```bash
cd path/to/Micromouse
```

### 2. Install dependencies

Create a virtual environment (recommended):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

**Key dependencies:**
- Flask - Web framework
- NumPy - Numerical computing
- Pandas - Data manipulation
- OpenCV - Image processing
- (and many others for data science/ML tasks)

## Running the Application

### Start the Flask Server

```bash
python app.py
```

You should see output similar to:

```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Access the Web Interface

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see the **Adversarial Maze Generator** interface with a canvas and control panel.

## Usage Guide

### Creating a Maze

1. **Select Grid Size**: Use the dropdown menu to choose a maze size (e.g., 16x16, 32x32)
2. **Draw Walls**: Click and drag on the canvas to draw walls
   - Click on cells to toggle walls
   - Walls are shown as black lines on the grid
3. **Reset**: Use the "Reset" button to clear the current maze

### Saving a Maze

1. Click the **"Save CSV"** button
2. A CSV file named `maze.csv` will be downloaded
3. The file includes:
   - Maze size
   - Start position (0, 0)
   - Goal positions (center 2x2 cells)
   - Cell wall configuration (North, East, South, West directions)

### Loading a Maze

1. Click the **"Load CSV"** button
2. Select a previously saved maze file
3. The maze will be reconstructed and displayed on the canvas
4. You can now edit or analyze it

### Testing/Running Pathfinding

1. Click the **"Run Test"** button to execute a pathfinding algorithm
2. The algorithm will navigate from start to goal
3. Results and metrics are displayed in the score box

### Additional Features

- **Stop**: Halt an ongoing algorithm execution
- **Score Box**: Displays statistics about the maze and algorithm performance
  - Distance traveled
  - Number of turns
  - Optimality metrics

## CSV Maze Format

Exported mazes follow this CSV structure:

```
id,size,start,goals,maze
6000,32,"(0, 0)","[(15,15),(15,16),(16,15),(16,16)]","0 0 0 1 0 1\n0 1 0 1 0 1\n..."
```

- **id**: Unique identifier (6000 for generated mazes)
- **size**: Maze dimensions (e.g., 32 for 32x32)
- **start**: Starting position as a coordinate tuple
- **goals**: List of goal cell coordinates (typically center 2x2 cells)
- **maze**: Multi-line string where each line is: `row col N E S W`
  - N, E, S, W: Wall presence (1 = wall exists, 0 = open)

## Existing Maze Files

The project includes several pre-built maze templates:

- `maze_32x32.csv` - Standard 32x32 maze
- `maze_32x32_circular.csv` - Circular pattern design
- `maze_32x32_rectangular.csv` - Rectangular pattern design
- `maze_32x32_adjusted.csv` - Modified variant
- `maze_32x32_iterative.csv` - Iteratively generated maze
- `maze_32x32_fixed.csv` - Fixed benchmark maze
- `flood_nightmare.csv` - Challenging flood-fill scenario
- `testMaze.csv` - Small test maze

Load any of these by clicking **"Load CSV"** and selecting the file.

## Notebook Usage

The `generator.ipynb` Jupyter notebook contains:

- Maze generation algorithms
- Visualization utilities
- Analysis tools for maze complexity
- Batch maze generation

To use the notebook:

```bash
jupyter notebook generator.ipynb
```

## Generator (`generator_true.py`)

This repository includes `generator_true.py`, an offline maze generator implementing the `CenterShyZigzagGenerator`.

- Algorithm summary:
  - Generates a perfect maze using a DFS-style algorithm.
  - "Center-shy" heuristic favors cells farther from the maze center.
  - "Zigzag" gives a large bonus for moves that turn relative to the previous move, producing winding corridors.
  - After generation the 2x2 center cells are explicitly connected (Micromouse goal area).

- Running the generator:

```bash
python generator_true.py
```

This runs `generate_and_save(size=32, seed=145)` by default and creates a file named `maze_32x32_centershy_zigzag.csv`.

- Notes:
  - The generated CSV uses `id = 0` by default (edit `generate_and_save()` if you need a different id).
  - To reproduce a maze, set `seed` in `generate_and_save()` or call the function from another script.
  - Filename format: `maze_{size}x{size}_centershy_zigzag.csv`.


## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

```bash
python app.py  # Flask will automatically try port 5001, 5002, etc.
```

Or modify the port in `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

### File Upload Issues

- Ensure the CSV file follows the correct format
- Check that the maze size matches the grid data
- Try loading a template file first to verify functionality

### Browser Compatibility

- **Recommended**: Chrome, Firefox, Edge (latest versions)
- **Canvas requires**: HTML5 support
- **JavaScript**: ES6 or higher

### Dependencies Not Found

Reinstall dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## Development

### Running in Debug Mode

Edit `app.py` and ensure:

```python
if __name__ == '__main__':
    app.run(debug=True)
```

This enables auto-reload on file changes and detailed error pages.

### Modifying the UI

Edit `templates/index.html` to change:
- Layout and styling
- Button functionality
- Canvas behavior
- Form fields

### Extending Backend Features

Edit `app.py` to add new routes and functionality:
- Add new pathfinding algorithms
- Implement maze generation methods
- Create analysis endpoints

## License

This project is for educational purposes in the INC242 course (Micromouse competition).

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed: `pip list | grep flask`
3. Ensure the Flask server is running on the correct port
4. Check browser console (F12) for JavaScript errors

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Course**: INC242 - Micromouse
