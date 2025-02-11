# External libraries
import argparse
import json
import os
import yaml

# Local libraries
import sotn_address

class PPF:
    def __init__(self, description):
        self.patches = []
        self.description = (description + 50 * ' ')[:50]
        self.bytes = bytearray()
        self.write_string('PPF30')
        self.write_byte(2) # Encoding method = PPF3.0
        self.write_string(self.description)
        self.write_byte(0) # Imagetype = BIN
        self.write_byte(0) # Blockcheck = Disabled
        self.write_byte(0) # Undo data = Not available
        self.write_byte(0) # Dummy
        assert len(self.bytes) == 60 # 0x3C
    
    def write_byte(self, byte):
        assert 0x00 <= byte < 0x100
        self.bytes.append(byte)
    
    def write_u8(self, value):
        write_value = value
        for _ in range(1):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_s8(self, value):
        write_value = (value & 0x7F) + (0x80 if value < 0 else 0x00)
        for _ in range(1):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_u16(self, value):
        write_value = value
        for _ in range(2):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_s16(self, value):
        write_value = (value & 0x7FFF) + (0x8000 if value < 0 else 0x0000)
        for _ in range(2):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_u32(self, value):
        write_value = value
        for _ in range(4):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_u32(self, value):
        write_value = value
        for _ in range(4):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_s32(self, value):
        write_value = (value & 0x7FFFFFFF) + (0x80000000 if value < 0 else 0x00000000)
        for _ in range(4):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_u64(self, value):
        write_value = value
        for _ in range(8):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_string(self, string):
        for char in string:
            self.write_byte(ord(char))
    
    def patch_value(self, value: int, type: str, address: sotn_address.Address):
        self.write_u64(address.to_disc_address())
        if type == 'u8':
            size = 1
            self.write_byte(size)
            self.write_u8(value)
        elif type == 's8':
            size = 1
            self.write_byte(size)
            self.write_s8(value)
        elif type == 'u16':
            size = 2
            self.write_byte(size)
            self.write_u16(value)
        elif type == 's16':
            size = 2
            self.write_byte(size)
            self.write_s16(value)
        elif type == 'u32':
            size = 4
            self.write_byte(size)
            self.write_u32(value)
        elif type == 's32':
            size = 4
            self.write_byte(size)
            self.write_s32(value)
        else:
            raise Exception('Incorrect size for value:', (value, size))

def get_changes_template_file(extract):
    result = {
        'Boss Teleporters': {},
        'Constants': {},
        'Stages': {},
        'Teleporters': {},
        'Castle Map': [],
    }
    for boss_teleporter_index in range(len(extract['Boss Teleporters']['Data'])):
        result['Boss Teleporters'][boss_teleporter_index] = {
            'Room X': extract['Boss Teleporters']['Data'][boss_teleporter_index]['Room X'],
            'Room Y': extract['Boss Teleporters']['Data'][boss_teleporter_index]['Room Y'],
        }
    for constant_name in extract['Constants']:
        result['Constants'][constant_name] = extract['Constants'][constant_name]['Value']
    for (stage_id, stage_data) in extract['Stages'].items():
        result['Stages'][stage_id] = {}
        result['Stages'][stage_id]['Rooms'] = {}
        for (room_id, room_data) in stage_data['Rooms'].items():
            relic_found_ind = False
            object_layout_h = None
            object_layout_v = None
            if room_data['Tileset ID']['Value'] != -1:
                object_layout_h = {}
                for (index, object_layout_data) in enumerate(room_data['Object Layout - Horizontal']['Data']):
                    entity_type_id = object_layout_data['Entity Type ID']
                    if entity_type_id == 11:
                        relic_found_ind = True
                        object_h = {
                            'Entity Type ID': entity_type_id,
                            'Params': object_layout_data['Params'],
                        }
                        object_layout_h[index] = object_h
                object_layout_v = {}
                for (index, object_layout_data) in enumerate(room_data['Object Layout - Vertical']['Data']):
                    entity_type_id = object_layout_data['Entity Type ID']
                    if entity_type_id == 11:
                        relic_found_ind = True
                        object_h = {
                            'Entity Type ID': entity_type_id,
                            'Params': object_layout_data['Params'],
                        }
                        object_layout_v[index] = object_h
            result['Stages'][stage_id]['Rooms'][room_id] = {
                'Left': room_data['Left']['Value'],
                'Top': room_data['Top']['Value'],
            }
            if relic_found_ind:
                room = result['Stages'][stage_id]['Rooms'][room_id]
                room['Object Layout - Horizontal'] = object_layout_h
                room['Object Layout - Vertical'] = object_layout_v
    for teleporter_index in range(len(extract['Teleporters']['Data'])):
        result['Teleporters'][teleporter_index] = {
            'Player X': extract['Teleporters']['Data'][teleporter_index]['Player X'],
            'Player Y': extract['Teleporters']['Data'][teleporter_index]['Player Y'],
            'Room Offset': extract['Teleporters']['Data'][teleporter_index]['Room Offset'],
            'Target Stage ID': extract['Teleporters']['Data'][teleporter_index]['Target Stage ID'],
        }
    for row in range(len(extract['Castle Map']['Data'])):
        row_data = extract['Castle Map']['Data'][row]
        result['Castle Map'].append(row_data)
    return result

def validate_changes(changes):
    if 'Boss Teleporters' in changes:
        # TODO(sestren): Validate boss teleporters
        pass
    if 'Constants' in changes:
        # TODO(sestren): Validate constants
        pass
    if 'Stages' in changes:
        for (stage_id, stage_data) in changes['Stages'].items():
            if 'Rooms' in stage_data:
                for (room_id, room_data) in stage_data['Rooms'].items():
                    if 'Top' in room_data:
                        # assert 0 <= room_data['Top'] <= 58
                        assert 0 <= room_data['Top'] <= 63
                    if 'Left' in room_data:
                        assert 0 <= room_data['Left'] <= 63
                    if 'Object Layout - Horizontal' in room_data:
                        # TODO(sestren): Validate changes to object layouts
                        pass
    if 'Teleporters' in changes:
        # TODO(sestren): Validate teleporters
        pass

def get_ppf(extract, changes):
    result = PPF('Just messing around')
    # Patch boss teleporters
    if 'Boss Teleporters' in changes:
        extract_metadata = extract['Boss Teleporters']['Metadata']
        for boss_teleporter_index in sorted(changes['Boss Teleporters']):
            boss_teleporter_data = changes['Boss Teleporters'][boss_teleporter_index]
            extract_data = extract['Boss Teleporters']['Data'][int(boss_teleporter_index)]
            # Boss Teleporter: Patch room X
            room_x = extract_data['Room X']
            if 'Room X' in boss_teleporter_data:
                if boss_teleporter_data['Room X'] != room_x:
                    room_x = boss_teleporter_data['Room X']
                    result.patch_value(
                        room_x,
                        extract_metadata['Fields']['Room X']['Type'],
                        sotn_address.Address(extract_metadata['Start'] + int(boss_teleporter_index) * extract_metadata['Size'] + extract_metadata['Fields']['Room X']['Offset']),
                    )
            # Boss Teleporter: Patch room Y
            room_y = extract_data['Room Y']
            if 'Room Y' in boss_teleporter_data:
                if boss_teleporter_data['Room Y'] != room_y:
                    room_y = boss_teleporter_data['Room Y']
                    result.patch_value(
                        room_y,
                        extract_metadata['Fields']['Room Y']['Type'],
                        sotn_address.Address(extract_metadata['Start'] + int(boss_teleporter_index) * extract_metadata['Size'] + extract_metadata['Fields']['Room Y']['Offset']),
                    )
    # Patch constants
    if 'Constants' in changes:
        for constant_id in sorted(changes['Constants']):
            constant_data = changes['Constants'][constant_id]
            constant_extract = extract['Constants'][constant_id]
            if constant_data != constant_extract['Value']:
                result.patch_value(
                    constant_data,
                    constant_extract['Type'],
                    sotn_address.Address(constant_extract['Start']),
                )
    # Patch stage data
    if 'Stages' in changes:
        for stage_id in sorted(changes['Stages']):
            # print(stage_id)
            stage_data = changes['Stages'][stage_id]
            stage_extract = extract['Stages'][stage_id]
            # Stage: Patch room data
            if 'Rooms' in stage_data:
                for room_id in sorted(stage_data['Rooms']):
                    # print('', room_id)
                    room_data = stage_data['Rooms'][room_id]
                    room_extract = stage_extract['Rooms'][room_id]
                    left = room_extract['Left']['Value']
                    right = room_extract['Right']['Value']
                    # Room: Patch left and right
                    if 'Left' in room_data:
                        if room_data['Left'] != left:
                            left = room_data['Left']
                            result.patch_value(
                                left,
                                room_extract['Left']['Type'],
                                sotn_address.Address(room_extract['Left']['Start']),
                            )
                            width = 1 + room_extract['Right']['Value'] - room_extract['Left']['Value']
                            right = left + width - 1
                            result.patch_value(
                                right,
                                room_extract['Right']['Type'],
                                sotn_address.Address(room_extract['Right']['Start']),
                            )
                    # Room: Patch top and bottom
                    top = room_extract['Top']['Value']
                    bottom = room_extract['Bottom']['Value']
                    if 'Top' in room_data:
                        if room_data['Top'] != top:
                            top = room_data['Top']
                            result.patch_value(
                                top,
                                room_extract['Top']['Type'],
                                sotn_address.Address(room_extract['Top']['Start']),
                            )
                            height = 1 + room_extract['Bottom']['Value'] - room_extract['Top']['Value']
                            bottom = top + height - 1
                            result.patch_value(
                                bottom,
                                room_extract['Bottom']['Type'],
                                sotn_address.Address(room_extract['Bottom']['Start']),
                            )
                    # Room: Patch layout rect if applicable and any derived values changed
                    if 'Tile Layout' in room_extract:
                        tile_layout_extract = room_extract['Tile Layout']
                        flags = 0xFF & (tile_layout_extract['Layout Rect']['Value'] >> 24)
                        layout_rect = (
                            left << 0 |
                            top << 6 |
                            right << 12  |
                            bottom << 18 |
                            flags << 24
                        )
                        if layout_rect != tile_layout_extract['Layout Rect']['Value']:
                            result.patch_value(
                                layout_rect,
                                tile_layout_extract['Layout Rect']['Type'],
                                sotn_address.Address(tile_layout_extract['Layout Rect']['Start']),
                            )
                    # Room: Patch object layout horizontal
                    if 'Object Layout - Horizontal' in room_data:
                        object_layout_data = room_data['Object Layout - Horizontal']
                        object_layout_extract = room_extract['Object Layout - Horizontal']
                        for object_id in sorted(object_layout_data):
                            object_index = int(object_id)
                            object_data = object_layout_data[object_id]
                            object_extract = object_layout_extract['Data'][object_index]
                            if 'Params' in object_data:
                                if object_data['Params'] != object_extract['Params']:
                                    result.patch_value(
                                        object_data['Params'],
                                        object_layout_extract['Metadata']['Fields']['Params']['Type'],
                                        sotn_address.Address(object_layout_extract['Metadata']['Start']),
                                    )
                    # Room: Patch object layout vertical
                    if 'Object Layout - Vertical' in room_data:
                        object_layout_data = room_data['Object Layout - Vertical']
                        object_layout_extract = room_extract['Object Layout - Vertical']
                        for object_id in sorted(object_layout_data):
                            object_index = int(object_id)
                            object_data = object_layout_data[object_id]
                            object_extract = object_layout_extract['Data'][object_index]
                            if 'Params' in object_data:
                                if object_data['Params'] != object_extract['Params']:
                                    result.patch_value(
                                        object_data['Params'],
                                        object_layout_extract['Metadata']['Fields']['Params']['Type'],
                                        sotn_address.Address(object_layout_extract['Metadata']['Start']),
                                    )
    # Patch teleporters
    if 'Teleporters' in changes:
        extract_metadata = extract['Teleporters']['Metadata']
        for teleporter_index in sorted(changes['Teleporters']):
            teleporter_data = changes['Teleporters'][teleporter_index]
            extract_data = extract['Teleporters']['Data'][int(teleporter_index)]
            # Teleporter: Patch player X
            player_x = extract_data['Player X']
            if 'Player X' in teleporter_data:
                if teleporter_data['Player X'] != player_x:
                    player_x = teleporter_data['Player X']
                    result.patch_value(player_x,
                        extract_metadata['Fields']['Player X']['Type'],
                        sotn_address.Address(extract_metadata['Start'] + int(teleporter_index) * extract_metadata['Size'] + extract_metadata['Fields']['Player X']['Offset']),
                    )
            # Teleporter: Patch player Y
            player_y = extract_data['Player Y']
            if 'Player Y' in teleporter_data:
                if teleporter_data['Player Y'] != player_y:
                    player_y = teleporter_data['Player Y']
                    result.patch_value(player_y,
                        extract_metadata['Fields']['Player Y']['Type'],
                        sotn_address.Address(extract_metadata['Start'] + int(teleporter_index) * extract_metadata['Size'] + extract_metadata['Fields']['Player Y']['Offset']),
                    )
            # Teleporter: Patch room offset
            room_offset = extract_data['Room Offset']
            if 'Room Offset' in teleporter_data:
                if teleporter_data['Room Offset'] != room_offset:
                    room_offset = teleporter_data['Room Offset']
                    result.patch_value(room_offset,
                        extract_metadata['Fields']['Room Offset']['Type'],
                        sotn_address.Address(extract_metadata['Start'] + int(teleporter_index) * extract_metadata['Size'] + extract_metadata['Fields']['Room Offset']['Offset']),
                    )
            # Teleporter: Patch target stage ID
            target_stage_id = extract_data['Target Stage ID']
            if 'Target Stage ID' in teleporter_data:
                if teleporter_data['Target Stage ID'] != target_stage_id:
                    target_stage_id = teleporter_data['Target Stage ID']
                    result.patch_value(target_stage_id,
                        extract_metadata['Fields']['Target Stage ID']['Type'],
                        sotn_address.Address(extract_metadata['Start'] + int(teleporter_index) * extract_metadata['Size'] + extract_metadata['Fields']['Target Stage ID']['Offset']),
                    )
    if 'Castle Map' in changes:
        extract_metadata = extract['Castle Map']['Metadata']
        for row in range(extract_metadata['Rows']):
            row_data = changes['Castle Map'][row]
            for col in range(0, 2 * extract_metadata['Columns'], 2):
                (left, right) = (col, col + 1)
                (little, big) = (int(row_data[left], base=16), int(row_data[right], base=16))
                pixel_pair_value = 0x10 * big + little
                col_span = col // 2
                result.patch_value(pixel_pair_value,
                    'u8',
                    sotn_address.Address(extract_metadata['Start'] + row * extract_metadata['Columns'] + col_span),
                )
    return result

if __name__ == '__main__':
    '''
    Usage
    python sotn_patcher.py CORE_DATA_JSON --changes CHANGES_JSON --ppf OUTPUT_PPF
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('extract_file', help='Input a filepath to the extract JSON file', type=str)
    parser.add_argument('--changes', help='Input an optional filepath to the changes JSON file', type=str)
    parser.add_argument('--ppf', help='Input an optional filepath to the output PPF file', type=str)
    args = parser.parse_args()
    with open(args.extract_file) as extract_file:
        extract = json.load(extract_file)
        if 'Extract' in extract:
            extract = extract['Extract']
        if args.changes is None:
            with open(os.path.join('build', 'changes.json'), 'w') as changes_file:
                changes = get_changes_template_file(extract)
                json.dump(changes, changes_file, indent='    ', sort_keys=True)
        else:
            with (
                open(args.changes) as changes_file,
                open(args.ppf, 'wb') as ppf_file,
            ):
                changes = json.load(changes_file)
                if 'Changes' in changes:
                    changes = changes['Changes']
                with open(os.path.join('data', 'aliases.yaml')) as aliases_file:
                    aliases = yaml.safe_load(aliases_file)
                for (stage_name, stage_changes) in changes['Stages'].items():
                    aliases_found = {}
                    # print(stage_name)
                    for room_name in stage_changes['Rooms']:
                        # print('', room_name)
                        if room_name in aliases['Rooms']:
                            room_index = aliases['Rooms'][room_name]['Index']
                            aliases_found[room_name] = str(room_index)
                        else:
                            pass
                            # print('Cannot find alias', (stage_name, room_name))
                            # raise Exception('Cannot find alias')
                    for (key, value) in aliases_found.items():
                        room_data = stage_changes['Rooms'].pop(key)
                        stage_changes['Rooms'][value] = room_data
                validate_changes(changes)
                patch = get_ppf(extract, changes)
                ppf_file.write(patch.bytes)
