# External libraries
import argparse
import copy
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
        'Options': {
            'Assign Power of Wolf relic a unique ID': False,
            'Enable debug mode': False,
            'Skip Maria cutscene in Alchemy Laboratory': False,
        },
        'Stages': {},
        'Strings': {},
        'Teleporters': {},
    }
    for boss_teleporter_id in range(len(extract['Boss Teleporters']['Data'])):
        result['Boss Teleporters'][boss_teleporter_id] = {
            'Room X': extract['Boss Teleporters']['Data'][boss_teleporter_id]['Room X'],
            'Room Y': extract['Boss Teleporters']['Data'][boss_teleporter_id]['Room Y'],
        }
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
            'Room': extract['Teleporters']['Data'][teleporter_id]['Room'] // 8, # NOTE(sestren): Divide by 8 to translate to room index
            'Stage': extract['Teleporters']['Data'][teleporter_id]['Target Stage ID'],
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
    for string_id in extract['Strings']['Data']:
        string = extract['Strings']['Data'][string_id]
        result['Strings'][string_id] = string
    return result

def validate_changes(changes):
    if 'Boss Teleporters' in changes:
        # TODO(sestren): Validate boss teleporters
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

def getID(aliases: dict, path: tuple):
    result = path[-1]
    scope = aliases
    for token in path:
        if token not in scope:
            break
        scope = scope[token]
    else:
        result = scope
    if type(result) == str:
        result = int(result)
    return result

def get_familiar_changes(changes, familiar_events):
    familiar_changes = {}
    if 'Stages' in changes:
        for familiar_event_name in familiar_events:
            familiar_event = familiar_events[familiar_event_name]
            stage_name = familiar_event['Stage']
            if stage_name not in changes['Stages']:
                continue
            room_name = familiar_event['Room']
            if room_name not in changes['Stages'][stage_name]['Rooms']:
                continue
            source_room = changes['Stages'][stage_name]['Rooms'][room_name]
            if 'Left' not in source_room or 'Top' not in source_room:
                continue
            sign = -1 if familiar_event['Inverted'] else 1
            for familiar_event_id in familiar_event['Familiar Event IDs']:
                familiar_changes[familiar_event_id] = {
                    'Room Y': source_room['Top'],
                    'Room X': sign * source_room['Left'],
                }
    return familiar_changes

def get_ppf(extract, changes, data):
    aliases = data['Aliases']
    result = PPF('Works with SOTN Shuffler Alpha Build 74')
    # Patch boss teleporters
    extract_metadata = extract['Boss Teleporters']['Metadata']
    for boss_teleporter_id in sorted(changes.get('Boss Teleporters', {})):
        boss_teleporter_data = changes['Boss Teleporters'][boss_teleporter_id]
        extract_id = getID(aliases, ('Boss Teleporters', boss_teleporter_id))
        extract_data = extract['Boss Teleporters']['Data'][extract_id]
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
    # Option - Enable debug mode
    if changes.get('Options', {}).get('Enable debug mode', False):
        constant_extract = extract['Constants']['Set initial NOCLIP value']
        result.patch_value(
            0xAC258850,
            constant_extract['Type'],
            sotn_address.Address(constant_extract['Start']),
        )
    # Option - Skip Maria cutscene in Alchemy Laboratory
    if changes.get('Options', {}).get('Skip Maria cutscene in Alchemy Laboratory', False):
        constant_extract = extract['Constants']['Should skip Maria Alchemy Laboratory']
        result.patch_value(
            0x0806E296,
            constant_extract['Type'],
            sotn_address.Address(constant_extract['Start']),
        )
    # Option - Disable clipping on screen edge of Demon Switch Wall
    if changes.get('Options', {}).get('Disable clipping on screen edge of Demon Switch Wall', False):
        for constant_name in (
            'Demon Switch Wall A Tile ID 08',
            'Demon Switch Wall A Tile ID 09',
            'Demon Switch Wall A Tile ID 10',
            'Demon Switch Wall A Tile ID 11',
            'Demon Switch Wall B Tile ID 08',
            'Demon Switch Wall B Tile ID 09',
            'Demon Switch Wall B Tile ID 10',
            'Demon Switch Wall B Tile ID 11',
        ):
            constant_extract = extract['Constants'][constant_name]
            result.patch_value(
                0x01BF,
                constant_extract['Type'],
                sotn_address.Address(constant_extract['Start'])
            )
    # Option - Disable clipping on screen edge of Snake Column Wall
    if changes.get('Options', {}).get('Disable clipping on screen edge of Snake Column Wall', False):
        for constant_name in (
            'Snake Column Wall A Tile ID 00',
            'Snake Column Wall A Tile ID 01',
            'Snake Column Wall A Tile ID 02',
            'Snake Column Wall A Tile ID 03',
            'Snake Column Wall B Tile ID 00',
            'Snake Column Wall B Tile ID 01',
            'Snake Column Wall B Tile ID 02',
            'Snake Column Wall B Tile ID 03',
        ):
            constant_extract = extract['Constants'][constant_name]
            result.patch_value(
                0x0000,
                constant_extract['Type'],
                sotn_address.Address(constant_extract['Start'])
            )
    # Option - Disable clipping on screen edge of Tall Zig Zag Room Wall
    if changes.get('Options', {}).get('Disable clipping on screen edge of Tall Zig Zag Room Wall', False):
        for (constant_name, value) in (
            ('Tall Zig Zag Room Wall A Tile ID 00', 0x05C6),
            ('Tall Zig Zag Room Wall A Tile ID 02', 0x05CE),
            ('Tall Zig Zag Room Wall A Tile ID 04', 0x05D6),
            ('Tall Zig Zag Room Wall A Tile ID 06', 0x05DE),
            ('Tall Zig Zag Room Wall A Tile ID 08', 0x05C6),
            ('Tall Zig Zag Room Wall A Tile ID 10', 0x05CE),
            ('Tall Zig Zag Room Wall A Tile ID 12', 0x05D6),
            ('Tall Zig Zag Room Wall A Tile ID 14', 0x05DE),
            ('Tall Zig Zag Room Wall A Tile ID 16', 0x05C6),
            ('Tall Zig Zag Room Wall A Tile ID 18', 0x05CE),
            ('Tall Zig Zag Room Wall A Tile ID 20', 0x05D6),
            ('Tall Zig Zag Room Wall A Tile ID 22', 0x05DE),
            ('Tall Zig Zag Room Wall B Tile ID 00', 0x05C6),
            ('Tall Zig Zag Room Wall B Tile ID 02', 0x05CE),
            ('Tall Zig Zag Room Wall B Tile ID 04', 0x05D6),
            ('Tall Zig Zag Room Wall B Tile ID 06', 0x05DE),
            ('Tall Zig Zag Room Wall B Tile ID 08', 0x05C6),
            ('Tall Zig Zag Room Wall B Tile ID 10', 0x05CE),
            ('Tall Zig Zag Room Wall B Tile ID 12', 0x05D6),
            ('Tall Zig Zag Room Wall B Tile ID 14', 0x05DE),
            ('Tall Zig Zag Room Wall B Tile ID 16', 0x05C6),
            ('Tall Zig Zag Room Wall B Tile ID 18', 0x05CE),
            ('Tall Zig Zag Room Wall B Tile ID 20', 0x05D6),
            ('Tall Zig Zag Room Wall B Tile ID 22', 0x05DE),
        ):
            constant_extract = extract['Constants'][constant_name]
            result.patch_value(
                value,
                constant_extract['Type'],
                sotn_address.Address(constant_extract['Start'])
            )
    # Option - Disable clipping on screen edge of Plaque Room With Breakable Wall
    if changes.get('Options', {}).get('Disable clipping on screen edge of Plaque Room With Breakable Wall', False):
        for (constant_name, value) in (
            ('Plaque Room With Breakable Wall A Tile ID 00', 0x030F),
            ('Plaque Room With Breakable Wall A Tile ID 01', 0x030E),
            ('Plaque Room With Breakable Wall A Tile ID 02', 0x0334),
            ('Plaque Room With Breakable Wall A Tile ID 03', 0x0766),
            ('Plaque Room With Breakable Wall A Tile ID 04', 0x0327),
            ('Plaque Room With Breakable Wall A Tile ID 05', 0x076B),
            ('Plaque Room With Breakable Wall A Tile ID 06', 0x0351),
            ('Plaque Room With Breakable Wall A Tile ID 07', 0x0323),
            ('Plaque Room With Breakable Wall A Tile ID 08', 0x030F),
            ('Plaque Room With Breakable Wall A Tile ID 09', 0x076D),
            ('Plaque Room With Breakable Wall A Tile ID 10', 0x0334),
            ('Plaque Room With Breakable Wall A Tile ID 11', 0x076E),
            ('Plaque Room With Breakable Wall A Tile ID 12', 0x0327),
            ('Plaque Room With Breakable Wall A Tile ID 13', 0x076F),
            ('Plaque Room With Breakable Wall A Tile ID 14', 0x0351),
            ('Plaque Room With Breakable Wall A Tile ID 15', 0x0770),
            ('Plaque Room With Breakable Wall A Tile ID 16', 0x030F),
            ('Plaque Room With Breakable Wall A Tile ID 17', 0x0771),
            ('Plaque Room With Breakable Wall A Tile ID 18', 0x0334),
            ('Plaque Room With Breakable Wall A Tile ID 19', 0x0772),
            ('Plaque Room With Breakable Wall A Tile ID 20', 0x0327),
            ('Plaque Room With Breakable Wall A Tile ID 21', 0x0773),
            ('Plaque Room With Breakable Wall A Tile ID 22', 0x0351),
            ('Plaque Room With Breakable Wall A Tile ID 23', 0x0774),
            ('Plaque Room With Breakable Wall B Tile ID 00', 0x030F),
            ('Plaque Room With Breakable Wall B Tile ID 01', 0x030E),
            ('Plaque Room With Breakable Wall B Tile ID 02', 0x0334),
            ('Plaque Room With Breakable Wall B Tile ID 03', 0x0766),
            ('Plaque Room With Breakable Wall B Tile ID 04', 0x0327),
            ('Plaque Room With Breakable Wall B Tile ID 05', 0x076B),
            ('Plaque Room With Breakable Wall B Tile ID 06', 0x0351),
            ('Plaque Room With Breakable Wall B Tile ID 07', 0x0323),
            ('Plaque Room With Breakable Wall B Tile ID 08', 0x030F),
            ('Plaque Room With Breakable Wall B Tile ID 09', 0x076D),
            ('Plaque Room With Breakable Wall B Tile ID 10', 0x0334),
            ('Plaque Room With Breakable Wall B Tile ID 11', 0x076E),
            ('Plaque Room With Breakable Wall B Tile ID 12', 0x0327),
            ('Plaque Room With Breakable Wall B Tile ID 13', 0x076F),
            ('Plaque Room With Breakable Wall B Tile ID 14', 0x0351),
            ('Plaque Room With Breakable Wall B Tile ID 15', 0x0770),
            ('Plaque Room With Breakable Wall B Tile ID 16', 0x030F),
            ('Plaque Room With Breakable Wall B Tile ID 17', 0x0771),
            ('Plaque Room With Breakable Wall B Tile ID 18', 0x0334),
            ('Plaque Room With Breakable Wall B Tile ID 19', 0x0772),
            ('Plaque Room With Breakable Wall B Tile ID 20', 0x0327),
            ('Plaque Room With Breakable Wall B Tile ID 21', 0x0773),
            ('Plaque Room With Breakable Wall B Tile ID 22', 0x0351),
            ('Plaque Room With Breakable Wall B Tile ID 23', 0x0774),
        ):
            constant_extract = extract['Constants'][constant_name]
            result.patch_value(
                value,
                constant_extract['Type'],
                sotn_address.Address(constant_extract['Start'])
            )
    # Option - Clock hands show minutes and seconds instead of hours and minutes
    if changes.get('Options', {}).get('Clock hands show minutes and seconds instead of hours and minutes', False):
        for (base, type) in (
            (0x03FD7C2C, 'A'), # Marble Gallery
            (0x0457E5D4, 'A'), # Black Marble Gallery
            (0x05811C94, 'B'), # Maria Clock Room Cutscene
        ):
            for (offset, a_value, b_value) in (
                (0x00, 0x8CA302D4, 0x8E6302D4), # lw v1,$2D4(X)
                (0x18, 0x00000000, 0x00000000), # nop
                (0x20, 0x00000000, 0x00000000), # nop
                (0x24, 0x00000000, 0x00000000), # nop
                (0x28, 0x00051900, 0x00041900), # sll v1,X,$4
                (0x2C, 0x00651823, 0x00641823), # subu v1,X
                (0x34, 0x00000000, 0x00000000), # nop
                (0x38, 0x00000000, 0x00000000), # nop
                (0x3C, 0x00000000, 0x00000000), # nop
            ):
                value = a_value if type == 'A' else b_value
                result.patch_value(value, 'u32', sotn_address.Address(base + offset))
    # Room shuffler - Normalize room connections
    # if changes.get('Options', {}).get('Normalize room connections', False):
    #     for (offset, value) in (
    #         # Shift the breakable floor in Underground Caverns to the right 3 tiles
    #         # https://github.com/SestrenExsis/SOTN-Shuffler/issues/82
    #         (0x0429FF64, 0x340802D6), # ori t0,zero,$2D6
    #         (0x042A006C, 0x340802D6), # ori t0,zero,$2D6
    #     ):
    #         result.patch_value(value, 'u32', sotn_address.Address(offset))
    # Insert boss stages into stage data prior to stage patching
    if 'Stages' in changes:
        for element in data['Boss Stages'].values():
            source_stage_name = element['Source Stage']
            if source_stage_name not in changes['Stages']:
                continue
            source_room_name = element['Source Room']
            if source_room_name not in changes['Stages'][source_stage_name]['Rooms']:
                continue
            target_stage_name = element['Target Stage']
            if target_stage_name not in changes['Stages']:
                changes['Stages'][target_stage_name] = {
                    'Rooms': {},
                }
            for (target_room_name, target_room) in element['Target Rooms'].items():
                source_room = changes['Stages'][source_stage_name]['Rooms'][source_room_name]
                changes['Stages'][target_stage_name]['Rooms'][target_room_name] = {
                    'Top': source_room['Top'] + target_room['Top'],
                    'Left': source_room['Left'] + target_room['Left'],
                }
    # Patch stage data
    for stage_id in sorted(changes.get('Stages', {})):
        stage_data = changes['Stages'][stage_id]
        stage_extract = extract['Stages'][stage_id]
        # Stage: Patch room data
        for room_id in sorted(stage_data.get('Rooms', {})):
            room_data = stage_data['Rooms'][room_id]
            extract_id = getID(aliases, ('Rooms', room_id))
            room_extract = stage_extract['Rooms'][str(extract_id)]
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
                # Room: Patch tilemap foreground and background
                if 'Tiles' in tile_layout_extract and 'Tilemap' in room_data:
                    # Fetch the source tilemap data and start with empty target tilemaps
                    tilemaps = {
                        'Source Background': [],
                        'Source Foreground': [],
                        'Target Background': [],
                        'Target Foreground': [],
                    }
                    for row_data in room_extract['Tilemap Foreground']['Data']:
                        tilemaps['Source Foreground'].append(list(map(lambda x: int(x, 16), row_data.split(' '))))
                        tilemaps['Target Foreground'].append([None] * len(tilemaps['Source Foreground'][-1]))
                    for row_data in room_extract['Tilemap Background']['Data']:
                        tilemaps['Source Background'].append(list(map(lambda x: int(x, 16), row_data.split(' '))))
                        tilemaps['Target Background'].append([None] * len(tilemaps['Source Background'][-1]))
                    for edit in room_data['Tilemap']:
                        layers = edit['Layer'].split(' and ')
                        source = edit['Source']
                        target = edit['Target']
                        target_rows = len(target)
                        target_cols = len(target[0])
                        # Copy source data to target directly if a space in the target is specified
                        # If target already has source data copied to it, preserve that data
                        for layer in layers:
                            for row in range(target_rows):
                                for col in range(target_cols):
                                    if target[row][col] == ' ' and tilemaps['Target ' + layer][row][col] is None:
                                        tilemaps['Target ' + layer][row][col] = tilemaps['Source ' + layer][row][col]
                        for (stamp_height, stamp_width) in (
                            (5, 5), (5, 4), (4, 5), (4, 4), (5, 3), (3, 5),
                            (4, 3), (3, 4), (5, 2), (2, 5), (3, 3), (4, 2),
                            (2, 4), (3, 2), (2, 3), (5, 1), (1, 5), (2, 2),
                            (3, 1), (1, 3), (2, 1), (1, 2), (1, 1),
                        ):
                            # Find valid target locations for the stamp
                            for layer in layers:
                                for target_top in range(target_rows - (stamp_height - 1)):
                                    for target_left in range(target_cols - (stamp_width - 1)):
                                        # Confirm target location has empty space for the stamp
                                        valid_target_ind = True
                                        for row in range(stamp_height):
                                            if not valid_target_ind:
                                                break
                                            for col in range(stamp_width):
                                                if not valid_target_ind:
                                                    break
                                                if tilemaps['Target ' + layer][target_top + row][target_left + col] is not None:
                                                    valid_target_ind = False
                                                    break
                                        if not valid_target_ind:
                                            continue
                                        # Stamp if a valid source location can be found
                                        valid_source_ind = False
                                        for source_top in range(target_rows - (stamp_height - 1)):
                                            if valid_source_ind:
                                                break
                                            for source_left in range(target_cols - (stamp_width - 1)):
                                                # Find first source location that matches the target location for the stamp
                                                valid_source_ind = True
                                                for row in range(stamp_height):
                                                    if not valid_source_ind:
                                                        break
                                                    for col in range(stamp_width):
                                                        source_value = source[source_top + row][source_left + col]
                                                        target_value = target[target_top + row][target_left + col]
                                                        if source_value != target_value:
                                                            valid_source_ind = False
                                                            break
                                                if not valid_source_ind:
                                                    continue
                                                # Apply the stamp
                                                for row in range(stamp_height):
                                                    for col in range(stamp_width):
                                                        assert tilemaps['Target ' + layer][target_top + row][target_left + col] is None
                                                        value = tilemaps['Source ' + layer][source_top + row][source_left + col]
                                                        tilemaps['Target ' + layer][target_top + row][target_left + col] = value
                                                break
                        # Debug info
                        # for layer in edit['Layer'].split(' and '):
                        #     rows = len(tilemaps['Target ' + layer])
                        #     cols = len(tilemaps['Target ' + layer][0])
                        #     print('Target ' + layer, (rows, cols))
                        #     for row in range(rows):
                        #         row_data = []
                        #         for col in range(cols):
                        #             cell = '#'
                        #             if tilemaps['Target ' + layer][row][col] is None:
                        #                 cell = '.'
                        #             elif tilemaps['Target ' + layer][row][col] == -1:
                        #                 cell = '?'
                        #             row_data.append(cell)
                        #         print(''.join(row_data))
                        # ...
                        for layer in edit['Layer'].split(' and '):
                            extract_data = room_extract['Tilemap ' + layer]['Data']
                            extract_metadata = room_extract['Tilemap ' + layer]['Metadata']
                            offset = 0
                            for (tile_row, tiles) in enumerate(tilemaps['Target ' + layer]):
                                extract_row_data = list(map(lambda x: int(x, 16), extract_data[tile_row].split(' ')))
                                for (tile_col, tile) in enumerate(tiles):
                                    extract_value = extract_row_data[tile_col]
                                    if tile == extract_value:
                                        offset += 2
                                        continue
                                    result.patch_value(tile, 'u16', sotn_address.Address(extract_metadata['Start'] + offset))
                                    offset += 2
    # Patch teleporters
    extract_metadata = extract['Teleporters']['Metadata']
    for teleporter_id in sorted(changes.get('Teleporters', {})):
        teleporter_data = changes['Teleporters'][teleporter_id]
        extract_id = getID(aliases, ('Teleporters', teleporter_id))
        extract_data = extract['Teleporters']['Data'][extract_id]
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
        room_offset = extract_data['Room']
        if 'Room' in teleporter_data:
            # NOTE(sestren): Multiply by 8 to translate room ID to room offset
            extract_room_offset = 8 * getID(aliases, ('Rooms', teleporter_data['Room']))
            if extract_room_offset != room_offset:
                room_offset = extract_room_offset
                result.patch_value(room_offset,
                    extract_metadata['Fields']['Room']['Type'],
                    sotn_address.Address(extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room']['Offset']),
                )
        # Teleporter: Patch target stage ID
        target_stage_id = extract_data['Target Stage ID']
        if 'Stage' in teleporter_data:
            extract_stage_id = getID(aliases, ('Stages', teleporter_data['Stage']))
            if extract_stage_id != target_stage_id:
                target_stage_id = extract_stage_id
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
    if 'Castle Map Reveals' in changes:
        changes_data = changes['Castle Map Reveals']
        extract_data = extract['Castle Map Reveals']['Data']
        extract_metadata = extract['Castle Map Reveals']['Metadata']
        offset = 0
        for (castle_map_reveal_id, castle_map_reveal) in enumerate(changes_data):
            # If the original extraction has fewer reveals than are in changes, default to the last ID in the extraction
            id = min(len(extract_data) - 1, castle_map_reveal_id)
            grid = castle_map_reveal.get('Grid', extract_data[id]['Grid'])
            rows = len(grid)
            bytes_per_row = (len(grid[0])) // 8
            left = castle_map_reveal.get('Left', extract_data[id]['Left'])
            top = castle_map_reveal.get('Top', extract_data[id]['Top'])
            for value in (left, top, bytes_per_row, rows):
                result.patch_value(value, 'u8',
                    sotn_address.Address(extract_metadata['Start'] + offset),
                )
                offset += 1
            for row in range(rows):
                assert 0 < len(grid[row]) <= 64
                assert (len(grid[row]) % 8) == 0
                for byte_id in range(bytes_per_row):
                    byte_value = 0
                    for bit_id in range(8):
                        col = 8 * byte_id + bit_id
                        if grid[row][col] != ' ':
                            byte_value += 2 ** bit_id
                    result.patch_value(byte_value, 'u8',
                        sotn_address.Address(extract_metadata['Start'] + offset),
                    )
                    offset += 1
        result.patch_value(0xFF, 'u8',
            sotn_address.Address(extract_metadata['Start'] + offset),
        )
        assert offset <= extract_metadata['Footprint']
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
    familiar_changes = get_familiar_changes(changes, data['Familiar Events'])
    extract_metadata = extract['Familiar Events']['Metadata']
    for familiar_event_id in sorted(familiar_changes):
        familiar_event_data = familiar_changes[familiar_event_id]
        extract_data = extract['Familiar Events']['Data'][familiar_event_id]
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
    if 'Stages' in changes:
        for (element_name, element_group) in data['Warp Coordinates'].items():
            object_extract = extract[element_name]
            for element in element_group.values():
                source_stage_name = element['Source Stage']
                if source_stage_name not in changes['Stages']:
                    continue
                source_room_name = element['Source Room']
                if source_room_name not in changes['Stages'][source_stage_name]['Rooms']:
                    continue
                source_room = changes['Stages'][source_stage_name]['Rooms'][source_room_name]
                for (source_field_name, target_field_name) in (
                    ('Left', 'Room X'),
                    ('Top', 'Room Y'),
                ):
                    if source_field_name not in source_room:
                        continue
                    result.patch_value(
                        source_room[source_field_name],
                        object_extract['Metadata']['Fields'][target_field_name]['Type'],
                        sotn_address.Address(
                            object_extract['Metadata']['Start'] + element['Index'] * object_extract['Metadata']['Size'] + object_extract['Metadata']['Fields'][target_field_name]['Offset']
                        ),
                    )
    object_layouts = {}
    # Option - Assign Power of Wolf relic a unique ID
    power_of_wolf_patch = changes.get('Options', {}).get('Assign Power of Wolf relic a unique ID', False)
    if power_of_wolf_patch:
        if 'Object Layouts' not in changes:
            changes['Object Layouts'] = {}
        if 'Location - Power of Wolf' not in changes['Object Layouts']:
            changes['Object Layouts']['Location - Power of Wolf'] = 'Relic - Power of Wolf'
    # Object layouts - Apply changes
    for location_name in sorted(changes.get('Object Layouts', {})):
        entity_name = changes['Object Layouts'][location_name]
        location_aliases = aliases['Object Layouts'].get(location_name, [])
        for location_alias in location_aliases:
            stage_name = location_alias['Stage']
            room_name = location_alias['Room']
            if (stage_name, room_name) not in object_layouts:
                room_id = str(aliases['Rooms'].get(room_name, None))
                room_extract = extract['Stages'][stage_name]['Rooms'][room_id]
                object_extract = room_extract['Object Layout - Horizontal']['Data'][1:-1]
                object_layouts[(stage_name, room_name)] = copy.deepcopy(object_extract)
            object_layout_id = location_alias['Object Layout ID']
            for (property_key, property_value) in aliases['Entities'].get(entity_name, {}).items():
                object_layouts[(stage_name, room_name)][object_layout_id][property_key] = property_value
            if power_of_wolf_patch and location_name == 'Location - Power of Wolf':
                object_layouts[(stage_name, room_name)][object_layout_id]['Entity Room Index'] = 18
    # Object layouts - Apply patches from changes
    for ((stage_name, room_name), object_layout) in object_layouts.items():
        horizontal_object_layout = list(sorted(object_layout,
            key=lambda x: (x['X'], x['Y'], x['Entity Room Index'], x['Entity Type ID'], x['Params'])
        ))
        vertical_object_layout = list(sorted(object_layout,
            key=lambda x: (x['Y'], x['X'], x['Entity Room Index'], x['Entity Type ID'], x['Params'])
        ))
        assert len(horizontal_object_layout) == len(vertical_object_layout)
        for (sort_method, sorted_object_layout) in (
            ('Horizontal', horizontal_object_layout),
            ('Vertical', vertical_object_layout),
        ):
            room_id = str(aliases['Rooms'].get(room_name, None))
            room_extract = extract['Stages'][stage_name]['Rooms'][room_id]
            object_extract = room_extract['Object Layout - ' + sort_method]
            for object_layout_id in range(len(sorted_object_layout)):
                sorted_object_layout[object_layout_id]
                # NOTE(sestren): Add +1 to the object layout ID to get the extract ID
                # NOTE(sestren): This accounts for the sentinel entity at the start of every entity list
                extract_id = object_layout_id + 1
                # print(object_extract['Data'][extract_id])
                for field_name in (
                    'Entity Room Index',
                    'Entity Type ID',
                    'Params',
                    'X',
                    'Y',
                ):
                    if sorted_object_layout[object_layout_id][field_name] == object_extract['Data'][extract_id][field_name]:
                        continue
                    result.patch_value(
                        sorted_object_layout[object_layout_id][field_name],
                        object_extract['Metadata']['Fields'][field_name]['Type'],
                        sotn_address.Address(
                            object_extract['Metadata']['Start'] + extract_id * object_extract['Metadata']['Size'] + object_extract['Metadata']['Fields'][field_name]['Offset']
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
    # TODO(sestren): Fix string-related bugs because I did them wrong
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
    # Adjust the target points for the Castle Teleporter and False Save Room locations
    for (constant_id, source_stage, source_room_name, offset_type, offset_amount) in (
        # Adjust the target point for the Castle Teleporter locations (in both DRA and RIC)
        ('DRA - Castle Keep Teleporter, Y Offset', 'Castle Keep', 'Castle Keep, Keep Area', 'Top', 847),
        ('DRA - Castle Keep Teleporter, X Offset', 'Castle Keep', 'Castle Keep, Keep Area', 'Left', 320),
        ('DRA - Reverse Keep Teleporter, Y Offset', 'Reverse Keep', 'Reverse Keep, Keep Area', 'Top', 1351),
        ('DRA - Reverse Keep Teleporter, X Offset', 'Reverse Keep', 'Reverse Keep, Keep Area', 'Left', 1728),
        ('RIC - Castle Keep Teleporter, Y Offset', 'Castle Keep', 'Castle Keep, Keep Area', 'Top', 847),
        ('RIC - Castle Keep Teleporter, X Offset', 'Castle Keep', 'Castle Keep, Keep Area', 'Left', 320),
        ('RIC - Reverse Keep Teleporter, Y Offset', 'Reverse Keep', 'Reverse Keep, Keep Area', 'Top', 1351),
        ('RIC - Reverse Keep Teleporter, X Offset', 'Reverse Keep', 'Reverse Keep, Keep Area', 'Left', 1728),
        # Adjust the False Save Room trigger, discovered by @MottZilla
        # See https://github.com/Xeeynamo/sotn-decomp/blob/ffce97b0022ab5d4118ad35c93dea86bb18b25cc/src/dra/5087C.c#L1012
        ('False Save Room, Room Y', 'Underground Caverns', 'Underground Caverns, False Save Room', 'Top', None),
        ('False Save Room, Room X', 'Underground Caverns', 'Underground Caverns, False Save Room', 'Left', None),
        ('Reverse False Save Room, Room Y', 'Reverse Caverns', 'Reverse Caverns, False Save Room', 'Top', None),
        ('Reverse False Save Room, Room X', 'Reverse Caverns', 'Reverse Caverns, False Save Room', 'Left', None),
    ):
        source_room = changes.get('Stages', {}).get(source_stage, {}).get('Rooms', {}).get(source_room_name, None)
        if source_room is None:
            continue
        constant_extract = extract['Constants'][constant_id]
        # NOTE(sestren): For the castle teleporter, use world coordinates and negate the value
        # NOTE(sestren): For the False Save Room, just use the room location
        # TODO(sestren): Consider a less hacky way to handle both cases
        change_value = source_room[offset_type]
        if offset_amount is not None:
            change_value = -1 * (256 * source_room[offset_type] + offset_amount)
        if change_value != constant_extract['Value']:
            result.patch_value(
                change_value,
                constant_extract['Type'],
                sotn_address.Address(constant_extract['Start']),
            )
    return result

if __name__ == '__main__':
    '''
    Usage
    python sotn_patcher.py EXTRACTION_JSON --data= --changes=CHANGES_JSON --ppf=OUTPUT_PPF
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('extract_file', help='Input a filepath to the extract JSON file', type=str)
    parser.add_argument('--data', help='Input an optional (required if changes argument is given) filepath to a folder containing various data dependency files', type=str)
    parser.add_argument('--changes', help='Input an optional (required if data argument is given) filepath to the changes JSON file', type=str)
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
                open(os.path.join(os.path.normpath(args.data), 'aliases.yaml')) as aliases_file,
                open(os.path.join(os.path.normpath(args.data), 'familiar_events.yaml')) as familiar_events_file,
                open(os.path.join(os.path.normpath(args.data), 'boss_stages.yaml')) as boss_stages_file,
                open(os.path.join(os.path.normpath(args.data), 'warp_coordinates.yaml')) as warp_coordinates_file,
                open(args.changes) as changes_file,
                open(args.ppf, 'wb') as ppf_file,
            ):
                data = {
                    'Aliases': yaml.safe_load(aliases_file),
                    'Boss Stages': yaml.safe_load(boss_stages_file),
                    'Familiar Events': yaml.safe_load(familiar_events_file),
                    'Warp Coordinates': yaml.safe_load(warp_coordinates_file),
                }
                changes = json.load(changes_file)
                if 'Changes' in changes:
                    changes = changes['Changes']
                validate_changes(changes)
                patch = get_ppf(extract, changes, data)
                ppf_file.write(patch.bytes)
