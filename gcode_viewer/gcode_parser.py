import re
import numpy as np
from copy import deepcopy

pattern = re.compile(r'([GTMXYZIJKFR]-?\d+(\.\d*)?)', re.IGNORECASE)

class GcodeError(Exception):

    pass

class ReadLines:
    
    def __init__(self, gcode_lines: str):

        self.gcode_lines = gcode_lines
        self.g_code = []
        self.is_inch = False
        self.is_metric = False
        self.relative_sys = False
        self.coordinates = {'X': 0, 'Y': 0, 'Z': 20, 'I': 0, 'J': 0, 'K': 0}
        self.coordinate_system = {'G17': False, 'G18': False, 'G19': False}

    def read_G_code(self):

        lines = self.gcode_lines
        if len(lines) == 0:
            raise GcodeError('Your G-code is absent!')
        lines = lines.split('\n')
        if lines[0].strip() != '%' or lines[-1].strip() != '%':
            raise GcodeError('Your G-code must start and end with the "%" symbol!')
    
        for line in lines[1:-1]:
            line = line.strip()
            if line.startswith('('):
                continue
            matches = pattern.findall(line)
            current_values = {}

            for match in matches:
                command = match[0]
                letter = command[0].upper()
                letter_value = float(command[1:])

                if letter == 'G':
                    if 'G' not in current_values:
                        current_values['G'] = []
                    current_values['G'].append(letter_value)
                
                    match letter_value:
                        case 17:
                            self.coordinate_system['G17'] = True
                            self.coordinate_system['G18'] = False
                            self.coordinate_system['G19'] = False
                        case 18:
                            self.coordinate_system['G17'] = False
                            self.coordinate_system['G18'] = True
                            self.coordinate_system['G19'] = False
                        case 19:
                            self.coordinate_system['G17'] = False
                            self.coordinate_system['G18'] = False
                            self.coordinate_system['G19'] = True
                        case 20:
                            self.is_inch = True
                        case 21:
                            self.is_metric = True
                        case 91:
                            self.relative_sys = True

                elif letter in ('X', 'Y', 'Z', 'I', 'J', 'K', 'F', 'R') and '.' in command:
                    self.coord_sys(letter)
                    integer, decimal = command[1:].split('.')
                    if len(decimal) > 4 and self.is_metric:
                        raise GcodeError(f"The fractional part exceeds the allowed number of digits after the decimal point in {command}!")
                    if self.relative_sys:
                        self.g91(letter, letter_value, current_values)
                    else:
                        current_values[letter] = letter_value

                elif letter in ('T', 'M'):
                    current_values[letter] = letter_value

                else:
                    raise GcodeError(f"Missing '.' symbol after integer part of number in {command}!")
                
            if self.is_inch:
                for inch_key in current_values.keys():
                    if inch_key in ('G', 'M', 'T', 'F'):
                        continue
                    else:
                        current_values[inch_key] *= 25.4

            self.g_code.append(current_values.copy())

        return self.g_code

    def coord_sys(self, letter):

        if self.coordinate_system['G17'] and letter == 'K':
            raise GcodeError("Coordinate {0} is not allowed with G17!".format(letter))
        if self.coordinate_system['G18'] and letter == 'J':
            raise GcodeError("Coordinate {0} is not allowed with G18!".format(letter))
        if self.coordinate_system['G19'] and letter == 'I':
            raise GcodeError("Coordinate {0} is not allowed with G19!".format(letter))

    def g91(self, letter, letter_value, current_values):

        if letter in ('X', 'Y', 'Z'):
            self.coordinates[letter] += letter_value
        elif letter in ('I', 'J', 'K'):
            self.coordinates[letter] += letter_value
        current_values[letter] = self.coordinates[letter]

class Get_Coords:

    def __init__(self, gcode: str):

        self.g_code = gcode
        self.returned_arr = []
        self.x_values, self.y_values, self.z_values = [], [], []
        self.i_values, self.j_values, self.k_values = [], [], []
        self.g_command, self.radiuses = [], []
        self.planesCheck = {'G17': False, 'G18': False, 'G19': False}
        self.r_flag = False

    def find_coords(self):

        print(self.g_code)
        for string in self.g_code:

            modified_dict = deepcopy(string) 

            g = string.get('G', self.g_command[-1] if self.g_command else [0])

            if any(num in g for num in [17, 18, 19]):
                if 17 in g:
                    self.planesCheck = {'G17': True, 'G18': False, 'G19': False}
                if 18 in g:
                    self.planesCheck = {'G17': False, 'G18': True, 'G19': False}
                if 19 in g:
                    self.planesCheck = {'G17': False, 'G18': False, 'G19': True}

            x = string.get('X', self.x_values[-1] if self.x_values else 0)
            y = string.get('Y', self.y_values[-1] if self.y_values else 0)
            z = string.get('Z', self.z_values[-1] if self.z_values else 0)    

            if any(val in (2.0, 3.0) for val in g):
                i = string.get('I', self.i_values[-1] if self.i_values else None)
                j = string.get('J', self.j_values[-1] if self.j_values else None)
                k = string.get('K', self.k_values[-1] if self.k_values else None)
                coords = {'I': i, 'J': j, 'K': k}
                coords = {key: value for key, value in coords.items() if value is not None} #sorted
                centers, starts, delta, distinctions = {}, {}, {}, {}
                coordinate_mapping = {'X': 'I', 'Y': 'J', 'Z': 'K'}
                
                center_list = []
                for axis, coord in coordinate_mapping.items():
                    if coord in coords:
                        centers[axis] = self.__dict__[f"{axis.lower()}_values"][-1] + coords[coord] #finding center
                        center_list.append(centers[axis])
                modified_dict['Center'] = center_list

                if any(clue in string for clue in ('I', 'J', 'K')):     #finding radious through I J K
                    if 'I' in coords and 'J' in coords:
                        radious = np.sqrt(coords['I']**2 + coords['J']**2)
                    elif 'K' in coords and 'I' in coords:
                        radious = np.sqrt(coords['K']**2 + coords['I']**2)
                    elif 'J' in coords and 'K' in coords:
                        radious = np.sqrt(coords['J']**2 + coords['K']**2)
                    elif all(coord_key in coords for coord_key in ('I', 'J', 'K')): #Эвклидова метрика
                        radious = np.sqrt(coords['I']**2 + coords['J']**2 + coords['K']**2)
                    self.radiuses.append(radious)
                elif 'R' in string: #or took radious from dict
                    sended_params = []
                    self.r_flag = True
                    radious = string.get('R', self.radiuses[-1] if self.radiuses else 0)
                    self.radiuses.append(radious)
                    if self.planesCheck['G17']:
                        sended_params = [self.x_values[-1], x, self.y_values[-1], y]
                    if self.planesCheck['G18']:
                        sended_params = [self.x_values[-1], x, self.z_values[-1], z]
                    if self.planesCheck['G19']:
                        sended_params = [self.y_values[-1], y, self.z_values[-1], z]
                    modified_dict['Center'] = self.find_center_through_R(radious, sended_params, g)
                modified_dict['R'] = float(radious)
            
                for axis in coordinate_mapping.keys():
                    starts[axis] = self.__dict__[f"{axis.lower()}_values"][-1]  #previous param is start coord

                for parameter_key, parameter_value in centers.items():
                    delta[parameter_key] = starts[parameter_key] - centers[parameter_key]   #for find angle

                if len(delta) == 2 or len(delta) == 0: #if we have 2 param for angle so its 2D
                    if not self.r_flag: 
                        planes = [('X', 'Y'), ('Z', 'Y'), ('Z', 'X')]
                        delta_param = list(delta.keys())
                        for plane in planes:
                            if plane[0] in delta_param and plane[1] in delta_param:
                                if plane == ('X', 'Y'):
                                    start_angle = np.arctan2(delta['Y'], delta['X'])
                                elif plane == ('Z', 'Y'):
                                    start_angle = np.arctan2(delta['Z'], delta['Y'])
                                elif plane == ('Z', 'X'):
                                    start_angle = np.arctan2(delta['Z'], delta['X'])
                    if self.r_flag:
                        if self.planesCheck['G17']:
                            start_angle = np.arctan2(self.y_values[-1] - modified_dict['Center'][1], self.x_values[-1] - modified_dict['Center'][0])
                        if self.planesCheck['G18']:
                            start_angle = np.arctan2(self.z_values[-1] - modified_dict['Center'][1], self.x_values[-1] - modified_dict['Center'][0])
                        if self.planesCheck['G19']:
                            start_angle = np.arctan2(self.z_values[-1] - modified_dict['Center'][1], self.y_values[-1] - modified_dict['Center'][0])

                elif len(delta) == 3:   #else 3D
                    first_vector, second_vector, u_axis, v_axis = self.find_angle_3D(centers, starts, x, y, z)
                    u_coord = np.dot(first_vector, u_axis)
                    v_coord = np.dot(first_vector, v_axis)
                    start_angle = np.arctan2(v_coord, u_coord)
                modified_dict['StartAngle'] = float(start_angle)

                for new_key, new_value in centers.items():  #distinction for second angle
                    for new_axis in ('X', 'Y', 'Z'):
                        if new_axis in centers:
                            distinctions[new_key] = string.get(new_key, self.__dict__[f"{new_key.lower()}_values"][-1]) - centers.get(new_key, 0)

                if len(distinctions) == 2 or len(distinctions) == 0:  #same definition as for start angle
                    planes = [('X', 'Y'), ('Z', 'Y'), ('Z', 'X')]
                    distinctions_param = list(distinctions.keys())
                    if not self.r_flag:
                        for flat in planes:
                            if flat[0] in distinctions_param and flat[1] in distinctions_param:
                                if flat == ('X', 'Y'):
                                    end_angle = np.arctan2(distinctions['Y'], distinctions['X'])
                                elif flat == ('Z', 'X'):
                                    end_angle = np.arctan2(distinctions['Z'], distinctions['X'])
                                elif flat == ('Z', 'Y'):
                                    end_angle = np.arctan2(distinctions['Z'], distinctions['Y'])
                    if self.r_flag:
                        if self.planesCheck['G17']:
                            x_temp = x if x is not None else self.x_values[-1]
                            y_temp = y if y is not None else self.y_values[-1]
                            end_angle = np.arctan2(y_temp - modified_dict['Center'][1], x_temp - modified_dict['Center'][0])
                        if self.planesCheck['G18']:
                            x_temp = x if x is not None else self.x_values[-1]
                            z_temp = z if z is not None else self.z_values[-1]
                            end_angle = np.arctan2(z_temp - modified_dict['Center'][1], x_temp - modified_dict['Center'][0])
                        if self.planesCheck['G19']:
                            y_temp = y if y is not None else self.y_values[-1]
                            z_temp = z if z is not None else self.z_values[-1]
                            end_angle = np.arctan2(z_temp - modified_dict['Center'][1], y_temp - modified_dict['Center'][0])

                elif len(distinctions) == 3:
                    u_coord_1 = np.dot(second_vector, u_axis)
                    v_coord_1 = np.dot(second_vector, v_axis)
                    end_angle = np.arctan2(v_coord_1, u_coord_1)
            
                if 2.0 in g and end_angle > start_angle:
                    end_angle -= 2 * np.pi
                elif 3.0 in g and end_angle < start_angle:
                    end_angle += 2 * np.pi

                modified_dict['EndAngle'] = float(end_angle)

                poped_keys = ['I', 'J', 'K']
                for pop_key in poped_keys:
                    if pop_key in modified_dict:
                        modified_dict.pop(pop_key)
            
                self.r_flag = False
                self.x_values.append(x)
                self.y_values.append(y)
                self.z_values.append(z)

            else:
                self.x_values.append(x)
                self.y_values.append(y)
                self.z_values.append(z)

            self.returned_arr.append(modified_dict)
            
        print(self.returned_arr)
        return self.returned_arr

    def find_angle_3D(self, centers, starts, x, y, z):

        first_vector = np.array([starts['X'] - centers['X'], starts['Y'] - centers['Y'], starts['Z'] - centers['Z']])
        second_vector = np.array([x - centers['X'], y - centers['Y'], z - centers['Z']])
        arr = [[first_vector[0], first_vector[1], first_vector[2]], [second_vector[0], second_vector[1], second_vector[2]]]
        i_arr = [[arr[0, 1], arr[0, 2]], [arr[1, 1], arr[1, 2]]]
        j_arr = [[arr[0, 0], arr[0, 2]], [arr[1, 0], arr[1, 2]]]
        k_arr = [[arr[0, 0], arr[0, 1]], [arr[1, 0], arr[1, 1]]]
        i_det, j_det, k_det = np.linalg.det(i_arr), np.linalg.det(j_arr), np.linalg.det(k_arr)
        result_det = np.array(i_det, -j_det, k_det)
        result_det_norm = np.linalg.norm(result_det)
        len_vector = np.linalg.norm(first_vector)
        u_axis = np.array([first_vector[0] / len_vector, first_vector[1] / len_vector, first_vector[2] / len_vector])
        w_axis = np.array([result_det[0] / result_det_norm, result_det[1] / result_det_norm, result_det[2] / result_det_norm])
        v_axis = np.cross(w_axis, u_axis)
        return first_vector, second_vector, u_axis, v_axis
        
    def find_center_through_R(self, radious, taken_array, g_param):

        chord_1 = taken_array[1] - taken_array[0]
        chord_2 = taken_array[3] - taken_array[2]

        centerChord1 = (taken_array[0] + taken_array[1]) / 2
        centerChord2 = (taken_array[2] + taken_array[3]) / 2

        chord_len = np.sqrt(chord_1 ** 2 + chord_2 ** 2)
        distance = np.sqrt(radious ** 2 - (chord_len / 2) ** 2)

        if g_param == 2:
            vec = (-chord_2/chord_len, chord_1/chord_len)
        else:
            vec = (chord_2/chord_len, -chord_1/chord_len)

        center1 = centerChord1 + distance * vec[0]
        center2 = centerChord2 + distance * vec[1]

        return [float(center1), float(center2)]
