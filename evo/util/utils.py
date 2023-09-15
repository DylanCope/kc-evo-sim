from datetime import datetime


def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def merge_dicts_recursively(d1: dict, d2: dict) -> dict:
    """
    This function merges two dictionaries recursively.
    If a key is present in both dictionaries, the value
    from d2 is used.

    Args:
        d1: First dictionary
        d2: Second dictionary

    Returns:
        Merged dictionary
    """
    merged = {}
    for k in set(d1.keys()).union(d2.keys()):
        if k in d1 and k in d2:
            if not isinstance(d1[k], type(d2[k])):
                raise ValueError(f'Cannot merge values of different types: {k}')

            if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                merged[k] = merge_dicts_recursively(d1[k], d2[k])
            else:
                merged[k] = d2[k]
        elif k in d1:
            merged[k] = d1[k]
        else:
            merged[k] = d2[k]

    return merged
