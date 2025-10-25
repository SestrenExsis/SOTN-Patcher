# External libraries
import argparse
import json
import os

def reverse_tilemap_changes(tilemap_changes: dict) -> dict:
    reversed_tilemap_changes = {}
    for layer in sorted(tilemap_changes.keys()):
        reversed_tilemap_change = []
        for row_data in reversed(tilemap_changes[layer]):
            flipped_row_data = ' '.join(reversed(row_data.split(' ')))
            reversed_tilemap_change.append(flipped_row_data)
        reversed_tilemap_changes[layer] = reversed_tilemap_change
    result = reversed_tilemap_changes
    return result

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

def get_prevent_softlocks_after_defeating_scylla():
    # 801A094C RAM, 0x0552794C GAM : 0x38420001 xori v0,$1     -> 0x304200FE andi v0,$FE
    # 801A3514 RAM, 0x0552A514 GAM : 0x3042FFCF andi v0,$FFCF  -> 0x3042FFCE andi v0,$FFCE
    patch = {
        'Description': 'Prevent softlocks after defeating Scylla',
        'Authors': [
            'Mottzilla',
        ],
        'Changes': {
            'Pokes': [],
        },
    }
    for (offset, data_type, value) in (
        (0x0552794C, 'u32', 0x304200FE),
        (0x0552A514, 'u16', 0x00CE),
    ):
        value_format = '{:08X}' if data_type == 'u32' else '{:04X}'
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': value_format.format(value),
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
        # 'Logic': {
        #     'Modification - Disable clipping on screen edge of Snake Column Wall': True,
        # },
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
            'Familiar Events': [
                # NOTE(sestren): Changing the camera Y from 772 to 767 allows the Demon to "see" the switch from either side of the wall
                {
                    'Familiar Event ID': 6,
                    'Camera Y': 767,
                },
                {
                    'Familiar Event ID': 11,
                    'Camera Y': 767,
                },
            ],
        },
        # 'Logic': {
        #     'Modification - Disable clipping on screen edge of Demon Switch Wall': True,
        # }
    }
    patch['Changes']['Entity Layouts'] = [
        {
            'Update': {
                'Room': 'Cave, Crumbling Stairwells With Demon Switch',
                'Entity Layout ID': 2,
            },
            'Properties': {
                # NOTE(sestren): Changing the Y position from 977 to 972 allows the Demon to hit the switch correctly in Inverted Castle
                'Y': 972,
            },
            'Stage': 'Cave',
        },
    ]
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
        # 'Logic': {
        #     'Commands': {
        #         'Alchemy Laboratory, Tall Zig Zag Room': {
        #             'Action - Break Wall': {
        #                 'Requirements': {
        #                     'Secret Wall - Default': {
        #                         'Section': 'Secret Wall',
        #                         'Status - Breakable Wall in Tall Zig Zag Room Broken': False,
        #                         'Modification - Disable clipping on screen edge of Tall Zig Zag Room Wall': True,
        #                     },
        #                 },
        #             },
        #         },
        #     },
        #     'State': {
        #         'Modification - Disable clipping on screen edge of Tall Zig Zag Room Wall': True,
        #     },
        # },
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
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '052D 0535 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0532 0536 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0000 0308 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0000 0309 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0000 053E .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0320 053F .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '034E 034F .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '034E 034F .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0339 033A .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0350 0351 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '032F 0330 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '0000 0000 .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Jewel Sword passageway',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Merman Room',
                    'Layer': 'Foreground',
                    'Top': 16,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Merman Room',
                    'Layer': 'Background',
                    'Top': 16,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Merman Room',
                    'Layer': 'Foreground',
                    'Top': 16,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Merman Room',
                    'Layer': 'Background',
                    'Top': 16,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Entrance',
                    'Room': 'Reverse Entrance, Merman Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 32,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Entrance',
                    'Room': 'Reverse Entrance, Merman Room',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 32,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    patch['Changes']['Constants'] = {}
    for stage_name in (
        'Castle Entrance',
        'Castle Entrance Revisited',
    ):
        constant_key = f'Breakable Wall in Merman Room ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            # Column 0
            (27, 0x030B),
            (28, 0x030E),
            (29, 0x0000),
            (30, 0x0000),
            (31, 0x06BD),
            (32, 0x06BF),
            # Column 1
            (33, 0x030C),
            (34, 0x030F),
            (35, 0x0000),
            (36, 0x0000),
            (37, 0x06BE),
            (38, 0x06C0),
            # Column 2
            (39, 0x054F),
            (40, 0x0000),
            (41, 0x0000),
            (42, 0x0000),
            (43, 0x06BD),
            (44, 0x06C1),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
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

def get_normalize_tall_stairwell_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... 0234 0235 0000 .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... 0177 011B 0239 023A .... .... .... .... 0248 024A .... .... .... ....',
            '.... .... .... 017B 0A7F 0164 .... .... .... 0155 0155 0123 .... .... .... ....',
            '.... .... .... 01A5 01A3 01A4 016D 016D .... 0183 01A8 01A9 .... .... .... ....',
            '.... .... .... .... 01A1 010E 0155 0155 0164 0164 0110 01A7 .... .... .... ....',
            '.... .... .... .... 0001 0001 0000 0000 0000 0000 0001 0001 .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Tall Stairwell, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Tall Stairwell': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Tall Stairwell',
                    'Layer': 'Foreground',
                    'Top': 138,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Tall Stairwell',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_ice_floe_room_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... 0001 0000 .... .... 0000 0001 .... .... .... .... ....',
            '.... .... .... .... .... 03B0 0000 .... .... 0000 03B5 .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0183 .... .... 0146 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Ice Floe Room, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Ice Floe Room': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Ice Floe Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 128,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Ice Floe Room',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 128,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Ice Floe Room',
                    'Layer': 'Foreground',
                    'Top': 30,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Ice Floe Room',
                    'Layer': 'Background',
                    'Top': 30,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_long_drop_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... 01A5 01A1 01A4 .... .... .... .... .... .... .... 01A8 01A9 01AA ....',
            '.... .... 0180 01A5 01A3 01A4 .... .... .... .... 01A8 01A9 01A7 01AA 0180 ....',
            '.... .... .... 0180 01A1 010E .... .... .... .... 0110 01A7 01AA 0180 .... ....',
            '.... .... .... 0180 0181 0182 .... .... .... .... 019F 01A0 0180 0180 .... ....',
            '.... .... .... 0180 01A1 01A2 .... .... .... .... 01A6 01A7 0180 0180 .... ....',
            '.... .... .... .... .... 0001 .... .... .... .... 0001 0001 .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Long Drop, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Long Drop': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Long Drop',
                    'Layer': 'Foreground',
                    'Top': 170,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Long Drop',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_exit_to_castle_entrance():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... .... .... .... 0000 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... 0000 038C .... .... .... ....',
            '.... .... .... 03BE 0000 .... .... .... 0000 0000 0386 03C8 .... .... .... ....',
            '.... .... 039A 03BF 0391 0392 .... .... 0000 0000 039C 03D1 .... .... .... ....',
            '.... .... 039F 037D 0393 0A80 0ABC .... 0000 0000 03ED 0180 .... .... .... ....',
            '.... .... .... .... 0001 0001 0000 .... 0000 0000 0001 0001 .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... 03FC .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 03FD 03FF 0000 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 040F 0402 0569 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 03F8 0408 0A6B .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 03FC 03FA 03FC .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 03FD 03FF 0A6D .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 040F 0402 0571 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 03F8 0408 06DB .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 03FC 03FA 0000 .... .... .... ....',
            '.... .... .... .... .... .... 0400 03FD 03FE 0A6C 0000 0000 .... .... .... ....',
            '.... .... .... .... .... .... 0564 040F .... 0573 0000 0000 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize UC-CE Exit, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Exit to Castle Entrance': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Exit to Castle Entrance',
                    'Layer': 'Foreground',
                    'Top': 10,
                    'Left': 16,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Exit to Castle Entrance',
                    'Layer': 'Background',
                    'Top': 4,
                    'Left': 16,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Exit to Castle Entrance',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Exit to Castle Entrance',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_left_ferryman_route_top_passage():
    tilemaps = {
        'Foreground': [
            ".... .... .... .... 0001 0001 .... .... 0000 0000 .... .... .... .... .... ....",
            ".... .... 03AB 0180 03AB 03CF 0000 0000 0000 0000 .... .... .... .... .... ....",
            ".... .... 07E2 036F 07E2 03F4 0000 0000 0000 03BA .... .... .... .... .... ....",
            ".... .... 0375 0373 0375 03F5 .... .... 0000 0000 .... .... .... .... .... ....",
        ],
        'Background': [
            ".... .... .... .... .... .... .... 0000 0000 0000 .... .... .... .... .... ....",
            ".... .... .... .... .... .... .... 06E5 057E 0000 .... .... .... .... .... ....",
            ".... .... .... .... .... .... .... 06DD 057E 0512 .... .... .... .... .... ....",
            ".... .... .... .... .... .... .... 06E3 05B5 05B1 .... .... .... .... .... ....",
            ".... .... .... .... .... .... .... 06E4 05B1 057E .... .... .... .... .... ....",
            ".... .... .... .... .... .... .... 06E5 057E 05B5 .... .... .... .... .... ....",
            ".... .... .... .... .... .... .... .... 05B5 05B7 .... .... .... .... .... ....",
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Left Ferryman Route, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Left Ferryman Route': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Left Ferryman Route',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 128,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Left Ferryman Route',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 128,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Left Ferryman Route',
                    'Layer': 'Foreground',
                    'Top': 28,
                    'Left': 64,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Left Ferryman Route',
                    'Layer': 'Background',
                    'Top': 25,
                    'Left': 64,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_hidden_crystal_entrance_top_passage():
    tilemaps = {
        'Foreground': [
            '.... ..... .... .... .... 0001 .... .... .... .... 0001 0001 .... .... .... ....',
            '.... ..... .... 0181 0181 0182 .... .... .... .... 019F 01A0 0180 0180 .... ....',
            '.... ..... .... .... 0180 0542 .... .... .... .... 019F 01A7 0180 0180 .... ....',
            '.... ..... .... .... 0180 0A74 .... .... .... .... 03BB 0397 0180 0180 .... ....',
            '.... ..... .... 0180 037B 0372 .... .... .... .... 0A73 03A2 0180 0180 .... ....',
            '.... ..... .... 0A75 0372 .... .... .... .... .... 037F 03BC 0370 03BC .... ....',
            '.... ..... .... 0375 .... .... .... .... .... .... .... 03BD 0374 03BD .... ....',
        ]
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Hidden Crystal Entrance, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Hidden Crystal Entrance': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######'
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Hidden Crystal Entrance',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Hidden Crystal Entrance',
                    'Layer': 'Foreground',
                    'Top': 41,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_secret_bookcase_rooms():
    patch = {
        'Description': 'Normalize Secret Bookcase rooms',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Long Library, Holy Rod Room': {
                    'Nodes': {
                        'Left Passage': {
                            'Type': '######....######'
                        },
                    },
                },
                'Long Library, Secret Bookcase Room': {
                    'Nodes': {
                        'Right Passage': {
                            'Type': '######....######'
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Long Library',
                    'Room': 'Long Library, Holy Rod Room',
                    'Layer': 'Foreground',
                    'Top': 3,
                    'Left': 0,
                    'Tiles': [
                        '028C 028D 028E',
                        '0294 028C 028E',
                        '029F 029E 029B',
                        '0339 0339 035E',
                        '.... .... ....',
                        '.... .... ....',
                        '.... .... ....',
                        '0285 0284 028B',
                        '028D 028C 028E',
                    ],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Long Library',
                    'Room': 'Long Library, Secret Bookcase Room',
                    'Layer': 'Foreground',
                    'Top': 4,
                    'Left': 15,
                    'Tiles': [
                        '02A4',
                        '02A3',
                        '....',
                        '....',
                        '....',
                        '....',
                        '0451',
                        '02A9',
                    ],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Forbidden Library',
                    'Room': 'Forbidden Library, Holy Rod Room',
                    'Layer': 'Foreground',
                    'Top': 4,
                    'Left': 13,
                    'Tiles': [
                        '028E 028C 028D',
                        '028B 0284 0285',
                        '.... .... ....',
                        '.... .... ....',
                        '.... .... ....',
                        '035E 0339 0339',
                        '029B 029E 029F',
                        '028E 0296 0297',
                        '028E 028D 028C',
                    ],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Forbidden Library',
                    'Room': 'Forbidden Library, Secret Bookcase Room',
                    'Layer': 'Foreground',
                    'Top': 4,
                    'Left': 0,
                    'Tiles': [
                        '02A9',
                        '0451',
                        '....',
                        '....',
                        '....',
                        '....',
                        '02A3',
                        '02A4',
                    ],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_room_id_09_bottom_passage():
    tilemaps = {
        'Foreground': [
            '0023 00E1 0328 010A 07C1 07C2 07B7 07C0 .... .... .... .... .... .... .... ....',
            '0329 032A 00E4 032B 07BF 07C5 07BF 07C0 .... .... .... .... .... .... .... ....',
            '032C 032D 032A 00E4 032E 07C0 07BF 07C0 .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 0090 0065 0066 0091 0067 0068 0023 0023 0023 .... ....',
            '.... .... .... .... .... .... 07BF 07C5 07C1 07AD 003B 000C 000C .... .... ....',
            '.... .... .... .... .... .... 0000 0000 0000 .... 0001 0001 0001 .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Room ID 09, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Room ID 09': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Room ID 09',
                    'Layer': 'Foreground',
                    'Top': 10,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Room ID 09',
                    'Layer': 'Foreground',
                    'Top': 00,
                    'Left': 16,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_room_id_10_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 0000 0000 0000 .... 0001 0001 0001 .... .... ....',
            '.... .... .... .... .... 0053 0011 0014 002E .... 003B 000C 000B .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... 0033 0034 0035 0346 0007 0008',
            '.... .... .... .... .... .... .... .... .... .... 003B 003C 0028 0348 000D 000E',
            '.... .... .... .... .... .... .... .... 01E7 01E8 01E8 01E8 .... .... .... ....',
            '.... 0023 00E1 01DC 007B 07AF 007B .... .... .... .... .... .... .... .... ....',
            '.... .... 00E7 00E4 00E5 0000 0000 0000 .... .... .... .... .... .... .... ....',
            '.... .... .... 00E7 00E4 00E5 0000 0000 0000 .... .... .... .... .... .... ....',
            '.... .... .... .... 00E7 00E4 00E5 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... 00E7 00E4 00E5 0000 0000 0000 .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... 0319 .... 0331 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 0319 0319 031A .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0319 0319 0314 .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 0319 0319 0313 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Room ID 10, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Room ID 10': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Room ID 10',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Room ID 10',
                    'Layer': 'Background',
                    'Top': 6,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Room ID 10',
                    'Layer': 'Foreground',
                    'Top': 6,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Room ID 10',
                    'Layer': 'Background',
                    'Top': 6,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_dk_bridge_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... 039A 03BF 03CA 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 .... .... .... .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... 04E1 .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize DK Bridge, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, DK Bridge': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, DK Bridge',
                    'Layer': 'Foreground',
                    'Top': 14,
                    'Left': 48,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, DK Bridge',
                    'Layer': 'Background',
                    'Top': 14,
                    'Left': 48,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, DK Bridge',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, DK Bridge',
                    'Layer': 'Background',
                    'Top': 1,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_exit_to_abandoned_mine_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 03CF 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... 037A 03E7 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... 037D 037E 0383 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... 03AB 0A74 038A 03BA .... .... .... .... .... .... .... ....',
            '.... .... .... 0370 03AC 0372 0AD0 .... .... .... .... .... .... .... .... ....',
            '.... .... .... 0374 0375 0000 .... .... .... .... .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0400 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 040E .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 03F7 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 03FB .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 03FF .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize UC-AM, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Exit to Abandoned Mine': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Exit to Abandoned Mine',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Exit to Abandoned Mine',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Exit to Abandoned Mine',
                    'Layer': 'Foreground',
                    'Top': 9,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Exit to Abandoned Mine',
                    'Layer': 'Background',
                    'Top': 9,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_small_stairwell_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 0000 0000 0000 0000 0001 0001 0001 .... .... ....',
            '.... .... .... .... .... 0090 0065 0066 0066 0066 0099 0023 0023 0023 .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 0337 0338 0339 0000 0000 .... .... ....',
            '.... .... .... .... .... .... .... .... 033A 033B 033C 0000 0000 .... .... ....',
            '.... .... .... .... .... .... .... .... 033D 033E 033F 0000 0000 .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... 031C .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... 0320 .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Small Stairwell, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Small Stairwell': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Small Stairwell',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Small Stairwell',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Small Stairwell',
                    'Layer': 'Foreground',
                    'Top': 26,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Small Stairwell',
                    'Layer': 'Background',
                    'Top': 26,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_plaque_room_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... 0023 00E1 0328 001E 001F 0020 0021 0036 003E 003F 0040 01BE .... .... ....',
            '000F 0329 032A 00E4 032B 0019 001A 001B 0036 0037 0038 0039 0101 .... .... ....',
            '0016 032C 032D 032A 00E4 032E 0020 0014 002E 002F 0030 0031 0101 .... .... ....',
            '.... .... .... .... .... 0090 0065 0066 0066 0066 0099 0023 0023 .... .... ....',
            '.... .... .... .... .... .... 0000 0000 0000 0000 0001 0001 0001 .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Plaque Room, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Plaque Room With Life Max-Up': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Plaque Room With Life Max-Up',
                    'Layer': 'Foreground',
                    'Top': 11,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Plaque Room With Life Max-Up',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
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

def get_normalize_underground_caverns_hidden_crystal_entrance_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... 0549 0000 .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... 0A84 0A81 059D .... .... .... 0557 038C .... .... .... ....',
            '.... .... .... .... 0551 0552 05F0 05F1 0739 073C 055A 038D .... .... .... ....',
            '.... .... .... .... 06F8 06FA 060C 060D 073A 0591 055D 0180 .... .... .... ....',
            '.... .... .... .... 0543 06F9 0000 0000 0000 0000 0180 .... .... .... .... ....',
            '.... .... .... .... 0001 0001 0000 0000 0000 0000 .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 03FD 03FE 03FF .... .... .... .... .... ....',
            '.... .... .... .... .... .... 040E 040F 0401 0402 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Hidden Crystal Entrance, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Hidden Crystal Entrance': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Hidden Crystal Entrance',
                    'Layer': 'Foreground',
                    'Top': 42,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Hidden Crystal Entrance',
                    'Layer': 'Background',
                    'Top': 42,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Hidden Crystal Entrance',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Hidden Crystal Entrance',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    patch['Changes']['Constants'] = {}
    for stage_name in (
        'Underground Caverns',
        'Reverse Caverns',
    ):
        constant_key = f'Crystal Floor Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in enumerate((
            # Phase 0
            0x05F0, 0x054D, 0x054E,
            0x060C, 0x0000, 0x0000,
            # Phase 1
            0x05F0, 0x0740, 0x0748,
            0x060C, 0x0000, 0x0000,
            # Phase 2
            0x05F0, 0x074D, 0x074E,
            0x060C, 0x0000, 0x0000,
            # Phase 3
            0x05F0, 0x0000, 0x0000,
            0x060C, 0x0000, 0x0000,
        )):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    patch['Changes']['Pokes'] = []
    for (offset, data_type, value) in (
        (0x0429FF64, 's16', 0x02C6),
        (0x042A006C, 's16', 0x02C6),
        (0x042A0080, 's16', 0x0003), # In Underground Caverns, only require 1 hit to destroy the floor
        (0x0480CF1C, 's16', 0x0039),
        (0x0480D02C, 's16', 0x0039),
    ):
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': '{:08X}'.format(value),
        })
    patch['Changes']['Entity Layouts'] = [
        {
            'Add To': {
                'Room': 'Underground Caverns, Hidden Crystal Entrance',
            },
            'Delete From': {
                'Entity Layout ID': 0,
                'Room': 'Underground Caverns, Hidden Crystal Entrance',
            },
            'Properties': {
                'X': 128,
                'Y': 720,
            },
            'Stage': 'Underground Caverns',
        },
        {
            'Add To': {
                'Room': 'Reverse Caverns, Hidden Crystal Entrance',
            },
            'Delete From': {
                'Entity Layout ID': 5,
                'Room': 'Reverse Caverns, Hidden Crystal Entrance',
            },
            'Properties': {
                'X': 128,
                'Y': 48,
            },
            'Stage': 'Reverse Caverns',
        },
    ]
    result = patch
    return result

def get_normalize_alchemy_laboratory_entryway_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... .... 0000 004C 0050 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 0031 0032 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 0004 0005 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0676 000B 000C .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 0011 0012 .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Alchemy Lab Entryway, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Alchemy Laboratory, Entryway': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Alchemy Laboratory',
                    'Room': 'Alchemy Laboratory, Entryway',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 16,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Necromancy Laboratory',
                    'Room': 'Necromancy Laboratory, Entryway',
                    'Layer': 'Foreground',
                    'Top': 11,
                    'Left': 16,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_alchemy_laboratory_glass_vats_bottom_passage():
    tilemaps = {
        'Foreground': [
              "0034 0020 0033 0034 004C 0050 0031 0032 0005 0006 0001 0002 0003 0004 0005 0006 0001 0002 0003 0004 0005 0006 0001 0002 0003 0004 0005 0006 004C 0050 0033 0034",
              "0024 0025 0023 0024 0031 0032 0004 0005 000C 0007 0008 0009 000A 000B 000C 0007 0008 0009 000A 000B 000C 0007 0008 0009 000A 001D 0014 0007 0031 0032 0023 0024",
              "0029 002A 0028 0029 0004 0005 0026 0027 0012 000D 0019 000F 0010 0011 0012 000D 000E 000F 0010 0011 0012 000D 0019 001F 0010 0016 0017 0018 0004 0005 0028 0029",
              "0005 0006 0004 0005 0026 0027 0011 0012 0126 0127 0288 0289 028A 028B 028A 028A 028A 028A 028A 012A 0122 0123 0124 0125 0126 0127 0288 0289 0026 0027 0004 0005",
              "0027 002B 0026 0027 0011 0012 0000 01DC 06A0 06A4 0298 0299 01D4 0128 00DA 028A 028A 028A 012B 0147 014C 01D5 01D8 01DC 06A0 06A4 0298 0299 0011 0012 0026 0027",
              "0052 0053 0051 0052 0000 059C 059D 0000 0000 0000 0296 0297 029F 02A0 028C 028D 028E 028A 020E 0210 0236 0000 0000 0000 0000 0000 0296 0297 05AD 05AE 0011 0012",
              "0034 0020 0033 0034 05A3 05A4 05A5 05A6 0000 0000 028F 0290 0291 0292 0293 00D8 00D9 00DB 029D 029E 0105 0000 0000 0000 0000 0000 028F 0290 05AA 0000 059C 059D",
              "0024 0025 0023 0024 05AB 05AC 05AD 05AE 0000 0000 0000 0000 00DC 0689 068A 068D 068E 0287 0100 0000 0000 0000 0101 0294 0295 0000 0000 0000 059E 05A3 05A4 05A5",
              "0029 002A 0028 0029 0000 05A9 05AA 0000 0000 0000 0000 0000 029A 029B 0691 0692 0695 0696 0155 0000 0000 0156 0159 015E 0162 0000 06A8 0000 05A7 05AB 05AC 05AD",
              "0005 0006 0004 0005 059D 0000 0000 0000 0000 0000 0000 0000 0108 0109 010A 010B 010C 010D 016A 0000 0000 0000 0000 0183 0184 0187 06A7 0000 013F 0000 05A9 05AA",
              "0027 002B 0026 0027 05A5 05A6 0000 0000 0000 0000 0000 05B0 010E 010F 0110 0111 0112 0113 0189 018A 0000 0000 018B 018C 01A5 01B3 0000 059E 003F 0038 003B 003F",
              "0052 0053 0051 0052 05AD 05AE 0000 0000 0000 0000 0000 05B1 0114 0115 0116 0117 0118 0119 01B4 01CA 0000 0000 01CB 01CC 01CD 0000 0000 05A7 0023 0024 0025 0023",
              "0034 0020 0033 0034 05AA 0000 0000 0000 0000 0000 011A 011B 011C 011D 011E 011F 0120 0121 01CE 01CF 01D0 0000 01D1 01D2 01D3 0000 003F 0038 0028 0029 002A 0028",
              "0024 0025 0023 0024 0037 0045 0000 0000 0000 0000 0048 0043 003E 0044 003A 0039 0037 0043 003E 0044 003A 0039 003C 003D 003E 003F 0023 0024 0004 0005 0006 0004",
              "0029 002A 0028 0029 0040 0046 0000 0000 0000 0000 0049 0041 0042 0023 0024 0025 0040 0041 0042 0023 0024 0025 0040 0041 0042 0023 0028 0029 0026 0027 002B 0026",
              "0005 0006 0004 0005 002E 0047 0000 0000 0000 0000 004A 002F 002D 0028 0029 002A 002E 002F 002D 0028 0029 002A 002E 002F 002D 0028 004C 0050 0051 0052 0053 0051"
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Glass Vats, Left-Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Alchemy Laboratory, Glass Vats': {
                    'Nodes': {
                        'Left-Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Alchemy Laboratory',
                    'Room': 'Alchemy Laboratory, Glass Vats',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Necromancy Laboratory',
                    'Room': 'Necromancy Laboratory, Glass Vats',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    patch['Changes']['Entity Layouts'] = [
        {
            'Update': {
                'Room': 'Alchemy Laboratory, Glass Vats',
                'Entity Layout ID': 0,
            },
            'Properties': {
                'X': 192,
            },
            'Stage': 'Alchemy Laboratory',
        },
        {
            'Update': {
                'Room': 'Alchemy Laboratory, Glass Vats',
                'Entity Layout ID': 1,
            },
            'Properties': {
                'X': 240,
            },
            'Stage': 'Alchemy Laboratory',
        },
        {
            'Update': {
                'Room': 'Alchemy Laboratory, Glass Vats',
                'Entity Layout ID': 2,
            },
            'Properties': {
                'X': 288,
            },
            'Stage': 'Alchemy Laboratory',
        },
        {
            'Update': {
                'Room': 'Alchemy Laboratory, Glass Vats',
                'Entity Layout ID': 3,
            },
            'Properties': {
                'X': 336,
            },
            'Stage': 'Alchemy Laboratory',
        },
        {
            'Update': {
                'Room': 'Alchemy Laboratory, Glass Vats',
                'Entity Layout ID': 4,
            },
            'Properties': {
                'X': 384,
            },
            'Stage': 'Alchemy Laboratory',
        },
    ]
    result = patch
    return result

def get_normalize_alchemy_laboratory_red_skeleton_lift_room_top_passage():
    tilemaps = {
        'Foreground': [
            ".... 0020 0033 0034 0001 0013 0000 0000 0000 0000 001B 0002 0006 0001 0002 0003 0001 0002 0003 0004 0005 0006 0001 0002 0003 0004 0005 0006 0001 0002 0003 0004 0005 0006 0004 0005 0006 0033 0034 0020 0033 0034 0020 0033 0034 0020 0033 0034",
            ".... 0025 0023 0024 0008 0046 0000 0000 0000 0000 001C 0009 0007 0008 0009 000A 0008 0009 000A 000B 000C 0007 0008 0009 000A 001D 0014 0007 0008 0009 000A 000B 000C 0007 000B 000C 0007 0023 0024 0025 0023 0024 0025 0023 0024 0025 0023 0024",
            ".... 002A 0028 0029 000E 001A 0000 0000 0000 0000 001E 001F 000D 0019 001F 0010 000E 000F 0010 0011 0012 000D 0019 001F 0010 0016 0017 0018 000E 000F 0010 0011 0012 000D 0011 0012 000D 0028 0029 002A 0028 0029 002A 0028 0029 002A 0028 0029",
            "0006 0004 0005 0000 0000 0598 0126 0127 0288 0289 028A 028B 028A 028A 028A 028A 028A 012A 0122 0123 0124 0125 0126 0127 0288 0289 028A 028B 028A 028A 028A 028A 028A 012A 0122 0123 0124 0004 0005 0006 0004 0005 0006 0004 0005 0006 0004 0005",
            "002B 0026 0027 0000 0000 059A 06A0 06A4 0298 0299 01D4 0128 00DA 028A 028A 028A 012B 0147 014C 01D5 01D8 01DC 06A0 06A4 0298 0299 01D4 0128 00DA 028A 028A 028A 012B 0147 014C 01D5 01D8 0026 0027 002B 0026 0027 002B 0026 0027 002B 0026 0027",
            "0018 0011 0012 0000 0000 0000 0000 0000 0296 0297 029F 02A0 028C 028D 028E 028A 020E 0210 0236 0000 0000 0000 0000 0000 0296 0297 029F 02A0 028C 028D 028E 028A 020E 0210 0236 0000 0000 0011 0012 0018 0011 0012 0018 0011 0012 0018 0011 0012",
            "0000 059C 05AD 05AE 0000 0000 0000 0000 028F 0290 0291 0292 0293 00D8 00D9 00DB 029D 029E 0105 0000 0000 0000 0000 0000 028F 0290 0291 0292 0293 00D8 00D9 00DB 029D 029E 0105 0000 0000 0000 004A 0047 0286 029C 0000 0172 0000 0000 0000 0000",
            "05A3 05A4 05AA 0000 0000 0000 0000 0000 0000 0000 00DC 0689 068A 068D 068E 0287 0100 0000 0000 0000 0101 0294 0295 0000 0000 0000 00DC 0689 068A 068D 068E 0287 0100 0000 0000 0000 0000 0000 001B 0013 0000 0000 0000 05A7 0000 0000 0000 0000",
            "05AB 05AC 059D 0000 0000 0000 0000 0000 0000 0000 029A 029B 0691 0692 0695 0696 0155 0000 0000 0156 0159 015E 0162 0000 06A8 0000 029A 029B 0691 0692 0695 0696 0155 0000 0000 0000 0000 0000 0049 0046 0000 0000 0000 059B 0000 059E 0000 0000",
            "0000 05A9 05A5 05A6 0000 0000 059E 0000 0000 0000 0108 0109 010A 010B 010C 010D 016A 0000 0000 0000 0000 0183 0184 0187 06A7 0000 0108 0109 010A 010B 010C 010D 016A 0000 0000 0000 0000 0000 004A 0047 0000 0000 0000 0000 0000 05A7 0000 0000",
            "0038 004B 003F 0038 0000 0000 05A7 0000 0000 05B0 010E 010F 0110 0111 0112 0113 0189 018A 0000 0000 018B 018C 01A5 01B3 0000 05B0 010E 010F 0110 0111 0112 0113 0189 018A 0000 0000 0000 0000 001B 0013 0000 0000 0048 003D 003E 003F 0038 0039",
            "0024 0025 0023 0024 0678 0679 013F 0000 0000 05B1 0114 0115 0116 0117 0118 0119 01B4 01CA 0000 0000 01CB 01CC 01CD 0000 0000 05B1 0114 0115 0116 0117 0118 0119 01B4 01CA 0000 0000 0000 0000 004D 0046 0000 0000 004D 0106 0107 0023 0024 0025",
            "0029 002A 0028 0029 059B 0000 013F 0000 011A 011B 011C 011D 011E 011F 0120 0121 01CE 01CF 01D0 0000 01D1 01D2 01D3 0000 011A 011B 011C 011D 011E 011F 0120 0121 01CE 01CF 01D0 0000 0000 0000 001E 001A 0000 0000 001E 001F 0010 0028 0029 002A"
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Red Skeleton Lift Room, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Alchemy Laboratory, Red Skeleton Lift Room': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Alchemy Laboratory',
                    'Room': 'Alchemy Laboratory, Red Skeleton Lift Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Necromancy Laboratory',
                    'Room': 'Necromancy Laboratory, Red Skeleton Lift Room',
                    'Layer': 'Foreground',
                    'Top': 19,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_alchemy_laboratory_red_skeleton_lift_room_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... .... 0000 0048 0045 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 0049 0046 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 0048 003D .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 004D 0041 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 004A 002F .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 001B 0002 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 001C 0009 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0000 001E 001F .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Red Skeleton Lift Room, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Alchemy Laboratory, Red Skeleton Lift Room': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Alchemy Laboratory',
                    'Room': 'Alchemy Laboratory, Red Skeleton Lift Room',
                    'Layer': 'Foreground',
                    'Top': 24,
                    'Left': 32,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Necromancy Laboratory',
                    'Room': 'Necromancy Laboratory, Red Skeleton Lift Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_underground_caverns_crystal_bend_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... 0001 0001 0000 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... 0180 0589 058A 058A 0000 0000 0000 0000 0588 .... .... .... .... ....',
            '.... .... 0180 0180 058D 0A7A 0000 0000 0000 0000 058B 058C .... .... .... ....',
            '.... .... 0180 0180 058F 0590 0000 0000 03BA 03BA 0A79 058E .... .... .... ....',
            '.... .... 0180 058F 0590 .... 0000 0000 0000 0000 05A0 05A1 .... .... .... ....',
            '.... .... 058F 0590 .... .... .... 0000 0000 0000 0588 .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... 0000 0000 .... .... .... 03BA 03BA .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 05BE 05B1 05B2 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 0581 057E 057F .... .... .... .... .... ....',
            '.... .... .... .... .... 0623 0582 05B9 05BB 05BC .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 05BA 05B7 05B8 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 05B1 05B2 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 057E 057F .... .... .... .... .... ....',
            '.... .... .... 05B9 05B5 .... .... .... 05BB 05BC .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Crystal Bend, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Underground Caverns, Crystal Bend': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Crystal Bend',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Underground Caverns',
                    'Room': 'Underground Caverns, Crystal Bend',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Crystal Bend',
                    'Layer': 'Foreground',
                    'Top': 24,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Reverse Caverns',
                    'Room': 'Reverse Caverns, Crystal Bend',
                    'Layer': 'Background',
                    'Top': 24,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_alchemy_laboratory_tall_zig_zag_room_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 003B 05B8 05B8 003B .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0271 05B9 05B9 027F .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0272 0230 0256 0280 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 06A9 06A1 06B6 06B7 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Tall Zig Zag Room, Bottom Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Alchemy Laboratory, Tall Zig Zag Room': {
                    'Nodes': {
                        'Lower Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Alchemy Laboratory',
                    'Room': 'Alchemy Laboratory, Tall Zig Zag Room',
                    'Layer': 'Foreground',
                    'Top': 44,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Necromancy Laboratory',
                    'Room': 'Necromancy Laboratory, Tall Zig Zag Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    patch['Changes']['Pokes'] = []
    for (offset, data_type, value) in (
        (0x049EFFD8, 's16', 0x02C7), # Alchemy Laboratory - 0x02E7 -> 0x02C7
        (0x049F008C, 's16', 0x02C7), # Alchemy Laboratory - 0x02E7 -> 0x02C7
        (0x049F00A0, 's16', 0x0003), # Alchemy Laboratory - only require 1 hit to destroy the floor
        (0x04DACB0C, 's16', 0x0038), # Necromancy Laboratory - 0x0018 -> 0x02C7
        (0x04DACBCC, 's16', 0x0038), # Necromancy Laboratory - 0x0018 -> 0x02C7
    ):
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': '{:08X}'.format(value),
        })
    patch['Changes']['Entity Layouts'] = [
        {
            'Update': {
                'Room': 'Alchemy Laboratory, Tall Zig Zag Room',
                'Entity Layout ID': 4,
            },
            'Properties': {
                'X': 128,
                'Y': 720,
            },
            'Stage': 'Alchemy Laboratory',
        },
        {
            'Update': {
                'Room': 'Necromancy Laboratory, Tall Zig Zag Room',
                'Entity Layout ID': 5,
            },
            'Properties': {
                'X': 128,
                'Y': 48,
            },
            'Stage': 'Necromancy Laboratory',
        },
    ]
    patch['Changes']['Constants'] = {}
    for stage_name in (
        'Alchemy Laboratory',
        'Necromancy Laboratory',
    ):
        constant_key = f'Laboratory Floor Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in (
            (12, 0x0224),
            (13, 0x024C),
            (14, 0x022A),
            (15, 0x0250),
        ):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_normalize_alchemy_laboratory_secret_life_max_up_room_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 026C .... .... 0276 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 026F .... .... 027B 0011 0012 .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 0249 024A .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... 024D 01BC .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Secret Life Max-Up Room, Top Passage',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Alchemy Laboratory, Secret Life Max-Up Room': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Alchemy Laboratory',
                    'Room': 'Alchemy Laboratory, Secret Life Max-Up Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Necromancy Laboratory',
                    'Room': 'Necromancy Laboratory, Secret Life Max-Up Room',
                    'Layer': 'Foreground',
                    'Top': 28,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_marble_gallery_stopwatch_room_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 0597 0597 0597 0597 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
        ],
    }
    patch = {
        'Description': 'Normalize Marble Gallery Stopwatch Room',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Marble Gallery, Stopwatch Room': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Stopwatch Room',
                    'Layer': 'Foreground',
                    'Top': 12,
                    'Left': 16,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Stopwatch Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 16,
                    'Tiles': [
                        '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
                        '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
                        '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
                        '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
                    ],
                },
            ],
        },
    }
    patch['Changes']['Pokes'] = []
    for (offset, data_type, value) in (
        (0x03FCE06C, 's16', 0x0001), # Marble Gallery - 0x0003 -> 0x0001
    ):
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': '{:08X}'.format(value),
        })
    result = patch
    return result

def get_normalize_marble_gallery_beneath_left_trapdoor_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 0000 .... .... .... .... .... .... .... ....',
        ],
    }
    patch = {
        'Description': 'Normalize Marble Gallery Stopwatch Room',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Marble Gallery, Beneath Left Trapdoor': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Beneath Left Trapdoor',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_marble_gallery_beneath_right_trapdoor_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... 02D5 02D5 .... .... 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... 02D6 02D6 0000 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... 02EE 02EE 032F .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... 02F0 02F0 .... .... .... .... .... .... .... .... .... ....',
            '.... .... 030B 02E3 02E4 02E5 02E6 02E7 .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 036E 036E .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 0335 0335 0362 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... 0335 0335 036B .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Marble Gallery Beneath Right Trapdoor',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Marble Gallery, Beneath Right Trapdoor': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Beneath Right Trapdoor',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Beneath Right Trapdoor',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Beneath Right Trapdoor',
                    'Layer': 'Foreground',
                    'Top': 9,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Beneath Right Trapdoor',
                    'Layer': 'Background',
                    'Top': 9,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    patch['Changes']['Object Layouts'] = [
        {
            'Stage': 'Marble Gallery',
            'Room': 'Marble Gallery, Beneath Right Trapdoor',
            'Object Layout ID': 1,
            'Properties': {
                'X': 129 + 32,
                'Y': 8,
            },
            'Notes': [
                "Marble Gallery's Entity Layout treatment is buggy, so this is being handled the old Object Layout way",
            ],
        },
        # {
        #     'Stage': 'Black Marble Gallery',
        #     'Room': 'Black Marble Gallery, Beneath Right Trapdoor',
        #     'Object Layout ID': 99,
        #     'Properties': {
        #         'X': 999,
        #         'Y': 999,
        #     },
        # },
    ]
    result = patch
    return result

def get_normalize_marble_gallery_slinger_staircase_right_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... 02EE 02EE 031A 031B .... .... 0000 0000 031B .... .... .... .... ....',
            '.... .... .... 02F0 02F0 031C .... .... 0000 0000 031C .... .... .... .... ....',
            '.... .... .... .... 02F3 02F3 .... .... 0597 0597 .... .... .... .... .... ....',
            '.... .... .... .... 02F7 02F8 .... .... 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... 0319 02E1 0000 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... 0597 0597 0000 0000 0000 0000 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Marble Gallery Slinger Staircase',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Marble Gallery, Slinger Staircase': {
                    'Nodes': {
                        'Right-Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Slinger Staircase',
                    'Layer': 'Foreground',
                    'Top': 16 + 10,
                    'Left': 32,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Slinger Staircase',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    patch['Changes']['Pokes'] = []
    for (offset, data_type, value) in (
        (0x03FCE06C, 's16', 0x0001), # Marble Gallery - 0x0003 -> 0x0001
    ):
        patch['Changes']['Pokes'].append({
            'Gamedata Address': '{:08X}'.format(offset),
            'Data Type': data_type,
            'Value': '{:08X}'.format(value),
        })
    patch['Changes']['Object Layouts'] = [
        {
            'Stage': 'Marble Gallery',
            'Room': 'Marble Gallery, Slinger Staircase',
            'Object Layout ID': 11,
            'Properties': {
                'X': 608 + 32,
                'Y': 476,
            },
            'Notes': [
                "Marble Gallery's Entity Layout treatment is buggy, so this is being handled the old Object Layout way",
            ],
        },
        {
            'Stage': 'Black Marble Gallery',
            'Room': 'Black Marble Gallery, Slinger Staircase',
            'Object Layout ID': 5,
            'Properties': {
                'X': 160,
                'Y': 36,
            },
        },
    ]
    patch['Changes']['Constants'] = {}
    constant_key = f'Trapdoor Offsets (Marble Gallery)'
    patch['Changes']['Constants'][constant_key] = []
    for (index, value) in (
        (2, 0x0566),
       ):
        patch['Changes']['Constants'][constant_key].append({
            'Index': index,
            'Value': '{:04X}'.format(value),
        })
    result = patch
    return result

def get_normalize_olroxs_quarters_tall_shaft_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... 06B4 06B4 06B4 06B4 0000 0000 0000 0000 06B4 06B4 06B4 .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D7 03D8 03D7 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 039D 0000 0000 0000 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03A1 0000 0000 0000 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 039D 0000 0000 0000 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03A1 0000 0000 0000 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 0412 0414 0412 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D7 03D8 03D7 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 039D 0000 0000 0000 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03A1 0000 0000 0000 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 039D 0000 0000 0000 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03A1 0000 0000 0000 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 0412 0414 0412 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D7 03D8 03D7 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 039D 0000 0000 0000 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03A1 0000 0000 0000 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 039D 0000 0000 0000 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03A1 0000 0000 0000 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 0412 0414 0412 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... 03D0 03D1 03D0 0207 0000 0000 0000 0000 025C 03D1 03D0 .... .... ....',
            '.... .... 03CC 03CD 03CC 0207 0000 0000 0000 0000 025C 03CD 03CC .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0489 03B2 03B3 06A2 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 03F9 03F7 03F8 03F7 03F8 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 03FB 03F8 03F7 03F8 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 03FC 03FD 03FE 03FD 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0489 03B2 03B3 06A2 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 03F9 03F7 03F8 03F7 03F8 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 03FB 03F8 03F7 03F8 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 03FC 03FD 03FE 03FD 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0489 03B2 03B3 06A2 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 03F9 03F7 03F8 03F7 03F8 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 03FB 03F8 03F7 03F8 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 03FC 03FD 03FE 03FD 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03F9 03F7 03F8 044A 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FB 03F8 03F7 0449 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03FC 03FD 03FE 044B 0000 0000 0000 .... .... ....',
            '.... .... 0000 0000 0000 0000 03C1 0402 0403 03C1 0000 0000 0000 .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Olrox's Quarters Tall Shaft",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                "Olrox's Quarters, Tall Shaft": {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Tall Shaft",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Tall Shaft",
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Tall Shaft",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Tall Shaft",
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    patch['Changes']['Entity Layouts'] = [
        {
            'Update': {
                'Room': "Olrox's Quarters, Tall Shaft",
                'Entity Layout ID': 0,
            },
            'Properties': {
                'X': 95 - 32,
                'Y': 1039,
            },
            'Stage': "Olrox's Quarters",
        },
        {
            'Update': {
                'Room': "Olrox's Quarters, Tall Shaft",
                'Entity Layout ID': 1,
            },
            'Properties': {
                'X': 95 - 32,
                'Y': 911,
            },
            'Stage': "Olrox's Quarters",
        },
        {
            'Update': {
                'Room': "Olrox's Quarters, Tall Shaft",
                'Entity Layout ID': 2,
            },
            'Properties': {
                'X': 95 - 32,
                'Y': 399,
            },
            'Stage': "Olrox's Quarters",
        },
        {
            'Update': {
                'Room': "Death Wing's Lair, Tall Shaft",
                'Entity Layout ID': 1,
            },
            'Properties': {
                'X': 161 + 32,
                'Y': 497,
            },
            'Stage': "Death Wing's Lair",
        },
        {
            'Update': {
                'Room': "Death Wing's Lair, Tall Shaft",
                'Entity Layout ID': 2,
            },
            'Properties': {
                'X': 161 + 32,
                'Y': 625,
            },
            'Stage': "Death Wing's Lair",
        },
        {
            'Update': {
                'Room': "Death Wing's Lair, Tall Shaft",
                'Entity Layout ID': 3,
            },
            'Properties': {
                'X': 161 + 32,
                'Y': 1137,
            },
            'Stage': "Death Wing's Lair",
        },
    ]
    result = patch
    return result

def get_normalize_olroxs_quarters_prison_right_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... 039D 0401 0000 0000 0000 .... 0404 040D 03FF .... .... ....',
            '.... .... .... .... 01FE 01FF 0000 0000 0000 .... 022D 01FD 0405 .... .... ....',
            '.... .... .... .... 0202 01FF 0000 0000 0000 .... 022D 0201 040A .... .... ....',
            '.... .... .... .... .... .... 0000 0000 0000 .... 06B4 .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... 0403 0402 0403 .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Olrox's Quarters Prison Right Bottom",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                "Olrox's Quarters, Prison": {
                    'Nodes': {
                        'Right-Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Prison",
                    'Layer': 'Foreground',
                    'Top': 12,
                    'Left': 80,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Prison",
                    'Layer': 'Background',
                    'Top': 12,
                    'Left': 80,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Prison",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Prison",
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_olroxs_quarters_prison_left_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... 039D 0401 0000 0000 0000 0000 0404 040D 03FF .... .... ....',
            '.... .... .... .... 01FE 01FF 0000 0000 0000 0000 022D 01FD 0405 .... .... ....',
            '.... .... .... .... 0202 01FF 0000 0000 0000 0000 022D 0201 040A .... .... ....',
            '.... .... .... .... .... 06B4 0000 0000 0000 0000 06B4 .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... 0403 0402 0403 0402 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Olrox's Quarters Prison Left Bottom",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                "Olrox's Quarters, Prison": {
                    'Nodes': {
                        'Left-Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Prison",
                    'Layer': 'Foreground',
                    'Top': 12,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Prison",
                    'Layer': 'Background',
                    'Top': 12,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Prison",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 80,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Prison",
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 80,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_olroxs_quarters_open_courtyard_top_passage():
    tilemaps = {
        'Foreground': [
            '06B4 06B4 06B4 06B4 06B4 06B4 0000 0000 0000 0000 06B4 06B4 06B4 06B4 06B4 06B4',
            '0201 0202 0201 0202 0201 01FF 0224 0224 0224 0224 022D 0201 022C 022D 022E 022F',
            '01FD 01FE 01FD 01FE 01FD 01FF 0224 0224 0224 0224 022D 01FD 022C 022D 0230 0231',
            '0201 0202 0201 0202 0201 01FF 0229 022A 0229 022A 022D 0201 022C 022D 022E 022F',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Olrox's Quarters Open Courtyard Top",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                "Olrox's Quarters, Open Courtyard": {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Open Courtyard",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 80,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Open Courtyard",
                    'Layer': 'Foreground',
                    'Top': 48 + 12,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_olroxs_quarters_catwalk_crypt_left_top_passage():
    # NOTE(sestren): In Death Wing's Lair, it is possible to clip through the barrier when flying upward from underneath
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 0000 0000 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0027 0027 002A 002B .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0021 0022 0049 004A .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Olrox's Quarters Catwalk Crypt Left Top",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                "Olrox's Quarters, Catwalk Crypt": {
                    'Nodes': {
                        'Left-Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Catwalk Crypt",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 16,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Catwalk Crypt",
                    'Layer': 'Foreground',
                    'Top': 13,
                    'Left': 80,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    patch['Changes']['Constants'] = {}
    for stage_name in (
        "Olrox's Quarters",
        "Death Wing's Lair",
    ):
        constant_key = f'Breakable Ceiling Tiles ({stage_name})'
        patch['Changes']['Constants'][constant_key] = []
        for (index, value) in enumerate((
            # Closed
            0x0027, 0x0027, 0x002A, 0x002B,
            0x000F, 0x000D, 0x000E, 0x000D,
            # Open
            0x0027, 0x0027, 0x002A, 0x002B,
            0x0021, 0x0022, 0x0049, 0x004A,
        )):
            patch['Changes']['Constants'][constant_key].append({
                'Index': index,
                'Value': '{:04X}'.format(value),
            })
    result = patch
    return result

def get_normalize_olroxs_quarters_sword_card_room_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 03C1 03C1 04EA 04ED .... .... .... .... .... ....',
            '.... .... .... .... .... .... 04DF 04E0 04EB 04EC .... .... .... .... .... ....',
            '.... .... .... .... .... .... 04EE 04EF 04F8 04F9 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 .... .... 0000 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Olrox's Quarters Sword Card Room Bottom",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                "Olrox's Quarters, Sword Card Room": {
                    'Nodes': {
                        'Left-Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Olrox's Quarters",
                    'Room': "Olrox's Quarters, Sword Card Room",
                    'Layer': 'Foreground',
                    'Top': 12,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Death Wing's Lair",
                    'Room': "Death Wing's Lair, Sword Card Room",
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 16,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_castle_entrance_after_drawbridge_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... 0127 0129 0132 0128 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012C 04F9 04F8 012D .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012E 012E 012E 012E .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012E 012E 012E 012E .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012E 012E 012E 012E .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 .... .... 0000 .... .... .... .... .... ....',
        ],
        'Foreground (Reverse Entrance)': [
            '.... .... .... .... .... .... 0127 00CF 00D0 0128 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012C 04F9 04F8 012D .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012E 012E 012E 012E .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012E 012E 012E 012E .... .... .... .... .... ....',
            '.... .... .... .... .... .... 012E 012E 012E 012E .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0000 .... .... 0000 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Castle Entrance After Drawbridge Bottom",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Castle Entrance, After Drawbridge': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
                'Castle Entrance Revisited, After Drawbridge': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, After Drawbridge',
                    'Layer': 'Foreground',
                    'Top': 32 + 10,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, After Drawbridge',
                    'Layer': 'Foreground',
                    'Top': 32 + 10,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, After Drawbridge',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 16,
                    'Tiles': reverse_tilemaps['Foreground (Reverse Entrance)'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_castle_entrance_drop_under_portcullis_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... 02D8 0000 .... .... 0000 0309 .... .... .... .... ....',
            '.... .... .... .... .... 02D7 0000 .... .... 0000 0307 .... .... .... .... ....',
            '.... .... .... .... .... 02D6 0000 .... .... 0000 0307 .... .... .... .... ....',
            '.... .... .... .... .... 02D8 0000 .... .... 0540 053F .... .... .... .... ....',
            '.... .... .... .... .... 02D7 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 02D6 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 02D4 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 02D6 0000 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... 02D7 0000 .... .... .... .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0563 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0562 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... 0564 .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Castle Entrance Under Portcullis Top",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Castle Entrance, Drop Under Portcullis': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
                'Castle Entrance Revisited, Drop Under Portcullis': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Drop Under Portcullis',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Drop Under Portcullis',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Drop Under Portcullis',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Drop Under Portcullis',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, Drop Under Portcullis',
                    'Layer': 'Foreground',
                    'Top': 16 + 7,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, Drop Under Portcullis',
                    'Layer': 'Background',
                    'Top': 16 + 7,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_castle_entrance_attic_entrance_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 0420 0421',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 0423 0425',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 041A 041B',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 041D 041E',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 0420 0421',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 0423 0425',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 041A 041B',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0000 041D 041E',
            '.... .... .... .... .... .... .... .... 0000 0000 0000 0000 0447 0448 0420 0421',
            '.... .... .... .... .... .... .... .... 0000 0000 0000 044C 044D 0434 0423 0425',
            '.... .... .... .... .... .... .... .... 0000 0000 044C 0450 0451 04FA 041A 041B',
            '.... .... .... .... .... .... .... .... 0000 0000 0505 0465 0464 0465 041D 041E',
            '.... .... .... .... .... .... .... .... 0000 0000 04FA 04FA 04FA 04FA 04FA 04FA',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0474 .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 047D .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0483 .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0489 .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 047B .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0489 .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 047B .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... .... .... 0489 .... ....',
            '.... .... .... .... .... .... .... .... .... .... .... 0488 0487 0000 .... ....',
            '.... .... .... .... .... .... .... .... .... .... 0481 0482 0000 0000 .... ....',
            '.... .... .... .... .... .... .... 0488 0487 0488 0481 0473 047B 047B .... ....',
            '.... .... .... .... .... .... .... 048A 0487 0487 048A 0000 0000 0000 .... ....',
            '.... .... .... .... .... .... .... 0000 0000 0000 0000 0000 0000 0000 .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Castle Entrance Attic Entrance Bottom",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Castle Entrance, Attic Entrance': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
                'Castle Entrance Revisited, Attic Entrance': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Attic Entrance',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Attic Entrance',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Attic Entrance',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Attic Entrance',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, Attic Entrance',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, Attic Entrance',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_castle_entrance_merman_room_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... .... .... .... 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 0000 0000 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 0000 0000 .... .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... .... .... 0323 0323 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 0323 0323 .... .... .... .... .... ....',
            '.... .... .... .... .... .... .... .... 0323 0323 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': "Normalize Castle Entrance Merman Room Top",
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Castle Entrance, Merman Room': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
                'Castle Entrance Revisited, Merman Room': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Merman Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance',
                    'Room': 'Castle Entrance, Merman Room',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Merman Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Castle Entrance Revisited',
                    'Room': 'Castle Entrance Revisited, Merman Room',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, Merman Room',
                    'Layer': 'Foreground',
                    'Top': 16 + 13,
                    'Left': 32,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': "Reverse Entrance",
                    'Room': 'Reverse Entrance, Merman Room',
                    'Layer': 'Background',
                    'Top': 16 + 13,
                    'Left': 32,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    patch['Changes']['Entity Layouts'] = [
        {
            'Update': {
                'Room': 'Castle Entrance, Merman Room',
                'Entity Layout ID': 7,
            },
            'Properties': {
                'X': 144 + 24,
                'Y': 56,
            },
            'Stage': 'Castle Entrance',
        },
        {
            'Update': {
                'Room': 'Castle Entrance Revisited, Merman Room',
                'Entity Layout ID': 6,
            },
            'Properties': {
                'X': 144 + 24,
                'Y': 56,
            },
            'Stage': 'Castle Entrance Revisited',
        },
    ]
    result = patch
    return result

def get_normalize_marble_gallery_three_paths_top_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... 068A 0000 .... .... 0000 0689 .... .... .... .... ....',
            '.... .... .... .... .... 0688 0000 .... .... 0000 0687 .... .... .... .... ....',
            '.... .... .... .... .... 0685 0000 .... .... 0000 0686 .... .... .... .... ....',
            '.... .... .... .... .... 068C 0000 .... .... 0000 068B .... .... .... .... ....',
        ],
        'Background': [
            '.... .... .... .... .... .... 06B9 06B3 06BC 06C0 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 06B6 06B7 06BE 06BF .... .... .... .... .... ....',
            '.... .... .... .... .... .... 06B9 06B3 06BC 06C0 .... .... .... .... .... ....',
            '.... .... .... .... .... .... 06B6 06B7 06BE 06BF .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Marble Gallery Three Paths Top',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Marble Gallery, Three Paths': {
                    'Nodes': {
                        'Top Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Three Paths',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Three Paths',
                    'Layer': 'Background',
                    'Top': 0,
                    'Left': 0,
                    'Tiles': tilemaps['Background'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Three Paths',
                    'Layer': 'Foreground',
                    'Top': 16 + 12,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Three Paths',
                    'Layer': 'Background',
                    'Top': 16 + 12,
                    'Left': 0,
                    'Tiles': reverse_tilemaps['Background'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_marble_gallery_gravity_boots_room_bottom_passage():
    tilemaps = {
        'Foreground': [
            '.... .... .... .... .... 06C6 0520 .... .... 0520 06CB .... .... .... .... ....',
            '.... .... .... .... .... 0541 0520 .... .... 0520 053B .... .... .... .... ....',
            '.... .... .... .... .... .... 0520 .... .... 0520 .... .... .... .... .... ....',
        ],
    }
    reverse_tilemaps = reverse_tilemap_changes(tilemaps)
    patch = {
        'Description': 'Normalize Marble Gallery Gravity Boots Bottom',
        'Authors': [
            'Sestren',
        ],
        'Mapper': {
            'Rooms': {
                'Marble Gallery, Gravity Boots Room': {
                    'Nodes': {
                        'Bottom Passage': {
                            'Type': '######....######',
                        },
                    },
                },
            },
        },
        'Changes': {
            'Tilemaps': [
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Marble Gallery',
                    'Room': 'Marble Gallery, Gravity Boots Room',
                    'Layer': 'Foreground',
                    'Top': 13,
                    'Left': 32,
                    'Tiles': tilemaps['Foreground'],
                },
                {
                    'Type': 'Tile ID-Based',
                    'Stage': 'Black Marble Gallery',
                    'Room': 'Black Marble Gallery, Gravity Boots Room',
                    'Layer': 'Foreground',
                    'Top': 0,
                    'Left': 32,
                    'Tiles': reverse_tilemaps['Foreground'],
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_confessional_chime_sound():
    patch = {
        'Description': 'Relocate sound entity that turns off chime',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Entity Layouts': [
                {
                    'Add Relative To': {
                        'Room': 'Royal Chapel, Confessional Booth',
                        'Node': 'Left Passage',
                        'X Offset': 0,
                        'Y Offset': 0,
                    },
                    'Delete From': {
                        'Entity Layout ID': 47,
                        'Room': 'Royal Chapel, Left Tower',
                    },
                    'Stage': 'Royal Chapel',
                },
            ],
        },
    }
    result = patch
    return result

def get_normalize_olroxs_quarters_secret_onyx_room_rubble():
    patch = {
        'Description': 'Relocate rubble in Secret Onyx Room',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Entity Layouts': [],
        },
    }
    for (stage_name, node_name, x_offset, entity_layout_id) in (
        ("Olrox's Quarters", 'Lower-Right Passage', 8, 0),
        ("Death Wing's Lair", 'Lower-Right Passage', -8, 6),
    ):
        entity_layout = {
            'Add Relative To': {
                'Room': f'{stage_name}, Grand Staircase',
                'Node': node_name,
                'X Offset': x_offset,
                'Y Offset': 24,
                'Entity Room Index': 180,
            },
            'Delete From': {
                'Entity Layout ID': entity_layout_id,
                'Room': f'{stage_name}, Secret Onyx Room',
            },
            'Stage': f'{stage_name}',
        }
        patch['Changes']['Entity Layouts'].append(entity_layout)
    result = patch
    return result

def get_normalize_waterfall_roar_sound():
    patch = {
        'Description': 'Relocate sound entities that fade waterfall roar',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Constants': {},
            'Entity Layouts': [],
        },
    }
    for (stage_name, node_name, index) in (
        ('Underground Caverns', 'Upper-Left Passage', 8),
        ('Underground Caverns', 'Lower-Left Passage', 12),
        ('Reverse Caverns', 'Upper-Right Passage', 0),
        ('Reverse Caverns', 'Lower-Right Passage', 4),
    ):
        constant_name = f'Waterfall Sound Parameters ({stage_name})'
        if constant_name not in patch['Changes']['Constants']:
            patch['Changes']['Constants'][constant_name] = []
        constant = {
            'Index': index,
            'Value Relative From': {
                'Room': f'{stage_name}, Waterfall',
                'Node': node_name,
                'Property': 'X'
            },
        }
        patch['Changes']['Constants'][constant_name].append(constant)
    for (stage_name, node_name, room_name, x_offset, entity_layout_id) in (
        ('Underground Caverns', 'Upper-Left Passage', 'DK Button', -128, 0),
        ('Underground Caverns', 'Upper-Right Passage', 'Pentagram Room', 128, 7),
        ('Underground Caverns', 'Lower-Left Passage', 'Room ID 19', -128, 1),
        ('Underground Caverns', 'Lower-Right Passage', 'Room ID 18', 128, 2),
        ('Reverse Caverns', 'Upper-Left Passage', 'DK Button', 128, 0),
        ('Reverse Caverns', 'Upper-Right Passage', 'Pentagram Room', -128, 7),
        ('Reverse Caverns', 'Lower-Left Passage', 'Room ID 19', 128, 1),
        ('Reverse Caverns', 'Lower-Right Passage', 'Room ID 18', -128, 2),
    ):
        entity_layout = {
            'Add Relative To': {
                'Room': f'{stage_name}, Waterfall',
                'Node': node_name,
                'X Offset': x_offset,
                'Y Offset': 0,
                'Entity Room Index': 180,
            },
            'Delete From': {
                'Entity Layout ID': entity_layout_id,
                'Room': f'{stage_name}, {room_name}',
            },
            'Stage': f'{stage_name}',
        }
        patch['Changes']['Entity Layouts'].append(entity_layout)
    result = patch
    return result

def get_assign_power_of_wolf_relic_a_unique_id():
    patch = {
        'Description': 'Prevent Trapdoor from deleting Power of Wolf',
        'Authors': [
            'Eldritch',
            'Mottzilla',
        ],
        'Changes': {
            'Entity Layouts': [
                {
                    'Update': {
                        'Room': 'Castle Entrance, After Drawbridge',
                        'Entity Layout ID': 9,
                    },
                    'Properties': {
                        'Entity Room Index': 180,
                    },
                    'Stage': 'Castle Entrance',
                },
                {
                    'Update': {
                        'Room': 'Castle Entrance Revisited, After Drawbridge',
                        'Entity Layout ID': 11,
                    },
                    'Properties': {
                        'Entity Room Index': 180,
                    },
                    'Stage': 'Castle Entrance Revisited',
                },
            ],
        },
    }
    result = patch
    return result

def get_prevent_palette_glitches_related_to_zombie_hallway():
    patch = {
        'Description': 'Prevent palette glitches related to Zombie Hallway',
        'Authors': [
            'Sestren',
        ],
        'Changes': {
            'Entity Layouts': [
                {
                    'Add Relative To': {
                        'Room': 'Castle Entrance, Zombie Hallway',
                        'Entity Layout ID': 180,
                        'Node': 'Left Passage',
                    },
                    'Properties': {
                        'Entity Room Index': 180,
                    },
                    'Delete From': {
                        'Entity Layout ID': 2,
                        'Room': 'Castle Entrance, Merman Room',
                    },
                    'Stage': 'Castle Entrance',
                    'Notes': [
                        'Relocate Entity that controls lightning and lighting effects',
                    ],
                },
            ],
        },
    }
    result = patch
    return result


if __name__ == '__main__':
    '''
    Some patches play nice with other patches, some don't.
    A good patcher will assemble patches and attempt to validate if they work together or not

    Usage
    python sotn_patcher.py
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('build_dir', help='Input a filepath to a folder that will contain the build files', type=str)
    args = parser.parse_args()
    for (file_name, patch) in (
        ('assign-power-of-wolf-relic-a-unique-id', get_assign_power_of_wolf_relic_a_unique_id()),
        ('clock-hands-display-minutes-and-seconds', get_clock_hands_patch()),
        ('enable-debug-mode', get_simple_patch("Enables the game's hidden debug mode", [
            (0x000D9364, 'u32', 0xAC258850, 'sw a1, -$77B0(at)'), # Original instruction was sw 0, -$77B0(at)
        ])),
        ('normalize-confessional-chime-sound', get_normalize_confessional_chime_sound()),
        ('normalize-dk-bridge-bottom-passage', get_normalize_dk_bridge_bottom_passage()),
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
        ('normalize-alchemy-laboratory-entryway-top-passage', get_normalize_alchemy_laboratory_entryway_top_passage()),
        ('normalize-alchemy-laboratory-glass-vats-bottom-passage', get_normalize_alchemy_laboratory_glass_vats_bottom_passage()),
        ('normalize-alchemy-laboratory-red-skeleton-lift-room-bottom-passage', get_normalize_alchemy_laboratory_red_skeleton_lift_room_bottom_passage()),
        ('normalize-alchemy-laboratory-red-skeleton-lift-room-top-passage', get_normalize_alchemy_laboratory_red_skeleton_lift_room_top_passage()),
        ('normalize-alchemy-laboratory-secret-life-max-up-room-top-passage', get_normalize_alchemy_laboratory_secret_life_max_up_room_top_passage()),
        ('normalize-alchemy-laboratory-tall-zig-zag-room-bottom-passage', get_normalize_alchemy_laboratory_tall_zig_zag_room_bottom_passage()),
        ('normalize-castle-entrance-after-drawbridge-bottom-passage', get_normalize_castle_entrance_after_drawbridge_bottom_passage()),
        ('normalize-castle-entrance-attic-entrance-bottom-passage', get_normalize_castle_entrance_attic_entrance_bottom_passage()),
        ('normalize-castle-entrance-drop-under-portcullis-top-passage', get_normalize_castle_entrance_drop_under_portcullis_top_passage()),
        ('normalize-castle-entrance-merman-room-top-passage', get_normalize_castle_entrance_merman_room_top_passage()),
        ('normalize-hidden-crystal-entrance-top-passage', get_normalize_hidden_crystal_entrance_top_passage()),
        ('normalize-ice-floe-room-top-passage', get_normalize_ice_floe_room_top_passage()),
        ('normalize-jewel-sword-passageway', get_normalize_jewel_sword_passageway_patch()),
        ('normalize-long-drop-bottom-passage', get_normalize_long_drop_bottom_passage()),
        ('normalize-marble-gallery-beneath-left-trapdoor-top-passage', get_normalize_marble_gallery_beneath_left_trapdoor_top_passage()),
        ('normalize-marble-gallery-beneath-right-trapdoor-top-passage', get_normalize_marble_gallery_beneath_right_trapdoor_top_passage()),
        ('normalize-marble-gallery-gravity-boots-room-bottom-passage', get_normalize_marble_gallery_gravity_boots_room_bottom_passage()),
        ('normalize-marble-gallery-slinger-staircase-right-bottom-passage', get_normalize_marble_gallery_slinger_staircase_right_bottom_passage()),
        ('normalize-marble-gallery-stopwatch-room-bottom-passage', get_normalize_marble_gallery_stopwatch_room_bottom_passage()),
        ('normalize-marble-gallery-three-paths-top-passage', get_normalize_marble_gallery_three_paths_top_passage()),
        ('normalize-olroxs-quarters-catwalk-crypt-left-top-passage', get_normalize_olroxs_quarters_catwalk_crypt_left_top_passage()),
        ('normalize-olroxs-quarters-open-courtyard-top-passage', get_normalize_olroxs_quarters_open_courtyard_top_passage()),
        ('normalize-olroxs-quarters-prison-left-bottom-passage', get_normalize_olroxs_quarters_prison_left_bottom_passage()),
        ('normalize-olroxs-quarters-prison-right-bottom-passage', get_normalize_olroxs_quarters_prison_right_bottom_passage()),
        ('normalize-olroxs-quarters-secret-onyx-room-rubble', get_normalize_olroxs_quarters_secret_onyx_room_rubble()),
        ('normalize-olroxs-quarters-sword-card-room-bottom-passage', get_normalize_olroxs_quarters_sword_card_room_bottom_passage()),
        ('normalize-olroxs-quarters-tall-shaft-top-passage', get_normalize_olroxs_quarters_tall_shaft_top_passage()),
        ('normalize-secret-bookcase-rooms', get_normalize_secret_bookcase_rooms()),
        ('normalize-tall-stairwell-bottom-passage', get_normalize_tall_stairwell_bottom_passage()),
        ('normalize-underground-caverns-crystal-bend-top-passage', get_normalize_underground_caverns_crystal_bend_top_passage()),
        ('normalize-underground-caverns-exit-to-abandoned-mine-top-passage', get_normalize_underground_caverns_exit_to_abandoned_mine_top_passage()),
        ('normalize-underground-caverns-exit-to-castle-entrance', get_normalize_underground_caverns_exit_to_castle_entrance()),
        ('normalize-underground-caverns-hidden-crystal-entrance-bottom-passage', get_normalize_underground_caverns_hidden_crystal_entrance_bottom_passage()),
        ('normalize-underground-caverns-left-ferryman-route-top-passage', get_normalize_underground_caverns_left_ferryman_route_top_passage()),
        ('normalize-underground-caverns-plaque-room-bottom-passage', get_normalize_underground_caverns_plaque_room_bottom_passage()),
        ('normalize-underground-caverns-room-id-09-bottom-passage', get_normalize_underground_caverns_room_id_09_bottom_passage()),
        ('normalize-underground-caverns-room-id-10-top-passage', get_normalize_underground_caverns_room_id_10_top_passage()),
        ('normalize-underground-caverns-small-stairwell-top-passage', get_normalize_underground_caverns_small_stairwell_top_passage()),
        ('normalize-waterfall-roar-sound', get_normalize_waterfall_roar_sound()),
        ('prevent-palette-glitches-related-to-zombie-hallway', get_prevent_palette_glitches_related_to_zombie_hallway()),
        ('prevent-softlocks-after-defeating-scylla', get_prevent_softlocks_after_defeating_scylla()),
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
        with open(os.path.join(os.path.normpath(args.build_dir), 'patches', file_name + '.json'), 'w') as patch_file:
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