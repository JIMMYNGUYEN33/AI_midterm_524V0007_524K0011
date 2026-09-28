class Board:
    def __init__(self, filepath):
        self.grid = []
        self.agent_pos = None
        self.boxes = set()
        self.targets = set()
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        max_len = max(len(line.strip('\n')) for line in lines)
        for r, line in enumerate(lines):
            row = list(line.strip('\n').ljust(max_len, ' '))
            for c, char in enumerate(row):
                if char == 'A':
                    self.agent_pos = (r, c)
                    row[c] = ' ' 
                elif char == 'B':
                    self.boxes.add((r, c))
                    row[c] = ' '
                elif char == 'D':
                    self.targets.add((r, c))
                    row[c] = 'D'
                elif char == 'C':
                    self.boxes.add((r, c))
                    self.targets.add((r, c))
                    row[c] = 'D' 
            self.grid.append(row)
        
        self.rows = len(self.grid)
        self.cols = max_len