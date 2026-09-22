import time
from agent1_controller import Agent1Bot
from agent2_controller import Agent2Bot

ACTIONS = {
    'North': (-1, 0),
    'South': (1, 0),
    'West': (0, -1),
    'East': (0, 1)
}

def move_agent(pos, act, walls, opp_pos, my_boxes, opp_boxes, neutral_boxes, goals):
    dr, dc = ACTIONS[act]
    nxt = (pos[0] + dr, pos[1] + dc)
    all_boxes = set(my_boxes) | set(opp_boxes) | set(neutral_boxes)

    # Đụng tường hoặc đối thủ
    if nxt in walls or nxt == opp_pos:
        return pos

    # Đẩy thùng
    if nxt in all_boxes:
        box_nxt = (nxt[0] + dr, nxt[1] + dc)
        # Ô phía sau thùng bị chặn
        if box_nxt in walls or box_nxt in all_boxes or box_nxt == opp_pos:
            return pos
        
        # Di chuyển thùng thành công
        if nxt in my_boxes: my_boxes.remove(nxt)
        elif nxt in opp_boxes: opp_boxes.remove(nxt)
        elif nxt in neutral_boxes: neutral_boxes.remove(nxt)

        if box_nxt in goals:
            my_boxes.add(box_nxt)
        else:
            neutral_boxes.add(box_nxt)

    return nxt

def simulate_competitive_game(n_steps=25):
    # Khởi tạo bản đồ 7x7 thông thoáng
    walls = set()
    for r in range(7):
        for c in range(7):
            if r == 0 or r == 6 or c == 0 or c == 6:
                walls.add((r, c))

    # 2 đích ở 2 góc
    goals = {(1, 3), (5, 3)}
    
    # 2 thùng trung lập ở giữa sân
    neutral_boxes = {(3, 2), (3, 4)}
    my_boxes = set()
    opp_boxes = set()

    # Vị trí xuất phát của 2 bot
    agent1_pos = (1, 1)
    agent2_pos = (5, 5)

    bot1 = Agent1Bot(walls, goals)
    bot2 = Agent2Bot(walls, goals)

    print(f"=== BẮT ĐẦU ĐỐI KHÁNG TRONG {n_steps} BƯỚC ===")

    for step in range(1, n_steps + 1):
        # 1. Thuật toán ra quyết định
        t1 = time.time()
        act1 = bot1.get_action(agent1_pos, agent2_pos, my_boxes, opp_boxes, neutral_boxes)
        t1_used = (time.time() - t1) * 1000

        t2 = time.time()
        act2 = bot2.get_action(agent2_pos, agent1_pos, opp_boxes, my_boxes, neutral_boxes)
        t2_used = (time.time() - t2) * 1000

        # 2. Thực hiện hành động đồng thời
        agent1_pos = move_agent(agent1_pos, act1, walls, agent2_pos, my_boxes, opp_boxes, neutral_boxes, goals)
        agent2_pos = move_agent(agent2_pos, act2, walls, agent1_pos, opp_boxes, my_boxes, neutral_boxes, goals)

        print(f"Lượt {step:02d}: A1 [{act1:5s}] pos={agent1_pos} ({t1_used:.1f}ms) | "
              f"A2 [{act2:5s}] pos={agent2_pos} ({t2_used:.1f}ms) | "
              f"Điểm: A1={len(my_boxes)} - A2={len(opp_boxes)}")

    print("=" * 50)
    print("KẾT THÚC:")
    print(f"- Agent 1: {len(my_boxes)} thùng trong đích")
    print(f"- Agent 2: {len(opp_boxes)} thùng trong đích")
    if len(my_boxes) > len(opp_boxes):
        print("=> AGENT 1 CHIẾN THẮNG!")
    elif len(opp_boxes) > len(my_boxes):
        print("=> AGENT 2 CHIẾN THẮNG!")
    else:
        print("=> HÒA!")

if __name__ == "__main__":
    simulate_competitive_game(n_steps=25)