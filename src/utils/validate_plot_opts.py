import matplotlib.colors as mcolors
from matplotlib.lines import Line2D as mlines

_VALID_COLOR_NAMES = [c for c in mcolors.BASE_COLORS.keys()]
_VALID_COLOR_NAMES.extend([c for c in mcolors.TABLEAU_COLORS.keys()])
_VALID_COLOR_NAMES.extend([c for c in mcolors.CSS4_COLORS.keys()])
_VALID_COLOR_NAMES = set(_VALID_COLOR_NAMES)


def valid_hex_color(color_arg: str) -> bool:
    if len(color_arg) == 7 and color_arg[0] == '#':
        for i in range(1, 6, 2):
            try:
                int(color_arg[i:i + 2], 16)
            except (ValueError, IndexError):
                return False
        return True
    return False

def validate_color(color_arg: str) -> bool:
    """ A function that takes in a color arg and returns true if it is a HEX
        value or a valid HTML color.
    """

    if color_arg in _VALID_COLOR_NAMES:
        return True

    elif valid_hex_color(color_arg):
        return True

    return False


def validate_ls(line_style: str) -> bool:
    return line_style.strip() in mlines.lineStyles.keys()

def validate_marker_size(marker_size) -> bool:
    if isinstance(marker_size, int) or isinstance(marker_size, float):
        return marker_size >= 0;
    else:
        return False

def validate_marker(marker: str) -> bool:
    return marker.strip() in mlines.markers.keys()
