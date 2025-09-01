# External libraries
import json
import os

def get_clock_hands_patch():
    patch = {
        'Description': 'Clock hands display minutes and seconds',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Pokes': [],
        },
    }
    for (base, stage_name) in (
        (0x03FD7C2C, 'Marble Gallery'),
        (0x0457E5D4, 'Black Marble Gallery'),
        (0x05811C94, 'Maria Clock Room Cutscene'),
    ):
        for (offset, value_a, value_b, note) in (
            (0x00, 0x8CA302D4, 0x8E6302D4, 'lw v1,$2D4(X)'),
            (0x18, 0x00000000, 0x00000000, 'nop'),
            (0x20, 0x00000000, 0x00000000, 'nop'),
            (0x24, 0x00000000, 0x00000000, 'nop'),
            (0x28, 0x00051900, 0x00041900, 'sll v1,X,$4'),
            (0x2C, 0x00651823, 0x00641823, 'subu v1,X'),
            (0x34, 0x00000000, 0x00000000, 'nop'),
            (0x38, 0x00000000, 0x00000000, 'nop'),
            (0x3C, 0x00000000, 0x00000000, 'nop'),
        ):
            value = value_a if stage_name in ('Marble Gallery', 'Black Marble Gallery') else value_b
            patch['Changes']['Pokes'].append({
                'Gamedata Address': '{:08X}'.format(base + offset),
                'Data Type': 'u32',
                'Value': '{:08X}'.format(value),
                'Notes': [
                    f'EntityClockRoomController in {stage_name}',
                    note,
                ]
            })
    result = patch
    return result

def get_prevent_softlocks_when_meeting_death_patch():
    patch = {
        'Description': 'Prevent softlocks when meeting Death',
        'Authors': [
            'Mottzilla',
        ],
        'Changes': {
            'Pokes': [],
        },
    }
    for (offset, data_type, value) in (
        (0x041E77B0, 'u32', 0x34020000),
        (0x041E77B4, 'u32', 0xAE22B98C),
    ):
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': '{:08X}'.format(value),
        })
    result = patch
    return result

def get_prevent_softlocks_at_snake_column_wall_patch():
    patch = {
        'Description': 'Prevent softlocks at Snake Column Wall',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
        },
    }
    for stage_name in (
        'Abandoned Mine',
        'Cave',
    ):
        constant_key = f'Snake Column Wall Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (0, 0x0000),
            (1, 0x0000),
            (2, 0x0000),
            (3, 0x0000),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_prevent_softlocks_at_demon_switch_wall_patch():
    patch = {
        'Description': 'Prevent softlocks at Demon Switch Wall',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
        },
    }
    for stage_name in (
        'Abandoned Mine',
        'Cave',
    ):
        constant_key = f'Demon Switch Wall Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (8, 0x01BF),
            (9, 0x01BF),
            (10, 0x01BF),
            (11, 0x01BF),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_prevent_softlocks_at_tall_zig_zag_room_wall_patch():
    patch = {
        'Description': 'Prevent softlocks at Tall Zig Zag Room Wall',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
        },
    }
    for stage_name in (
        'Alchemy Laboratory',
        'Necromancy Laboratory',
    ):
        constant_key = f'Tall Zig Zag Room Wall Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (0, 0x05C6),
            (2, 0x05CE),
            (4, 0x05D6),
            (6, 0x05DE),
            (8, 0x05C6),
            (10, 0x05CE),
            (12, 0x05D6),
            (14, 0x05DE),
            (16, 0x05C6),
            (18, 0x05CE),
            (20, 0x05D6),
            (22, 0x05DE),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_prevent_softlocks_at_plaque_room_wall_patch():
    patch = {
        'Description': 'Prevent softlocks at Plaque Room Wall',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
            'Pokes': [],
        },
    }
    for stage_name in (
        'Underground Caverns',
    ):
        constant_key = f'Plaque Room With Breakable Wall Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (0, 0x030F),
            (1, 0x030E),
            (2, 0x0334),
            (3, 0x0766),
            (4, 0x0327),
            (5, 0x076B),
            (6, 0x0351),
            (7, 0x0323),
            (8, 0x030F),
            (9, 0x076D),
            (10, 0x0334),
            (11, 0x076E),
            (12, 0x0327),
            (13, 0x076F),
            (14, 0x0351),
            (15, 0x0770),
            (16, 0x030F),
            (17, 0x0771),
            (18, 0x0334),
            (19, 0x0772),
            (20, 0x0327),
            (21, 0x0773),
            (22, 0x0351),
            (23, 0x0774),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    for (offset, data_type, value) in (
        # NOTE(sestren): The entity responsible for the breakable wall works differently in the Inverted Castle
        # https://github.com/SestrenExsis/SOTN-Shuffler/issues/92
        # Shift the starting point left 1 tile
        (0x0480D210, 'u32', 0x3406009E), # ori a2,zero,$9E
        (0x0480D2B0, 'u32', 0x3406009E), # ori a2,zero,$9E
        # Rewrite the original location directly on the tilemap
        # TODO(sestren): Edit this like any other tilemap instead of directly overwriting
        (0x047DB702, 'u16', 0x0351),
        (0x047DB722, 'u16', 0x0327),
        (0x047DB742, 'u16', 0x0334),
        (0x047DB762, 'u16', 0x030F),
    ):
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': '{:08X}'.format(value),
        })
    result = patch
    return result

def get_prevent_softlocks_at_pendulum_room_wall_patch():
    patch = {
        'Description': 'Prevent softlocks at Pendulum Room Wall',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
        },
    }
    for stage_name in (
        'Clock Tower',
        'Reverse Clock Tower',
    ):
        constant_key = f'Pendulum Room Wall Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (0, 0x0561),
            (2, 0x0000),
            (4, 0x0000),
            (6, 0x0563),
            (8, 0x0561),
            (10, 0x0000),
            (12, 0x0000),
            (14, 0x0563),
            (16, 0x0561),
            (18, 0x0000),
            (20, 0x0000),
            (22, 0x0563),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_prevent_softlocks_at_left_gear_room_wall_patch():
    patch = {
        'Description': 'Prevent softlocks at Left Gear Room Wall',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
            'Pokes': [],
        },
    }
    for stage_name in (
        'Clock Tower',
        'Reverse Clock Tower',
    ):
        constant_key = f'Left Gear Room Wall Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (1, 0x0565),
            (3, 0x056D),
            (5, 0x0575),
            (7, 0x057D),
            (9, 0x0565),
            (11, 0x056D),
            (13, 0x0575),
            (15, 0x057D),
            (17, 0x0565),
            (19, 0x056D),
            (21, 0x0575),
            (23, 0x057D),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_normalize_jewel_sword_passageway_patch():
    patch = {
        'Description': 'Normalize Jewel Sword passageway',
        'Authors': [
            'Sestren',
        ],
        'Changes': {},
    }
    pokes = []
    # Eliminate left-most column of passage to Jewel Sword Room in Merman Room
    # TODO(sestren): Figure out how to patch the entity and array in Reverse Entrance
    for (base, context) in (
        (0x041E23E8, 'Castle Entrance, Merman Room (EntityJewelSwordDoor)'),
        # (0x047FFFFF, 'Reverse Entrance, Merman Room (EntityJewelSwordDoor)'), 
        (0x0494FC88, 'Castle Entrance Revisited, Merman Room (EntityJewelSwordDoor)'),
    ):
        for (offset, data_type, value, note) in (
            (0x0A8, 's16', 0x3F0, 'addiu a2,t0,$3F0'),
            (0x0D0, 's16', 0x006, 'slti v0,a1,$6'),
            (0x0E8, 's16', 0x3F0, 'addiu a2,t0,$3F0'),
        ):
            pokes.append((value, data_type, base + offset, [context, note]))
    for (base, context) in (
        (0x041A8AAC, 'Castle Entrance, Merman Room (rockTiles3)'),
        # (0x0471F020, 'Reverse Entrance, Merman Room (rockTiles3)'),
        (0x0491B974, 'Castle Entrance Revisited, Merman Room (rockTiles3)'),
    ):
        for (offset, data_type, value, note) in (
            # Column 0
            (0x036, 'u16', 0x030B, 'Column 0, Row 0'),
            (0x038, 'u16', 0x030E, 'Column 0, Row 1'),
            (0x03A, 'u16', 0x0000, 'Column 0, Row 2'),
            (0x03C, 'u16', 0x0000, 'Column 0, Row 3'),
            (0x03E, 'u16', 0x06BD, 'Column 0, Row 4'),
            (0x040, 'u16', 0x06BF, 'Column 0, Row 5'),
            # Column 1
            (0x042, 'u16', 0x030C, 'Column 1, Row 0'),
            (0x044, 'u16', 0x030F, 'Column 1, Row 1'),
            (0x046, 'u16', 0x0000, 'Column 1, Row 2'),
            (0x048, 'u16', 0x0000, 'Column 1, Row 3'),
            (0x04A, 'u16', 0x06BE, 'Column 1, Row 4'),
            (0x04C, 'u16', 0x06C0, 'Column 1, Row 5'),
            # Column 2
            (0x04E, 'u16', 0x054F, 'Column 2, Row 0'),
            (0x050, 'u16', 0x0000, 'Column 2, Row 1'),
            (0x052, 'u16', 0x0000, 'Column 2, Row 2'),
            (0x054, 'u16', 0x0000, 'Column 2, Row 3'),
            (0x056, 'u16', 0x06BD, 'Column 2, Row 4'),
            (0x058, 'u16', 0x06C1, 'Column 2, Row 5'),
        ):
            pokes.append((value, data_type, base + offset, [context, note]))
    for (base_fg, base_bg, context) in (
        (0x041C4638, 0x041C5238, 'Castle Entrance, Merman Room'),
        (0x049356F4, 0x049362F4, 'Castle Entrance Revisited, Merman Room'),
    ):
        for (row, col, value_fg, value_bg, note) in (
            # Column 0
            (21 + 0, 0, 0x052D, 0x034E, 'Column 0, Row 0'),
            (21 + 1, 0, 0x0532, 0x034E, 'Column 0, Row 1'),
            (21 + 2, 0, 0x0000, 0x0339, 'Column 0, Row 2'),
            (21 + 3, 0, 0x0000, 0x0350, 'Column 0, Row 3'),
            (21 + 4, 0, 0x0000, 0x032F, 'Column 0, Row 4'),
            (21 + 5, 0, 0x0320, 0x0000, 'Column 0, Row 5'),
            # Column 1
            (21 + 0, 1, 0x0535, 0x034F, 'Column 1, Row 0'),
            (21 + 1, 1, 0x0536, 0x034F, 'Column 1, Row 1'),
            (21 + 2, 1, 0x0308, 0x033A, 'Column 1, Row 2'),
            (21 + 3, 1, 0x0309, 0x0351, 'Column 1, Row 3'),
            (21 + 4, 1, 0x053E, 0x0330, 'Column 1, Row 4'),
            (21 + 5, 1, 0x053F, 0x0000, 'Column 1, Row 5'),
        ):
            tiles_per_row = 16 * 3
            offset = 2 * (tiles_per_row * row + col)
            pokes.append((value_fg, 'u16', base_fg + offset, [context, note + ', Foreground Layer']))
            pokes.append((value_bg, 'u16', base_bg + offset, [context, note + ', Background Layer']))
    for (base_fg, base_bg, context) in (
        (0x04733488, 0x04734088, 'Reverse Entrance, Merman Room'),
    ):
        for (row, col, value_fg, value_bg, note) in (
            # Column 0
            (5 + 0, 46, 0x053F, 0x0000, 'Column 0, Row 0'),
            (5 + 1, 46, 0x053E, 0x0330, 'Column 0, Row 1'),
            (5 + 2, 46, 0x0309, 0x0351, 'Column 0, Row 2'),
            (5 + 3, 46, 0x0308, 0x033A, 'Column 0, Row 3'),
            (5 + 4, 46, 0x0536, 0x034F, 'Column 0, Row 4'),
            (5 + 5, 46, 0x0535, 0x034F, 'Column 0, Row 5'),
            # Column 1
            (5 + 0, 47, 0x0320, 0x0000, 'Column 1, Row 0'),
            (5 + 1, 47, 0x0000, 0x032F, 'Column 1, Row 1'),
            (5 + 2, 47, 0x0000, 0x0350, 'Column 1, Row 2'),
            (5 + 3, 47, 0x0000, 0x0339, 'Column 1, Row 3'),
            (5 + 4, 47, 0x0532, 0x034E, 'Column 1, Row 4'),
            (5 + 5, 47, 0x052D, 0x034E, 'Column 1, Row 5'),
        ):
            tiles_per_row = 16 * 3
            offset = 2 * (tiles_per_row * row + col)
            pokes.append((value_fg, 'u16', base_fg + offset, [context, note + ', Foreground Layer']))
            pokes.append((value_bg, 'u16', base_bg + offset, [context, note + ', Background Layer']))
    patch['Changes']['Pokes'] = []
    for (value, data_type, offset, notes) in pokes:
        value_format = '{:08X}' if data_type == 'u32' else '{:04X}'
        poke = {
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': value_format.format(value),
            'Notes': []
        }
        for note in notes:
            poke['Notes'].append(note)
        patch['Changes']['Pokes'].append(poke)
    result = patch
    return result

def get_simple_patch(description, pokes):
    patch = {
        'Description': description,
        'Changes': {
            'Pokes': [],
        },
    }
    for (offset, data_type, value, note) in pokes:
        patch['Changes']['Pokes'].append(
            {
                'Gamedata Address': '{:08X}'.format(offset),
                'Data Type': data_type,
                'Value': '{:08X}'.format(value),
                'Notes':
                [
                    note,
                ]
            }
        )
    result = patch
    return result

if __name__ == '__main__':
    '''
    Some patches play nice with other patches, some don't.
    A good patcher will assemble patches and attempt to validate if they work together or not

    Usage
    python sotn_patcher.py
    '''
    for (file_name, patch) in (
        ('clock-hands-display-minutes-and-seconds', get_clock_hands_patch()),
        ('enable-debug-mode', get_simple_patch("Enables the game's hidden debug mode", [
            (0x000D9364, 'u32', 0xAC258850, 'sw a1, -$77B0(at)'), # Original instruction was sw 0, -$77B0(at)
        ])),
        ('normalize-ferryman-gate', get_simple_patch('Normalize Ferryman Gate', [
            # 0x801C5C7C - EntityFerrymanController
            # ------------------------------------------
            # Equivalent to the following C code
            # ------------------------------------------
            # offset = self->posX.i.hi + g_Tilemap.scrollX.i.hi;
            # if (self->facingLeft) {
            #     if (offset > 3040) {
            #         self->step++;
            #     }
            #     else if (offset > 2720) {
            #         g_CastleFlags[0xC2] = true;
            #     }
            # } else {
            #     if (offset < 288) {
            #         self->step++;
            #     }
            #     else if (offset < 3104) {
            #         g_CastleFlags[0xC2] = true;
            #     }
            # }
            (0x0429D47C + 0x3F8, 'u32', 0x96040014, 'lhu     a0,0x14(s0)'),   # 801C6074
            (0x0429D47C + 0x3FC, 'u32', 0x00000000, 'nop'),                   # 801C6078
            (0x0429D47C + 0x400, 'u32', 0x1080000E, 'beqz    a0,$801C60B8'),  # 801C607C
            (0x0429D47C + 0x404, 'u32', 0x00431021, 'addu    v0,v0,v1'),      # 801C6080
            (0x0429D47C + 0x408, 'u32', 0x00021400, 'sll     v0,v0,0x10'),    # 801C6084
            (0x0429D47C + 0x40C, 'u32', 0x00021C03, 'sra     v1,v0,0x10'),    # 801C6088
            (0x0429D47C + 0x410, 'u32', 0x28620BE1, 'slti    v0,v1,0xBE1'),   # 801C608C
            (0x0429D47C + 0x414, 'u32', 0x14400004, 'bnez    v0,$801C60A4'),  # 801C6090
            (0x0429D47C + 0x418, 'u32', 0x00000000, 'nop'),                   # 801C6094
            (0x0429D47C + 0x41C, 'u32', 0x9602002C, 'lhu     v0,0x2c(s0)'),   # 801C6098
            (0x0429D47C + 0x420, 'u32', 0x0807185A, 'j       $801C6168'),     # 801C609C
            (0x0429D47C + 0x424, 'u32', 0x24420001, 'addiu   v0,v0,1'),       # 801C60A0
            (0x0429D47C + 0x428, 'u32', 0x28620AA1, 'slti    v0,v1,0xaa1'),   # 801C60A4
            (0x0429D47C + 0x42C, 'u32', 0x14400030, 'bnez    v0,$801C616C'),  # 801C60A8
            (0x0429D47C + 0x430, 'u32', 0x34020001, 'li      v0,0x1'),        # 801C60AC
            (0x0429D47C + 0x434, 'u32', 0x08071839, 'j       $801C60E4'),     # 801C60B0
            (0x0429D47C + 0x438, 'u32', 0x00000000, 'nop'),                   # 801C60B4
            (0x0429D47C + 0x43C, 'u32', 0x00021400, 'sll     v0,v0,0x10'),    # 801C60B8
            (0x0429D47C + 0x440, 'u32', 0x00021C03, 'sra     v1,v0,0x10'),    # 801C60BC
            (0x0429D47C + 0x444, 'u32', 0x28620120, 'slti    v0,v1,0x120'),   # 801C60C0
            (0x0429D47C + 0x448, 'u32', 0x10400004, 'beqz    v0,$801C60D8'),  # 801C60C4
            (0x0429D47C + 0x44C, 'u32', 0x00000000, 'nop'),                   # 801C60C8
            (0x0429D47C + 0x450, 'u32', 0x9602002C, 'lhu     v0,0x2c(s0)'),   # 801C60CC
            (0x0429D47C + 0x454, 'u32', 0x0807185A, 'j       $801C6168'),     # 801C60D0
            (0x0429D47C + 0x458, 'u32', 0x24420001, 'addiu   v0,v0,1'),       # 801C60D4
            (0x0429D47C + 0x45C, 'u32', 0x28620C20, 'slti    v0,v1,0xc20'),   # 801C60D8
            (0x0429D47C + 0x460, 'u32', 0x10400023, 'beqz    v0,$801C616C'),  # 801C60DC
            (0x0429D47C + 0x464, 'u32', 0x34020001, 'li      v0,0x1'),        # 801C60E0
            (0x0429D47C + 0x468, 'u32', 0x3C018004, 'lui     at,$8004'),      # 801C60E4
            (0x0429D47C + 0x46C, 'u32', 0xA022BEAE, 'sb      v0,-$4152(at)'), # 801C60E8
            (0x0429D47C + 0x470, 'u32', 0x0807185B, 'j       $801C616C'),     # 801C60EC
            (0x0429D47C + 0x474, 'u32', 0x00000000, 'nop'),                   # 801C60F0
            (0x0429D47C + 0x478, 'u32', 0x00000000, 'nop'),                   # 801C60F4
            (0x0429D47C + 0x47C, 'u32', 0x00000000, 'nop'),                   # 801C60F8
            (0x0429D47C + 0x480, 'u32', 0x00000000, 'nop'),                   # 801C60FC
        ])),
        ('normalize-jewel-sword-passageway', get_normalize_jewel_sword_passageway_patch()),
        ('prevent-softlocks-at-demon-switch-wall', get_prevent_softlocks_at_demon_switch_wall_patch()),
        ('prevent-softlocks-at-left-gear-room-wall', get_prevent_softlocks_at_left_gear_room_wall_patch()),
        ('prevent-softlocks-at-pendulum-room-wall', get_prevent_softlocks_at_pendulum_room_wall_patch()),
        ('prevent-softlocks-at-plaque-room-wall', get_prevent_softlocks_at_plaque_room_wall_patch()),
        ('prevent-softlocks-at-snake-column-wall', get_prevent_softlocks_at_snake_column_wall_patch()),
        ('prevent-softlocks-at-tall-zig-zag-room-wall', get_prevent_softlocks_at_tall_zig_zag_room_wall_patch()),
        ('prevent-softlocks-when-meeting-death', get_prevent_softlocks_when_meeting_death_patch()),
        ('skip-maria-cutscene-in-alchemy-laboratory', get_simple_patch('Skip Maria cutscene in Alchemy Laboratory', [
            (0x049F66EC, 'u32', 0x0806E296, 'bne v0,0,$801B8A58'), # Original instruction was bne v0,0,$801B8A58
        ])),
    ):
        with open(os.path.join('build', 'patches', file_name + '.json'), 'w') as patch_file:
            json.dump(patch, patch_file, indent='    ', sort_keys=True)
    # # Option - Preserve unsaved map data
    # if changes.get('Options', {}).get('Preserve unsaved map data', 'None') != 'None':
    #     preservation_method = changes['Options']['Preserve unsaved map data']
    #     assert preservation_method in ('None', 'Revelation', 'Exploration')
    #     # 0x801B948C - LoadSaveData
    #     # ------------------------------------------
    #     # Equivalent to the following C code (for Revelation Mode)
    #     # ------------------------------------------
    #     # i = 0;
    #     # while (i < LEN(g_CastleFlags)) {
    #     #     g_CastleFlags[i] = savePtr->castleFlags[i];
    #     #     g_CastleMap[i] = ((0x55 & g_CastleMap[i]) << 1) | (0xAA & g_CastleMap[i]) | savePtr->castleMap[i];
    #     #     i++
    #     # }
    #     # while (i < LEN(g_CastleMap)) {
    #     #     g_CastleMap[i] = ((0x55 & g_CastleMap[i]) << 1) | (0xAA & g_CastleMap[i]) | savePtr->castleMap[i];
    #     #     i++;
    #     # }
    #     # ------------------------------------------
    #     revelation_ind = (preservation_method == 'Revelation')
    #     for (base, type) in (
    #         (0x000DFA70, 'A'), # SEL or DRA?
    #         (0x03AE0C8C, 'B'), # SEL or DRA?
    #     ):
    #         for (offset, value) in (
    #             (0x0180, 0x3C068007), # lui     a2,$8007          ; %hi(g_CastleMap)
    #             (0x0184, 0x24C6BB74), # addiu   a2,a2,-$448C      ; %lo(g_CastleMap)
    #             (0x0188, 0x3C028004), # lui     v0,$8004          ; %hi(g_Settings+0x108)
    #             (0x018C, 0x2442CB00), # addiu   v0,v0,-$3500      ; %lo(g_Settings+0x108)
    #             (0x0190, 0x8C430000), # lw      v1,0(v0)          
    #             (0x0194, 0x3C048004), # lui     a0,$8004          ; %hi(g_Settings+0x10c)
    #             (0x0198, 0x8C84CB04), # lw      a0,-$34FC(a0)     ; %lo(g_Settings+0x10c)
    #             (0x019C, 0x01431825), # or      v1,t2,v1          
    #             (0x01A0, 0x01642025), # or      a0,t3,a0          
    #             (0x01A4, 0xAC430000), # sw      v1,0(v0)          
    #             (0x01A8, 0x3C018004), # lui     at,$8004          ; %hi(g_Settings+0x10c)
    #             (0x01AC, 0xAC24CB04), # sw      a0,-$34FC(at)     ; %lo(g_Settings+0x10c)
    #             (0x01B0, 0x01052021), # addu    a0,t0,a1          
    #             (0x01B4, 0x908206C8), # lbu     v0,0x6c8(a0)      
    #             (0x01B8, 0x3C018004), # lui     at,$8004          ; %hi(g_CastleFlags)
    #             (0x01BC, 0x00250821), # addu    at,at,a1          
    #             (0x01C0, 0xA022BDEC), # sb      v0,-$4214(at)     ; %lo(g_CastleFlags)
    #             (0x01C4, 0x24A50001), # addiu   a1,a1,1           
    #             (0x01C8, 0x90C30000), # lbu     v1,0(a2)          
    #             (0x01CC, 0x908409C8), # lbu     a0,0x9c8(a0)      
    #             (0x01D0, 0x30620055), # andi    v0,v1,0x55        
    #             (0x01D4, 0x00021040 if revelation_ind else 0x00000000),
    #                                   # sll     v0,v0,0x1         (for Revelation)
    #                                   # nop                       (for Exploration)
    #             (0x01D8, 0x306300AA), # andi    v1,v1,0xaa        
    #             (0x01DC, 0x00431025), # or      v0,v0,v1          
    #             (0x01E0, 0x00441025), # or      v0,v0,a0          
    #             (0x01E4, 0xA0C20000), # sb      v0,0(a2)          
    #             (0x01E8, 0x28A20300), # slti    v0,a1,0x300       
    #             (0x01EC, 0x1440FFF0), # bnez    v0,154c ~>        
    #             (0x01F0, 0x24C60001), # addiu   a2,a2,1           
    #         ):
    #             result.patch_value(value, 'u32', base + offset)