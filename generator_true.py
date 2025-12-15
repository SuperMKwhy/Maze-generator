import random
import csv
import io

class CenterShyZigzagGenerator:
    def __init__(self, size, seed=None):
        self.size = size
        if seed is not None:
            random.seed(seed)
        
        # Grid format: (x, y) -> [N, E, S, W] (1=Wall, 0=Open)
        # 0:N, 1:E, 2:S, 3:W
        self.grid = {}
        for x in range(size):
            for y in range(size):
                self.grid[(x, y)] = [1, 1, 1, 1]

    def remove_wall(self, c1, c2):
        x1, y1 = c1
        x2, y2 = c2

        # Determine direction
        if x2 == x1 and y2 == y1 + 1:   # c2 is North of c1
            self.grid[c1][0] = 0
            self.grid[c2][2] = 0
        elif x2 == x1 + 1 and y2 == y1: # c2 is East of c1
            self.grid[c1][1] = 0
            self.grid[c2][3] = 0
        elif x2 == x1 and y2 == y1 - 1: # c2 is South of c1
            self.grid[c1][2] = 0
            self.grid[c2][0] = 0
        elif x2 == x1 - 1 and y2 == y1: # c2 is West of c1
            self.grid[c1][3] = 0
            self.grid[c2][1] = 0

    def get_unvisited_neighbors(self, x, y, visited):
        neighbors = []
        # Directions: N, E, S, W
        offsets = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if (nx, ny) not in visited:
                    neighbors.append((nx, ny))
        return neighbors

    def generate(self):
        # Configuration matches JS: start at (0,0)
        start_x, start_y = 0, 0
        
        # Visited set
        visited = set()
        visited.add((start_x, start_y))
        
        # Stack for DFS
        stack = [(start_x, start_y)]
        
        # Center coordinates for heuristic
        cx = (self.size / 2) - 0.5
        cy = (self.size / 2) - 0.5

        while stack:
            curr = stack[-1] # Peek
            curr_x, curr_y = curr
            
            neighbors = self.get_unvisited_neighbors(curr_x, curr_y, visited)
            
            if neighbors:
                # --- 1. Calculate Previous Move Direction ---
                prev_dx, prev_dy = 0, 0
                if len(stack) >= 2:
                    parent = stack[-2]
                    prev_dx = curr_x - parent[0]
                    prev_dy = curr_y - parent[1]

                # --- 2. Score Neighbors (The Heuristic) ---
                scored_neighbors = []
                for n in neighbors:
                    nx, ny = n
                    
                    # Center Shy Score (Distance from center)
                    # Higher distance = Better score (pushes to edges)
                    dist_score = abs(nx - cx) + abs(ny - cy)
                    
                    # Zigzag Bonus
                    # If the move to neighbor requires a turn relative to previous move -> BIG BONUS
                    cur_dx = nx - curr_x
                    cur_dy = ny - curr_y
                    
                    turn_bonus = 0
                    if (prev_dx != 0 or prev_dy != 0):
                        if cur_dx != prev_dx or cur_dy != prev_dy:
                            turn_bonus = 100.0
                    
                    final_score = (dist_score * 10) + turn_bonus
                    scored_neighbors.append({'score': final_score, 'coords': n})

                # Sort: High Score (Turns/Outer) -> Low Score (Straight/Inner)
                scored_neighbors.sort(key=lambda item: item['score'], reverse=True)
                
                best_n = scored_neighbors[0]['coords']
                trap_n = scored_neighbors[-1]['coords'] # The "Worst" neighbor
                
                branched = False

                # --- 3. Trap Logic (The Deceptive Part) ---
                # 25% chance to open BOTH paths if we have choices
                # This creates a junction that looks enticing but might be a dead end later
                if len(neighbors) > 1 and random.random() < 0.0 and best_n != trap_n:
                    # 1. Prepare Trap (Push first, so it's processed LAST in LIFO stack)
                    # This leaves a pending path to explore later
                    self.remove_wall(curr, trap_n)
                    visited.add(trap_n)
                    stack.append(trap_n)
                    
                    # 2. Prepare Best (Push second, so it's processed NOW)
                    self.remove_wall(curr, best_n)
                    visited.add(best_n)
                    stack.append(best_n)
                    
                    branched = True
                
                if not branched:
                    # Standard DFS move
                    self.remove_wall(curr, best_n)
                    visited.add(best_n)
                    stack.append(best_n)
            else:
                # Dead end, backtrack
                stack.pop()
        
        # After generation, ensure the Goal Area logic exists (Standard Micromouse)
        # The algorithm might partition the center, but usually micromouse mazes 
        # have an open center. Let's strictly open the 2x2 center post-gen.
        mid = self.size // 2
        center_cells = [
            (mid - 1, mid - 1), (mid, mid - 1),
            (mid - 1, mid),     (mid, mid)
        ]
        # Connect these 4 cells to each other
        self.remove_wall((mid-1, mid-1), (mid, mid-1))
        self.remove_wall((mid-1, mid-1), (mid-1, mid))
        self.remove_wall((mid, mid), (mid, mid-1))
        self.remove_wall((mid, mid), (mid-1, mid))

    def to_csv_string(self):
        lines = []
        # Format: x y N E S W
        for x in range(self.size):
            for y in range(self.size):
                w = self.grid[(x, y)]
                lines.append(f"{x} {y} {w[0]} {w[1]} {w[2]} {w[3]}")
        return "\n".join(lines)

def generate_and_save(size=32, seed=None):
    # Setup Generator
    gen = CenterShyZigzagGenerator(size, seed)
    gen.generate()
    
    # Metadata
    maze_id = 0 # ID used in your app.py for this algo
    start_pos = "(0, 0)"
    
    # Goals calculation
    mid = size // 2
    g1 = mid - 1
    g2 = mid
    goals_pos = f"[({g1},{g1}),({g1},{g2}),({g2},{g1}),({g2},{g2})]"
    
    # Get Maze Data
    maze_data = gen.to_csv_string()
    
    # Write File
    filename = f"maze_{size}x{size}_centershy_zigzag.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['id', 'size', 'start', 'goals', 'maze'])
        writer.writerow([maze_id, size, start_pos, goals_pos, maze_data])
        
    print(f"Generated {filename} (Seed: {seed if seed else 'Random'})")

if __name__ == "__main__":
    # You can change the seed to get different variations
    # or set seed=None for random every time
    generate_and_save(size=32, seed=145)