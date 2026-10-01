import heapq
import time
from collections import deque


ACTIONS = {
    "North": (-1, 0),
    "South": (1, 0),
    "West": (0, -1),
    "East": (0, 1),
}


class SokobanProblem:
    def __init__(self, map_file):
        self.map_file = map_file
        self.grid = []
        self.walls = set()
        self.goals = set()
        self.initial_boxes = set()
        self.initial_agent = None

        with open(map_file, "r", encoding="utf-8") as file:
            lines = [line.rstrip("\n\r") for line in file]

        if not lines:
            raise ValueError("Map file is empty.")

        self.rows = len(lines)
        self.cols = max(len(line) for line in lines)

        for row_index, line in enumerate(lines):
            row = list(line.ljust(self.cols, " "))
            for col_index, char in enumerate(row):
                position = (row_index, col_index)
                if char == "%":
                    self.walls.add(position)
                elif char == "D":
                    self.goals.add(position)
                elif char == "B":
                    self.initial_boxes.add(position)
                elif char == "A":
                    self.initial_agent = position
                elif char == "C":
                    self.initial_boxes.add(position)
                    self.goals.add(position)
            self.grid.append(row)

        if self.initial_agent is None:
            raise ValueError("Map does not contain an agent 'A'.")
        if len(self.initial_boxes) != len(self.goals):
            raise ValueError("Number of boxes and goals must be equal.")

        self._neighbor_indices = self._build_neighbor_indices()
        self.goal_distances = self._compute_goal_distances()
        self._heuristic_cache = {}

    def in_bounds(self, position):
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _build_neighbor_indices(self):
        neighbors = []
        for row in range(self.rows):
            for col in range(self.cols):
                position = (row, col)
                if position in self.walls:
                    neighbors.append((-1, -1, -1, -1))
                    continue

                adjacent = []
                for dr, dc in ACTIONS.values():
                    next_position = (row + dr, col + dc)
                    if not self.in_bounds(next_position) or next_position in self.walls:
                        adjacent.append(-1)
                    else:
                        adjacent.append(next_position[0] * self.cols + next_position[1])
                neighbors.append(tuple(adjacent))
        return tuple(neighbors)

    def is_goal(self, state):
        return set(state[1]) == self.goals

    def get_successors(self, state):
        agent, boxes = state
        boxes = set(boxes)

        for action, (dr, dc) in ACTIONS.items():
            next_agent = (agent[0] + dr, agent[1] + dc)
            if not self.in_bounds(next_agent) or next_agent in self.walls:
                continue

            if next_agent not in boxes:
                yield (next_agent, frozenset(boxes)), action, 1
                continue

            destination = (next_agent[0] + dr, next_agent[1] + dc)
            if (
                not self.in_bounds(destination)
                or destination in self.walls
                or destination in boxes
            ):
                continue

            next_boxes = set(boxes)
            next_boxes.remove(next_agent)
            next_boxes.add(destination)
            yield (next_agent, frozenset(next_boxes)), action, 1

    def successors(self, state):
        yield from self.get_successors(state)

    def _compute_goal_distances(self):
        distances_by_goal = {}
        for goal in self.goals:
            distances = {goal: 0}
            queue = deque([goal])

            while queue:
                current = queue.popleft()
                for dr, dc in ACTIONS.values():
                    previous_box = (current[0] - dr, current[1] - dc)
                    required_agent = (current[0] - 2 * dr, current[1] - 2 * dc)

                    if (
                        not self.in_bounds(previous_box)
                        or not self.in_bounds(required_agent)
                        or previous_box in self.walls
                        or required_agent in self.walls
                        or previous_box in distances
                    ):
                        continue

                    distances[previous_box] = distances[current] + 1
                    queue.append(previous_box)

            distances_by_goal[goal] = distances
        return distances_by_goal

    def heuristic(self, boxes):
        key = frozenset(boxes)
        if key in self._heuristic_cache:
            return self._heuristic_cache[key]

        ordered_boxes = tuple(sorted(key))
        ordered_goals = tuple(sorted(self.goals))
        costs = {0: 0}

        for box in ordered_boxes:
            next_costs = {}
            for mask, current_cost in costs.items():
                for index, goal in enumerate(ordered_goals):
                    if mask & (1 << index):
                        continue

                    distance = self.goal_distances[goal].get(box, float("inf"))
                    if distance == float("inf"):
                        continue

                    new_mask = mask | (1 << index)
                    new_cost = current_cost + distance
                    next_costs[new_mask] = min(
                        next_costs.get(new_mask, float("inf")),
                        new_cost,
                    )
            costs = next_costs

        result = costs.get((1 << len(ordered_goals)) - 1, float("inf"))
        self._heuristic_cache[key] = result
        return result


def _reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        current, action = came_from[current]
        path.append(action)
    path.reverse()
    return path


def _search(problem, use_heuristic, time_limit):
    start_time = time.perf_counter()
    start = (problem.initial_agent, frozenset(problem.initial_boxes))
    frontier = []
    counter = 0
    initial_h = problem.heuristic(start[1]) if use_heuristic else 0
    heapq.heappush(frontier, (initial_h, counter, 0, start))
    came_from = {}
    cost_so_far = {start: 0}
    nodes_expanded = 0

    while frontier:
        elapsed = time.perf_counter() - start_time
        if elapsed > time_limit:
            return [], nodes_expanded, elapsed

        _, _, current_cost, current = heapq.heappop(frontier)
        if current_cost != cost_so_far.get(current):
            continue

        nodes_expanded += 1
        if problem.is_goal(current):
            return _reconstruct_path(came_from, current), nodes_expanded, elapsed

        for next_state, action, step_cost in problem.get_successors(current):
            new_cost = current_cost + step_cost
            if new_cost >= cost_so_far.get(next_state, float("inf")):
                continue

            heuristic = problem.heuristic(next_state[1]) if use_heuristic else 0
            if heuristic == float("inf"):
                continue

            cost_so_far[next_state] = new_cost
            came_from[next_state] = (current, action)
            counter += 1
            heapq.heappush(
                frontier,
                (new_cost + heuristic, counter, new_cost, next_state),
            )

    elapsed = time.perf_counter() - start_time
    return [], nodes_expanded, elapsed


def _search_ucs(problem, time_limit):
    start_time = time.perf_counter()
    position_bits = max(1, (problem.rows * problem.cols - 1).bit_length())
    position_mask = (1 << position_bits) - 1

    start_agent = (
        problem.initial_agent[0] * problem.cols
        + problem.initial_agent[1]
    )
    start_boxes = sum(
        1 << (row * problem.cols + col)
        for row, col in problem.initial_boxes
    )
    goal_mask = sum(
        1 << (row * problem.cols + col)
        for row, col in problem.goals
    )
    start = (start_boxes << position_bits) | start_agent

    frontier = deque([start])
    visited = {start}
    came_from = {}
    nodes_expanded = 0
    action_names = tuple(ACTIONS)

    while frontier:
        elapsed = time.perf_counter() - start_time
        if elapsed > time_limit:
            return [], nodes_expanded, elapsed

        current = frontier.popleft()
        agent = current & position_mask
        boxes = current >> position_bits
        nodes_expanded += 1

        if boxes == goal_mask:
            path = []
            while current in came_from:
                previous, action_index = came_from[current]
                path.append(action_names[action_index])
                current = previous
            path.reverse()
            return path, nodes_expanded, elapsed

        for action_index, destination in enumerate(problem._neighbor_indices[agent]):
            if destination < 0:
                continue

            destination_bit = 1 << destination
            next_boxes = boxes
            if boxes & destination_bit:
                box_destination = problem._neighbor_indices[destination][action_index]
                if box_destination < 0 or boxes & (1 << box_destination):
                    continue
                next_boxes = (boxes ^ destination_bit) | (1 << box_destination)

            next_state = (next_boxes << position_bits) | destination
            if next_state in visited:
                continue

            visited.add(next_state)
            came_from[next_state] = (current, action_index)
            frontier.append(next_state)

    elapsed = time.perf_counter() - start_time
    return [], nodes_expanded, elapsed


def solve_astar(problem, time_limit=30):
    return _search(problem, True, time_limit)


def solve_ucs(problem, time_limit=30):
    return _search_ucs(problem, time_limit)


if __name__ == "__main__":
    for name, solver in (("A*", solve_astar), ("UCS", solve_ucs)):
        problem = SokobanProblem("maps/example_map.txt")
        path, nodes, elapsed = solver(problem)
        status = "SUCCESS" if path else "FAILED"
        print(f"{name} {status}")
        print(f"Cost: {len(path)}")
        print(f"Nodes: {nodes}")
        print(f"Time: {elapsed:.3f} seconds")
