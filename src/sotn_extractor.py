# External libraries
import argparse
import json
import os
import yaml

# Local libraries
import sotn_address

def _hex(val: int, size: int) -> str:
    result = ('{:0' + str(size) + 'X}').format(val)
    return result

if __name__ == '__main__':
    '''
    Extract game data from a binary file and output it to a JSON file

    Usage
    python src/sotn_extractor.py INPUT_BIN OUTPUT_JSON
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('binary_filepath', help='Input a filepath to the input BIN file', type=str)
    parser.add_argument('json_filepath', help='Input a filepath for creating the output JSON file', type=str)
    args = parser.parse_args()
    with (
        open(args.binary_filepath, 'br') as binary_file,
        open(os.path.join('data', 'extraction-points.yaml')) as extraction_points_file,
    ):
        extraction_points = yaml.safe_load(extraction_points_file)
        extracted_data = {
            'Extractions': {},
            'Rooms': {},
            'Layers': {},
            'Room-Layers': {},
            'Teleporters': {},
        }
        extracted_data['Extractions']['Rooms'] = {}
        for (stage_name, stage) in extraction_points['Stages'].items():
            if 'Rooms' not in stage or 'Start' not in stage['Rooms']:
                continue
            room_address_start = sotn_address.Address(stage['Rooms']['Start'], 'GAMEDATA')
            rooms_address = sotn_address.Address(room_address_start.address, 'GAMEDATA')
            extracted_data['Extractions']['Rooms'][stage_name] = {
                'Disc Address': rooms_address.to_disc_address(),
                'Gamedata Address': rooms_address.address,
            }
            rooms = []
            current_address = sotn_address.Address(rooms_address.address, 'GAMEDATA')
            while True:
                room_index = len(rooms)
                print((stage_name, room_index), end='--> ')
                room_name = stage['Rooms']['Names'][room_index]
                print(room_name)
                extracted_data['Extractions']['Rooms'][stage_name + ', ' + room_name] = {
                    'Disc Address': current_address.to_disc_address(),
                    'Gamedata Address': current_address.address,
                }
                data = []
                for i in range(8):
                    binary_file.seek(current_address.to_disc_address(i))
                    byte = binary_file.read(1)
                    data.append(byte)
                room = {
                    'Stage': stage_name,
                    'Room ID': room_index,
                    'Left': int.from_bytes(data[0], byteorder='little', signed=False),
                    'Top':  int.from_bytes(data[1], byteorder='little', signed=False),
                    'Right':  int.from_bytes(data[2], byteorder='little', signed=False),
                    'Bottom':  int.from_bytes(data[3], byteorder='little', signed=False),
                    'Layer ID':  int.from_bytes(data[4], byteorder='little', signed=False),
                    'Tile Def ID':  int.from_bytes(data[5], byteorder='little', signed=True),
                    'Entity Gfx ID':  int.from_bytes(data[6], byteorder='little', signed=False),
                    'Entity Layout ID':  int.from_bytes(data[7], byteorder='little', signed=False),
                }
                room['Columns'] = 1 + room['Right'] - room['Left']
                room['Rows'] = 1 + room['Bottom'] - room['Top']
                room['LTRB'] = _hex((
                    ((0x3F & room['Bottom']) << 24) |
                    ((0x3F & room['Right']) << 16) |
                    ((0x3F & room['Top']) << 8) |
                    ((0x3F & room['Left']) << 0)
                ), 8)
                room['Packed LTRB'] = _hex((
                    ((0x3F & room['Bottom']) << 18) |
                    ((0x3F & room['Right']) << 12) |
                    ((0x3F & room['Top']) << 6) |
                    ((0x3F & room['Left']) << 0)
                ), 6)
                room['Room Name'] = room_name
                rooms.append(room)
                current_address.address += 8
                binary_file.seek(current_address.to_disc_address())
                byte = binary_file.read(1)
                value = int.from_bytes(byte, byteorder='little', signed=False)
                if value == 0x40:
                    break
            extracted_data['Rooms'][stage_name] = rooms
        # Extract layer data
        extracted_data['Extractions']['Layers'] = {}
        extracted_data['Extractions']['Room-Layers'] = {}
        for (stage_name, stage) in extraction_points['Stages'].items():
            if (
                'Layers' not in stage or
                'Start' not in stage['Layers'] or
                'Count' not in stage['Layers']
            ):
                continue
            layers_address_start = sotn_address.Address(stage['Layers']['Start'], 'GAMEDATA')
            layer_count = stage['Layers']['Count']
            layers_address = sotn_address.Address(layers_address_start.address, 'GAMEDATA')
            extracted_data['Extractions']['Layers'][stage_name] = {
                'Disc Address': layers_address.to_disc_address(),
                'Gamedata Address': layers_address.address,
            }
            layers = []
            current_address = sotn_address.Address(layers_address.address, 'GAMEDATA')
            for _ in range(layer_count):
                extracted_data['Extractions']['Layers'][stage_name + ', Layer ID ' + f'{len(layers):02d}'] = {
                    'Disc Address': current_address.to_disc_address(),
                    'Gamedata Address': current_address.address,
                }
                layer = {}
                data = []
                for i in range(16):
                    binary_file.seek(current_address.to_disc_address(i))
                    byte = binary_file.read(1)
                    data.append(int.from_bytes(byte))
                layer = {
                    'Layer ID': len(layers),
                    'Tilemap': _hex(int.from_bytes(data[0:4], byteorder='little', signed=False), 8),
                    'Tiledef': _hex(int.from_bytes(data[4:8], byteorder='little', signed=False), 8),
                    'Packed Layout': _hex(int.from_bytes(data[8:12], byteorder='little', signed=False), 8),
                    'Z-Priority':  int.from_bytes(data[12:14], byteorder='little', signed=False),
                    'Unknown 1': int.from_bytes(data[14:15], byteorder='little', signed=False),
                    'Unknown 2': int.from_bytes(data[15:16], byteorder='little', signed=False),
                }
                layers.append(layer)
                current_address.address += 16
            extracted_data['Layers'][stage_name] = layers
            # Extract room-layer assignments, starting from the address where layouts left off
            extracted_data['Extractions']['Room-Layers'][stage_name] = {
                'Disc Address': current_address.to_disc_address(),
                'Gamedata Address': current_address.address,
            }
            extracted_data['Room-Layers'][stage_name] = []
            room_layers = []
            for room_id in range(len(extracted_data['Rooms'][stage_name])):
                if extracted_data['Rooms'][stage_name][room_id]['Tile Def ID'] == -1:
                    continue
                data = []
                for i in range(8):
                    binary_file.seek(current_address.to_disc_address(8 * room_id + i))
                    byte = binary_file.read(1)
                    data.append(int.from_bytes(byte))
                layer_ids = []
                for (layer_id, layer) in enumerate(layers):
                    if layer['Packed Layout'][2:] == extracted_data['Rooms'][stage_name][room_id]['Packed LTRB']:
                        layer_ids.append(layer_id)
                room_layer = {
                    'Stage': stage_name,
                    'Room ID': room_id,
                    'Foreground Layer Pointer': _hex(int.from_bytes(data[0:4], byteorder='little', signed=False), 8),
                    'Background Layer Pointer': _hex(int.from_bytes(data[4:8], byteorder='little', signed=False), 8),
                    'Layer IDs': layer_ids,
                }
                room_layers.append(room_layer)
            extracted_data['Room-Layers'][stage_name] = room_layers
            # Extract teleporter data
            teleporters_address = sotn_address.Address(
                extraction_points['Teleporters']['Start'], 'GAMEDATA'
            )
            extracted_data['Extractions']['Teleporters'] = {}
            teleporters = []
            current_address = sotn_address.Address(teleporters_address.address, 'GAMEDATA')
            for _ in range(extraction_points['Teleporters']['Count']):
                extracted_data['Extractions']['Teleporters']['Teleporter ID ' + f'{len(teleporters):03d}'] = {
                    'Disc Address': current_address.to_disc_address(),
                    'Gamedata Address': current_address.address,
                }
                data = []
                for i in range(10):
                    binary_file.seek(current_address.to_disc_address(i))
                    byte = binary_file.read(1)
                    data.append(int.from_bytes(byte))
                room_id = int.from_bytes(data[4:6], byteorder='little', signed=False) // 8
                teleporter = {
                    'Teleporter ID': len(teleporters),
                    'Player X': int.from_bytes(data[0:2], byteorder='little', signed=False),
                    'Player Y':  int.from_bytes(data[2:4], byteorder='little', signed=False),
                    'Room ID': room_id,
                    'Source Stage ID':  int.from_bytes(data[6:8], byteorder='little', signed=False),
                    'Target Stage ID':  int.from_bytes(data[8:10], byteorder='little', signed=False),
                }
                teleporters.append(teleporter)
                current_address.address += 10
            extracted_data['Teleporters'] = teleporters
        with open(args.json_filepath, 'w') as extracted_data_json:
            json.dump(extracted_data, extracted_data_json, indent='    ', sort_keys=True)
