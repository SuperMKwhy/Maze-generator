import os
import csv
import io
import json
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_csv', methods=['POST'])
def generate_csv():
    data = request.json
    size = int(data.get('size'))
    grid_data = data.get('grid') # This is a list of lists from JS
    
    # Convert JS grid [r][c][n,e,s,w] to the dictionary format
    final_grid = {}
    for r in range(size):
        for c in range(size):
            # JS sends [N, E, S, W]
            final_grid[(r, c)] = grid_data[r][c]

    # --- UPDATED DYNAMIC LOGIC START ---
    target_start = "(0, 0)" 
    
    # Calculate center dynamically based on size
    # For size 16: mid=8 -> goals are 7,8
    # For size 32: mid=16 -> goals are 15,16
    mid = size // 2
    goals = [
        (mid - 1, mid - 1), 
        (mid - 1, mid), 
        (mid, mid - 1), 
        (mid, mid)
    ]
    
    # Header
    csv_content = 'id,size,start,goals,maze\n'
    
    maze_lines = []
    for r in range(size):
        line_parts = []
        for c in range(size):
            w = final_grid[(r, c)]
            # Format: r c N E S W
            line_parts.append(f"{r} {c} {int(w[0])} {int(w[1])} {int(w[2])} {int(w[3])}")
        maze_lines.append("\n".join(line_parts))
    
    full_maze_string = "\n".join(maze_lines)
    
    # Format nicely for CSV
    maze_col = full_maze_string
    
    # ID 6000 for Zigzag Spiral
    row_str = f'6000,{size},"{target_start}","{str(goals).replace(" ", "")}","{maze_col}"'
    csv_content += row_str
    # --- UPDATED DYNAMIC LOGIC END ---

    # Create an in-memory file to download
    mem_file = io.BytesIO()
    mem_file.write(csv_content.encode('utf-8'))
    mem_file.seek(0)
    
    return send_file(
        mem_file,
        as_attachment=True,
        download_name='maze.csv',
        mimetype='text/csv'
    )

@app.route('/load_csv', methods=['POST'])
def load_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Parse CSV
    stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
    csv_reader = csv.reader(stream)
    
    header = next(csv_reader, None) # Skip header
    row = next(csv_reader, None)    # Get the data row
    
    if not row:
        return jsonify({"error": "Empty CSV"}), 400
    
    try:
        maze_size = int(row[1])
        maze_data_str = row[4] # The big multiline string
        
        # Initialize empty grid
        grid_reconstructed = [[[0,0,0,0] for _ in range(maze_size)] for _ in range(maze_size)]
        
        lines = maze_data_str.split('\n')
        for line in lines:
            parts = line.strip().split(' ')
            if len(parts) >= 6:
                r, c = int(parts[0]), int(parts[1])
                n, e, s, w = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
                if 0 <= r < maze_size and 0 <= c < maze_size:
                    grid_reconstructed[r][c] = [n, e, s, w]
                    
        return jsonify({
            "size": maze_size,
            "grid": grid_reconstructed
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)