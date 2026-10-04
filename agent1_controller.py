import time
from collections import deque

ACTIONS = {
    'North': (-1, 0),
    'South': (1, 0),
    'West': (0, -1),
    'East': (0, 1),
    'Wait': (0, 0)
}


class Agent1Bot:
    def __init__(self, walls, goals):
        self.walls = set(walls)
        self.goals = set(goals)
        self.last_nodes_expanded = 0

    def _plan_box(self, agent_start, box_start, target_goals, obstacles, deadline):
        """BFS over (agent_position, box_position) for one box."""
        start = (agent_start, box_start)
        queue = deque([(agent_start, box_start, [])])
        visited = {start}

        while queue and time.time() < deadline:
            agent, box, path = queue.popleft()
            self.last_nodes_expanded += 1

            if box in target_goals:
                return path

            for action, (dr, dc) in ACTIONS.items():
                if action == 'Wait':
                    continue

                nxt = (agent[0] + dr, agent[1] + dc)

                # Normal movement
                if nxt != box:
                    if nxt in self.walls or nxt in obstacles:
                        continue

                    state = (nxt, box)
                    if state in visited:
                        continue

                    visited.add(state)
                    queue.append((nxt, box, path + [action]))
                    continue

                # Push box
                new_box = (box[0] + dr, box[1] + dc)

                if new_box in self.walls:
                    continue

                if new_box in obstacles:
                    continue

                state = (box, new_box)

                if state in visited:
                    continue

                visited.add(state)
                queue.append((box, new_box, path + [action]))

        return None

    def get_action(
        self,
        my_pos,
        opp_pos,
        my_boxes,
        opp_boxes,
        neutral_boxes
    ):
        self.last_nodes_expanded = 0
        deadline = time.time() + 0.75

        all_boxes = (
            set(my_boxes)
            | set(opp_boxes)
            | set(neutral_boxes)
        )

        # Ưu tiên box của mình, sau đó box neutral,
        # cuối cùng mới lấy box của đối thủ.
        targets = [
            b for b in my_boxes
            if b not in self.goals
        ]

        targets += [
            b for b in neutral_boxes
            if b not in self.goals
        ]

        targets += [
            b for b in opp_boxes
            if b not in self.goals
        ]

        best_path = None
        best_score = float('inf')

        for box in targets:
            if time.time() >= deadline:
                break

            obstacles = (
                self.walls
                | (all_boxes - {box})
                | {opp_pos}
            )

            path = self._plan_box(
                my_pos,
                box,
                self.goals,
                obstacles,
                deadline
            )

            if path is None:
                continue

            score = len(path)

            if box in my_boxes:
                score -= 20
            elif box in neutral_boxes:
                score -= 10

            if score < best_score:
                best_score = score
                best_path = path

        if best_path:
            return best_path[0]

        return 'Wait'