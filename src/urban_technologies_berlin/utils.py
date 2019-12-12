
from colour import Color


def _color_ramp_factory(color_a: str, color_b: str, value_range: (int, int)) -> object:
    """
    Helper function that initializes and returns a color ramp function.

    Args:
        color_a (str): color at the lower bound of the columns ``value_range``
        color_b (str): color at the upper bound of the columns ``value_range``
        value_range (tuple): range to map the colors

    Returns:
        object: function that returns a value from a create color ramp
    """

    lower_bound = int(value_range[0])
    upper_bound = int(value_range[1])
    amount_steps = upper_bound - lower_bound

    # linear transformation to map the input into ``value_range``
    def transform(x):
        return int((x - value_range[0])/(value_range[1] - value_range[0]) * amount_steps)

    colors = list(Color(color_a).range_to(Color(color_b), amount_steps + 1))  # +1 because of exclusive last index
    color_list = [color.get_hex() for color in colors]

    def color_ramp(x):

        return color_list[transform(x)]

    return color_ramp


def style_function_factory(column: str, color_a: str, color_b: str, value_range: (int, int)) -> object:
    """
    Creates a ``style_function`` for folium that colors the given ``value_range``
    of the given ``column`` from ``color_a`` to ``color_b``.

    Args:
        column (str): of the ``GeoDataFrame`` that gets visualized
        color_a (str): color at the lower bound of the columns ``value_range``
        color_b (str): color at the upper bound of the columns ``value_range``
        value_range (tuple): range of ``column`` values

    Returns:
        object: function that can be used as ``style_function`` for folium
    """

    color_ramp = _color_ramp_factory(color_a, color_b, value_range)

    # style options: https://leafletjs.com/reference-1.5.0.html#path-option
    def style_function(x):
        return {
            "color": color_ramp(int(x["properties"][column])),
            "stroke": False,
            "fill": True,
            "fillOpacity": 0.5
        }

    return style_function
