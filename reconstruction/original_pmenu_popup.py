"""Native PMenu stack visibility, separate from its selected tree node.

43095F/4313B0: application event 2 compound at (599,0), 100x95.
432690 ->5EBEA0 pushes PMenu only on an accepted event 2 when not top.
4C2FB0 ->5EC060 installs the initial child, not PMenu, as the top panel.
432970 dismisses on x<524 or (y<96 and x>700), via4329F0/532980.
47AD60 ->5ED2A0 removes/re-pushes an already-open menu during child changes.
This does NOT qualify the missing header compound's dynamic bitmap/text draw.
"""

PMENU_OPEN_RECT = (599, 0, 100, 95)


def pmenu_open_press(x: int, y: int, *, active: bool) -> bool:
    if type(x) is not int or type(y) is not int or type(active) is not bool:
        raise ValueError('Exact native pointer coordinates and popup state required')
    return not active and 599 <= x < 699 and 0 <= y < 95


def pmenu_app_pointer_dismiss(x: int, y: int) -> bool:
    if type(x) is not int or type(y) is not int:
        raise ValueError('Exact native pointer coordinates required')
    return x < 524 or (y < 96 and x > 700)
