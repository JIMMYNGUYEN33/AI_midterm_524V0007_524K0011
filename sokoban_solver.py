import heapq
import time
from collections import deque

ACTIONS = {
    'North': (-1, 0),
    'South': (1, 0),
    'West': (0, -1),
    'East': (0, 1)
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

    def is_corner_deadlock(self, r, c):
        if (r, c) in self.goals:
            return False
        
        stuck_horizontally = (r, c - 1) in self.walls or (r, c + 1) in self.walls
        stuck_vertically = (r - 1, c) in self.walls or (r + 1, c) in self.walls
        
        return stuck_horizontally and stuck_vertically

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
                if self.is_corner_deadlock(box_nr, box_nc):
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
        _, boxes = state
        total_h = 0
        available_goals = set(self.goals)
        
        for b in boxes:
            min_dist = float('inf')
            best_goal = None
            
            for g in available_goals:
                if b in self.dist_matrix[g]:
                    d = self.dist_matrix[g][b]
                    if d < min_dist:
                        min_dist = d
                        best_goal = g
                        
            if min_dist == float('inf'):
                return float('inf')
                
            total_h += min_dist
            if best_goal:
                available_goals.remove(best_goal)

        return total_h


def solve_ucs(problem):
    start_state = (problem.initial_agent, frozenset(problem.initial_boxes))
    pq = []
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


def verify_heuristic_properties(problem, path, optimal_cost):
    print("\n" + "=" * 55)
    print("--- KIỂM CHỨNG TÍNH CHẤT HEURISTIC (YÊU CẦU 4) ---")
    
    start_state = (problem.initial_agent, frozenset(problem.initial_boxes))
    h_start = problem.heuristic(start_state)
    
    # 1. Admissibility: h(n) <= h*(n)
    is_admissible = h_start <= optimal_cost
    print(f"[1] Admissibility:")
    print(f"    - h(start) = {h_start} | Chi phí thực h*(start) = {optimal_cost}")
    print(f"    -> Kết luận thỏa h(n) <= h*(n): {is_admissible}")

    # 2. Consistency: h(n) <= c(n, a, n') + h(n') với c = 1
    curr_agent, curr_boxes = start_state
    curr_boxes = set(curr_boxes)
    consistent = True
    
    for step_idx, action in enumerate(path):
        dr, dc = ACTIONS[action]
        curr_state = (curr_agent, frozenset(curr_boxes))
        h_curr = problem.heuristic(curr_state)
        
        next_agent = (curr_agent[0] + dr, curr_agent[1] + dc)
        next_boxes = set(curr_boxes)
        if next_agent in next_boxes:
            box_next = (next_agent[0] + dr, next_agent[1] + dc)
            next_boxes.remove(next_agent)
            next_boxes.add(box_next)
            
        next_state = (next_agent, frozenset(next_boxes))
        h_next = problem.heuristic(next_state)
        
        if h_curr > 1 + h_next:
            consistent = False
            print(f"    [!] Vi phạm tại bước {step_idx}: h(n)={h_curr} > 1 + h(n')={1 + h_next}")
            break
            
        curr_agent = next_agent
        curr_boxes = next_boxes

    print(f"[2] Consistency:")
    print(f"    -> Thỏa mãn h(n) <= 1 + h(n') trên toàn bộ lộ trình: {consistent}")
    print("=" * 55)


if __name__ == "__main__":
    map_path = "example_map.txt"
    print("--- ĐANG KHỞI TẠO BÀI TOÁN TỪ FILE MAP ---")
    problem = SokobanProblem(map_path)
    print(f"Agent tại: {problem.initial_agent}")
    print(f"Số thùng: {len(problem.initial_boxes)} | Số đích: {len(problem.goals)}")
    print("-" * 50)

    # 1. Chạy thử thuật toán A* trước (vì A* có heuristic định hướng, chạy nhanh hơn nhiều so với UCS)
    print("1. Đang chạy A* Search...")
    start_time = time.time()
    path_astar, cost_astar, nodes_astar = solve_astar(problem)
    time_astar = time.time() - start_time

    if path_astar is not None:
        print("   -> Kết quả: THÀNH CÔNG")
        print(f"   -> Thời gian chạy: {time_astar:.4f} giây")
        print(f"   -> Tổng chi phí (Cost): {cost_astar}")
        print(f"   -> Số Nodes đã duyệt (Space): {nodes_astar}")
        print(f"   -> Số bước: {len(path_astar)}")
        print(f"   -> Lộ trình bước đi:")
        print(path_astar)
        
        verify_heuristic_properties(problem, path_astar, cost_astar)
    else:
        print("   -> A* không tìm thấy đường đi.")

    print("-" * 50)

    # 2. Chạy thử thuật toán UCS
    print("2. Đang chạy Uniform Cost Search (UCS)...")
    start_time = time.time()
    path_ucs, cost_ucs, nodes_ucs = solve_ucs(problem)
    time_ucs = time.time() - start_time

    if path_ucs is not None:
        print("   -> Kết quả: THÀNH CÔNG")
        print(f"   -> Thời gian chạy: {time_ucs:.4f} giây")
        print(f"   -> Tổng chi phí (Cost): {cost_ucs}")
        print(f"   -> Số Nodes đã duyệt (Space): {nodes_ucs}")
        print(f"   -> Số bước: {len(path_ucs)}")
    else:
        print("   -> UCS không tìm thấy đường đi.")

    print("-" * 50)