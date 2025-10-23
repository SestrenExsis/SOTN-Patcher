import copy
import json
import os
import yaml

if __name__ == '__main__':
    '''
    Usage
    python find_entity_layout_ids.py build/extraction.json data/aliases.yaml build/aliases2.yaml
    '''
    with (
        open(os.path.join('build', 'extraction.json')) as extract_file,
        open(os.path.join('data', 'aliases.yaml')) as aliases_file,
        open(os.path.join('build','aliases2.yaml'), 'w') as aliases2_file,
    ):
        # Marble Gallery is laid out weird, not contiguous 2D data
        extract = json.load(extract_file)
        aliases = yaml.safe_load(aliases_file)
        aliases2 = copy.deepcopy(aliases)
        for (room_name, room) in aliases['Rooms'].items():
            stage_name = room_name.split(', ')[0]
            room_index = room['Room Index']
            extract_room = extract['Stages'][stage_name]['Rooms'][str(room_index)]
            objects = extract_room.get('Object Layout - Horizontal', {}).get('Data', [])
            if len(objects) < 1:
                continue
            expected_objects = objects[1:-1]
            entity_layout_ids = []
            for (entity_layout_id, entities) in enumerate(extract['Entity Layouts'][stage_name]['Data']):
                if len(entities) != len(expected_objects):
                    continue
                match_ind = True
                for i in range(len(entities)):
                    expected_object = expected_objects[i]
                    entity = entities[i]
                    if len(expected_object) != len(entity):
                        match_ind = False
                        break
                    for (key, value) in expected_object.items():
                        if entity[key] != value:
                            match_ind = False
                            break
                if match_ind:
                    print((stage_name, room_index), entity_layout_id)
                    entity_layout_ids.append(entity_layout_id)
            for index in range(len(entity_layout_ids)):
                key = 'Entity Layout ID'
                if index > 0:
                    key += ' Copy ' + str(index)
                aliases2['Rooms'][room_name][key] = entity_layout_ids[index]
        yaml.dump(aliases2, aliases2_file)
