import time
import tracemalloc
from collections import deque

from sokoban_solver import SokobanProblem, solve_astar, solve_ucs


def benchmark(problem, solver, name, time_limit=8):
    problem._heuristic_cache.clear()
    tracemalloc.start()
    started = time.perf_counter()
    path, expanded, elapsed = solver(problem, time_limit=time_limit)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "algorithm": name,
        "solved": bool(path),
        "cost": len(path),
        "nodes": expanded,
        "time_seconds": elapsed,
        "peak_memory_mb": peak / (1024 * 1024),
        "wall_time_seconds": time.perf_counter() - started,
    }


def sample_states(problem, limit=1000):
    start = (problem.initial_agent, frozenset(problem.initial_boxes))
    queue = deque([start])
    visited = {start}
    yielded = 0

    while queue and yielded < limit:
        state = queue.popleft()
        yielded += 1
        yield state

        for next_state, _, _ in problem.get_successors(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append(next_state)


def verify_heuristic(problem, sample_limit=10, state_time_limit=1.0):
    admissible = True
    consistent = True
    checked_states = 0
    checked_edges = 0
    admissibility_checks = 0
    timed_out_states = 0

    for state in sample_states(problem, sample_limit):
        checked_states += 1
        heuristic = problem.heuristic(state[1])
        exact_cost = _remaining_cost(problem, state, state_time_limit)
        if exact_cost is None:
            timed_out_states += 1
        else:
            admissibility_checks += 1
        if exact_cost is not None and heuristic > exact_cost:
            admissible = False

        for next_state, _, cost in problem.get_successors(state):
            checked_edges += 1
            next_heuristic = problem.heuristic(next_state[1])
            if heuristic > cost + next_heuristic:
                consistent = False

    result = {
        "states_checked": checked_states,
        "edges_checked": checked_edges,
        "admissibility_checks": admissibility_checks,
        "timed_out_states": timed_out_states,
        "admissible_on_sample": (
            admissible
            if admissibility_checks
            else None
        ),
        "consistent_on_sample": consistent,
    }
    return result


def _remaining_cost(problem, start, time_limit):
    started = time.perf_counter()
    queue = deque([(start, 0)])
    visited = {start}

    while queue:
        if time.perf_counter() - started >= time_limit:
            return None

        state, cost = queue.popleft()
        if problem.is_goal(state):
            return cost

        for next_state, _, step_cost in problem.get_successors(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, cost + step_cost))

    return None


def run_experiments(map_file="maps/example_map.txt"):
    results = [
        benchmark(SokobanProblem(map_file), solve_astar, "A*"),
        benchmark(SokobanProblem(map_file), solve_ucs, "UCS"),
    ]
    problem = SokobanProblem(map_file)
    heuristic_result = verify_heuristic(
        problem,
        sample_limit=3,
        state_time_limit=0.25,
    )

    print("Algorithm comparison")
    for result in results:
        print(result)

    print("Heuristic verification")
    print(heuristic_result)
    return results, heuristic_result


if __name__ == "__main__":
    run_experiments()
