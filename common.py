class Direction:
    """Enumerates movement directions

    This enumeration is used to describe the direction of an class that
    provides physical movement (e.g., an Arm or Drive Train).  All directions
    are from the perspective of the center of the robot facing towards the
    front.

    Attributes:
        left.
        right.
        forward.
        backward.
        up.
        down.

    """
    left = 1
    right = 2
    forward = 3
    backward = 4
    up = 5
    down = 6

class ProgramState:
    """Enumerates robot game states.

    This enumeration is used to keep track of the current game state as
    provided by the playing field (FMS).

    Attributes:
        disabled.
        autonomous.
        teleop.

    """
    disabled = 1
    autonomous = 2
    teleop = 3
