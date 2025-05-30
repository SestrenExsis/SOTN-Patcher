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
    
    def indirect(self, offset: int, data_type: str='u8', include_meta: bool=False):
        assert data_type in ('u8', 's8', 'u16', 's16', 'u32', 's32')
        dispatch = {
            'u8': self.u8,
            's8': self.s8,
            'u16': self.u16,
            's16': self.s16,
            'u32': self.u32,
            's32': self.s32,
        }
        result = dispatch[data_type](offset, include_meta)
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
                # (0x00, 'Function Updates??'), # 801C37B8 for Marble Gallery
                # (0x04, 'Function Hit Detection??'), # 801C3BBC for Marble Gallery
                # (0x08, 'Function Update Room Pos??'), # 801C5D4C for Marble Gallery
                (0x0C, 'Entities'), # 801C5BD4 for Marble Gallery
                (0x10, 'Rooms'), # 801827E0 for Marble Gallery
                # (0x14, 'Sprites??'), # 8018002C for Marble Gallery
                # (0x18, 'CLUTs??'), # 8018014C for Marble Gallery
                # (0x1C, 'Layouts??'), # 80180778 for Marble Gallery
                (0x20, 'Layouts'), # or maybe Layers??? 801804B0 for Marble Gallery
                # (0x24, 'Graphics??'), # 8018074C for Marble Gallery
                # (0x28, 'Functions 4??'), # 801C3AB4 for Marble Gallery
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
                room_data = {
                    'Left': cursors['Current Room'].u8(0x00, True),
                    'Top': cursors['Current Room'].u8(0x01, True),
                    'Right': cursors['Current Room'].u8(0x02, True),
                    'Bottom': cursors['Current Room'].u8(0x03, True),
                    'Tile Layout ID': cursors['Current Room'].u8(0x04, True),
                    'Tileset ID': cursors['Current Room'].s8(0x05, True),
                    'Object Graphics ID': cursors['Current Room'].u8(0x06, True),
                    'Object Layout ID': cursors['Current Room'].u8(0x07, True),
                }
                stages[stage_name]['Rooms'][room_id] = room_data
                # Tile layout for the current room
                if stages[stage_name]['Rooms'][room_id]['Tileset ID']['Value'] == -1:
                    continue
                tile_layout_id = stages[stage_name]['Rooms'][room_id]['Tile Layout ID']['Value']
                tile_layout_offset = cursors['Layouts'].u32(0x08 * tile_layout_id) - OFFSET
                cursors['Current Tile Layout'] = cursors['Stage'].clone(tile_layout_offset)
                tile_layout = {
                    'Tiles': cursors['Current Tile Layout'].u32(0x0, True),
                    'Defs': cursors['Current Tile Layout'].u32(0x4, True),
                    'Layout Rect': cursors['Current Tile Layout'].u32(0x8, True),
                    'Z Priority': cursors['Current Tile Layout'].u16(0xC, True),
                    'Flags': cursors['Current Tile Layout'].u16(0xE, True),
                }
                stages[stage_name]['Rooms'][room_id]['Tile Layout'] = tile_layout
                # Tile map for the current room
                stage_offset = tile_layout['Tiles']['Value'] - OFFSET
                cursors['Tilemap'] = cursors['Stage'].clone(stage_offset)
                rows = 16 * (1 + room_data['Bottom']['Value'] - room_data['Top']['Value'])
                cols = 16 * (1 + room_data['Right']['Value'] - room_data['Left']['Value'])
                for (plane_id, plane) in enumerate((
                    'Foreground',
                    'Background',
                )):
                    plane_cursor = cursors['Tilemap'].clone(2 * (plane_id * rows * cols))
                    tilemap_data = []
                    for row in range(rows):
                        row_data = []
                        for col in range(cols):
                            offset = 2 * ((plane_id * rows * cols) + (row * cols) + col)
                            value = cursors['Tilemap'].u16(offset)
                            row_data.append(sotn_address._hex(value, 4))
                        tilemap_data.append(' '.join(row_data))
                    stages[stage_name]['Rooms'][room_id]['Tilemap ' + plane] = {
                        'Metadata': {
                            'Start': plane_cursor.cursor.address,
                            'Rows': rows,
                            'Columns': cols,
                            'Type': 'tile-array',
                        },
                        'Data': tilemap_data,
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
                        data = {
                            'X': x,
                            'Y': y,
                            'Entity Type ID': entity_type_id,
                            'Entity Room Index': entity_room_index,
                            'Params': params,
                        }
                        objects['Data'].append(data)
                        if x == -1:
                            break
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
                    'Room': {
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
                'Room': cursor.u16(0x0A * teleporter_id + 0x04),
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
        # Extract constant data stored as arrays
        constants = {}
        for (starting_address, data_type, array_size, array_name) in (
            # Unique item drops in First Castle
            (0x03CE01E4, 'u16', 13, 'Unique Item Drops (Abandoned Mine)'),
            (0x049BFBB0, 'u16', 11, 'Unique Item Drops (Alchemy Laboratory)'),
            (0x0550808C, 'u16', 37, 'Unique Item Drops (Boss - Scylla)'),
            (0x041A948C, 'u16', 10, 'Unique Item Drops (Castle Entrance)'),
            (0x0491BE18, 'u16', 10, 'Unique Item Drops (Castle Entrance Revisited)'),
            (0x04AEFD10, 'u16', 19, 'Unique Item Drops (Castle Keep)'),
            (0x03BB474C, 'u16', 21, 'Unique Item Drops (Catacombs)'),
            (0x04A6811C, 'u16', 12, 'Unique Item Drops (Clock Tower)'),
            (0x03B00FE8, 'u16', 8, 'Unique Item Drops (Colosseum)'),
            (0x03E61290, 'u16', 11, 'Unique Item Drops (Long Library)'),
            (0x03F8C100, 'u16', 14, 'Unique Item Drops (Marble Gallery)'),
            (0x040FBFEC, 'u16', 13, "Unique Item Drops (Olrox's Quarters)"),
            (0x04048A2C, 'u16', 7, 'Unique Item Drops (Outer Wall)'),
            (0x03D5B6C0, 'u16', 16, 'Unique Item Drops (Royal Chapel)'),
            (0x04259128, 'u16', 37, 'Unique Item Drops (Underground Caverns)'),
            # Unique item drops in Inverted Castle
            (0x0439BFCC, 'u16', 8, 'Unique Item Drops (Cave)'),
            (0x04D81CC8, 'u16', 10, 'Unique Item Drops (Necromancy Laboratory)'),
            (0x0471EF10, 'u16', 10, 'Unique Item Drops (Reverse Entrance)'),
            (0x04C847C8, 'u16', 25, 'Unique Item Drops (Reverse Keep)'),
            (0x043083C8, 'u16', 18, 'Unique Item Drops (Floating Catacombs)'),
            (0x04E22EC8, 'u16', 12, 'Unique Item Drops (Reverse Clock Tower)'),
            (0x04C0823C, 'u16', 8, 'Unique Item Drops (Reverse Colosseum)'),
            (0x044B0BC8, 'u16', 9, 'Unique Item Drops (Forbidden Library)'),
            (0x0453E78C, 'u16', 12, 'Unique Item Drops (Black Marble Gallery)'),
            (0x04681540, 'u16', 12, "Unique Item Drops (Death Wing's Lair)"),
            (0x045EEAE4, 'u16', 8, 'Unique Item Drops (Reverse Outer Wall)'),
            (0x04416D2C, 'u16', 18, 'Unique Item Drops (Anti-Chapel)'),
            (0x047C4E20, 'u16', 27, 'Unique Item Drops (Reverse Caverns)'),
            # Relic Container Drops
            (0x049BF79C, 'u16', 4, 'Relic Container Drops'),
            # Breakable Wall Tiles
            (0x03CE009C, 'u16', 24, 'Demon Switch Wall Tiles (Abandoned Mine)'),
            (0x0439BFEC, 'u16', 24, 'Demon Switch Wall Tiles (Cave)'),
            (0x03CE00CC, 'u16', 24, 'Snake Column Wall Tiles (Abandoned Mine)'),
            (0x0439C01C, 'u16', 24, 'Snake Column Wall Tiles (Cave)'),
            # NOTE(sestren): Snake Column Wall C Tile ID was found at 0x0596D620, maybe that's for Boss - Death?
            (0x049BF654, 'u16', 32, 'Tall Zig Zag Room Wall Tiles (Alchemy Laboratory)'),
            (0x04D81C68, 'u16', 32, 'Tall Zig Zag Room Wall Tiles (Necromancy Laboratory)'),
            (0x042590B0, 'u16', 32, 'Plaque Room With Breakable Wall Tiles (Underground Caverns)'),
            (0x047C4EEC, 'u16', 32, 'Plaque Room With Breakable Wall Tiles (Reverse Caverns)'),
            (0x04A68038, 'u16', 32, 'Left Gear Room Wall Tiles (Clock Tower)'),
            (0x04E22FC8, 'u16', 32, 'Left Gear Room Wall Tiles (Reverse Clock Tower)'),
            (0x04A67FF8, 'u16', 32, 'Pendulum Room Wall Tiles (Clock Tower)'),
            (0x04E22F88, 'u16', 32, 'Pendulum Room Wall Tiles (Reverse Clock Tower)'),
        ):
            assert data_type == 'u16' # NOTE(sestren): Only handling u16s for now
            cursor = BIN(binary_file, starting_address)
            data = []
            for index in range(array_size):
                value = cursor.u16(2 * index)
                data.append(value)
            constants[array_name] = {
                'Metadata': {
                    'Start': cursor.cursor.address,
                    'Count': array_size,
                    'Size': 0x02,
                    'Type': 'u16',
                },
                'Data': data,
            }
        # Extract other constant data
        for (constant_address, constant_name, constant_data_type) in (
            # Found in the GetTeleportToOtherCastle function of the decomp
            (0x000FFCE4, 'DRA - Castle Keep Teleporter, X Offset', 's16'), # 0x2442E0C0 --> subiu v0, $1F40
            (0x000FFD18, 'DRA - Castle Keep Teleporter, Y Offset', 's16'), # 0x2442F7B1 --> subiu v0, $084F
            (0x000FFD68, 'DRA - Reverse Keep Teleporter, X Offset', 's16'), # 0x2463DF40 --> subiu v1, $20C0
            (0x000FFD9C, 'DRA - Reverse Keep Teleporter, Y Offset', 's16'), # 0x2442C7B9 --> subiu v0, $3847
            # NOTE(sestren): An extra copy of the above locations exists in the RIC overlay with a relative offset of approximately 0x03186028
            (0x03285D0C, 'RIC - Castle Keep Teleporter, X Offset', 's16'), # 0x2442E0C0 --> subiu v0, $1F40
            (0x03285D40, 'RIC - Castle Keep Teleporter, Y Offset', 's16'), # 0x2442F7B1 --> subiu v0, $084F
            (0x03285D90, 'RIC - Reverse Keep Teleporter, X Offset', 's16'), # 0x2463DF40 --> subiu v1, $20C0
            (0X03285DD0, 'RIC - Reverse Keep Teleporter, Y Offset', 's16'), # 0x2442C7B9 --> subiu v0, $3847
            # Must be updated so that False Save Room still sends you to Nightmare (Solved by @MottZilla)
            (0x000E7DC8, 'False Save Room, Room X', 'u16'), # 0x2D00 --> 45
            (0x000E7DD0, 'False Save Room, Room Y', 'u16'), # 0x2100 --> 33
            (0x000E7DA4, 'Reverse False Save Room, Room X', 'u16'), # 0x1200 --> 18
            (0x000E7DAC, 'Reverse False Save Room, Room Y', 'u16'), # 0x1E00 --> 30
            # To enable NOCLIP mode; set to 0xAC258850 --> sw a1, -$77B0(at)
            (0x000D9364, 'Set initial NOCLIP value', 'u32'), # 0xAC208850 --> sw 0, -$77B0(at)
            # Buy Castle Map, set to NOP to draw every tile within the boundaries
            (0x000E7B1C, 'Should reveal map tile', 'u32'), # 0x10400020 --> beq v0,0,$800F23A0
            # (0x0009840C, 'Castle map reveal boundary', 'u32') # 0x06082600 --> {0, 26, 8, 6} # Change to 0x40400000???
            # (0x049F761C, 'Stun player when meeting Maria in Alchemy Lab', 'u32'), # 0x34100001 --> ori s0,0,$1 # Change to 0x36100000 --> ori s0,$0
            (0x049F66EC, 'Should skip Maria Alchemy Laboratory', 'u32'), # 0x144002DA --> bne v0,0,$801B8A58 # Change to 0x0806E296 --> j $801B8A58
            # Hard-coded drops from Bone Scimitars in Castle Entrance
            (0x041FD8FC, 'Bone Scimitar Item Drop 1', 'u16'), # 0x0013 --> Item - Short Sword
            (0x041FD900, 'Bone Scimitar Item Drop 2', 'u16'), # 0x001A --> Item - Red Rust
        ):
            cursor = BIN(binary_file, constant_address)
            constants[constant_name] = cursor.indirect(0, constant_data_type, True)
        # Extract string data
        cursor = BIN(binary_file, 0x03ACEFD4)
        strings = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Count': 27,
                'Type': 'string',
                'Note': 'Strings in SOTN are null-terminated, Shift JIS-encoded character arrays',
            },
            'Data': {},
        }
        offset = 0
        UNKNOWN_CHAR = '*'
        for string_id in range(strings['Metadata']['Count']):
            # Strings are assumed to be 4-byte aligned
            assert (offset % 4) == 0
            string = ''
            while True:
                char_code = cursor.u8(offset)
                if char_code == 0x00:
                    # Strings must end in a Null character
                    offset += 4 - (offset % 4)
                    break
                elif char_code == 0x81:
                    # Shift JIS has some 2-byte characters that start with 0x81
                    offset += 1
                    char_code = cursor.u8(offset)
                    if char_code == 0x44:
                        string += '.'
                    elif char_code == 0x48:
                        string += '?'
                    elif char_code == 0x66:
                        string += "'"
                    elif char_code == 0x68:
                        string += '"'
                    else:
                        string += UNKNOWN_CHAR
                elif char_code == 0x82:
                    # Shift JIS has some 2-byte characters that start with 0x82
                    offset += 1
                    char_code = cursor.u8(offset)
                    if 0x4F <= char_code <= 0x58:
                        string += chr(ord('0') + (char_code - 0x4F))
                    else:
                        string += UNKNOWN_CHAR
                elif chr(char_code) in 'abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    string += chr(char_code)
                elif chr(char_code) in '0123456789':
                    string += chr(char_code)
                else:
                    string += UNKNOWN_CHAR
                offset += 1
            strings['Data'][string_id] = string
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
        # Extract Castle Map reveal data (when purchased in the Shop)
        cursor = BIN(binary_file, 0x0009840C)
        castle_map_reveals = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Count': 0,
                'Type': 'binary-string-array',
                'Footprint': 0,
            },
            'Data': [],
        }
        while True:
            castle_map_reveal = {
                'Left': cursor.u8(0x00),
                'Top': cursor.u8(0x01),
                'Bytes Per Row': cursor.u8(0x02),
                'Rows': cursor.u8(0x03),
                'Grid': [],
            }
            castle_map_reveals['Metadata']['Footprint'] += 4
            grid_cursor = cursor.clone(0x04)
            for row in range(castle_map_reveal['Rows']):
                grid_row_cursor = grid_cursor.clone(row * castle_map_reveal['Bytes Per Row'])
                row_data = ''
                for col in range(castle_map_reveal['Bytes Per Row']):
                    data = grid_row_cursor.u8(col)
                    castle_map_reveals['Metadata']['Footprint'] += 1
                    byte_data = ''.join(reversed('{:08b}'.format(data)))
                    row_data += byte_data.replace('0', ' ').replace('1', '#')
                castle_map_reveal['Grid'].append(row_data)
            castle_map_reveals['Data'].append(castle_map_reveal)
            castle_map_reveals['Metadata']['Count'] += 1
            grid_cursor = grid_cursor.clone(castle_map_reveal['Rows'] * castle_map_reveal['Bytes Per Row'])
            if grid_cursor.u8(0) == 0xFF:
                castle_map_reveals['Metadata']['Footprint'] += 4 - (castle_map_reveals['Metadata']['Footprint'] % 4)
                break
        # Extract Warp Room coordinates list
        cursor = BIN(binary_file, 0x04D12E5C)
        warp_room_coordinates = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Size': 0x04,
                'Count': 5,
                'Fields': {
                    'Room X': {
                        'Offset': 0x00,
                        'Type': 'u16',
                    },
                    'Room Y': {
                        'Offset': 0x02,
                        'Type': 'u16',
                    },
                },
            },
            'Data': [],
        }
        for warp_room_coordinate_id in range(warp_room_coordinates['Metadata']['Count']):
            data = {
                'Room X': cursor.u16(0x04 * warp_room_coordinate_id + 0x00),
                'Room Y': cursor.u16(0x04 * warp_room_coordinate_id + 0x02),
            }
            warp_room_coordinates['Data'].append(data)
        # Extract Reverse Warp Room coordinates list
        cursor = BIN(binary_file, 0x04EBE65C)
        reverse_warp_room_coordinates = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Size': 0x04,
                'Count': 5,
                'Fields': {
                    'Room X': {
                        'Offset': 0x00,
                        'Type': 'u16',
                    },
                    'Room Y': {
                        'Offset': 0x02,
                        'Type': 'u16',
                    },
                },
            },
            'Data': [],
        }
        for reverse_warp_room_coordinate_id in range(reverse_warp_room_coordinates['Metadata']['Count']):
            data = {
                'Room X': cursor.u16(0x04 * reverse_warp_room_coordinate_id + 0x00),
                'Room Y': cursor.u16(0x04 * reverse_warp_room_coordinate_id + 0x02),
            }
            reverse_warp_room_coordinates['Data'].append(data)
        # Extract familiar events
        cursor = BIN(binary_file, 0x0392A760)
        familiar_events = {
            'Metadata': {
                'Start': cursor.cursor.address,
                'Size': 0x30,
                'Count': 49,
                'Fields': {
                    'Unknown 00': {
                        'Offset': 0x00,
                        'Type': 'u32',
                    },
                    'Unknown 04': {
                        'Offset': 0x04,
                        'Type': 'u32',
                    },
                    'Servant ID': {
                        'Offset': 0x08,
                        'Type': 's32',
                    },
                    'Room X': {
                        'Offset': 0x0C,
                        'Type': 's32',
                    },
                    'Room Y': {
                        'Offset': 0x10,
                        'Type': 's32',
                    },
                    'Camera X': {
                        'Offset': 0x14,
                        'Type': 's32',
                    },
                    'Camera Y': {
                        'Offset': 0x18,
                        'Type': 's32',
                    },
                    'Condition': {
                        'Offset': 0x1C,
                        'Type': 's32',
                    },
                    'Delay': {
                        'Offset': 0x20,
                        'Type': 's32',
                    },
                    'Entity ID': {
                        'Offset': 0x24,
                        'Type': 's32',
                    },
                    'Params': {
                        'Offset': 0x28,
                        'Type': 's32',
                    },
                    'Unknown 2C': {
                        'Offset': 0x2C,
                        'Type': 'u32',
                    },
                },
            },
            'Data': [],
        }
        for familiar_event_id in range(familiar_events['Metadata']['Count']):
            data = {}
            for (field_name, field) in familiar_events['Metadata']['Fields'].items():
                offset = familiar_event_id * familiar_events['Metadata']['Size'] + field['Offset']
                data[field_name] = cursor.indirect(offset, field['Type'])
            familiar_events['Data'].append(data)
        # Store extracted data
        extraction = {
            'Boss Teleporters': boss_teleporters,
            'Castle Map': castle_map,
            'Castle Map Reveals': castle_map_reveals,
            'Constants': constants,
            'Familiar Events': familiar_events,
            'Reverse Warp Room Coordinates': reverse_warp_room_coordinates,
            'Stages': stages,
            'Strings': strings,
            'Teleporters': teleporters,
            'Warp Room Coordinates': warp_room_coordinates,
        }
        with open(args.json_filepath, 'w') as extraction_json:
            json.dump(extraction, extraction_json, indent='  ', sort_keys=True)
