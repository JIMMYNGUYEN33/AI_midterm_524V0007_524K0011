import time
import sys
from engine import simultaneous_step
from agent1_controller import Agent1Bot
from agent2_controller import Agent2Bot


def make_map(size=7):
    walls = {(r, c) for r in range(size) for c in range(size)
             if r in (0, size - 1) or c in (0, size - 1)}
    goals = {(1, 3), (5, 3)}
    neutral = {(3, 2), (3, 4)}
    return walls, goals, neutral


def play(cls1, cls2, n_steps=25, verbose=False):
    walls, goals, neutral = make_map()
    b1, b2 = set(), set()
    p1, p2 = (1, 1), (5, 5)
    bot1, bot2 = cls1(walls, goals), cls2(walls, goals)

    for step in range(1, n_steps + 1):
        t = time.time()
        a1 = bot1.get_action(p1, p2, b1, b2, neutral)
        ms1 = (time.time() - t) * 1000
        t = time.time()
        a2 = bot2.get_action(p2, p1, b2, b1, neutral)
        ms2 = (time.time() - t) * 1000

        p1, p2 = simultaneous_step(p1, p2, b1, b2, neutral, a1, a2, walls, goals,
                           priority=1 if step % 2 else 2)

        if verbose:
            print(f"Lượt {step:02d}: A1 [{a1:5s}] {p1} ({ms1:.1f}ms) | "
                  f"A2 [{a2:5s}] {p2} ({ms2:.1f}ms) | {len(b1)} - {len(b2)}")
    return len(b1), len(b2)


def fairness_test(n_steps=25):
    s1, s2 = play(Agent1Bot, Agent2Bot, n_steps)   
    t2, t1 = play(Agent2Bot, Agent1Bot, n_steps)   
    print(f"Ván 1 (Bot1 trên, Bot2 dưới): {s1} - {s2}")
    print(f"Ván 2 (Bot2 trên, Bot1 dưới): {t2} - {t1}")
    print(f"Tổng: Bot1 = {s1 + t1}, Bot2 = {s2 + t2}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    print(f"=== ĐỐI KHÁNG {n} BƯỚC ===")
    r1, r2 = play(Agent1Bot, Agent2Bot, n, verbose=True)
    print("=> HÒA!" if r1 == r2 else f"=> AGENT {1 if r1 > r2 else 2} THẮNG!")
    print("\n=== KIỂM TRA CÔNG BẰNG ===")
    fairness_test(n)