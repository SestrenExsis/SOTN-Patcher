# External libraries
import argparse
import json
import os

# Local libraries
import sotn_address

class Room:
    def __init__(self, room_index: int, box: tuple[int], flags: set[str], foreground_layer_id: int):
        self.room_index = room_index
        self.top = box[0]
        self.left = box[1]
        self.height = box[2]
        self.width = box[3]
        self.flags = flags
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
    
    def patch_string(self, offset_in_file: int, value: str):
        self.write_u64(offset_in_file)
        size = len(value)
        self.write_byte(size)
        self.write_string(value)
    
    def patch_room_data(self, room: Room, address: sotn_address.Address):
        self.write_u64(address.to_disc_address(8 * room.room_index))
        size = 4
        self.write_byte(size)
        self.write_byte(room.left)
        self.write_byte(room.top)
        self.write_byte(room.left + room.width - 1)
        self.write_byte(room.top + room.height - 1)
    
    def patch_teleporter_data(self, teleporter: Teleporter, address: sotn_address.Address):
        self.write_u64(address.to_disc_address(10 * teleporter.teleporter_index))
        size = 10
        self.write_byte(size) 
        self.write_u16(teleporter.x)
        self.write_u16(teleporter.y)
        self.write_u16(8 * teleporter.room_index)
        self.write_u16(teleporter.current_stage_id)
        self.write_u16(teleporter.next_stage_id)
    
    def patch_packed_room_data(self, room: Room, address: sotn_address.Address):
        write_address = address.to_disc_address(0x10 * room.foreground_layer_id + 0x08)
        self.write_u64(write_address)
        size = 4
        self.write_byte(size)
        flags_byte = 0x00
        flags = {
            'Load On Left': 0x40,
            'Load On Right': 0x41,
            'Save With Left Opening': 0x20,
            'Save With Right Opening': 0x22,
            'Scroll Type 1': 0x01,
            'Special Type 1': 0x80,
            'Special Type 2': 0x92,
        }
        for flag_name in room.flags:
            if flag_name in flags:
                flags_byte |= flags[flag_name]
        data = [
            flags_byte,
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

def get_room_rando_ppf(core_data, changes):
    addresses = {
        ('Teleporter Data'): sotn_address.Address(0x00097C5C),
        ('Room Data', 'Alchemy Laboratory'): sotn_address.Address(0x049C0F2C),
        ('Room Data', 'Castle Entrance'): sotn_address.Address(0x041AB4C4),
        ('Room Data', 'Castle Entrance Revisited'): sotn_address.Address(0x0491E27C),
        ('Room Data', 'Marble Gallery'): sotn_address.Address(0x03F8D7E0),
        ('Room Data', 'Olrox\'s Quarters'): sotn_address.Address(0x040FE2A0),
        ('Room Data', 'Outer Wall'): sotn_address.Address(0x0404A488),
        ('Layer Data', 'Alchemy Laboratory'): sotn_address.Address(0x049BE964),
        ('Layer Data', 'Castle Entrance'): sotn_address.Address(0x041A79C4),
        ('Layer Data', 'Castle Entrance Revisited'): sotn_address.Address(0x0491A9D0),
        ('Layer Data', 'Marble Gallery'): sotn_address.Address(0x03F8B150),
        ('Layer Data', 'Olrox\'s Quarters'): sotn_address.Address(0x040FB110),
        ('Layer Data', 'Outer Wall'): sotn_address.Address(0x040471D4),
    }
    result = PPF('Shuffled rooms in first few stages of the game')
    for room_name in sorted(changes['Rooms'].keys()):
        if (
            changes['Rooms'][room_name]['Top'] == core_data['Rooms'][room_name]['Top'] and
            changes['Rooms'][room_name]['Left'] == core_data['Rooms'][room_name]['Left']
        ):
            continue
        flags = set()
        if core_data['Rooms'][room_name]['Flags'] is not None:
            flags = set(core_data['Rooms'][room_name]['Flags'])
        foreground_layer_id = None
        if 'Foreground Layer ID' in core_data['Rooms'][room_name]:
            foreground_layer_id = core_data['Rooms'][room_name]['Foreground Layer ID']
        room = Room(
            core_data['Rooms'][room_name]['Index'],
            (
                changes['Rooms'][room_name]['Top'],
                changes['Rooms'][room_name]['Left'],
                core_data['Rooms'][room_name]['Rows'],
                core_data['Rooms'][room_name]['Columns'],
            ),
            flags,
            foreground_layer_id,
        )
        result.patch_room_data(
            room,
            addresses[('Room Data', core_data['Rooms'][room_name]['Stage'])]
        )
        if 'Foreground Layer ID' in core_data['Rooms'][room_name]:
            result.patch_packed_room_data(
                room,
                addresses[('Layer Data', core_data['Rooms'][room_name]['Stage'])]
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
        if args.changes is None:
            changes = {
                'Rooms': {}
            }
            for room_name in core_data['Rooms']:
                changes['Rooms'][room_name] = {
                    'Left': core_data['Rooms'][room_name]['Left'],
                    'Top': core_data['Rooms'][room_name]['Top'],
                }
            with open(os.path.join('build', 'changes.json'), 'w') as changes_file:
                json.dump(changes, changes_file, indent='    ', sort_keys=True)
        else:
            with (
                open(args.ppf, 'w') as ppf_file,
                open(args.changes) as changes_file,
            ):
                changes = json.load(changes_file)
                patch = get_room_rando_ppf(core_data, changes)
                with open(args.ppf, 'wb') as ppf_file:
                    ppf_file.write(patch.bytes)
