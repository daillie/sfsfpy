def sum_hex(a: str, b: str):
    a = hex_to_int(a)
    b = hex_to_int(b)

    return hex(a + b)


def sub_hex(a: str, b: str):
    a = hex_to_int(a)
    b = hex_to_int(b)

    return hex(a - b)


def hex_to_int(hex_str: str) -> int:
    if not isinstance(hex_str, str):
        raise Exception('%s is not string' % hex_str)
    return int(hex_str, 16)
