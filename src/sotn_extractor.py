# External libraries
import argparse
import json

# Local libraries
import sotn_address

class BIN:
    def __init__(self, binary_file, stage_offset: int=0):
        self.binary_file = binary_file
        self.cursor = sotn_address.Address(stage_offset, 'GAMEDATA')
    
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
    
    def s32(self, offset: int=0, include_meta: bool=False):
        result = None
        size = 4
        value = self.read(offset, size, 'little', True)
        if include_meta:
            result = {
                'Value': value,
                'Start': self.cursor.address + offset,
                'Type': 's32',
            }
        else:
            result = value
        return result

if __name__ == '__main__':
    '''
    Extract game data from a binary file and output it to a JSON file

    Usage
    python src/sotn_extractor.py INPUT_BIN OUTPUT_JSON
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
            'Anti-Chapel': {
                'Stage': {
                    'Start': 0x04416000,
                    'Size': 295736,
                },
            },
            'Black Marble Gallery': {
                'Stage': {
                    'Start': 0x0453D800,
                    'Size': 347020,
                },
            },
            'Boss - Olrox': {
                'Stage': {
                    'Start': 0x0534C800,
                    'Size': 320948,
                },
            },
            'Boss - Granfaloon': {
                'Stage': {
                    'Start': 0x053F7000,
                    'Size': 205756,
                },
            },
            'Boss - Minotaur and Werewolf': {
                'Stage': {
                    'Start': 0x05473800,
                    'Size': 223540,
                },
            },
            'Boss - Scylla': {
                'Stage': {
                    'Start': 0x05507000,
                    'Size': 210224,
                },
            },
            'Boss - Doppelganger 10': {
                'Stage': {
                    'Start': 0x05593000,
                    'Size': 347704,
                },
            },
            'Boss - Hippogryph': {
                'Stage': {
                    'Start': 0x05638800,
                    'Size': 218672,
                },
            },
            'Boss - Richter': {
                'Stage': {
                    'Start': 0x056C8800,
                    'Size': 333544,
                },
            },
            'Boss - Cerberus': {
                'Stage': {
                    'Start': 0x0596D000,
                    'Size': 144480,
                },
            },
            'Boss - Trio': {
                'Stage': {
                    'Start': 0x05775000,
                    'Size': 160988,
                },
            },
            'Boss - Beelzebub': {
                'Stage': {
                    'Start': 0x05870000,
                    'Size': 139104,
                },
            },
            'Boss - Death': {
                'Stage': {
                    'Start': 0x058ED800,
                    'Size': 190792,
                },
            },
            'Boss - Medusa': {
                'Stage': {
                    'Start': 0x059E9800,
                    'Size': 132656,
                },
            },
            'Boss - Creature': {
                'Stage': {
                    'Start': 0x05A65000,
                    'Size': 154660,
                },
            },
            'Boss - Doppelganger 40': {
                'Stage': {
                    'Start': 0x05AE3800,
                    'Size': 345096,
                },
            },
            'Boss - Shaft and Dracula': {
                'Stage': {
                    'Start': 0x05B93800,
                    'Size': 213060,
                },
            },
            'Boss - Succubus': {
                'Stage': {
                    'Start': 0x04F31000,
                    'Size': 147456,
                },
            },
            'Boss - Akmodan II': {
                'Stage': {
                    'Start': 0x05C24000,
                    'Size': 142572,
                },
            },
            'Boss - Galamoth': {
                'Stage': {
                    'Start': 0x05C9F800,
                    'Size': 161212,
                },
            },
            'Castle Center': {
                'Stage': {
                    'Start': 0x03C65000,
                    'Size': 119916,
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
            'Cave': {
                'Stage': {
                    'Start': 0x0439B800,
                    'Size': 174880,
                },
            },
            'Clock Tower': {
                'Stage': {
                    'Start': 0x04A67000,
                    'Size': 271168,
                },
            },
            'Colosseum': {
                'Stage': {
                    'Start': 0x03B00000,
                    'Size': 352636,
                },
            },
            'Cutscene - Meeting Maria in Clock Room': {
                'Stage': {
                    'Start': 0x057F9800,
                    'Size': 0,
                },
            },
            'Death Wing\'s Lair': {
                'Stage': {
                    'Start': 0x04680800,
                    'Size': 313816,
                },
            },
            'Floating Catacombs': {
                'Stage': {
                    'Start': 0x04307000,
                    'Size': 278188,
                },
            },
            'Forbidden Library': {
                'Stage': {
                    'Start': 0x044B0000,
                    'Size': 201776,
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
            'Necromancy Laboratory': {
                'Stage': {
                    'Start': 0x04D81000,
                    'Size': 281512,
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
            'Reverse Caverns': {
                'Stage': {
                    'Start': 0x047C3800,
                    'Size': 384020,
                },
            },
            'Reverse Castle Center': {
                'Stage': {
                    'Start': 0x04B87800,
                    'Size': 186368,
                },
            },
            'Reverse Clock Tower': {
                'Stage': {
                    'Start': 0x04E22000,
                    'Size': 260960,
                },
            },
            'Reverse Colosseum': {
                'Stage': {
                    'Start': 0x04C07800,
                    'Size': 234384,
                },
            },
            'Reverse Entrance': {
                'Stage': {
                    'Start': 0x0471E000,
                    'Size': 304428,
                },
            },
            'Reverse Keep': {
                'Stage': {
                    'Start': 0x04C84000,
                    'Size': 200988,
                },
            },
            'Reverse Outer Wall': {
                'Stage': {
                    'Start': 0x045EE000,
                    'Size': 357020,
                },
            },
            'Reverse Warp Rooms': {
                'Stage': {
                    'Start': 0x04EBE000,
                    'Size': 92160,
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
            'Warp Rooms': {
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
                (0x0C, 'Entities'), # 801C3C98 for Castle Entrance
                (0x10, 'Rooms'), # 80183CC4 for Castle Entrance
                # (0x14, '???'), # 8018002C for Castle Entrance
                # (0x18, '???'), # 801801C0 for Castle Entrance
                # (0x1C, '???'), # 8018077C for Castle Entrance
                (0x20, 'Layouts'), # 801804C4 for Castle Entrance
                # (0x24, '???'), # 8018072C for Castle Entrance
                # (0x28, '???'), # 801C1B78 for Castle Entrance
            ):
                stage_offset = cursors['Stage'].u32(address) - OFFSET
                cursors[cursor_name] = cursors['Stage'].clone(stage_offset)
            #
            # Room data
            stages[stage_name]['Rooms'] = {}
            for room_id in range(256):
                cursors['Current Room'] = cursors['Rooms'].clone(0x08 * room_id)
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
                    objects = {
                        'Metadata': {
                            'Start': cursors[direction].cursor.address,
                            'Size': 0x0A,
                            'Count': 0,
                            'Fields': {
                                'X': {
                                    'Offset': 0x00,
                                    'Type': 's16',
                                },
                                'Y': {
                                    'Offset': 0x02,
                                    'Type': 's16',
                                },
                                'Entity Type ID': {
                                    'Offset': 0x04,
                                    'Type': 'u16',
                                },
                                'Entity Room Index': {
                                    'Offset': 0x06,
                                    'Type': 'u16',
                                },
                                'Params': {
                                    'Offset': 0x08,
                                    'Type': 'u16',
                                },
                            },
                        },
                        'Data': [],
                    }
                    offset = 0
                    while True:
                        x = cursors[direction].s16(offset + 0x0)
                        y = cursors[direction].s16(offset + 0x2)
                        entity_type_id = cursors[direction].u16(offset + 0x4)
                        entity_room_index = cursors[direction].u16(offset + 0x6)
                        params = cursors[direction].u16(offset + 0x8)
                        offset += 10
                        if x == -2:
                            continue
                        elif x == -1:
                            break
                        data = {
                            'X': x,
                            'Y': y,
                            'Entity Type ID': entity_type_id,
                            'Entity Room Index': entity_room_index,
                            'Params': params,
                        }
                        objects['Data'].append(data)
                    objects['Metadata']['Count'] = len(objects['Data'])
                    stages[stage_name]['Rooms'][room_id]['Object Layout - ' + direction] = objects
        # Extract teleporter data
        cursor = BIN(binary_file, 0x00097C5C)
        teleporters = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Size': 0x0A,
                'Count': 131,
                'Fields': {
                    'Player X': {
                        'Offset': 0x00,
                        'Type': 'u16',
                    },
                    'Player Y': {
                        'Offset': 0x02,
                        'Type': 'u16',
                    },
                    'Room Offset': {
                        'Offset': 0x04,
                        'Type': 'u16',
                    },
                    'Source Stage ID': {
                        'Offset': 0x06,
                        'Type': 'u16',
                    },
                    'Target Stage ID': {
                        'Offset': 0x08,
                        'Type': 'u16',
                    },
                },
            },
            'Data': [],
        }
        for teleporter_id in range(131):
            data = {
                'Player X': cursor.u16(0x0A * teleporter_id + 0x00),
                'Player Y': cursor.u16(0x0A * teleporter_id + 0x02),
                'Room Offset': cursor.u16(0x0A * teleporter_id + 0x04),
                'Source Stage ID': cursor.u16(0x0A * teleporter_id + 0x06),
                'Target Stage ID': cursor.u16(0x0A * teleporter_id + 0x08),
            }
            teleporters['Data'].append(data)
        # Extract boss teleporter data
        cursor = BIN(binary_file, 0x0009817C)
        boss_teleporters = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Size': 0x14,
                'Count': 28,
                'Fields': {
                    'Room X': {
                        'Offset': 0x00,
                        'Type': 'u8',
                    },
                    'Room Y': {
                        'Offset': 0x04,
                        'Type': 'u8',
                    },
                    'Stage ID': {
                        'Offset': 0x08,
                        'Type': 'u32',
                    },
                    'Event ID': {
                        'Offset': 0x0C,
                        'Type': 's8',
                    },
                    'Teleporter Index': {
                        'Offset': 0x10,
                        'Type': 's32',
                    },
                },
            },
            'Data': [],
        }
        for boss_teleporter_id in range(28):
            data = {
                'Room X': cursor.u8(0x14 * boss_teleporter_id + 0x00),
                'Room Y': cursor.u8(0x14 * boss_teleporter_id + 0x04),
                'Stage ID': cursor.u32(0x14 * boss_teleporter_id + 0x08),
                'Event ID': cursor.s8(0x14 * boss_teleporter_id + 0x0C),
                'Teleporter Index': cursor.s32(0x14 * boss_teleporter_id + 0x10),
            }
            boss_teleporters['Data'].append(data)
        # Extract constant data
        constants = {}
        cursor = BIN(binary_file, 0x049BF79C)
        for drop_index in range(2, 4):
            data = cursor.u16(2 * drop_index, True)
            constants[f'Relic Container Drop ID {str(drop_index)}'] = data
        cursor = BIN(binary_file, 0x000FFCE4) # 0x2442E0C0 --> subiu v0, $1F40
        constants[f'Castle Teleporter, X Offset'] = cursor.s16(0, True)
        cursor = BIN(binary_file, 0x000FFD18) # 0x2442F7B1 --> subiu v0, $084F
        constants[f'Castle Teleporter, Y Offset'] = cursor.s16(0, True)
        # Extract castle map data
        cursor = BIN(binary_file, 0x001AF800)
        castle_map = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Rows': 256,
                'Columns': 128,
                'Type': 'indexed-bitmap',
            },
            'Data': [],
        }
        for row in range(castle_map['Metadata']['Rows']):
            row_cursor = cursor.clone(row * castle_map['Metadata']['Columns'])
            row_data = ''
            for col in range(castle_map['Metadata']['Columns']):
                data = row_cursor.u8(col)
                row_data += ''.join(reversed('{:02X}'.format(data)))
            castle_map['Data'].append(row_data)
        # TODO(sestren): Extract Warp Room coordinates list
        # Store extracted data
        extraction = {
            'Constants': constants,
            'Stages': stages,
            'Teleporters': teleporters,
            'Boss Teleporters': boss_teleporters,
            'Castle Map': castle_map,
        }
        with open(args.json_filepath, 'w') as extraction_json:
            json.dump(extraction, extraction_json, indent='  ', sort_keys=True)
