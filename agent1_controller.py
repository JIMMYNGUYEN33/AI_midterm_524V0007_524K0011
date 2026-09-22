import time
from collections import deque

ACTIONS = {
    'North': (-1, 0),
    'South': (1, 0),
    'West': (0, -1),
    'East': (0, 1)
}

class Agent1Bot:
    def __init__(self, walls, goals):
        self.walls = set(walls)
        self.goals = set(goals)

    def _bfs_path(self, start, target, obstacles):
        """Tìm đường đi ngắn nhất từ start tới target tránh obstacles."""
        if start == target:
            return []
        queue = deque([(start, [])])
        visited = {start}
        while queue:
            curr, path = queue.popleft()
            if curr == target:
                return path
            for act, (dr, dc) in ACTIONS.items():
                nxt = (curr[0] + dr, curr[1] + dc)
                if nxt not in self.walls and nxt not in obstacles and nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [act]))
        return None

    def get_action(self, my_pos, opp_pos, my_boxes, opp_boxes, neutral_boxes):
        start_time = time.time()
        all_boxes = set(my_boxes) | set(opp_boxes) | set(neutral_boxes)
        target_boxes = list(neutral_boxes) + list(opp_boxes)
        obstacles = self.walls | all_boxes | {opp_pos}

        best_move = None
        min_cost = float('inf')

        # Duyệt qua các thùng có thể can thiệp
        for box in target_boxes:
            if time.time() - start_time > 0.8:
                break
            
            # Tìm đích gần nhất cho thùng này
            for g in self.goals:
                for act, (dr, dc) in ACTIONS.items():
                    # Thử xem đẩy theo hướng act có đưa thùng gần đích g hơn không
                    next_box = (box[0] + dr, box[1] + dc)
                    
                    # Ô đẩy tới phải hợp lệ
                    if next_box in self.walls or next_box in all_boxes or next_box == opp_pos:
                        continue

                    # Ô agent cần đứng để đẩy thùng (phía đối diện)
                    push_pos = (box[0] - dr, box[1] - dc)
                    if push_pos in self.walls or (push_pos in all_boxes and push_pos != my_pos) or push_pos == opp_pos:
                        continue

                    # Chi phí khoảng cách từ thùng tới đích
                    box_to_goal = abs(next_box[0] - g[0]) + abs(next_box[1] - g[1])
                    
                    # Nếu agent đã đứng đúng vị trí đẩy
                    if my_pos == push_pos:
                        if box_to_goal < min_cost:
                            min_cost = box_to_goal
                            best_move = act
                    else:
                        # Agent cần đi bộ tới push_pos (tránh mọi thùng và đối thủ)
                        path_to_push = self._bfs_path(my_pos, push_pos, obstacles)
                        if path_to_push:
                            total_cost = len(path_to_push) + box_to_goal * 2
                            if total_cost < min_cost:
                                min_cost = total_cost
                                best_move = path_to_push[0]

        if best_move:
            return best_move

        # Nước đi vu vơ hợp lệ nếu không tìm được đường đẩy
        for act, (dr, dc) in ACTIONS.items():
            nxt = (my_pos[0] + dr, my_pos[1] + dc)
            if nxt not in self.walls and nxt != opp_pos and nxt not in all_boxes:
                return act

        return 'North'