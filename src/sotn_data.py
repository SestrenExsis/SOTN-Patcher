import argparse
import json

if __name__ == '__main__':
    '''
    Convert extracted game data into a usable JSON file

    Usage
    python src/sotn_data.py INPUT_JSON OUTPUT_JSON
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('extracted_data_filepath', help='Input a filepath to the extracted data stored as a JSON file', type=str)
    parser.add_argument('data_core_filepath', help='Input a filepath for creating the output JSON file', type=str)
    args = parser.parse_args()
    with open(args.extracted_data_filepath) as extracted_data_file:
        extracted_data = json.load(extracted_data_file)
        rooms = {}
        for (stage_name, rooms_data) in extracted_data['Rooms'].items():
            for room_data in rooms_data:
                room_id = room_data['Room ID']
                room_layers = extracted_data['Room-Layers'][stage_name]
                layers = extracted_data['Layers'][stage_name]
                try:
                    foreground_layer_id = room_layers[room_id]['Layer IDs'][0]
                    packed_layout = layers[foreground_layer_id]['Packed Layout']
                    special_flag = int(packed_layout[:2], 16)
                    layer_key = stage_name + ', Layer ID ' + f'{foreground_layer_id:02d}'
                    layer_data_address = extracted_data['Extractions']['Layers'][layer_key]['Gamedata Address']
                except (IndexError, KeyError):
                    foreground_layer_id = None
                    special_flag = None
                    layer_data_address = None
                room_key = stage_name + ', ' + room_data['Room Name']
                room = {
                    'Stage': room_data['Stage'],
                    'Room ID': room_id,
                    'Top': room_data['Top'],
                    'Left': room_data['Left'],
                    'Rows': room_data['Rows'],
                    'Columns': room_data['Columns'],
                    'Special Flag': special_flag,
                    'Foreground Layer ID': foreground_layer_id,
                    'Room Name': room_data['Room Name'],
                    'Addresses': {
                        'Room Data': extracted_data['Extractions']['Rooms'][room_key]['Gamedata Address'],
                        'Packed Room Data': None if layer_data_address is None else layer_data_address + 8,
                    }
                }
                rooms[room_key] = room
        entity_layouts = {}
        for (stage_name, entity_layouts_data) in extracted_data['Entity Layouts - Horizontal'].items():
            ext_meta_horizontal = extracted_data['Entity Layouts - Horizontal'][stage_name]['Extraction Metadata']
            ext_meta_vertical = extracted_data['Entity Layouts - Vertical'][stage_name]['Extraction Metadata']
            entity_layouts[stage_name] = []
            for (entity_layout_id, entity_layout_data) in enumerate(entity_layouts_data['Elements']):
                if entity_layout_data['X'] == -2:
                    horizontal_address_start = (1 + entity_layout_data['Element Index']) * ext_meta_horizontal['Element Size'] + ext_meta_horizontal['Gamedata Address']
                    vertical_address_start = (1 + entity_layout_data['Element Index']) * ext_meta_vertical['Element Size'] + ext_meta_vertical['Gamedata Address']
                    entity_layout = {
                        'Entities': [],
                        'Entity Layout ID': len(entity_layouts[stage_name]),
                        'Addresses': {
                            'Horizontal Data': horizontal_address_start,
                            'Vertical Data': vertical_address_start,
                        },
                    }
                elif entity_layout_data['X'] == -1:
                    entity_layouts[stage_name].append(entity_layout)
                else:
                    entity = {
                        'Entity ID': len(entity_layout['Entities']),
                        'X': entity_layout_data['X'],
                        'Y': entity_layout_data['Y'],
                        'Entity Type ID': entity_layout_data['Entity Type ID'],
                        'Entity Room Index': entity_layout_data['Entity Room Index'],
                        'Params': entity_layout_data['Params'],
                    }
                    entity_layout['Entities'].append(entity)
        data_core = {
            'Rooms': rooms,
            'Entity Layouts': entity_layouts,
        }
        with open(args.data_core_filepath, 'w') as data_core_file:
            json.dump(data_core, data_core_file, indent='    ', sort_keys=True)
