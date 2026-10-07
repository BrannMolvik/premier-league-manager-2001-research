"""Native 461900 bit-0 callback registration and 461BB0/461C10/461C70 stop.

The callbacks are unconditional on key value: WM_KEYDOWN, WM_LBUTTONDOWN,
WM_RBUTTONDOWN. WM_SYSKEYDOWN and key-up are not registered here.
"""
NATIVE_STARTUP_INPUT_MESSAGES = (0x100, 0x201, 0x204)
WM_KEYDOWN = 0x100
VK_ESCAPE = 0x1B
SKIP_RECEIPT_PREFIX = 'FM2001_STARTUP_SKIPPED='


def startup_input_allowed(flag_bit0: bool, message: int) -> bool:
    return (flag_bit0 is True and type(message) is int
            and message in NATIVE_STARTUP_INPUT_MESSAGES)


def parse_native_skip_receipt(stdout: str, flag_bit0: bool) -> int:
    lines = str(stdout).strip().splitlines()
    if len(lines) != 1 or not lines[0].startswith(SKIP_RECEIPT_PREFIX):
        raise ValueError('Missing exact native startup-input receipt')
    value = lines[0][len(SKIP_RECEIPT_PREFIX):]
    if not value.isascii() or not value.isdecimal():
        raise ValueError('Invalid native startup-input receipt')
    message = int(value)
    if not startup_input_allowed(flag_bit0, message):
        raise ValueError('Unregistered startup input or non-skippable media')
    return message
