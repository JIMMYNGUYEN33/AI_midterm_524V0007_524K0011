ACTIONS = {
    'North': (-1, 0),
    'South': (1, 0),
    'West': (0, -1),
    'East': (0, 1),
    'Wait': (0, 0)
}


def _add_positions(pos, delta):
    return (
        pos[0] + delta[0],
        pos[1] + delta[1]
    )


def _plan_movement(
    pos,
    act,
    opp_pos,
    walls,
    all_boxes
):
    delta = ACTIONS.get(act, (0, 0))

    if delta == (0, 0):
        return pos, None

    next_pos = _add_positions(pos, delta)

    # Không đi xuyên tường / agent kia
    if next_pos in walls or next_pos == opp_pos:
        return pos, None

    # Nếu phía trước có box
    if next_pos in all_boxes:

        box_target = _add_positions(
            next_pos,
            delta
        )

        # Không thể đẩy vào tường
        if box_target in walls:
            return pos, None

        # Không thể đẩy vào box khác
        if box_target in all_boxes:
            return pos, None

        # Không thể đẩy vào agent kia
        if box_target == opp_pos:
            return pos, None

        return next_pos, (
            next_pos,
            box_target
        )

    return next_pos, None


def simultaneous_step(
    p1,
    p2,
    b1,
    b2,
    neutral_boxes,
    act1,
    act2,
    walls,
    goals,
    priority=0
):
    """Apply both agents' actions simultaneously."""

    all_boxes = (
        set(b1)
        | set(b2)
        | set(neutral_boxes)
    )

    t1, push1 = _plan_movement(
        p1,
        act1,
        p2,
        walls,
        all_boxes
    )

    t2, push2 = _plan_movement(
        p2,
        act2,
        p1,
        walls,
        all_boxes
    )

    # Hai agent đi cùng một ô
    if t1 == t2:

        if priority == 1:
            t2 = p2
            push2 = None

        elif priority == 2:
            t1 = p1
            push1 = None

        else:
            t1 = p1
            t2 = p2
            push1 = None
            push2 = None

    # Hai agent đổi chỗ cho nhau
    elif t1 == p2 and t2 == p1:

        t1 = p1
        t2 = p2

        push1 = None
        push2 = None

    else:

        # Không cho push vào vị trí agent kia
        if push1 and (
            push1[1] == t2
            or push1[1] == p2
        ):

            if priority != 1:
                t1 = p1
                push1 = None

        if push2 and (
            push2[1] == t1
            or push2[1] == p1
        ):

            if priority != 2:
                t2 = p2
                push2 = None

        # Hai agent cùng đẩy một box
        if push1 and push2:

            if push1[1] == push2[1]:

                if priority == 1:
                    t2 = p2
                    push2 = None

                else:
                    t1 = p1
                    push1 = None

    new_b1 = set(b1)
    new_b2 = set(b2)
    new_neutral = set(neutral_boxes)

    for push, owner_set in (
        (push1, new_b1),
        (push2, new_b2)
    ):

        if push is None:
            continue

        src, dst = push

        # Xóa box khỏi tất cả ownership
        new_b1.discard(src)
        new_b2.discard(src)
        new_neutral.discard(src)

        # Nếu box được đưa vào goal
        if dst in goals:
            owner_set.add(dst)

        else:
            # Box trở lại neutral
            new_neutral.add(dst)

    return (
        t1,
        t2,
        new_b1,
        new_b2,
        new_neutral
    )