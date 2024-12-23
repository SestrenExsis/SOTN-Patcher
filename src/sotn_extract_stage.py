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
                'Type': 'u8',
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
                'Type': 's8',
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
                'Type': 'u16',
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
                'Type': 's16',
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
                'Type': 'u32',
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
            #
            # Room data
            stages[stage_name]['Rooms'] = {}
            for room_id in range(256):
                print(room_id)
                cursors['Current Room'] = cursors['Room'].clone(0x08 * room_id)
                if cursors['Current Room'].u8() == 0x40:
                    break
                stages[stage_name]['Rooms'][room_id] = {
                    'Left': cursors['Current Room'].u8(0x00, True),
                    'Top': cursors['Current Room'].u8(0x01, True),
                    'Right': cursors['Current Room'].u8(0x02, True),
                    'Bottom': cursors['Current Room'].u8(0x03, True),
                    'Tile Layout ID': cursors['Current Room'].u8(0x04, True),
                    'Tileset ID': cursors['Current Room'].s8(0x05, True),
                    'Object Graphics ID': cursors['Current Room'].u8(0x06, True),
                    'Object Layout ID': cursors['Current Room'].u8(0x07, True),
                }
                # Tile layout for the current room
                if stages[stage_name]['Rooms'][room_id]['Tileset ID']['Value'] == -1:
                    continue
                tile_layout_id = stages[stage_name]['Rooms'][room_id]['Tile Layout ID']['Value']
                tile_layout_offset = cursors['Layouts'].u32(0x08 * tile_layout_id) - OFFSET
                cursors['Current Tile Layout'] = cursors['Stage'].clone(tile_layout_offset)
                stages[stage_name]['Rooms'][room_id]['Tile Layout'] = {
                    'Tiles': cursors['Current Tile Layout'].u32(0x0, True),
                    'Defs': cursors['Current Tile Layout'].u32(0x4, True),
                    'Layout Rect': cursors['Current Tile Layout'].u32(0x8, True),
                    'Z Priority': cursors['Current Tile Layout'].u16(0xC, True),
                    'Flags': cursors['Current Tile Layout'].u16(0xE, True),
                }
                # Object layouts for the current room
                object_layout_id = stages[stage_name]['Rooms'][room_id]['Object Layout ID']['Value']
                for (direction, indirect_offset) in (
                    ('Horizontal', 0x1C),
                    ('Vertical', 0x28),
                ):
                    cursors[direction + ' Indirect'] = cursors['Stage'].clone(cursors['Entities'].u16(indirect_offset))
                    # Object list
                    object_layout_offset = cursors[direction + ' Indirect'].u32(4 * object_layout_id) - OFFSET
                    cursors[direction] = cursors['Stage'].clone(object_layout_offset)
                    objects = []
                    offset = 0
                    while True:
                        x = cursors[direction].s16(offset + 0x0, True)
                        y = cursors[direction].s16(offset + 0x2, True)
                        entity_type_id = cursors[direction].u16(offset + 0x4, True)
                        entity_room_index = cursors[direction].u16(offset + 0x6, True)
                        params = cursors[direction].u16(offset + 0x8, True)
                        offset += 10
                        if x['Value'] == -2:
                            continue
                        elif x['Value'] == -1:
                            break
                        _object = {
                            'X': x,
                            'Y': y,
                            'Entity Type ID': entity_type_id,
                            'Entity Room Index': entity_room_index,
                            'Params': params,
                        }
                        objects.append(_object)
                    stages[stage_name]['Rooms'][room_id]['Object Layout - ' + direction] = objects
        # Extract teleporter data
        teleporters = {}
        cursor = BIN(binary_file, 0x00097C5C)
        for teleporter_id in range(131):
            data = {
                'Player X': cursor.u16(10 * teleporter_id + 0x0, True),
                'Player Y':  cursor.u16(10 * teleporter_id + 0x2, True),
                'Room Offset': cursor.u16(10 * teleporter_id + 0x4, True),
                'Source Stage ID':  cursor.u16(10 * teleporter_id + 0x6, True),
                'Target Stage ID':  cursor.u16(10 * teleporter_id + 0x8, True),
            }
            teleporters[teleporter_id] = data
        # Extract constant data
        constants = {}
        cursor = BIN(binary_file, 0x049BF79C)
        for drop_index in range(2, 4):
            data = cursor.u16(2 * drop_index, True)
            constants[f'Relic Container Drop ID {str(drop_index)}'] = data
        # Store extracted data
        extraction = {
            'Constants': constants,
            'Stages': stages,
            'Teleporters': teleporters,
        }
        with open(args.json_filepath, 'w') as extraction_json:
            json.dump(extraction, extraction_json, indent='  ', sort_keys=True)
