ACTIONS = {'North': (-1, 0), 'South': (1, 0), 'West': (0, -1), 'East': (0, 1)}


def _add(p, d):
    return (p[0] + d[0], p[1] + d[1])


def _plan(pos, act, opp_pos, walls, all_boxes):
    """Trả về (ô đích của agent, (ô hộp cũ, ô hộp mới) hoặc None)."""
    d = ACTIONS.get(act, (0, 0))
    nxt = _add(pos, d)
    if nxt in walls or nxt == opp_pos:
        return pos, None
    if nxt in all_boxes:
        box_to = _add(nxt, d)
        if box_to in walls or box_to in all_boxes or box_to == opp_pos:
            return pos, None
        return nxt, (nxt, box_to)
    return nxt, None


def simultaneous_step(p1, p2, b1, b2, neutral, act1, act2, walls, goals, priority=0):
    """priority: 1 hoặc 2 = bên thắng khi tranh chấp, 0 = hủy cả hai."""
    all_boxes = b1 | b2 | neutral
    t1, push1 = _plan(p1, act1, p2, walls, all_boxes)
    t2, push2 = _plan(p2, act2, p1, walls, all_boxes)

    if t1 == t2:
        lose1, lose2 = priority != 1, priority != 2
    else:
        lose1 = push1 is not None and push1[1] == t2
        lose2 = push2 is not None and push2[1] == t1
        if push1 and push2 and push1[1] == push2[1]:
            lose1 = lose1 or priority != 1
            lose2 = lose2 or priority != 2

    if lose1:
        t1, push1 = p1, None
    if lose2:
        t2, push2 = p2, None

    for push, owner in ((push1, b1), (push2, b2)):
        if push is not None:
            src, dst = push
            for s in (b1, b2, neutral):
                s.discard(src)
            (owner if dst in goals else neutral).add(dst)
    return t1, t2