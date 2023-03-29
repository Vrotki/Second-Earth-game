import parameters
import utility

class terrain:
    def __init__(self, input_dict, global_manager):
        '''
        Takes min_parametername and max_parametername as parameter_dict entries for each parameter type in parameter_types
        '''
        self.global_manager = global_manager
        self.parameter_dict = {}
        self.name = input_dict['name']
        for current_parameter_type in self.global_manager.get('parameter_types'):
            self.parameter_dict[current_parameter_type] = parameters.parameter(current_parameter_type, 
                                                                    input_dict['min_' + current_parameter_type], 
                                                                    input_dict['max_' + current_parameter_type])
        global_manager.get('terrain_list').append(self)

    def __str__(self):
        return_value = '\nName: ' + self.name
        for current_parameter_type in self.global_manager.get('parameter_types'):
            current_parameter = self.parameter_dict[current_parameter_type]
            return_value += '\n\t' + str(current_parameter.name).capitalize() + ': ' + str(current_parameter.min) + '-' + str(current_parameter.max)
        return_value += '\n\tVolume: ' + str(self.volume())
        return_value += '\n'
        return(return_value)
    
    def to_save_dict(self):
        '''
        Returns save_dict in same format that terrain takes as parameter_dict
        '''
        save_dict = {}
        save_dict['name'] = self.name
        for parameter_type in self.global_manager.get('parameter_types'):
            current_parameter = self.parameter_dict[parameter_type]
            save_dict['min_' + current_parameter.name] = current_parameter.min
            save_dict['max_' + current_parameter.name] = current_parameter.max
        return(save_dict)

    def remove(self):
        self.global_manager.set('terrain_list', utility.remove_from_list(self.global_manager.get('terrain_list'), self))

    def in_bounds(self, terrain_dict):
        for current_parameter_type in self.global_manager.get('parameter_types'):
            parameter_value = terrain_dict[current_parameter_type]
            if not self.parameter_dict[current_parameter_type].in_bounds(parameter_value):
                return(False)
        return(True)

    def volume(self):
        return_value = 1
        for current_parameter_type in self.global_manager.get('parameter_types'):
            return_value *= self.parameter_dict[current_parameter_type].width()
        return(return_value)

class point():
    def __init__(self, input_dict, global_manager):
        self.global_manager = global_manager
        self.parameter_dict = {}
        for current_parameter_type in self.global_manager.get('parameter_types'):
            self.parameter_dict[current_parameter_type] = input_dict[current_parameter_type]
        global_manager.get('point_list').append(self)

    def __str__(self):
        return_value = ''
        segment_size = 30
        for current_parameter_type in self.global_manager.get('parameter_types'):
            current_line = self.fill_empty_space(segment_size, current_parameter_type, False)
            for i in range(0, 6):
                starting_text = str(i + 1) + ': '
                text = self.global_manager.get('parameter_keywords')[current_parameter_type][i + 1]

                local_terrain = utility.get_terrain(self.generate_adjacent_parameter_dict(current_parameter_type, i + 1), self.global_manager)
                if local_terrain == 'none':
                    text += '()'
                else:
                    text += '(' + local_terrain.name +')'
                current_line += starting_text + self.fill_empty_space(segment_size - 3, text, False)
            return_value += '\n' + current_line

            current_line = ''
            for i in range(0, 7):
                text = ''
                if self.parameter_dict[current_parameter_type] == i:
                    text = 'X'
                current_line += self.fill_empty_space(segment_size, text, False)
            return_value += '\n' + current_line + '\n'
        return(return_value)
    
    def generate_adjacent_parameter_dict(self, changed_parameter_type, new_value):
        return_dict = {}
        for current_parameter_type in self.global_manager.get('parameter_types'):
            if current_parameter_type == changed_parameter_type:
                return_dict[current_parameter_type] = new_value
            else:
                return_dict[current_parameter_type] = self.parameter_dict[current_parameter_type]
        return(return_dict)

    def fill_empty_space(self, length, string, to_start = True):
        add_to_start = to_start #True
        string = str(string)
        while(len(string) < length):
            if add_to_start:
                string = ' ' + string
                add_to_start = False
            else:
                string = string + ' '
                add_to_start = to_start #True
        return(string)
    