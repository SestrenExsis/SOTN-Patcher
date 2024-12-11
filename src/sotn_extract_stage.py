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
    
    def u8(self, offset: int=0):
        # self.cursor.address += offset
        result = self.read(offset, 1, 'little', False)
        return result
    
    def u16(self, offset: int=0):
        # self.cursor.address += offset
        result = self.read(offset, 2, 'little', False)
        return result
    
    def s16(self, offset: int=0):
        # self.cursor.address += offset
        result = self.read(offset, 2, 'little', True)
        return result
    
    def u32(self, offset: int=0):
        # self.cursor.address += offset
        result = self.read(offset, 4, 'little', False)
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
                'Metadata': {
                    'Start': 0x03CDF800,
                    'Size': 193576,
                },
                'Data': {},
            },
            'Alchemy Laboratory': {
                'Metadata': {
                    'Start': 0x049BE800,
                    'Size': 309120,
                },
                'Data': {},
            },
            'Castle Entrance': {
                'Metadata': {
                    'Start': 0x041A7800,
                    'Size': 0,
                },
                'Data': {},
            },
            'Castle Entrance Revisited': {
                'Metadata': {
                    'Start': 0x0491A800,
                    'Size': 0,
                },
                'Data': {},
            },
            'Castle Keep': {
                'Metadata': {
                    'Start': 0x04AEF000,
                    'Size': 247132,
                },
                'Data': {},
            },
            'Catacombs': {
                'Metadata': {
                    'Start': 0x03BB3000,
                    'Size': 361920,
                },
                'Data': {},
            },
            'Clock Tower': {
                'Metadata': {
                    'Start': 0x04A67000,
                    'Size': 271168,
                },
                'Data': {},
            },
            'Center Cube': {
                'Metadata': {
                    'Start': 0x03C65000,
                    'Size': 119916,
                },
                'Data': {},
            },
            'Colosseum': {
                'Metadata': {
                    'Start': 0x03B00000,
                    'Size': 352636,
                },
                'Data': {},
            },
            'Long Library': {
                'Metadata': {
                    'Start': 0x03E5F800,
                    'Size': 348876,
                },
                'Data': {},
            },
            'Marble Gallery': {
                'Metadata': {
                    'Start': 0x03F8B000,
                    'Size': 390540,
                },
                'Data': {},
            },
            'Olrox\'s Quarters': {
                'Metadata': {
                    'Start': 0x040FB000,
                    'Size': 327100,
                },
                'Data': {},
            },
            'Outer Wall': {
                'Metadata': {
                    'Start': 0x04047000,
                    'Size': 356452,
                },
                'Data': {},
            },
            'Royal Chapel': {
                'Metadata': {
                    'Start': 0x03D5A800,
                    'Size': 373764,
                },
                'Data': {},
            },
            'Underground Caverns': {
                'Metadata': {
                    'Start': 0x04257800,
                    'Size': 391260,
                },
                'Data': {},
            },
            'Warp Room': {
                'Metadata': {
                    'Start': 0x04D12800,
                    'Size': 83968,
                },
                'Data': {},
            },
        }
        for stage_name in stages.keys():
            cursors = {}
            stage_offset = stages[stage_name]['Metadata']['Start']
            cursors['Stage'] = BIN(binary_file, stage_offset)
            # Extract room count
            room_offset = cursors['Stage'].u32(0x10) - OFFSET
            cursors['Room'] = cursors['Stage'].clone(room_offset)
            room_count = 0
            while cursors['Room'].u8(0x08 * room_count) != 0x40:
                room_count += 1
            # Extract room layouts
            ids = []
            for room_id in range(room_count):
                id = cursors['Room'].u8(0x08 * room_id + 0x5)
                if id == 0xFF:
                    ids.append(None)
                else:
                    ids.append(cursors['Room'].u8(0x08 * room_id + 0x4))
            layouts = []
            layouts_offset = cursors['Stage'].u32(0x20) - OFFSET
            cursors['Layouts'] = cursors['Stage'].clone(layouts_offset)
            for id in ids:
                if id is None:
                    layouts.append(None)
                    continue
                layout_offset = cursors['Layouts'].u32(0x08 * id) - OFFSET
                cursors['Layout'] = cursors['Stage'].clone(layout_offset)
                # Parse the layout data.
                layout_data = {
                    'Tiles': cursors['Layout'].u32(0) - OFFSET,
                    'Defs': cursors['Layout'].u32(0x4) - OFFSET,
                    'Dims': cursors['Layout'].u32(0x8) & 0xFFFFFF,
                }
                layout_data['Bottom'] = layout_data['Dims'] >> 18
                layout_data['Right'] = (layout_data['Dims'] >> 12) & 0x3F
                layout_data['Top'] = (layout_data['Dims'] >> 6) & 0x3F
                layout_data['Left'] = (layout_data['Dims']) & 0x3F
                layout_data['Width'] = 1 + layout_data['Right'] - layout_data['Left']
                layout_data['Height'] = 1 + layout_data['Bottom'] - layout_data['Top']
                layout_data['Room Flags'] = cursors['Layout'].u8(0xa)
                layout_data['Draw Flags'] = cursors['Layout'].u8(0xd)
                layouts.append(layout_data)
            # Extract entity layouts
            object_layout_ids = []
            for i in range(room_count):
                object_layout_id = cursors['Room'].u8(0x04 + 0x08 * i + 0x03)
                object_layout_ids.append(object_layout_id)
            entities_offset = cursors['Stage'].u32(0x0C) - OFFSET
            cursors['Entities'] = cursors['Stage'].clone(entities_offset)
            cursors['Entities X Indirect'] = cursors['Stage'].clone(cursors['Entities'].u16(0x1C))
            cursors['Entities Y Indirect'] = cursors['Stage'].clone(cursors['Entities'].u16(0x28))
            rooms = []
            for room_id in range(room_count):
                if ids[room_id] is None:
                    rooms.append(None)
                    continue
                horizontal_entity_layout_offset = cursors['Entities X Indirect'].u32(
                    4 * object_layout_ids[room_id]
                ) - OFFSET
                cursors['Entity X'] = cursors['Stage'].clone(horizontal_entity_layout_offset)
                h_entities = []
                offset = 0
                while True:
                    x = cursors['Entity X'].s16(offset + 0x0)
                    y = cursors['Entity X'].s16(offset + 0x2)
                    entity_type_id = cursors['Entity X'].s16(offset + 0x4)
                    entity_room_index = cursors['Entity X'].s16(offset + 0x6)
                    params = cursors['Entity X'].s16(offset + 0x8)
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
                    4 * object_layout_ids[room_id]
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
                room = {
                    'H': h_entities,
                    'V': v_entities,
                }
                rooms.append(room)
            # Store extracted data
            stages[stage_name]['Data'] = {
                'Room Count': room_count,
                'Layouts': layouts,
                'Object Layout IDs': object_layout_ids,
                'Rooms': rooms,
            }
        with open(args.json_filepath, 'w') as stages_json:
            json.dump(stages, stages_json, indent='    ', sort_keys=True)
