# Contains functionality for worker units
import random

from .pmobs import pmob
from ...util import actor_utility
from ...util import market_utility
from ...util import text_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class worker(pmob):
    """
    pmob that is required for resource buildings to produce commodities, officers to form group, and vehicles to function
    """

    def __init__(self, from_save, input_dict, original_constructor: bool = True):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker_type': string value - Type of worker this is, like 'European'. Each type of worker has a separate upkeep, labor pool, and abilities
        Output:
            None
        """
        super().__init__(from_save, input_dict, original_constructor=False)
        self.number = 2  # Workers is plural
        self.is_worker = True
        self.is_church_volunteers = False
        self.worker_type = input_dict["worker_type"]  # European, religious
        status.worker_types[self.worker_type].number += 1
        if not from_save:
            status.worker_types[self.worker_type].on_recruit()
        self.set_controlling_minister_type(constants.type_minister_dict["production"])

        if not from_save:
            self.second_image_variant = random.randrange(0, len(self.image_variants))
        self.update_image_bundle()
        if not from_save:
            if ("select_on_creation" in input_dict) and input_dict[
                "select_on_creation"
            ]:
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, None, override_exempt=True
                )
                actor_utility.calibrate_actor_info_display(
                    status.mob_info_display, self
                )  # updates mob info display list to account for is_worker changing
                self.selection_sound()
        constants.money_label.check_for_updates()
        self.finish_init(original_constructor, from_save, input_dict)

    def replace(self, attached_group="none"):
        """
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        Input:
            None
        Output:
            None
        """
        super().replace()
        if attached_group == "none":
            destination = self
        else:
            destination = attached_group
        destination_message = (
            f" for the {destination.name} at ({destination.x}, {destination.y})"
        )
        status.worker_types[self.worker_type].on_recruit(purchased=True)
        if not self.worker_type in ["religious"]:
            text_utility.print_to_screen(
                f"Replacement {self.worker_type} workers have been automatically hired{destination_message}."
            )

        elif self.worker_type == "religious":
            text_utility.print_to_screen(
                "Replacement church volunteers have been automatically found among nearby colonists."
            )

    def to_save_dict(self):
        """
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'worker_type': string value - Type of worker this is, like 'European'. Each type of worker has a separate upkeep, labor pool, and abilities
        """
        save_dict = super().to_save_dict()
        save_dict["worker_type"] = self.worker_type
        return save_dict

    def fire(self, wander=True):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Additionally has a chance to decrease the upkeep of other workers of this worker's type by increasing the size of
                the labor pool
        Input:
            None
        Output:
            None
        """
        super().fire()
        status.worker_types[self.worker_type].on_fire(wander=wander)

    def can_show_tooltip(self):
        """
        Description:
            Returns whether this worker's tooltip can be shown. Along with the superclass' requirements, worker tooltips cannot be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        """
        if not (self.in_group or self.in_vehicle):
            return super().can_show_tooltip()
        else:
            return False

    def crew_vehicle(self, vehicle):  # to do: make vehicle go to front of info display
        """
        Description:
            Orders this worker to crew the inputted vehicle, attaching this worker to the vehicle and allowing the vehicle to function
        Input:
            vehicle vehicle: vehicle to which this worker is attached
        Output:
            None
        """
        self.in_vehicle = True
        self.hide_images()
        vehicle.set_crew(self)
        moved_mob = vehicle
        for current_image in moved_mob.images:  # moves vehicle to front
            if not current_image.current_cell == "none":
                while not moved_mob == current_image.current_cell.contained_mobs[0]:
                    current_image.current_cell.contained_mobs.append(
                        current_image.current_cell.contained_mobs.pop(0)
                    )
        self.remove_from_turn_queue()
        vehicle.add_to_turn_queue()
        if (
            not flags.loading_save
        ):  # Don't select vehicle if loading in at start of game
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, None, override_exempt=True
            )
            vehicle.select()
            vehicle.selection_sound()

    def uncrew_vehicle(self, vehicle):
        """
        Description:
            Orders this worker to stop crewing the inputted vehicle, making this worker independent from the vehicle and preventing the vehicle from functioning
        Input:
            vehicle vehicle: vehicle to which this worker is no longer attached
        Output:
            None
        """
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        self.show_images()
        if self.images[0].current_cell.get_intact_building("port") == "none":
            self.set_disorganized(True)
        vehicle.set_crew("none")
        vehicle.end_turn_destination = "none"
        vehicle.hide_images()
        vehicle.show_images()  # bring vehicle to front of tile
        vehicle.remove_from_turn_queue()
        actor_utility.calibrate_actor_info_display(
            status.mob_info_display, None, override_exempt=True
        )
        vehicle.select()
        self.add_to_turn_queue()
        self.update_image_bundle()

    def join_group(self):
        """
        Description:
            Hides this worker when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        """
        self.in_group = True
        self.hide_images()
        self.remove_from_turn_queue()

    def leave_group(self, group):
        """
        Description:
            Reveals this worker when its group is disbanded, allowing it to be directly interacted with. Does not select this worker, meaning that the officer will be selected rather than the worker when a group is disbanded
        Input:
            group group: group from which this worker is leaving
        Output:
            None
        """
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()
        self.disorganized = group.disorganized
        self.go_to_grid(self.images[0].current_cell.grid, (self.x, self.y))
        if self.movement_points > 0:
            self.add_to_turn_queue()
        self.update_image_bundle()

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        """
        super().remove()
        status.worker_types[self.worker_type].number -= 1
        constants.money_label.check_for_updates()

    def image_variants_setup(self, from_save, input_dict):
        """
        Description:
            Sets up this unit's image variants
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        """
        if not input_dict["worker_type"] == "religious":
            for variant_type in [
                "soldier",
                "porter",
            ]:  # adds image_dict['soldier']: '.../soldier.png' and image_dict['porter']: '.../porter.png' if any are present in folders
                variants = actor_utility.get_image_variants(
                    self.image_dict["default"], keyword=variant_type
                )
                if len(variants) > 0:
                    self.image_dict[variant_type] = random.choice(variants)
        super().image_variants_setup(from_save, input_dict)

    def get_image_id_list(self, override_values={}):
        """
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        """
        image_id_list = super().get_image_id_list(override_values)
        image_id_list.remove(self.image_dict["default"])  # remove default middle worker
        image_id_list.append(
            actor_utility.generate_unit_component_image_id(
                self.image_dict["default"], "left"
            )
        )
        image_id_list.append(
            actor_utility.generate_unit_component_image_id(
                self.image_variants[self.second_image_variant], "right"
            )
        )
        return image_id_list

    def get_worker(self) -> "pmob":
        """
        Description:
            Returns the worker associated with this unit, if any (self if worker, crew if vehicle, worker component if group)
        Input:
            None
        Output:
            worker: Returns the worker associated with this unit, if any
        """
        return self


class church_volunteers(worker):
    """
    Worker with no cost that can join with a head missionary to form missionaries, created through religious campaigns
    """

    def __init__(self, from_save, input_dict):
        """
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
        Output:
            None
        """
        input_dict["worker_type"] = "religious"
        super().__init__(from_save, input_dict)
        self.set_controlling_minister_type(constants.type_minister_dict["religion"])
