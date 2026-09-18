import heapq
from collections import deque

ACTIONS = {
    'Up': (-1, 0),
    'Down': (1, 0),
    'Left': (0, -1),
    'Right': (0, 1)
}

class SokobanProblem:
    def __init__(self, map_file_path):
        self.walls = set()
        self.goals = set()
        self.initial_boxes = set()
        self.initial_agent = None
        self.load_map(map_file_path)
        self.dist_matrix = self._compute_all_goal_distances()

    def load_map(self, file_path):
        with open(file_path, 'r') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]
        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                if char == '%':
                    self.walls.add((r, c))
                elif char == 'A':
                    self.initial_agent = (r, c)
                elif char == 'B':
                    self.initial_boxes.add((r, c))
                elif char == 'D':
                    self.goals.add((r, c))
                elif char == 'C':
                    self.goals.add((r, c))
                    self.initial_boxes.add((r, c))

    def _compute_all_goal_distances(self):
        """Tính ma trận khoảng cách đường đi thực tế từ mọi ô tới các đích D (tránh tường)"""
        dist_matrix = {}
        for goal in self.goals:
            dist_matrix[goal] = {}
            queue = deque([(goal, 0)])
            visited = {goal}
            while queue:
                curr, dist = queue.popleft()
                dist_matrix[goal][curr] = dist
                cr, cc = curr
                for dr, dc in ACTIONS.values():
                    nr, nc = cr + dr, cc + dc
                    nxt = (nr, nc)
                    if nxt not in self.walls and nxt not in visited:
                        visited.add(nxt)
                        queue.append((nxt, dist + 1))
        return dist_matrix

    def is_goal(self, boxes):
        return boxes == self.goals

    def get_successors(self, state):
        agent_pos, boxes = state
        successors = []
        ar, ac = agent_pos

        for action_name, (dr, dc) in ACTIONS.items():
            nr, nc = ar + dr, ac + dc
            next_agent = (nr, nc)

            if next_agent in self.walls:
                continue

            if next_agent in boxes:
                box_nr, box_nc = nr + dr, nc + dc
                next_box = (box_nr, box_nc)
                if next_box in self.walls or next_box in boxes:
                    continue
                new_boxes = set(boxes)
                new_boxes.remove(next_agent)
                new_boxes.add(next_box)
                next_state = (next_agent, frozenset(new_boxes))
                successors.append((next_state, action_name, 1))
            else:
                next_state = (next_agent, boxes)
                successors.append((next_state, action_name, 1))

        return successors

    def heuristic(self, state):
        """
        Heuristic: Tổng khoảng cách BFS ngắn nhất từ mỗi thùng tới ô đích gần nhất.
        Đảm bảo admissibility & consistency, không dùng Euclidean/Manhattan.
        """
        _, boxes = state
        total_h = 0
        for b in boxes:
            min_dist = float('inf')
            for g in self.goals:
                if b in self.dist_matrix[g]:
                    d = self.dist_matrix[g][b]
                    if d < min_dist:
                        min_dist = d
            total_h += (min_dist if min_dist != float('inf') else 100)
        return total_h


def solve_ucs(problem):
    start_state = (problem.initial_agent, frozenset(problem.initial_boxes))
    pq = []
    # (g_cost, tie_breaker, current_state, path)
    count = 0
    heapq.heappush(pq, (0, count, start_state, []))
    explored = {}
    nodes_expanded = 0

    while pq:
        g, _, state, path = heapq.heappop(pq)
        nodes_expanded += 1

        if problem.is_goal(state[1]):
            return path, g, nodes_expanded

        if state in explored and explored[state] <= g:
            continue
        explored[state] = g

        for next_state, action, cost in problem.get_successors(state):
            new_g = g + cost
            if next_state not in explored or new_g < explored[next_state]:
                count += 1
                heapq.heappush(pq, (new_g, count, next_state, path + [action]))

    return None, float('inf'), nodes_expanded


def solve_astar(problem):
    start_state = (problem.initial_agent, frozenset(problem.initial_boxes))
    pq = []
    count = 0
    h_start = problem.heuristic(start_state)
    # (f_cost, g_cost, tie_breaker, current_state, path)
    heapq.heappush(pq, (h_start, 0, count, start_state, []))
    explored = {}
    nodes_expanded = 0

    while pq:
        f, g, _, state, path = heapq.heappop(pq)
        nodes_expanded += 1

        if problem.is_goal(state[1]):
            return path, g, nodes_expanded

        if state in explored and explored[state] <= g:
            continue
        explored[state] = g

        for next_state, action, cost in problem.get_successors(state):
            new_g = g + cost
            if next_state not in explored or new_g < explored[next_state]:
                count += 1
                h_val = problem.heuristic(next_state)
                new_f = new_g + h_val
                heapq.heappush(pq, (new_f, new_g, count, next_state, path + [action]))

    return None, float('inf'), nodes_expanded