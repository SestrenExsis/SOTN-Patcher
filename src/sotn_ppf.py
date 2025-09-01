# External libraries
import argparse
import collections
import copy
import json
import os
import yaml

# Local libraries
import sotn_address

class PPF:
    def __init__(self, description, patch, debug: bool=False):
        self.debug = debug
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
        for high in sorted(patch.writes.keys()):
            left = 0
            right = 0
            lows = list(reversed(sorted(patch.writes[high].keys())))
            while len(lows) > 0:
                right = left = lows.pop()
                while (len(lows) > 0) and (lows[-1] == (right + 1)):
                    right = lows.pop()
                disc_address = patch.partition_size * high + left
                size = 1 + (right - left)
                self.write_u64(disc_address)
                self.write_byte(size)
                values = []
                for low in range(left, right + 1):
                    value = patch.writes[high][low]
                    self.write_byte(value)
                    values.append(value)
                if self.debug:
                    print(disc_address, size, values)
    
    def write_byte(self, byte):
        assert 0x00 <= byte < 0x100
        self.bytes.append(byte)
    
    def write_u64(self, value):
        write_value = value
        for _ in range(8):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
    
    def write_string(self, string):
        for char in string:
            self.write_byte(ord(char))

class Patch:
    def __init__(self):
        self.writes = {}
        self.cursor = sotn_address.Address(0)
        self.partition_size = 0x80
    
    def write_byte(self, byte):
        assert 0x00 <= byte < 0x100
        (high, low) = divmod(self.cursor.to_disc_address(), self.partition_size)
        if high not in self.writes:
            self.writes[high] = {}
        self.writes[high][low] = byte
    
    def write_u8(self, value):
        write_value = value
        for _ in range(1):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
            self.cursor.address += 1
    
    def write_s8(self, value):
        write_value = (value & 0x7F) + (0x80 if value < 0 else 0x00)
        for _ in range(1):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
            self.cursor.address += 1
    
    def write_u16(self, value):
        write_value = value
        for _ in range(2):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
            self.cursor.address += 1
    
    def write_s16(self, value):
        write_value = (value & 0x7FFF) + (0x8000 if value < 0 else 0x0000)
        for _ in range(2):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
            self.cursor.address += 1
    
    def write_u32(self, value):
        write_value = value
        for _ in range(4):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
            self.cursor.address += 1
    
    def write_s32(self, value):
        write_value = (value & 0x7FFFFFFF) + (0x80000000 if value < 0 else 0x00000000)
        for _ in range(4):
            write_value, byte = divmod(write_value, 0x100)
            self.write_byte(byte)
            self.cursor.address += 1
    
    def patch_value(self, value: int, data_type: str, game_address: int):
        self.cursor.address = game_address
        if data_type == 'u8':
            self.write_u8(value)
        elif data_type == 's8':
            self.write_s8(value)
        elif data_type == 'u16':
            self.write_u16(value)
        elif data_type == 's16':
            self.write_s16(value)
        elif data_type == 'u32':
            self.write_u32(value)
        elif data_type == 's32':
            self.write_s32(value)
        else:
            raise Exception('Incorrect type for patch_value:', (value, data_type, game_address))

def get_changes_template_file(extract, aliases):
    result = {
        'Boss Teleporters': {},
        'Castle Map': [],
        'Castle Map Reveals': [],
        'Constants': {},
        'Options': {
            'Assign Power of Wolf relic a unique ID': False,
            'Enable debug mode': False,
            'Skip Maria cutscene in Alchemy Laboratory': False,
        },
        'Stages': {},
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
            room_name = room_id
            for (alias_room_name, alias_room) in aliases['Rooms'].items():
                if alias_room_name.startswith(stage_id + ', ') and alias_room['Room Index'] == int(room_id):
                    room_name = alias_room_name
                    break
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
            result['Stages'][stage_id]['Rooms'][room_name] = {
                'Left': room_data['Left']['Value'],
                'Top': room_data['Top']['Value'],
            }
            if relic_found_ind:
                room = result['Stages'][stage_id]['Rooms'][room_name]
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
    # Add constants
    for constant_name in sorted(extract['Constants']):
        constant = extract['Constants'][constant_name]
        if constant.get('Type', None) in ('string', 'shifted-string'):
            if constant_name in (
                'Message - Richter Mode Instructions 1',
                'Message - Richter Mode Instructions 2',
            ):
                result['Constants'][constant_name] = constant['Value']
    return result

def validate_changes(changes):
    if 'Boss Teleporters' in changes:
        # TODO(sestren): Validate boss teleporters
        pass
    for (stage_id, stage_data) in changes.get('Stages', {}).items():
        for (room_id, room_data) in stage_data.get('Rooms', {}).items():
            assert 0 <= room_data.get('Top', 0) <= 63 # Should it be 58 instead of 63?
            assert 0 <= room_data.get('Left', 0) <= 63
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
        result = token
        if token not in scope:
            break
        scope = scope[token]
    else:
        result = scope
    if type(result) == str:
        result = int(result)
    return result

def transformed_value(value, transformations):
    result = value
    for transformation in transformations:
        (mnemonic, operand) = transformation[:-1].split('(')
        if mnemonic == 'mul':
            result *= int(operand)
        elif mnemonic == 'add':
            result += int(operand)
    return result

def get_patch(extract, changes, data):
    aliases = data['Aliases']
    result = Patch()
    # Apply common patches
    for (option_name, patch_file_name) in (
        ('Clock hands show minutes and seconds instead of hours and minutes', 'clock-hands-display-minutes-and-seconds'),
        ('Disable clipping on screen edge of Demon Switch Wall', 'prevent-softlocks-at-demon-switch-wall'),
        ('Disable clipping on screen edge of Left Gear Room Wall', 'prevent-softlocks-at-left-gear-room-wall'),
        ('Disable clipping on screen edge of Pendulum Room Wall', 'prevent-softlocks-at-pendulum-room-wall'),
        ('Disable clipping on screen edge of Snake Column Wall', 'prevent-softlocks-at-snake-column-wall'),
        ('Disable clipping on screen edge of Tall Zig Zag Room Wall', 'prevent-softlocks-at-tall-zig-zag-room-wall'),
        ('Enable debug mode', 'enable-debug-mode'),
        ('Normalize Ferryman Gate', 'normalize-ferryman-gate'),
        ('Normalize room connections', 'normalize-jewel-sword-passageway'),
        ('Prevent softlocks related to Death cutscene in Castle Entrance', 'prevent-softlocks-when-meeting-death'),
        ('Shift wall in Plaque Room With Breakable Wall away from screen edge', 'prevent-softlocks-at-plaque-room-wall'),
        ('Skip Maria cutscene in Alchemy Laboratory', 'skip-maria-cutscene-in-alchemy-laboratory'),
    ):
        if not changes.get('Options', {}).get(option_name, False):
            continue
        with open(os.path.join('build', 'patches', patch_file_name + '.json')) as patch_file:
            patch = json.load(patch_file)
            patch_changes = patch.get('Changes', {})
            # New pokes are added to the end of the poke list
            for poke in patch_changes.get('Pokes', []):
                if 'Pokes' not in changes:
                    changes['Pokes'] = []
                changes['Pokes'].append(poke)
            # New constants overwrite previous constants
            for (constant_key, constant_value) in patch_changes.get('Constants', {}).items():
                if 'Constants' not in changes:
                    changes['Constants'] = {}
                changes['Constants'][constant_key] = constant_value
            # NOTE(sestren): For the moment, only 'Pokes' and 'Constants' in the patch file's changes are being handled
    # Option - Preserve unsaved map data
    if changes.get('Options', {}).get('Preserve unsaved map data', 'None') != 'None':
        preservation_method = changes['Options']['Preserve unsaved map data']
        assert preservation_method in ('None', 'Revelation', 'Exploration')
        # 0x801B948C - LoadSaveData
        # ------------------------------------------
        # Equivalent to the following C code (for Revelation Mode)
        # ------------------------------------------
        # i = 0;
        # while (i < LEN(g_CastleFlags)) {
        #     g_CastleFlags[i] = savePtr->castleFlags[i];
        #     g_CastleMap[i] = ((0x55 & g_CastleMap[i]) << 1) | (0xAA & g_CastleMap[i]) | savePtr->castleMap[i];
        #     i++
        # }
        # while (i < LEN(g_CastleMap)) {
        #     g_CastleMap[i] = ((0x55 & g_CastleMap[i]) << 1) | (0xAA & g_CastleMap[i]) | savePtr->castleMap[i];
        #     i++;
        # }
        # ------------------------------------------
        revelation_ind = (preservation_method == 'Revelation')
        for (base, option) in (
            (0x000DFA70, 'A'), # SEL or DRA?
            (0x03AE0C8C, 'B'), # SEL or DRA?
        ):
            for (offset, value) in (
                (0x0180, 0x3C068007), # lui     a2,$8007          ; %hi(g_CastleMap)
                (0x0184, 0x24C6BB74), # addiu   a2,a2,-$448C      ; %lo(g_CastleMap)
                (0x0188, 0x3C028004), # lui     v0,$8004          ; %hi(g_Settings+0x108)
                (0x018C, 0x2442CB00), # addiu   v0,v0,-$3500      ; %lo(g_Settings+0x108)
                (0x0190, 0x8C430000), # lw      v1,0(v0)          
                (0x0194, 0x3C048004), # lui     a0,$8004          ; %hi(g_Settings+0x10c)
                (0x0198, 0x8C84CB04), # lw      a0,-$34FC(a0)     ; %lo(g_Settings+0x10c)
                (0x019C, 0x01431825), # or      v1,t2,v1          
                (0x01A0, 0x01642025), # or      a0,t3,a0          
                (0x01A4, 0xAC430000), # sw      v1,0(v0)          
                (0x01A8, 0x3C018004), # lui     at,$8004          ; %hi(g_Settings+0x10c)
                (0x01AC, 0xAC24CB04), # sw      a0,-$34FC(at)     ; %lo(g_Settings+0x10c)
                (0x01B0, 0x01052021), # addu    a0,t0,a1          
                (0x01B4, 0x908206C8), # lbu     v0,0x6c8(a0)      
                (0x01B8, 0x3C018004), # lui     at,$8004          ; %hi(g_CastleFlags)
                (0x01BC, 0x00250821), # addu    at,at,a1          
                (0x01C0, 0xA022BDEC), # sb      v0,-$4214(at)     ; %lo(g_CastleFlags)
                (0x01C4, 0x24A50001), # addiu   a1,a1,1           
                (0x01C8, 0x90C30000), # lbu     v1,0(a2)          
                (0x01CC, 0x908409C8), # lbu     a0,0x9c8(a0)      
                (0x01D0, 0x30620055), # andi    v0,v1,0x55        
                (0x01D4, 0x00021040 if revelation_ind else 0x00000000),
                                      # sll     v0,v0,0x1         (for Revelation)
                                      # nop                       (for Exploration)
                (0x01D8, 0x306300AA), # andi    v1,v1,0xaa        
                (0x01DC, 0x00431025), # or      v0,v0,v1          
                (0x01E0, 0x00441025), # or      v0,v0,a0          
                (0x01E4, 0xA0C20000), # sb      v0,0(a2)          
                (0x01E8, 0x28A20300), # slti    v0,a1,0x300       
                (0x01EC, 0x1440FFF0), # bnez    v0,154c ~>        
                (0x01F0, 0x24C60001), # addiu   a2,a2,1           
            ):
                result.patch_value(value, 'u32', base + offset)
    # Insert boss stages into stage data prior to stage patching
    if 'Stages' in changes:
        for (address, source_stage_name, source_room_name, offset, edge) in (
            # func_800F1A3C for Underground Caverns
            (0x000E7248 + 0x00, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 5, 'Left'),
            (0x000E7248 + 0x08, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x0C, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 7, 'Left'),
            (0x000E7248 + 0x14, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x18, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 3, 'Left'),
            (0x000E7248 + 0x20, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x24, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 4, 'Left'),
            (0x000E7248 + 0x2C, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x30, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 5, 'Left'),
            (0x000E7248 + 0x38, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x3C, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 8, 'Left'),
            (0x000E7248 + 0x44, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            # func_800F1A3C for Reverse Caverns
            (0x000E7248 + 0x50, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 5, 'Left'),
            (0x000E7248 + 0x54, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x60, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 7, 'Left'),
            (0x000E7248 + 0x64, 'Underground Caverns', 'Underground Caverns, Left Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x70, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 3, 'Left'),
            (0x000E7248 + 0x74, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x80, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 4, 'Left'),
            (0x000E7248 + 0x84, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0x90, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 5, 'Left'),
            (0x000E7248 + 0x94, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
            (0x000E7248 + 0xA0, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 8, 'Left'),
            (0x000E7248 + 0xA4, 'Underground Caverns', 'Underground Caverns, Right Ferryman Route', 1, 'Top'),
        ):
            if source_stage_name not in changes['Stages']:
                continue
            if source_room_name not in changes['Stages'][source_stage_name]['Rooms']:
                continue
            source_room = changes['Stages'][source_stage_name]['Rooms'][source_room_name]
            value = source_room[edge] + offset
            result.patch_value(value, 'u8', address)
    # Patch boss teleporters
    extract_metadata = extract['Boss Teleporters']['Metadata']
    for boss_teleporter_id in sorted(changes.get('Boss Teleporters', {})):
        boss_teleporter_data = changes['Boss Teleporters'][boss_teleporter_id]
        extract_id = getID(aliases, ('Boss Teleporters', boss_teleporter_id))
        extract_data = extract['Boss Teleporters']['Data'][extract_id]
        # Boss Teleporter: Patch room X
        room_x = extract_data['Room X']
        if boss_teleporter_data.get('Room X', room_x) != room_x:
            room_x = boss_teleporter_data['Room X']
            result.patch_value(
                room_x,
                extract_metadata['Fields']['Room X']['Type'],
                extract_metadata['Start'] + int(boss_teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room X']['Offset'],
            )
        # Boss Teleporter: Patch room Y
        room_y = extract_data['Room Y']
        if boss_teleporter_data.get('Room Y', room_y) != room_y:
            room_y = boss_teleporter_data['Room Y']
            result.patch_value(
                room_y,
                extract_metadata['Fields']['Room Y']['Type'],
                extract_metadata['Start'] + int(boss_teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room Y']['Offset'],
            )
    # Patch stage data
    stages_remaining = collections.deque()
    for stage_id in sorted(changes.get('Stages', {})):
        stages_remaining.appendleft(stage_id)
    while len(stages_remaining) > 0:
        stage_id = stages_remaining.pop()
        stage_data = changes['Stages'][stage_id]
        stage_extract = extract['Stages'][stage_id]
        # Stage: Patch room data
        for room_id in sorted(stage_data.get('Rooms', {})):
            room_data = stage_data['Rooms'][room_id]
            extract_id = getID(aliases, ('Rooms', room_id, 'Room Index'))
            room_extract = stage_extract['Rooms'][str(extract_id)]
            left = room_extract['Left']['Value']
            right = room_extract['Right']['Value']
            # Room: Patch left and right
            if room_data.get('Left', left) != left:
                left = room_data['Left']
                result.patch_value(left, room_extract['Left']['Type'], room_extract['Left']['Start'])
                width = 1 + room_extract['Right']['Value'] - room_extract['Left']['Value']
                right = left + width - 1
                result.patch_value(right, room_extract['Right']['Type'], room_extract['Right']['Start'])
            # Room: Patch top and bottom
            top = room_extract['Top']['Value']
            bottom = room_extract['Bottom']['Value']
            if room_data.get('Top', top) != top:
                top = room_data['Top']
                result.patch_value(top, room_extract['Top']['Type'], room_extract['Top']['Start'])
                height = 1 + room_extract['Bottom']['Value'] - room_extract['Top']['Value']
                bottom = top + height - 1
                result.patch_value(bottom, room_extract['Bottom']['Type'], room_extract['Bottom']['Start'])
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
                    result.patch_value(layout_rect, tile_layout_extract['Layout Rect']['Type'], tile_layout_extract['Layout Rect']['Start'])
                # Room: Patch dependents
                for dependent in aliases['Rooms'][room_id].get('Dependents', {}):
                    if dependent['Type'] == 'Room':
                        target_stage_name = dependent['Stage']
                        if target_stage_name not in stages_remaining:
                            stages_remaining.appendleft(target_stage_name)
                        target_room_name = dependent['Room']
                        if target_stage_name not in changes['Stages']:
                            changes['Stages'][target_stage_name] = {
                                'Rooms': {},
                            }
                        changes['Stages'][target_stage_name]['Rooms'][target_room_name] = {
                            'Top': top + dependent['Top'],
                            'Left': left + dependent['Left'],
                        }
                    elif dependent['Type'] == 'Secret Map Tile':
                        array_extract = extract['Constants']['Secret Map Tile Reveals']
                        array_extract_meta = array_extract['Metadata']
                        for (element_index, element_value) in (
                            (dependent['Index'] + 0, left + dependent['Left']),
                            (dependent['Index'] + 1, top + dependent['Top']),
                        ):
                            if element_value == array_extract['Data'][element_index]:
                                continue
                            result.patch_value(
                                element_value,
                                array_extract['Metadata']['Type'],
                                array_extract_meta['Start'] + element_index * array_extract_meta['Size'],
                            )
                    elif dependent['Type'] == 'Warp Coordinate':
                        object_extract = extract[dependent['Array Name']]
                        object_meta = object_extract['Metadata']
                        for (element_value, target_field_name) in (
                            (left, 'Room X'),
                            (top, 'Room Y'),
                        ):
                            result.patch_value(
                                element_value,
                                object_extract['Metadata']['Fields'][target_field_name]['Type'],
                                object_meta['Start'] + dependent['Warp Index'] * object_meta['Size'] + object_meta['Fields'][target_field_name]['Offset'],
                            )
                    elif dependent['Type'] == 'Familiar Event':
                        # NOTE(sestren): Familiar events exist as a complete copy in 7 different locations, one for each familiar in the code
                        # TODO(sestren): Replace this hacky way of doing it with a better approach
                        familiar_event_id = dependent['Familiar Event ID']
                        copy_offsets = [
                            0x0392A760, # Possibly for Bat Familiar
                            0x0394BDB0, # Possibly for Ghost Familiar
                            0x0396FD2C, # Possibly for Faerie Familiar
                            0x03990890, # Possibly for Demon Familiar
                            0x039AF9E4, # Possibly for Sword Familiar
                            0x039D1D38, # Possibly for Yousei Familiar
                            0x039F2664, # Possibly for Nose Demon Familiar
                        ]
                        object_extract = extract['Familiar Events']
                        object_meta = object_extract['Metadata']
                        extract_data = extract['Familiar Events']['Data'][familiar_event_id]
                        sign = -1 if dependent['Inverted'] else 1
                        # Familiar event: Patch room X
                        if (extract_data.get('Room X', sign * left)) != (sign * left):
                            base_offset = object_meta['Start'] + int(familiar_event_id) * object_meta['Size'] + object_meta['Fields']['Room X']['Offset'] - copy_offsets[0]
                            for copy_offset in copy_offsets:
                                offset = base_offset + copy_offset
                                result.patch_value(sign * left, object_meta['Fields']['Room X']['Type'], offset)
                        # Familiar event: Patch room Y
                        if extract_data.get('Room Y', top) != top:
                            base_offset = object_meta['Start'] + int(familiar_event_id) * object_meta['Size'] + object_meta['Fields']['Room Y']['Offset'] - copy_offsets[0]
                            for copy_offset in copy_offsets:
                                offset = base_offset + copy_offset
                                result.patch_value(top, object_meta['Fields']['Room Y']['Type'], offset)
                    elif dependent['Type'] == 'Direct Write':
                        values = {
                            'Top': top,
                            'Left': left,
                        }
                        value = transformed_value(
                            values.get(dependent['Property'], 0),
                            dependent.get('Transformations', [])
                        )
                        result.patch_value(value, dependent['Data Type'], dependent['Address'])
                    elif dependent['Type'] == 'Tile Layout':
                        for (dependent_property_name, dependent_value) in (
                            ('Z Priority', left + dependent['Left']),
                            ('Flags', top + dependent['Top']),
                        ):
                            dependent_room_id = getID(aliases, ('Rooms', dependent['Room'], 'Room Index'))
                            dependent_extract = extract['Stages'][dependent['Stage']]['Rooms'][str(dependent_room_id)]['Tile Layout'][dependent_property_name]
                            result.patch_value(dependent_value, dependent_extract['Type'], dependent_extract['Start'])
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
                        tilemaps['Source Foreground'].append(list(map(lambda x: get_value(x), row_data.split(' '))))
                        tilemaps['Target Foreground'].append([None] * len(tilemaps['Source Foreground'][-1]))
                    for row_data in room_extract['Tilemap Background']['Data']:
                        tilemaps['Source Background'].append(list(map(lambda x: get_value(x), row_data.split(' '))))
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
                                extract_row_data = list(map(lambda x: get_value(x), extract_data[tile_row].split(' ')))
                                for (tile_col, tile) in enumerate(tiles):
                                    extract_value = extract_row_data[tile_col]
                                    if tile == extract_value:
                                        offset += 2
                                        continue
                                    result.patch_value(tile, 'u16', extract_metadata['Start'] + offset)
                                    offset += 2
    # Patch teleporters
    extract_metadata = extract['Teleporters']['Metadata']
    for teleporter_name in sorted(changes.get('Teleporters', {})):
        teleporter_data = changes['Teleporters'][teleporter_name]
        teleporter_id = getID(aliases, ('Teleporters', teleporter_name))
        extract_data = extract['Teleporters']['Data'][teleporter_id]
        # Teleporter: Patch player X
        player_x = extract_data['Player X']
        if teleporter_data.get('Player X', player_x) != player_x:
            player_x = teleporter_data['Player X']
            result.patch_value(player_x,
                extract_metadata['Fields']['Player X']['Type'],
                extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Player X']['Offset'],
            )
        # Teleporter: Patch player Y
        player_y = extract_data['Player Y']
        if teleporter_data.get('Player Y', player_y) != player_y:
            player_y = teleporter_data['Player Y']
            result.patch_value(player_y,
                extract_metadata['Fields']['Player Y']['Type'],
                extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Player Y']['Offset'],
            )
        # Teleporter: Patch room offset
        room_offset = extract_data['Room']
        if 'Room' in teleporter_data:
            # NOTE(sestren): Multiply by 8 to translate room ID to room offset
            extract_room_offset = 8 * getID(aliases, ('Rooms', teleporter_data['Room'], 'Room Index'))
            if extract_room_offset != room_offset:
                room_offset = extract_room_offset
                result.patch_value(room_offset,
                    extract_metadata['Fields']['Room']['Type'],
                    extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Room']['Offset'],
                )
        # Teleporter: Patch target stage ID
        target_stage_id = extract_data['Target Stage ID']
        if 'Stage' in teleporter_data:
            extract_stage_id = getID(aliases, ('Stages', teleporter_data['Stage']))
            if extract_stage_id != target_stage_id:
                target_stage_id = extract_stage_id
                result.patch_value(target_stage_id,
                    extract_metadata['Fields']['Target Stage ID']['Type'],
                    extract_metadata['Start'] + int(teleporter_id) * extract_metadata['Size'] + extract_metadata['Fields']['Target Stage ID']['Offset'],
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
            result.patch_value(pixel_pair_value, 'u8', extract_metadata['Start'] + row * extract_metadata['Columns'] + col_span)
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
                result.patch_value(value, 'u8', extract_metadata['Start'] + offset)
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
                    result.patch_value(byte_value, 'u8', extract_metadata['Start'] + offset)
                    offset += 1
        result.patch_value(0xFF, 'u8', extract_metadata['Start'] + offset)
        assert offset <= extract_metadata['Footprint']
    object_layouts = {}
    # Option - Assign Power of Wolf relic a unique ID
    power_of_wolf_patch = changes.get('Options', {}).get('Assign Power of Wolf relic a unique ID', False)
    if power_of_wolf_patch:
        if 'Quest Rewards' not in changes:
            changes['Quest Rewards'] = {}
        if 'Location - Castle Entrance, After Drawbridge (Power of Wolf)' not in changes['Quest Rewards']:
            changes['Quest Rewards']['Location - Castle Entrance, After Drawbridge (Power of Wolf)'] = 'Relic - Power of Wolf'
    # Color Palettes
    for (palette_index, rgba32) in enumerate(changes.get('Castle Map Color Palette', [])):
        red = get_value(rgba32[1:3]) // 8
        green = get_value(rgba32[3:5]) // 8
        blue = get_value(rgba32[5:7]) // 8
        alpha = get_value(rgba32[7:9]) // 128
        value = (alpha << 15) + (blue << 10) + (green << 5) + red
        array_extract_meta = extract['Constants']['Castle Map Color Palette']['Metadata']
        result.patch_value(value, 'u16', array_extract_meta['Start'] + palette_index * array_extract_meta['Size'])
    # Quest Rewards - Part 1
    for location_name in sorted(changes.get('Quest Rewards', {})):
        reward_name = changes['Quest Rewards'][location_name]
        # print((location_name, reward_name))
        reward_type = reward_name.split(' - ')[0]
        reward_data = aliases['Quest Rewards'][location_name]
        for data_element in reward_data[reward_type + ' Data']:
            if data_element['Type'] == 'Object Layout':
                stage_name = data_element['Stage']
                room_name = data_element['Room']
                if (stage_name, room_name) not in object_layouts:
                    room_id = str(aliases['Rooms'].get(room_name, {}).get('Room Index', None))
                    room_extract = extract['Stages'][stage_name]['Rooms'][room_id]
                    object_extract = room_extract['Object Layout - Horizontal']['Data'][1:-1]
                    object_layouts[(stage_name, room_name)] = copy.deepcopy(object_extract)
                object_layout_id = data_element['Object Layout ID']
                for (property_key, property_value) in aliases['Entities'].get(reward_name, {}).items():
                    if property_value is None:
                        continue
                    object_layouts[(stage_name, room_name)][object_layout_id][property_key] = property_value
                if power_of_wolf_patch and location_name == 'Location - Castle Entrance, After Drawbridge (Power of Wolf)':
                    object_layouts[(stage_name, room_name)][object_layout_id]['Entity Room Index'] = 18
                if 'Params' in data_element:
                    object_layouts[(stage_name, room_name)][object_layout_id]['Params'] = data_element['Params']
            elif data_element['Type'] == 'Stage Item Drop':
                constant_name = data_element['Constant']
                item_drop_index = data_element['Item Drop Index']
                array_extract_meta = extract['Constants'][constant_name]['Metadata']
                item_id = aliases['Items'][reward_name]
                result.patch_value(
                    item_id,
                    array_extract_meta['Type'],
                    array_extract_meta['Start'] + item_drop_index * array_extract_meta['Size'],
                )
            elif data_element['Type'] == 'Enemy Definition':
                enemy_def_id = data_element['Enemy Definition ID']
                field_name = data_element['Property']
                array_extract_meta = extract['Enemy Definitions']['Metadata']
                field_extract_meta = array_extract_meta['Fields'][field_name]
                item_id = aliases['Items'][reward_name]
                result.patch_value(
                    item_id,
                    field_extract_meta['Type'],
                    array_extract_meta['Start'] + enemy_def_id * array_extract_meta['Size'] + field_extract_meta['Offset'],
                )
            elif data_element['Type'] == 'Breakable Container Drop':
                # TODO(sestren): Combine this with 'Stage Item Drop' above (make it type 'Array' instead?)
                constant_name = data_element['Constant']
                drop_index = data_element['Breakable Drop Index']
                assert 2 <= drop_index <= 3 # NOTE(sestren): Drop indexes outside this range are not relics and should be handled differently
                array_extract_meta = extract['Constants'][constant_name]['Metadata']
                relic_id = aliases['Entities'][reward_name]['Params']
                result.patch_value(
                    relic_id,
                    array_extract_meta['Type'],
                    array_extract_meta['Start'] + drop_index * array_extract_meta['Size'],
                )
            elif data_element['Type'] == 'Shop Purchase Option':
                # Update label on shop item
                if 'Constants' not in changes:
                    changes['Constants'] = {}
                label_key = 'Message - Shop Item Name 1'
                if label_key not in changes['Constants']:
                    changes['Constants'][label_key] = aliases['Entities'][reward_name]['Label']
                constant_name = data_element['Constant']
                shop_index = data_element['Shop Index']
                relic_id = aliases['Entities'][reward_name]['Params']
                array_extract_meta = extract['Constants'][constant_name]['Metadata']
                result.patch_value(
                    relic_id,
                    array_extract_meta['Type'],
                    array_extract_meta['Start'] + shop_index * array_extract_meta['Size'],
                )
                # https://github.com/Xeeynamo/sotn-decomp/blob/3e18d5e8654cdfd77fbebeabefebb7333c1da98f/src/st/lib/e_shop.c#L1899
                result.patch_value(0x64 + relic_id, 'u8', 0x03E92308)
            elif data_element['Type'] == 'Direct Write':
                value = 0
                if data_element['Property'] == 'Item ID':
                    value = aliases['Items'][reward_name]
                else:
                    value = aliases['Entities'][reward_name][data_element['Property']]
                value = transformed_value(value, data_element.get('Transformations', []))
                assert value >= 0
                result.patch_value(value, data_element['Data Type'], data_element['Address'])
    # TODO(sestren): Instead of checksums for tests, output the address writes for comparison
    # Quest Rewards - Part 2
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
            room_id = str(aliases['Rooms'].get(room_name, {}).get('Room Index', None))
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
                        object_extract['Metadata']['Start'] + extract_id * object_extract['Metadata']['Size'] + object_extract['Metadata']['Fields'][field_name]['Offset'],
                    )
    # Patch strings
    # NOTE(sestren): For now, there is nothing preventing strings from overflowing their boundaries
    # TODO(sestren): Ensure strings fit by truncating strings that are too long
    NULL_CHAR = 0x00
    SPACE_CHAR = 0x20
    PERIOD_CHAR = 0x44
    QUESTION_MARK_CHAR = 0x48
    APOSTROPHE_CHAR = 0x66
    QUOTE_CHAR = 0x68
    DOUBLE_BYTE_CHAR = 0x81
    NULL_CHAR_SHIFTED = 0xFF
    for constant_name in changes.get('Constants', {}):
        constant_extract = extract['Constants'][constant_name]
        if 'Metadata' in constant_extract:
            data_elements = changes['Constants'][constant_name]
            array_extract_meta = extract['Constants'][constant_name]['Metadata']
            for data_element in data_elements:
                result.patch_value(
                    get_value(data_element['Value']),
                    array_extract_meta['Type'],
                    array_extract_meta['Start'] + data_element['Index'] * array_extract_meta['Size'],
                )
        elif constant_extract['Type'] == 'string':
            data_element = changes['Constants'][constant_name]
            offset = 0
            # Strings in SOTN are null-terminated, Shift JIS-encoded character arrays
            for char in data_element:
                if char in '".?\'':
                    result.patch_value(DOUBLE_BYTE_CHAR, 'u8', constant_extract['Start'] + offset)
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
                    result.patch_value(0x82, 'u8', constant_extract['Start'] + offset)
                    offset += 1
                    char_code = 0x4f + (ord(char) - ord('0'))
                else:
                    char_code = SPACE_CHAR
                result.patch_value(char_code, 'u8', constant_extract['Start'] + offset)
                offset += 1
            padding = 4 - (offset % 4)
            for _ in range(padding):
                result.patch_value(NULL_CHAR, 'u8', constant_extract['Start'] + offset)
                offset += 1
        elif constant_extract['Type'] == 'shifted-string':
            data_element = changes['Constants'][constant_name]
            offset = 0
            # Shifted strings in SOTN are terminated with an 0xFF, and every character is shifted smaller by 0x20
            for char in data_element:
                char_code = ord('*') - 0x20
                if char in '0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    char_code = ord(char) - 0x20
                result.patch_value(char_code, 'u8', constant_extract['Start'] + offset)
                offset += 1
            padding = constant_extract['Size'] - offset
            assert padding > 0
            for i in range(padding):
                null_char = NULL_CHAR if i > 0 else NULL_CHAR_SHIFTED
                result.patch_value(null_char, 'u8', constant_extract['Start'] + offset)
                offset += 1
        else:
            raise Exception('Unhandled case when processing changes in Constants')
    # Adjust the target points for the Castle Teleporter and False Save Room locations
    for (constant_id, source_stage, source_room_name, offset_type, offset_amount) in (
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
            result.patch_value(change_value, constant_extract['Type'], constant_extract['Start'])
    # Patch pokes or direct writes
    for poke in changes.get('Pokes', []):
        result.patch_value(get_value(poke['Value']), poke['Data Type'], get_value(poke['Gamedata Address']))
    return result

# Intended for hex-strings or integers
def get_value(value: (str | int)) -> int:
    result = None
    if type(value) == int:
        result = value
    elif type(value) == str:
        result = int(value, 16)
    assert result is not None
    return result

if __name__ == '__main__':
    '''
    Usage
    python sotn_ppf.py EXTRACTION_JSON --data= --changes=CHANGES_JSON --ppf=OUTPUT_PPF
    '''
    DESCRIPTION = 'Designed to work with SOTN Shuffler'
    parser = argparse.ArgumentParser()
    parser.add_argument('extract_file', help='Input a filepath to the extract JSON file', type=str)
    parser.add_argument('--data', help='Input an optional (required if changes argument is given) filepath to a folder containing various data dependency files', type=str)
    parser.add_argument('--changes', help='Input an optional (required if data argument is given) filepath to the changes JSON file', type=str)
    parser.add_argument('--template', help='Input an optional filepath to the output template file, if one is generated', type=str)
    parser.add_argument('--ppf', help='Input an optional filepath to the output PPF file', type=str)
    args = parser.parse_args()
    with open(args.extract_file) as extract_file:
        extract = json.load(extract_file)
        if 'Extract' in extract:
            extract = extract['Extract']
        if args.changes is None:
            if args.template is None:
                args.template = "build/vanilla-changes.json"
            with (
                open(os.path.join(os.path.normpath(args.template)), 'w') as changes_file,
                open(os.path.join(os.path.normpath(args.data), 'aliases.yaml')) as aliases_file,
            ):
                aliases = yaml.safe_load(aliases_file)
                changes = get_changes_template_file(extract, aliases)
                json.dump(changes, changes_file, indent='    ', sort_keys=True)
        else:
            with (
                open(os.path.join(os.path.normpath(args.data), 'aliases.yaml')) as aliases_file,
                open(args.changes) as changes_file,
                open(args.ppf, 'wb') as ppf_file,
            ):
                data = {
                    'Aliases': yaml.safe_load(aliases_file),
                }
                changes = json.load(changes_file)
                if 'Changes' in changes:
                    changes = changes['Changes']
                validate_changes(changes)
                patch = get_patch(extract, changes, data)
                ppf = PPF(DESCRIPTION, patch, False)
                ppf_file.write(ppf.bytes)
