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
        'Castle Map': [],
        'Castle Map Reveals': [],
        'Constants': {},
        'Familiar Events': {},
        'Stages': {},
        'Strings': {},
        'Teleporters': {},
        'Warp Room Coordinates': {},
    }
    for boss_teleporter_id in range(len(extract['Boss Teleporters']['Data'])):
        result['Boss Teleporters'][boss_teleporter_id] = {
            'Room X': extract['Boss Teleporters']['Data'][boss_teleporter_id]['Room X'],
            'Room Y': extract['Boss Teleporters']['Data'][boss_teleporter_id]['Room Y'],
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
                            'Entity Room Index': object_layout_data['Entity Room Index'],
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
                            'Entity Room Index': object_layout_data['Entity Room Index'],
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
    for teleporter_id in range(len(extract['Teleporters']['Data'])):
        result['Teleporters'][teleporter_id] = {
            'Player X': extract['Teleporters']['Data'][teleporter_id]['Player X'],
            'Player Y': extract['Teleporters']['Data'][teleporter_id]['Player Y'],
            'Room Offset': extract['Teleporters']['Data'][teleporter_id]['Room Offset'],
            'Target Stage ID': extract['Teleporters']['Data'][teleporter_id]['Target Stage ID'],
        }
    for row in range(len(extract['Castle Map']['Data'])):
        row_data = extract['Castle Map']['Data'][row]
        result['Castle Map'].append(row_data)
    for castle_map_reveal_id in range(len(extract['Castle Map Reveals']['Data'])):
        castle_map_reveal = {
            'Bytes Per Row': extract['Castle Map Reveals']['Data'][castle_map_reveal_id]['Bytes Per Row'],
            'Left': extract['Castle Map Reveals']['Data'][castle_map_reveal_id]['Left'],
            'Rows': extract['Castle Map Reveals']['Data'][castle_map_reveal_id]['Rows'],
            'Top': extract['Castle Map Reveals']['Data'][castle_map_reveal_id]['Top'],
            'Grid': extract['Castle Map Reveals']['Data'][castle_map_reveal_id]['Grid'],
        }
        result['Castle Map Reveals'].append(castle_map_reveal)
    for familiar_event_id in range(len(extract['Familiar Events']['Data'])):
        result['Familiar Events'][familiar_event_id] = {
            'Room X': extract['Familiar Events']['Data'][familiar_event_id]['Room X'],
            'Room Y': extract['Familiar Events']['Data'][familiar_event_id]['Room Y'],
        }
    for warp_room_coordinate_id in range(len(extract['Warp Room Coordinates']['Data'])):
        result['Warp Room Coordinates'][warp_room_coordinate_id] = {
            'Room X': extract['Warp Room Coordinates']['Data'][warp_room_coordinate_id]['Room X'],
            'Room Y': extract['Warp Room Coordinates']['Data'][warp_room_coordinate_id]['Room Y'],
        }
    for string_id in extract['Strings']['Data']:
        string = extract['Strings']['Data'][string_id]
        result['Strings'][string_id] = string
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
    extract_metadata = extract['Boss Teleporters']['Metadata']
    for boss_teleporter_id in sorted(changes.get('Boss Teleporters', {})):
        boss_teleporter_data = changes['Boss Teleporters'][boss_teleporter_id]
        extract_data = extract['Boss Teleporters']['Data'][int(boss_teleporter_id)]
        # Boss Teleporter: Patch room X
        room_x = extract_data['Room X']
        if 'Room X' in boss_teleporter_data:
            if boss_teleporter_data['Room X'] != room_x:
                room_x = boss_teleporter_data['Room X']
                result.patch_value(
                    room_x,
                    extract_metadata['Fields']['Room X']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(boss_teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room X']['Offset']),
                )
        # Boss Teleporter: Patch room Y
        room_y = extract_data['Room Y']
        if 'Room Y' in boss_teleporter_data:
            if boss_teleporter_data['Room Y'] != room_y:
                room_y = boss_teleporter_data['Room Y']
                result.patch_value(
                    room_y,
                    extract_metadata['Fields']['Room Y']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(boss_teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room Y']['Offset']),
                )
    # Patch constants
    for constant_id in sorted(changes.get('Constants', {})):
        constant_data = changes['Constants'][constant_id]
        constant_extract = extract['Constants'][constant_id]
        if constant_data != constant_extract['Value']:
            result.patch_value(
                constant_data,
                constant_extract['Type'],
                sotn_address.Address(constant_extract['Start']),
            )
    # Patch stage data
    for stage_id in sorted(changes.get('Stages', {})):
        stage_data = changes['Stages'][stage_id]
        stage_extract = extract['Stages'][stage_id]
        # Stage: Patch room data
        for room_id in sorted(stage_data.get('Rooms', {})):
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
            # Room: Patch object layouts
            for room_property in (
                'Object Layout - Horizontal',
                'Object Layout - Vertical',
            ):
                if room_property not in room_data:
                    continue
                object_changes = room_data[room_property]
                object_extract = room_extract[room_property]
                for element_id in sorted(object_changes):
                    element_index = int(element_id)
                    for field_name in (
                        'Entity Room Index',
                        'Entity Type ID',
                        'Params',
                    ):
                        if not (
                            field_name in object_changes[element_id] and
                            object_changes[element_id][field_name] != object_extract['Data'][element_index][field_name]
                        ):
                            continue
                        result.patch_value(
                            object_changes[element_id][field_name],
                            object_extract['Metadata']['Fields'][field_name]['Type'],
                            sotn_address.Address(
                                object_extract['Metadata']['Start'] + element_index * object_extract['Metadata']['Size'] + object_extract['Metadata']['Fields'][field_name]['Offset']
                            ),
                        )
    # Patch teleporters
    extract_metadata = extract['Teleporters']['Metadata']
    for teleporter_id in sorted(changes.get('Teleporters', {})):
        teleporter_data = changes['Teleporters'][teleporter_id]
        extract_data = extract['Teleporters']['Data'][int(teleporter_id)]
        # Teleporter: Patch player X
        player_x = extract_data['Player X']
        if 'Player X' in teleporter_data:
            if teleporter_data['Player X'] != player_x:
                player_x = teleporter_data['Player X']
                result.patch_value(player_x,
                    extract_metadata['Fields']['Player X']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Player X']['Offset']),
                )
        # Teleporter: Patch player Y
        player_y = extract_data['Player Y']
        if 'Player Y' in teleporter_data:
            if teleporter_data['Player Y'] != player_y:
                player_y = teleporter_data['Player Y']
                result.patch_value(player_y,
                    extract_metadata['Fields']['Player Y']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Player Y']['Offset']),
                )
        # Teleporter: Patch room offset
        room_offset = extract_data['Room Offset']
        if 'Room Offset' in teleporter_data:
            if teleporter_data['Room Offset'] != room_offset:
                room_offset = teleporter_data['Room Offset']
                result.patch_value(room_offset,
                    extract_metadata['Fields']['Room Offset']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room Offset']['Offset']),
                )
        # Teleporter: Patch target stage ID
        target_stage_id = extract_data['Target Stage ID']
        if 'Target Stage ID' in teleporter_data:
            if teleporter_data['Target Stage ID'] != target_stage_id:
                target_stage_id = teleporter_data['Target Stage ID']
                result.patch_value(target_stage_id,
                    extract_metadata['Fields']['Target Stage ID']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Target Stage ID']['Offset']),
                )
    extract_metadata = extract['Castle Map']['Metadata']
    for row in range(extract_metadata.get('Rows', {})):
        if 'Castle Map' not in changes:
            continue
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
    for castle_map_reveal_id in changes.get('Castle Map Reveals', []):
        pass
    # Patch familiar events
    # NOTE(sestren): Familiar events exist as a complete copy in 7 different locations, one for each familiar in the code
    # TODO(sestren): Replace this hacky way of doing it with a better approach
    copy_offsets = [
        0x0392A760, # Possibly for Bat Familiar
        0x0394BDB0, # Possibly for Ghost Familiar
        0x0396FD2C, # Possibly for Faerie Familiar
        0x03990890, # Possibly for Demon Familiar
        0x039AF9E4, # Possibly for Sword Familiar
        0x039D1D38, # Possibly for Yousei Familiar
        0x039F2664, # Possibly for Nose Demon Familiar
    ]
    extract_metadata = extract['Familiar Events']['Metadata']
    for familiar_event_id in sorted(changes.get('Familiar Events', {})):
        familiar_event_data = changes['Familiar Events'][familiar_event_id]
        extract_data = extract['Familiar Events']['Data'][int(familiar_event_id)]
        # Familiar event: Patch room X
        room_x = extract_data['Room X']
        if 'Room X' in familiar_event_data:
            if familiar_event_data['Room X'] != room_x:
                room_x = familiar_event_data['Room X']
                base_offset = extract_metadata['Start'] + int(familiar_event_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room X']['Offset'] - copy_offsets[0]
                for copy_offset in copy_offsets:
                    offset = base_offset + copy_offset
                    result.patch_value(room_x,
                        extract_metadata['Fields']['Room X']['Type'],
                        sotn_address.Address(offset),
                    )
        # Familiar event: Patch room Y
        room_y = extract_data['Room Y']
        if 'Room Y' in familiar_event_data:
            if familiar_event_data['Room Y'] != room_y:
                room_y = familiar_event_data['Room Y']
                base_offset = extract_metadata['Start'] + int(familiar_event_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room Y']['Offset'] - copy_offsets[0]
                for copy_offset in copy_offsets:
                    offset = base_offset + copy_offset
                    result.patch_value(room_y,
                        extract_metadata['Fields']['Room Y']['Type'],
                        sotn_address.Address(offset),
                    )
    # Patch warp room coordinates
    object_extract = extract.get('Warp Room Coordinates', {})
    object_changes = changes.get('Warp Room Coordinates', {})
    for element_id in sorted(object_changes):
        element_index = int(element_id)
        for field_name in (
            'Room X',
            'Room Y',
        ):
            if not (
                field_name in object_changes.get(element_id, {}) and
                object_changes[element_id][field_name] != object_extract['Data'][element_index][field_name]
            ):
                continue
            result.patch_value(
                object_changes[element_id][field_name],
                object_extract['Metadata']['Fields'][field_name]['Type'],
                sotn_address.Address(
                    object_extract['Metadata']['Start'] + element_index * object_extract['Metadata']['Size'] + object_extract['Metadata']['Fields'][field_name]['Offset']
                ),
            )
    # Patch strings
    # NOTE(sestren): There are no guards in place requiring that the resulting array of strings
    # NOTE(sestren): fits into place or uses up the same amount of bytes. It is the
    # NOTE(sestren): responsibility of the user to ensure that custom string arrays will not
    # NOTE(sestren): cause issues.
    NULL_CHAR = 0x00
    SPACE_CHAR = 0x20
    PERIOD_CHAR = 0x44
    QUESTION_MARK_CHAR = 0x48
    APOSTROPHE_CHAR = 0x66
    QUOTE_CHAR = 0x68
    DOUBLE_BYTE_CHAR = 0x81
    extract_metadata = extract['Strings']['Metadata']
    offset = 0
    # NOTE(sestren): Going through all the strings on the extract side is necessary because strings take up a variable amount of bytes
    for (string_id, extracted_string) in extract['Strings']['Data'].items():
        if 'Strings' not in changes:
            continue
        string = extracted_string
        if string_id in changes['Strings']:
            string = changes['Strings'][string_id]
        if str(string_id) in changes['Strings']:
            string = changes['Strings'][str(string_id)]
        for char in string:
            if char in '".?\'':
                result.patch_value(DOUBLE_BYTE_CHAR, 'u8',
                    sotn_address.Address(extract_metadata['Start'] + offset),
                )
                offset += 1
            char_code = SPACE_CHAR
            if char == '"':
                char_code = QUOTE_CHAR
            elif char == ".":
                char_code = PERIOD_CHAR
            elif char == "?":
                char_code = QUESTION_MARK_CHAR
            elif char == "'":
                char_code = APOSTROPHE_CHAR
            elif char in 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                char_code = ord(char)
            elif char in '0123456789':
                result.patch_value(0x82, 'u8',
                    sotn_address.Address(extract_metadata['Start'] + offset),
                )
                offset += 1
                char_code = 0x4f + (ord(char) - ord('0'))
            else:
                char_code = SPACE_CHAR
            result.patch_value(char_code, 'u8',
                sotn_address.Address(extract_metadata['Start'] + offset),
            )
            offset += 1
        padding = 4 - (offset % 4)
        for _ in range(padding):
            result.patch_value(NULL_CHAR, 'u8',
                sotn_address.Address(extract_metadata['Start'] + offset),
            )
            offset += 1
    return result

if __name__ == '__main__':
    '''
    Usage
    python sotn_patcher.py CORE_DATA_JSON --changes CHANGES_JSON --ppf OUTPUT_PPF
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('extract_file', help='Input a filepath to the extract JSON file', type=str)
    parser.add_argument('--changes', help='Input an optional filepath to the changes JSON file', type=str)
    parser.add_argument('--aliases', help='Input an optional filepath to the aliases YAML file', type=str)
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
                open(args.aliases) as aliases_file,
                open(args.ppf, 'wb') as ppf_file,
            ):
                changes = json.load(changes_file)
                if 'Changes' in changes:
                    changes = changes['Changes']
                aliases = yaml.safe_load(aliases_file)
                for (stage_name, stage_changes) in changes.get('Stages', {}).items():
                    aliases_found = {}
                    # print(stage_name)
                    for room_name in stage_changes['Rooms']:
                        # print('', room_name)
                        if room_name in aliases['Rooms']:
                            room_id = aliases['Rooms'][room_name]['Index']
                            aliases_found[room_name] = str(room_id)
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
