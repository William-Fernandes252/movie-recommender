from typing import Any


from django.template.defaulttags import register


@register.filter
def get_dict_val(dictionary: dict, key: str, key_as_str=True) -> Any:
    """Return the value of a key in a dictionary.

    Args:
        dictionary (dict): The dictionary to search.
        key (str): The key to search for.
        key_as_str (bool, optional): If the key should be treated as a string.
        Defaults to True.

    Returns:
        Any: The value of the key in the dictionary.
    """
    if not isinstance(dictionary, dict):
        return None
    if key_as_str:
        return dictionary.get(str(key))
    return dictionary.get(key)
