# External libraries
import argparse
import json
import os
import yaml

# Local libraries
import sotn_address

def _hex(val: int, size: int) -> str:
    result = ('{:0' + str(size) + 'X}').format(val)
    return result

class Room:
    def __init__(self, room_index: int, box: tuple[int], special_flag: int, foreground_layer_id: int):
        self.room_index = room_index
        self.top = box[0]
        self.left = box[1]
        self.height = box[2]
        self.width = box[3]
        self.special_flag = special_flag
        self.foreground_layer_id = foreground_layer_id

class Teleporter:
    def __init__(self, teleporter_index: int, x: int, y: int, room_index: int, current_stage_id: int, next_stage_id: int):
        self.teleporter_index = teleporter_index
        self.x = x
        self.y = y
        self.room_index = room_index
        self.current_stage_id = current_stage_id
        self.next_stage_id = next_stage_id

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
    
    def write_string(self, string):
        for char in string:
            self.write_byte(ord(char))
    
    def write_u16(self, value):
        for _ in range(2):
            value, byte = divmod(value, 0x100)
            self.write_byte(byte)
    
    def write_u32(self, value):
        for _ in range(4):
            value, byte = divmod(value, 0x100)
            self.write_byte(byte)
    
    def write_u64(self, value):
        for _ in range(8):
            value, byte = divmod(value, 0x100)
            self.write_byte(byte)
    
    def patch_value(self, value: int, size: int, address: sotn_address.Address):
        self.write_u64(address.to_disc_address())
        self.write_byte(size)
        if size == 1:
            self.write_byte(value)
        elif size == 2:
            self.write_u16(value)
        elif size == 4:
            self.write_u32(value)
        else:
            raise Exception('Incorrect size for value:', (value, size))
    
    def patch_string(self, offset_in_file: int, value: str):
        self.write_u64(offset_in_file)
        size = len(value)
        self.write_byte(size)
        self.write_string(value)
    
    def patch_room_data(self, room: Room, address: sotn_address.Address):
        self.write_u64(address.to_disc_address())
        size = 4
        self.write_byte(size)
        self.write_byte(room.left)
        self.write_byte(room.top)
        self.write_byte(room.left + room.width - 1)
        self.write_byte(room.top + room.height - 1)
    
    def patch_teleporter_data(self, teleporter: Teleporter, address: sotn_address.Address):
        self.write_u64(address.to_disc_address())
        size = 10
        self.write_byte(size) 
        self.write_u16(teleporter.x)
        self.write_u16(teleporter.y)
        self.write_u16(8 * teleporter.room_index)
        self.write_u16(teleporter.current_stage_id)
        self.write_u16(teleporter.next_stage_id)
    
    def patch_packed_room_data(self, room: Room, address: sotn_address.Address):
        write_address = address.to_disc_address()
        self.write_u64(write_address)
        size = 4
        self.write_byte(size)
        data = [
            room.special_flag,
            0x3F & (room.top + room.height - 1), # bottom
            0x3F & (room.left + room.width - 1), # right
            0x3F & (room.top),
            0x3F & (room.left),
        ]
        self.write_u32(
            (data[0] << 24) |
            (data[1] << 18) |
            (data[2] << 12) |
            (data[3] << 6) |
            (data[4] << 0)
        )

def get_changes_template_file(core_data):
    result = {
        'Rooms': {},
        'Constants': {},
    }
    for room_name in core_data['Rooms']:
        result['Rooms'][room_name] = {
            'Left': core_data['Rooms'][room_name]['Left'],
            'Top': core_data['Rooms'][room_name]['Top'],
        }
    for constant_name in core_data['Constants']:
        result['Constants'][constant_name] = core_data['Constants'][constant_name]['Value']
    return result

def validate_changes(changes):
    if 'Rooms' in changes:
        for room_name in changes['Rooms']:
            assert 0 <= changes['Rooms'][room_name]['Top'] <= 58
            assert 0 <= changes['Rooms'][room_name]['Left'] <= 63
    if 'Constants' in changes:
        for constant_name in changes['Constants']:
            assert 0 <= changes['Constants'][constant_name] <= 255

def get_ppf(core_data, changes):
    result = PPF('Shuffled rooms in first few stages of the game')
    if 'Rooms' in changes:
        for room_name in sorted(changes['Rooms'].keys()):
            print(room_name, changes['Rooms'][room_name], end=' ...')
            if (
                changes['Rooms'][room_name]['Top'] == core_data['Rooms'][room_name]['Top'] and
                changes['Rooms'][room_name]['Left'] == core_data['Rooms'][room_name]['Left']
            ):
                print(' SKIPPED')
                continue
            print(' ', 'patching', end=' ...')
            room = Room(
                core_data['Rooms'][room_name]['Room ID'],
                (
                    changes['Rooms'][room_name]['Top'],
                    changes['Rooms'][room_name]['Left'],
                    core_data['Rooms'][room_name]['Rows'],
                    core_data['Rooms'][room_name]['Columns'],
                ),
                core_data['Rooms'][room_name]['Special Flag'],
                core_data['Rooms'][room_name]['Foreground Layer ID'],
            )
            if 'Room Data' in core_data['Rooms'][room_name]['Insertion Metadata']:
                try:
                    result.patch_room_data(
                        room,
                        sotn_address.Address(
                            core_data['Rooms'][room_name]['Insertion Metadata']['Room Data']['Address Start']
                        )
                    )
                except KeyError:
                    print(' ', 'patch_room_data ERROR')
                    pass
            if 'Packed Room Data' in core_data['Rooms'][room_name]['Insertion Metadata']:
                try:
                    result.patch_packed_room_data(
                        room,
                        sotn_address.Address(
                            core_data['Rooms'][room_name]['Insertion Metadata']['Packed Room Data']['Address Start']
                        )
                    )
                except (KeyError, TypeError):
                    print(' ', 'patch_packed_room_data ERROR')
                    pass
            print(' DONE')
    if 'Constants' in changes:
        for constant_name in sorted(changes['Constants'].keys()):
            print(changes['Constants'][constant_name])
            if changes['Constants'][constant_name] == core_data['Constants'][constant_name]:
                continue
            print(' ', 'patching')
            result.patch_value(
                changes['Constants'][constant_name],
                2,
                sotn_address.Address(
                    core_data['Constants'][constant_name]['Insertion Metadata']['Address Start']
                ),
            )
    return result

if __name__ == '__main__':
    '''
    Usage
    python sotn_patcher.py CORE_DATA_JSON --changes CHANGES_JSON --ppf OUTPUT_PPF
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('core_data', help='Input a filepath to the core data JSON file', type=str)
    parser.add_argument('--changes', help='Input an optional filepath to the changes JSON file', type=str)
    parser.add_argument('--ppf', help='Input an optional filepath to the output PPF file', type=str)
    args = parser.parse_args()
    with open(args.core_data) as core_data_file:
        core_data = json.load(core_data_file)
        if 'Data Core' in core_data:
            core_data = core_data['Data Core']
        if args.changes is None:
            with open(os.path.join('build', 'changes.json'), 'w') as changes_file:
                changes = get_changes_template_file(core_data)
                json.dump(changes, changes_file, indent='    ', sort_keys=True)
        else:
            with (
                open(args.changes) as changes_file,
                open(args.ppf, 'wb') as ppf_file,
            ):
                changes = json.load(changes_file)
                if 'Changes' in changes:
                    changes = changes['Changes']
                validate_changes(changes)
                patch = get_ppf(core_data, changes)
                ppf_file.write(patch.bytes)
