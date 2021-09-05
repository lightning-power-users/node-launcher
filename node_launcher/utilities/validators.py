
from string import ascii_lowercase

valid_domain_characters = list(ascii_lowercase)
valid_domain_characters.extend(list(range(10)))
valid_domain_characters.extend(['-'])


def hex_to_decimal(x: str) -> int:
    try:
        return int(x, 2**4)
    except ValueError:
        return -1


def is_non_empty(x) -> bool:
    return len(str(x)) > 0


def is_integer(x) -> bool:
    try:
        int(x)
        return True
    except ValueError:
        return False


def is_float(x) -> bool:
    try:
        float(x)
        return True
    except ValueError:
        return False


def is_positive_integer(x) -> bool:
    return is_integer(x) and int(x) > 0


def is_non_negative_integer(x) -> bool:
    return is_integer(x) and int(x) >= 0


def is_integer_in_range(_min, _max, x) -> bool:
    return is_integer(x) and (_min <= int(x) < _max)


def is_ratio(x):
    return is_non_empty(x) and x[-1] == 'x' and is_float(x[0:-1])


def is_binary(x) -> bool:
    return is_integer_in_range(0, 2, x)


def is_port(x) -> bool:
    return is_integer_in_range(1, 2**16, x)


def is_user_and_pass(x) -> bool:
    components = x.split(':')
    return len(components) == 2 and all([len(component) > 0 for component in components])


def has_only_chars(x, cs) -> bool:
    for c in x:
        if c not in cs:
            return False
    return True


def is_ipv4_address(x) -> bool:
    components = x.split('.')
    return len(components) == 4 and all([is_integer_in_range(0, 2**8, component) for component in components])


# TODO: I'm not sure but I believe that ipv6 addresses can have missing field if it's 0.
# That's currently not allowed here
def is_ipv6_address(x) -> bool:
    # This is because bitcoin.conf expects ipv6 addresses to be surrounded by []
    x = x.strip('[').strip(']')
    components = x.split(':')
    return len(components) == 8 and all(
        [is_integer_in_range(0, 2**16, hex_to_decimal(component)) for component in components]
    )


def is_ip_address(x) -> bool:
    return is_ipv4_address(x) or is_ipv6_address(x)


def is_named_address(x):
    return is_non_empty(x) and all([
        is_non_empty(component) and has_only_chars(component.lower(), valid_domain_characters)
        for component in x.split('.')
    ])


def is_address_without_port(x):
    components = x.split(':')
    return (len(components) == 1 or len(components) == 8) and (is_ip_address(x) or is_named_address(x))


def is_address_with_port(x) -> bool:
    components = x.split(':')
    len_components = len(components)
    if len_components == 2 or len_components == 9:
        if len_components == 9:
            components = [':'.join(components[0:-1]), components[-1]]
            # Makind sure that if it's an ipv6 address, that the ip part is surrounded by []
            if components[0][0] != '[' or components[0][-1] != ']':
                return False
        if is_address_without_port(components[0]) and is_port(components[1]):
            return True

    return False


def is_tcp_address_with_port(x: str) -> bool:
    if x.startswith('tcp://'):
        return is_address_with_port(x[6:])
    return False


def is_address(x) -> bool:
    return is_address_with_port(x) or is_address_without_port(x)


# TODO: Needs improvement
def is_file_path(x):
    return is_non_empty(x)


# TODO: Needs improvement
def is_folder_path(x):
    return is_non_empty(x)


# TODO: Needs improvement on second component check
def is_subnet(x):
    components = x.split('/')
    return len(components) == 2 and is_address_without_port(components[0]) and is_non_empty(components[1])


def is_ip_or_subnet(x):
    return is_ip_address(x) or is_subnet(x)
