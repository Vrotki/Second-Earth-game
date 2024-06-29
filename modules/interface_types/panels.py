# Contains functionality for panels

from .buttons import button
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class panel(button):
    """
    A button that does nothing when clicked and has an optional tooltip
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "panel"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Panels have no on_click behavior, but, since they aren't whitespace, they don't prevent units from being deselected
        Input:
            None
        Output:
            string: Returns 'none' to designate that this click did nothing - still prevents units from deselected but also allows other buttons to be clicked
        """
        flags.choosing_advertised_commodity = False
        flags.choosing_destination = False
        return "none"

    def update_tooltip(self):
        """
        Description:
            Panels have no tooltips
        Input:
            None
        Output:
            None
        """
        return

    def set_tooltip(self):
        """
        Description:
            Panels have no tooltips
        Input:
            None
        Output:
            None
        """
        return

    def can_show_tooltip(self):
        """
        Description:
            Panels have no tooltips
        Input:
            None
        Output:
            None
        """
        return False

    def draw(self):
        """
        Description:
            Draws this panel, ignoring outlines from the panel being clicked
        Input:
            None
        Output:
            None
        """
        if self.showing:
            super().draw(allow_show_outline=False)


class safe_click_panel(panel):
    """
    Panel that prevents selected units/ministers/countries from being deselected when its area is clicked
    """

    def can_show(self):
        """
        Description:
            Returns whether this panel should be drawn - it is drawn when an actor/minister is selected
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        """
        if super().can_show():
            for parameter in ["displayed_mob", "displayed_tile", "displayed_minister"]:
                if getattr(status, parameter):
                    return True
        return False
