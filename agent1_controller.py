import heapq
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
    def __init__(self, walls, goals, algorithm="BFS"):
        self.walls = set(walls)
        self.goals = set(goals)
        self.algorithm = algorithm.upper()
        if self.algorithm not in {"BFS", "UCS", "A*"}:
            raise ValueError("algorithm must be BFS, UCS, or A*")
        self.last_nodes_expanded = 0
        self.min_row = min(row for row, _ in self.walls)
        self.max_row = max(row for row, _ in self.walls)
        self.min_col = min(col for _, col in self.walls)
        self.max_col = max(col for _, col in self.walls)
        self.goal_push_distances = self._build_goal_push_distances()

    def _build_goal_push_distances(self):
        distances_by_goal = {}
        directions = tuple(delta for delta in ACTIONS.values() if delta != (0, 0))

        for goal in self.goals:
            distances = {goal: 0}
            queue = deque([goal])

            while queue:
                box = queue.popleft()
                for dr, dc in directions:
                    previous_box = (box[0] - dr, box[1] - dc)
                    required_agent = (box[0] - 2 * dr, box[1] - 2 * dc)
                    if (
                        not self._in_bounds(previous_box)
                        or not self._in_bounds(required_agent)
                        or previous_box in self.walls
                        or required_agent in self.walls
                        or previous_box in distances
                    ):
                        continue
                    distances[previous_box] = distances[box] + 1
                    queue.append(previous_box)

            distances_by_goal[goal] = distances

        return distances_by_goal

    def _in_bounds(self, position):
        row, col = position
        return (
            self.min_row <= row <= self.max_row
            and self.min_col <= col <= self.max_col
        )

    def _heuristic(self, box, target_goals):
        return min(
            (
                self.goal_push_distances[goal].get(box, float("inf"))
                for goal in target_goals
            ),
            default=float("inf"),
        )

    def _plan_box(self, agent_start, box_start, target_goals, obstacles, deadline):
        start = (agent_start, box_start)
        if (
            self.algorithm == "A*"
            and self._heuristic(box_start, target_goals) == float("inf")
        ):
            return None

        if self.algorithm == "BFS":
            frontier = deque([(start, 0, [])])
        else:
            frontier = []
            heapq.heappush(
                frontier,
                (self._priority(0, box_start, target_goals), 0, 0, start, []),
            )
        best_cost = {start: 0}
        counter = 0

        while frontier and time.time() < deadline:
            if self.algorithm == "BFS":
                state, cost, path = frontier.popleft()
            else:
                _, _, cost, state, path = heapq.heappop(frontier)
                if cost != best_cost.get(state):
                    continue

            agent, box = state
            self.last_nodes_expanded += 1

            if box in target_goals:
                return path

            for action, (dr, dc) in ACTIONS.items():
                if action == 'Wait':
                    continue

                nxt = (agent[0] + dr, agent[1] + dc)

                if nxt != box:
                    if not self._in_bounds(nxt) or nxt in self.walls or nxt in obstacles:
                        continue

                    state = (nxt, box)
                    new_cost = cost + 1
                    if new_cost >= best_cost.get(state, float("inf")):
                        continue

                    best_cost[state] = new_cost
                    next_path = path + [action]
                    if self.algorithm == "BFS":
                        frontier.append((state, new_cost, next_path))
                    else:
                        counter += 1
                        heapq.heappush(
                            frontier,
                            (
                                self._priority(new_cost, box, target_goals),
                                counter,
                                new_cost,
                                state,
                                next_path,
                            ),
                        )
                    continue

                new_box = (box[0] + dr, box[1] + dc)

                if not self._in_bounds(new_box) or new_box in self.walls:
                    continue

                if new_box in obstacles:
                    continue

                state = (box, new_box)

                new_cost = cost + 1
                if new_cost >= best_cost.get(state, float("inf")):
                    continue

                if (
                    self.algorithm == "A*"
                    and self._heuristic(new_box, target_goals) == float("inf")
                ):
                    continue

                best_cost[state] = new_cost
                next_path = path + [action]
                if self.algorithm == "BFS":
                    frontier.append((state, new_cost, next_path))
                else:
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (
                            self._priority(new_cost, new_box, target_goals),
                            counter,
                            new_cost,
                            state,
                            next_path,
                        ),
                    )

        return None

    def _priority(self, cost, box, target_goals):
        if self.algorithm == "A*":
            return cost + self._heuristic(box, target_goals)
        return cost

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

        targets = [
            (b, self.goals) for b in my_boxes
            if b not in self.goals
        ]

        targets += [
            (b, self.goals) for b in neutral_boxes
            if b not in self.goals
        ]

        targets += [
            (b, self.goals) for b in opp_boxes
            if b not in self.goals
        ]
        targets += [
            (b, self.goals - {b}) for b in opp_boxes
            if b in self.goals and len(self.goals) > 1
        ]

        best_path = None
        best_score = float('inf')

        for box, target_goals in targets:
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
                target_goals,
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
            elif box in opp_boxes and box in self.goals:
                score -= 20

            if score < best_score:
                best_score = score
                best_path = path

        if best_path:
            return best_path[0]

        return 'Wait'