import heapq
import time
from collections import deque


# =========================================================
# ACTIONS
# =========================================================

ACTIONS = {
    "North": (-1, 0),
    "South": (1, 0),
    "West": (0, -1),
    "East": (0, 1),
}


# =========================================================
# SOKOBAN PROBLEM
# =========================================================

class SokobanProblem:

    def __init__(self, map_file):

        self.map_file = map_file

        self.grid = []

        self.walls = set()
        self.goals = set()
        self.initial_boxes = set()
        self.initial_agent = None

        # -------------------------------------------------
        # READ MAP
        # -------------------------------------------------

        with open(
            map_file,
            "r",
            encoding="utf-8"
        ) as f:

            lines = [
                line.rstrip("\n\r")
                for line in f
            ]

        self.rows = len(lines)

        if self.rows == 0:
            raise ValueError(
                "Map file is empty."
            )

        self.cols = max(
            len(line)
            for line in lines
        )

        # -------------------------------------------------
        # PARSE MAP
        # -------------------------------------------------

        for r, line in enumerate(lines):

            row = list(
                line.ljust(
                    self.cols,
                    " "
                )
            )

            for c, char in enumerate(row):

                pos = (r, c)

                # Wall
                if char == "%":

                    self.walls.add(pos)

                # Goal
                elif char == "D":

                    self.goals.add(pos)

                # Box
                elif char == "B":

                    self.initial_boxes.add(pos)

                # Agent
                elif char == "A":

                    self.initial_agent = pos

                # Box on goal
                elif char == "C":

                    self.initial_boxes.add(pos)
                    self.goals.add(pos)

            self.grid.append(row)

        if self.initial_agent is None:

            raise ValueError(
                "Map does not contain an agent 'A'."
            )

        if len(self.initial_boxes) != len(
            self.goals
        ):

            raise ValueError(
                "Number of boxes and goals "
                "must be equal."
            )

        # Cache for heuristic
        self.goal_distances = (
            self._compute_goal_distances()
        )

    # =====================================================
    # BOUNDS
    # =====================================================

    def in_bounds(self, pos):

        r, c = pos

        return (
            0 <= r < self.rows
            and
            0 <= c < self.cols
        )

    # =====================================================
    # WALKABLE
    # =====================================================

    def is_walkable(self, pos):

        if not self.in_bounds(pos):
            return False

        return pos not in self.walls

    # =====================================================
    # GOAL TEST
    # =====================================================

    def is_goal(self, state):

        agent, boxes = state

        return set(boxes) == self.goals

    # =====================================================
    # SUCCESSORS
    # =====================================================

    def get_successors(self, state):

        agent, boxes = state

        boxes = set(boxes)

        for action, (dr, dc) in ACTIONS.items():

            next_agent = (
                agent[0] + dr,
                agent[1] + dc
            )

            # Outside map
            if not self.in_bounds(
                next_agent
            ):
                continue

            # Wall
            if next_agent in self.walls:
                continue

            # -------------------------------------------------
            # NORMAL MOVE
            # -------------------------------------------------

            if next_agent not in boxes:

                next_state = (
                    next_agent,
                    frozenset(boxes)
                )

                yield (
                    next_state,
                    action,
                    1
                )

            # -------------------------------------------------
            # PUSH BOX
            # -------------------------------------------------

            else:

                box_destination = (
                    next_agent[0] + dr,
                    next_agent[1] + dc
                )

                # Outside map
                if not self.in_bounds(
                    box_destination
                ):
                    continue

                # Wall
                if box_destination in self.walls:
                    continue

                # Another box
                if box_destination in boxes:
                    continue

                new_boxes = set(boxes)

                new_boxes.remove(
                    next_agent
                )

                new_boxes.add(
                    box_destination
                )

                next_state = (
                    next_agent,
                    frozenset(new_boxes)
                )

                yield (
                    next_state,
                    action,
                    1
                )

    # =====================================================
    # ALIAS
    # =====================================================

    def successors(self, state):

        yield from self.get_successors(
            state
        )

    # =====================================================
    # COMPUTE DISTANCE FROM GOALS
    # =====================================================

    def _compute_goal_distances(self):

        all_distances = {}

        for goal in self.goals:

            distances = {
                goal: 0
            }

            queue = deque(
                [goal]
            )

            while queue:

                current = queue.popleft()

                r, c = current

                for dr, dc in ACTIONS.values():

                    nxt = (
                        r + dr,
                        c + dc
                    )

                    # IMPORTANT:
                    # Keep BFS inside map
                    if not self.in_bounds(
                        nxt
                    ):
                        continue

                    if nxt in self.walls:
                        continue

                    if nxt in distances:
                        continue

                    distances[nxt] = (
                        distances[current] + 1
                    )

                    queue.append(
                        nxt
                    )

            all_distances[goal] = distances

        return all_distances

    # =====================================================
    # HEURISTIC
    # =====================================================

    def heuristic(self, boxes):

        boxes = set(boxes)

        remaining_goals = set(
            self.goals
        )

        total = 0

        for box in boxes:

            best_distance = float("inf")
            best_goal = None

            for goal in remaining_goals:

                distance = (
                    self.goal_distances
                    .get(goal, {})
                    .get(
                        box,
                        float("inf")
                    )
                )

                if distance < best_distance:

                    best_distance = distance
                    best_goal = goal

            if best_goal is None:

                return float("inf")

            total += best_distance

            remaining_goals.remove(
                best_goal
            )

        return total


# =========================================================
# RECONSTRUCT PATH
# =========================================================

def _reconstruct_path(
    came_from,
    current
):

    path = []

    while current in came_from:

        previous, action = (
            came_from[current]
        )

        path.append(action)

        current = previous

    path.reverse()

    return path


# =========================================================
# A*
# =========================================================

def solve_astar(
    problem,
    time_limit=30
):

    start_time = time.time()

    start_state = (
        problem.initial_agent,
        frozenset(
            problem.initial_boxes
        )
    )

    # Priority queue:
    # (f, counter, g, state)

    frontier = []

    counter = 0

    start_h = problem.heuristic(
        start_state[1]
    )

    heapq.heappush(
        frontier,
        (
            start_h,
            counter,
            0,
            start_state
        )
    )

    came_from = {}

    cost_so_far = {
        start_state: 0
    }

    nodes_expanded = 0

    while frontier:

        # Time limit
        if (
            time.time() - start_time
            > time_limit
        ):

            return [], nodes_expanded, (
                time.time() - start_time
            )

        (
            _,
            _,
            current_cost,
            current
        ) = heapq.heappop(
            frontier
        )

        nodes_expanded += 1

        # Goal
        if problem.is_goal(current):

            path = _reconstruct_path(
                came_from,
                current
            )

            elapsed = (
                time.time()
                - start_time
            )

            return (
                path,
                nodes_expanded,
                elapsed
            )

        # Successors
        for (
            next_state,
            action,
            step_cost
        ) in problem.get_successors(
            current
        ):

            new_cost = (
                current_cost
                + step_cost
            )

            if (
                next_state not in cost_so_far
                or
                new_cost
                < cost_so_far[next_state]
            ):

                cost_so_far[
                    next_state
                ] = new_cost

                came_from[
                    next_state
                ] = (
                    current,
                    action
                )

                h = problem.heuristic(
                    next_state[1]
                )

                if h == float("inf"):
                    continue

                counter += 1

                priority = (
                    new_cost + h
                )

                heapq.heappush(
                    frontier,
                    (
                        priority,
                        counter,
                        new_cost,
                        next_state
                    )
                )

    elapsed = (
        time.time()
        - start_time
    )

    return (
        [],
        nodes_expanded,
        elapsed
    )


# =========================================================
# UCS
# =========================================================

def solve_ucs(
    problem,
    time_limit=30
):

    start_time = time.time()

    start_state = (
        problem.initial_agent,
        frozenset(
            problem.initial_boxes
        )
    )

    frontier = []

    counter = 0

    heapq.heappush(
        frontier,
        (
            0,
            counter,
            start_state
        )
    )

    came_from = {}

    cost_so_far = {
        start_state: 0
    }

    nodes_expanded = 0

    while frontier:

        # Time limit
        if (
            time.time() - start_time
            > time_limit
        ):

            return [], nodes_expanded, (
                time.time() - start_time
            )

        (
            current_cost,
            _,
            current
        ) = heapq.heappop(
            frontier
        )

        nodes_expanded += 1

        # Goal
        if problem.is_goal(current):

            path = _reconstruct_path(
                came_from,
                current
            )

            elapsed = (
                time.time()
                - start_time
            )

            return (
                path,
                nodes_expanded,
                elapsed
            )

        # Successors
        for (
            next_state,
            action,
            step_cost
        ) in problem.get_successors(
            current
        ):

            new_cost = (
                current_cost
                + step_cost
            )

            if (
                next_state not in cost_so_far
                or
                new_cost
                < cost_so_far[next_state]
            ):

                cost_so_far[
                    next_state
                ] = new_cost

                came_from[
                    next_state
                ] = (
                    current,
                    action
                )

                counter += 1

                heapq.heappush(
                    frontier,
                    (
                        new_cost,
                        counter,
                        next_state
                    )
                )

    elapsed = (
        time.time()
        - start_time
    )

    return (
        [],
        nodes_expanded,
        elapsed
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    map_file = (
        "maps/example_map.txt"
    )

    problem = SokobanProblem(
        map_file
    )

    print("=" * 50)
    print("SOKOBAN SOLVER")
    print("=" * 50)

    # -----------------------------------------------------
    # A*
    # -----------------------------------------------------

    print("\nRunning A*...")

    path_astar, nodes_astar, time_astar = (
        solve_astar(problem)
    )

    if path_astar:

        print("A* SUCCESS")
        print(
            "Cost:",
            len(path_astar)
        )
        print(
            "Steps:",
            len(path_astar)
        )
        print(
            "Nodes:",
            nodes_astar
        )
        print(
            "Time:",
            round(time_astar, 3),
            "seconds"
        )

    else:

        print("A* FAILED")

    # -----------------------------------------------------
    # UCS
    # -----------------------------------------------------

    print("\nRunning UCS...")

    path_ucs, nodes_ucs, time_ucs = (
        solve_ucs(problem)
    )

    if path_ucs:

        print("UCS SUCCESS")
        print(
            "Cost:",
            len(path_ucs)
        )
        print(
            "Steps:",
            len(path_ucs)
        )
        print(
            "Nodes:",
            nodes_ucs
        )
        print(
            "Time:",
            round(time_ucs, 3),
            "seconds"
        )

    else:

        print("UCS FAILED")