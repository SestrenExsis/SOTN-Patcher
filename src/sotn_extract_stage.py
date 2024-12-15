# External libraries
import argparse
import json
import os
import struct
import yaml

# Local libraries
import sotn_address

class BIN:
    def __init__(self, binary_file, stage_offset: int=0):
        self.binary_file = binary_file
        self.cursor = sotn_address.Address(stage_offset, 'GAMEDATA')
        print(self.cursor.to_disc_address())
    
    def clone(self, offset: int=0):
        result = BIN(self.binary_file, self.cursor.address + offset)
        return result
    
    def set(self, offset: int):
        self.cursor.address = offset
    
    def seek(self, offset: int):
        self.cursor.address += offset
    
    def read(self, offset, byte_count, endianness, sign):
        bytes = []
        for i in range(byte_count):
            binary_file.seek(self.cursor.to_disc_address(offset + i))
            byte = binary_file.read(1)
            bytes.append(int.from_bytes(byte))
        # self.cursor.address += byte_count
        result = int.from_bytes(bytes, byteorder=endianness, signed=sign)
        return result
    
    def u8(self, offset: int=0, include_meta: bool=False):
        result = None
        size = 1
        value = self.read(offset, size, 'little', False)
        if include_meta:
            result = {
                'Value': value,
                'Start': self.cursor.address + offset,
                'Size': size,
            }
        else:
            result = value
        return result
    
    def s8(self, offset: int=0, include_meta: bool=False):
        result = None
        size = 1
        value = self.read(offset, size, 'little', True)
        if include_meta:
            result = {
                'Value': value,
                'Start': self.cursor.address + offset,
                'Size': size,
            }
        else:
            result = value
        return result
    
    def u16(self, offset: int=0, include_meta: bool=False):
        result = None
        size = 2
        value = self.read(offset, size, 'little', False)
        if include_meta:
            result = {
                'Value': value,
                'Start': self.cursor.address + offset,
                'Size': size,
            }
        else:
            result = value
        return result
    
    def s16(self, offset: int=0, include_meta: bool=False):
        result = None
        size = 2
        value = self.read(offset, size, 'little', True)
        if include_meta:
            result = {
                'Value': value,
                'Start': self.cursor.address + offset,
                'Size': size,
            }
        else:
            result = value
        return result
    
    def u32(self, offset: int=0, include_meta: bool=False):
        result = None
        size = 4
        value = self.read(offset, size, 'little', False)
        if include_meta:
            result = {
                'Value': value,
                'Start': self.cursor.address + offset,
                'Size': size,
            }
        else:
            result = value
        return result

if __name__ == '__main__':
    '''
    Extract game data from a binary file and output it to a JSON file

    Usage
    python src/sotn_extract_stage.py INPUT_BIN OUTPUT_JSON
    '''
    OFFSET = 0x80180000
    parser = argparse.ArgumentParser()
    parser.add_argument('binary_filepath', help='Input a filepath to the input BIN file', type=str)
    parser.add_argument('json_filepath', help='Input a filepath for creating the output JSON file', type=str)
    args = parser.parse_args()
    with (
        open(args.binary_filepath, 'br') as binary_file,
    ):
        stages = {
            'Abandoned Mine': {
                'Stage': {
                    'Start': 0x03CDF800,
                    'Size': 193576,
                },
            },
            'Alchemy Laboratory': {
                'Stage': {
                    'Start': 0x049BE800,
                    'Size': 309120,
                },
            },
            'Castle Entrance': {
                'Stage': {
                    'Start': 0x041A7800,
                    'Size': 0,
                },
            },
            'Castle Entrance Revisited': {
                'Stage': {
                    'Start': 0x0491A800,
                    'Size': 0,
                },
            },
            'Castle Keep': {
                'Stage': {
                    'Start': 0x04AEF000,
                    'Size': 247132,
                },
            },
            'Catacombs': {
                'Stage': {
                    'Start': 0x03BB3000,
                    'Size': 361920,
                },
            },
            'Clock Tower': {
                'Stage': {
                    'Start': 0x04A67000,
                    'Size': 271168,
                },
            },
            'Center Cube': {
                'Stage': {
                    'Start': 0x03C65000,
                    'Size': 119916,
                },
            },
            'Colosseum': {
                'Stage': {
                    'Start': 0x03B00000,
                    'Size': 352636,
                },
            },
            'Long Library': {
                'Stage': {
                    'Start': 0x03E5F800,
                    'Size': 348876,
                },
            },
            'Marble Gallery': {
                'Stage': {
                    'Start': 0x03F8B000,
                    'Size': 390540,
                },
            },
            'Olrox\'s Quarters': {
                'Stage': {
                    'Start': 0x040FB000,
                    'Size': 327100,
                },
            },
            'Outer Wall': {
                'Stage': {
                    'Start': 0x04047000,
                    'Size': 356452,
                },
            },
            'Royal Chapel': {
                'Stage': {
                    'Start': 0x03D5A800,
                    'Size': 373764,
                },
            },
            'Underground Caverns': {
                'Stage': {
                    'Start': 0x04257800,
                    'Size': 391260,
                },
            },
            'Warp Room': {
                'Stage': {
                    'Start': 0x04D12800,
                    'Size': 83968,
                },
            },
        }
        for stage_name in stages.keys():
            cursors = {}
            stage_offset = stages[stage_name]['Stage']['Start']
            cursors['Stage'] = BIN(binary_file, stage_offset)
            for (address, cursor_name) in (
                # (0x00, '???'), # 801C187C for Castle Entrance
                # (0x04, '???'), # 801C1C80 for Castle Entrance
                # (0x08, '???'), # 801C3E10 for Castle Entrance
                (0x0C, 'Entities'),
                (0x10, 'Room'),
                # (0x14, '???'), # 8018002C for Castle Entrance
                # (0x18, '???'), # 801801C0 for Castle Entrance
                # (0x1C, '???'), # 8018077C for Castle Entrance
                (0x20, 'Layouts'),
                # (0x24, '???'), # 8018072C for Castle Entrance
                # (0x28, '???'), # 801C1B78 for Castle Entrance
            ):
                stage_offset = cursors['Stage'].u32(address) - OFFSET
                cursors[cursor_name] = cursors['Stage'].clone(stage_offset)
            # Extract room data
            room_count = 0
            stages[stage_name]['Rooms'] = []
            while cursors['Room'].u8(0x08 * room_count) != 0x40:
                room = {
                    'Left': cursors['Room'].u8(0x08 * room_count + 0x00, True),
                    'Top': cursors['Room'].u8(0x08 * room_count + 0x01, True),
                    'Right': cursors['Room'].u8(0x08 * room_count + 0x02, True),
                    'Bottom': cursors['Room'].u8(0x08 * room_count + 0x03, True),
                    'Tile Layout ID': cursors['Room'].u8(0x08 * room_count + 0x04, True),
                    'Tileset ID': cursors['Room'].s8(0x08 * room_count + 0x05, True),
                    'Object Graphics ID': cursors['Room'].u8(0x08 * room_count + 0x06, True),
                    'Object Layout ID': cursors['Room'].u8(0x08 * room_count + 0x07, True),
                }
                stages[stage_name]['Rooms'].append(room)
                room_count += 1
            # Extract layouts
            stages[stage_name]['Layouts'] = []
            for (room_id, room) in enumerate(stages[stage_name]['Rooms']):
                if room['Tileset ID']['Value'] == -1:
                    continue
                id = room['Tile Layout ID']['Value']
                layout_offset = cursors['Layouts'].u32(0x08 * id) - OFFSET
                cursors['Current Layout'] = cursors['Stage'].clone(layout_offset)
                # Parse the layout data.
                ltrb = 0xFFFFFF & cursors['Current Layout'].u32(0x8)
                layout_data = {
                    'Tiles': cursors['Current Layout'].u32(0) - OFFSET,
                    'Defs': cursors['Current Layout'].u32(0x4) - OFFSET,
                    'Packed LTRB': ltrb,
                }
                layout_data['Left'] = 0x3F & (ltrb)
                layout_data['Top'] = 0x3F & (ltrb >> 6)
                layout_data['Right'] = 0x3F & (ltrb >> 12)
                layout_data['Bottom'] = 0x3F & (ltrb >> 18)
                layout_data['Rows'] = 1 + layout_data['Bottom'] - layout_data['Top']
                layout_data['Columns'] = 1 + layout_data['Right'] - layout_data['Left']
                layout_data['Room Flags'] = cursors['Current Layout'].u8(0xa)
                layout_data['Draw Flags'] = cursors['Current Layout'].u8(0xd)
                stages[stage_name]['Layouts'].append(layout_data)
            # Extract entity layouts
            cursors['Entities X Indirect'] = cursors['Stage'].clone(cursors['Entities'].u16(0x1C))
            cursors['Entities Y Indirect'] = cursors['Stage'].clone(cursors['Entities'].u16(0x28))
            entity_layouts = []
            for (room_id, room) in enumerate(stages[stage_name]['Rooms']):
                if room['Tileset ID']['Value'] == -1:
                    entity_layouts.append(None)
                    continue
                horizontal_entity_layout_offset = cursors['Entities X Indirect'].u32(
                    4 * stages[stage_name]['Rooms'][room_id]['Object Layout ID']['Value']
                ) - OFFSET
                cursors['Entity X'] = cursors['Stage'].clone(horizontal_entity_layout_offset)
                h_entities = []
                offset = 0
                while True:
                    x = cursors['Entity X'].s16(offset + 0x0)
                    y = cursors['Entity X'].s16(offset + 0x2)
                    entity_type_id = cursors['Entity X'].u16(offset + 0x4)
                    entity_room_index = cursors['Entity X'].u16(offset + 0x6)
                    params = cursors['Entity X'].u16(offset + 0x8)
                    offset += 10
                    if x == -2:
                        continue
                    elif x == -1:
                        break
                    entity = {
                        'X': x,
                        'Y': y,
                        'Entity Type ID': entity_type_id,
                        'Entity Room Index': entity_room_index,
                        'Params': params,
                    }
                    h_entities.append(entity)
                vertical_entity_layout_offset = cursors['Entities Y Indirect'].u32(
                    4 * stages[stage_name]['Rooms'][room_id]['Object Layout ID']['Value']
                ) - OFFSET
                cursors['Entity Y'] = cursors['Stage'].clone(vertical_entity_layout_offset)
                v_entities = []
                offset = 0
                while True:
                    x = cursors['Entity Y'].s16(offset + 0x0)
                    y = cursors['Entity Y'].s16(offset + 0x2)
                    entity_type_id = cursors['Entity Y'].s16(offset + 0x4)
                    entity_room_index = cursors['Entity Y'].s16(offset + 0x6)
                    params = cursors['Entity Y'].s16(offset + 0x8)
                    offset += 10
                    if x == -2:
                        continue
                    elif x == -1:
                        break
                    entity = {
                        'X': x,
                        'Y': y,
                        'Entity Type ID': entity_type_id,
                        'Entity Room Index': entity_room_index,
                        'Params': params,
                    }
                    v_entities.append(entity)
                entity_layout = {
                    'Entities Horizontal': h_entities,
                    'Entities Vertical': v_entities,
                }
                entity_layouts.append(entity_layout)
            # Store extracted data
            stages[stage_name]['Data'] = {
                'Entity Layouts': entity_layouts,
                'Room Count': room_count,
            }
        with open(args.json_filepath, 'w') as stages_json:
            json.dump(stages, stages_json, indent='    ', sort_keys=True)
