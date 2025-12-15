import csv
import os

class MazeProcessor:
    def __init__(self, size):
        self.size = size
        # Grid format: (x, y) -> {'N': 1, 'E': 1, 'S': 1, 'W': 1}
        self.grid = {}
        # Initialize grid with all walls present
        for x in range(size):
            for y in range(size):
                self.grid[(x, y)] = {'N': 1, 'E': 1, 'S': 1, 'W': 1}

    def load_from_string(self, raw_string):
        """Parses the 'maze' column string from CSV into the grid object."""
        lines = raw_string.strip().split('\n')
        for line in lines:
            parts = list(map(int, line.strip().split()))
            # Expecting: x y N E S W
            if len(parts) >= 6:
                x, y, n, e, s, w = parts
                if (x, y) in self.grid:
                    self.grid[(x, y)] = {'N': n, 'E': e, 'S': s, 'W': w}

    def open_wall(self, c1, c2):
        """Removes the wall between cell1 and cell2 if it exists."""
        x1, y1 = c1
        x2, y2 = c2
        
        # Check bounds
        if not (0 <= x1 < self.size and 0 <= y1 < self.size): return
        if not (0 <= x2 < self.size and 0 <= y2 < self.size): return

        # Determine direction and remove wall from both sides
        if x2 == x1 and y2 == y1 + 1: # c2 is North of c1
            self.grid[c1]['N'] = 0
            self.grid[c2]['S'] = 0
        elif x2 == x1 and y2 == y1 - 1: # c2 is South of c1
            self.grid[c1]['S'] = 0
            self.grid[c2]['N'] = 0
        elif x2 == x1 + 1 and y2 == y1: # c2 is East of c1
            self.grid[c1]['E'] = 0
            self.grid[c2]['W'] = 0
        elif x2 == x1 - 1 and y2 == y1: # c2 is West of c1
            self.grid[c1]['W'] = 0
            self.grid[c2]['E'] = 0

    def get_total_wall_count(self):
        total_flags = 0
        for coord in self.grid:
            cell = self.grid[coord]
            total_flags += (cell['N'] + cell['E'] + cell['S'] + cell['W'])
        return total_flags / 2

    def process_perimeter_cell(self, cell, x_min, x_max, y_min, y_max, target_walls):
        """
        Processes a single cell on the perimeter.
        Removes walls connecting to the INTERIOR of the rectangle.
        Preserves walls on the EXTERIOR boundary of the rectangle.
        Returns True if target is reached.
        """
        cx, cy = cell
        
        # Logic: "Remove all wall, *except outer wall*"
        # This means we try to open connections to all 4 neighbors.
        # But we only actually modify the grid if the neighbor is INSIDE or ON the boundary.
        # Since we are iterating the perimeter, 'opening' a wall to a neighbor 
        # that is within the rectangle bounds effectively clears the internal walls 
        # while keeping the outer boundary walls intact (because we don't open 
        # walls to neighbors outside the bounds).

        # West: Open if neighbor is within x_min
        if cx > x_min: self.open_wall((cx, cy), (cx - 1, cy))
        
        # East: Open if neighbor is within x_max
        if cx < x_max: self.open_wall((cx, cy), (cx + 1, cy))
        
        # South: Open if neighbor is within y_min
        if cy > y_min: self.open_wall((cx, cy), (cx, cy - 1))
        
        # North: Open if neighbor is within y_max
        if cy < y_max: self.open_wall((cx, cy), (cx, cy + 1))

        # Check count immediately after processing this cell
        if self.get_total_wall_count() <= target_walls:
            return True
        return False

    def reduce_walls_rectangular_spiral(self, target_walls):
        # 1. Start at Center 2x2
        # For size 32, center is 15,16
        x_min, x_max = 15, 16
        y_min, y_max = 15, 16
        
        print(f"Starting Wall Reduction. Current: {int(self.get_total_wall_count())}, Target: {target_walls}")

        # Initial Block Processing (Standard order)
        # Just ensure the center 2x2 is open to each other
        initial_cells = [(15, 16), (16, 16), (16, 15), (15, 15)]
        for c in initial_cells:
            if self.process_perimeter_cell(c, x_min, x_max, y_min, y_max, target_walls):
                print("Target reached at initial center.")
                return

        # 2. Define Expansion Sequence
        # Pattern deduced: NW, SE, NW, NW, SE, SE, NW, NW, SE, SE...
        # NW = x_min--, y_max++
        # SE = x_max++, y_min--
        
        expansion_steps = ['NW', 'SE'] # Initial single steps
        for _ in range(10): # Repeat double steps enough times to cover grid
            expansion_steps.extend(['NW', 'NW', 'SE', 'SE'])
        
        step_index = 1
        
        for action in expansion_steps:
            # Check bounds to prevent expanding beyond grid size
            if x_min <= 0 and y_max >= self.size - 1 and x_max >= self.size - 1 and y_min <= 0:
                break

            # Apply Expansion
            prev_xmin, prev_xmax, prev_ymin, prev_ymax = x_min, x_max, y_min, y_max
            
            if action == 'NW':
                if x_min > 0: x_min -= 1
                if y_max < self.size - 1: y_max += 1
            elif action == 'SE':
                if x_max < self.size - 1: x_max += 1
                if y_min > 0: y_min -= 1
            
            # If bounds didn't change (e.g. hitting edge), skip
            if (x_min == prev_xmin and x_max == prev_xmax and 
                y_min == prev_ymin and y_max == prev_ymax):
                continue

            # Generate Perimeter Path (Clockwise from Top-Left)
            # 1. Top Edge (x_min, y_max) to (x_max, y_max)
            # 2. Right Edge (x_max, y_max-1) to (x_max, y_min)
            # 3. Bottom Edge (x_max-1, y_min) to (x_min, y_min)
            # 4. Left Edge (x_min, y_min+1) to (x_min, y_max-1)
            
            perimeter_path = []
            
            # Top Edge
            for x in range(x_min, x_max + 1):
                perimeter_path.append((x, y_max))
            
            # Right Edge
            for y in range(y_max - 1, y_min - 1, -1):
                perimeter_path.append((x_max, y))
                
            # Bottom Edge
            for x in range(x_max - 1, x_min - 1, -1):
                perimeter_path.append((x, y_min))
                
            # Left Edge
            for y in range(y_min + 1, y_max):
                perimeter_path.append((x_min, y))
            
            # Process Path
            for cell in perimeter_path:
                stop = self.process_perimeter_cell(cell, x_min, x_max, y_min, y_max, target_walls)
                if stop:
                    print(f"Target reached at cell {cell} during Step {step_index} ({action}).")
                    return
            
            print(f"Step {step_index} ({action}): Expanded to ({x_min}-{x_max}, {y_min}-{y_max}). Walls: {int(self.get_total_wall_count())}")
            step_index += 1

    def to_string(self):
        lines = []
        for x in range(self.size):
            for y in range(self.size):
                c = self.grid[(x, y)]
                lines.append(f"{x} {y} {c['N']} {c['E']} {c['S']} {c['W']}")
        return "\n".join(lines)

def process_maze_file(input_filename, output_filename, target_walls):
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    try:
        with open(input_filename, 'r', newline='') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            row = next(reader, None)
            
            if not row:
                print("Error: CSV file is empty.")
                return

            maze_id = row[0]
            size = int(row[1])
            start_pos = row[2]
            goals_pos = row[3]
            raw_maze_string = row[4]

            print(f"Processing Maze... Size: {size}")

            processor = MazeProcessor(size)
            processor.load_from_string(raw_maze_string)

            # --- KEY LOGIC HERE ---
            processor.reduce_walls_rectangular_spiral(target_walls)
            # ----------------------

            new_maze_string = processor.to_string()

        with open(output_filename, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['id', 'size', 'start', 'goals', 'maze'])
            writer.writerow([maze_id, size, start_pos, goals_pos, new_maze_string])

        print(f"Done. Saved to {output_filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # --- SETUP ---
    INPUT_FILE = 'maze_result.csv'   # Must exist
    OUTPUT_FILE = 'maze_output.csv' # Will be created
    
    # Set your target wall count
    wall_density = 0.4
    TARGET_WALL_COUNT = wall_density * 2 * 32 * 31 
    
    process_maze_file(INPUT_FILE, OUTPUT_FILE, TARGET_WALL_COUNT)