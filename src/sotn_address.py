import argparse

class Address:
    '''
    ### gamedata address
      - The location of a specific piece of gamedata
      - Used as the canonical address
    ### disc address
      - The location of gamedata as it is found on the disc image
      - To get the location on disc, call get_disc_address passing the 
        canonical or gamedata address as a parameter
    '''
    SECTOR_HEADER_SIZE = 24
    SECTOR_DATA_SIZE = 2048
    SECTOR_ERROR_CORRECTION_DATA_SIZE = 280
    SECTOR_SIZE = SECTOR_HEADER_SIZE + SECTOR_DATA_SIZE + SECTOR_ERROR_CORRECTION_DATA_SIZE
    def __init__(self, address: int, address_type: str='GAMEDATA'):
        if address_type == 'DISC':
            self.address = self.get_gamedata_address(address)
        elif address_type == 'GAMEDATA':
            self.address = address
        else:
            raise ValueError('Unknown address type: ' + address_type)
    
    def to_disc_address(self, offset: int=0) -> int:
        result = self.get_disc_address(self.address + offset)
        return result

    @classmethod
    def get_disc_address(self, gamedata_address: int) -> int:
        sector, offset = divmod(gamedata_address, self.SECTOR_DATA_SIZE)
        result = sector * self.SECTOR_SIZE + self.SECTOR_HEADER_SIZE + offset
        return result

    @classmethod
    def get_gamedata_address(self, disc_address: int) -> int:
        HDR = self.SECTOR_HEADER_SIZE
        DAT = self.SECTOR_DATA_SIZE
        sector, offset = divmod(disc_address, self.SECTOR_SIZE)
        if offset < HDR:
            return None
        elif offset >= (HDR + DAT):
            return None
        result = sector * DAT + (offset - HDR) % DAT
        return result

def _hex(val: int, size: int):
    result = ('{:0' + str(size) + 'X}').format(val)
    return result

if __name__ == '__main__':
    '''
    Usage
    python sotn_address.py 0x049BEA1C DISC
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('address', help='Input a hex address', type=str)
    parser.add_argument('type', help='Address type ("GAMEDATA" or "DISC")', type=str)
    args = parser.parse_args()
    address = Address(int(args.address, 16), args.type)
    print('Game:', _hex(address.address, 8))
    print('Disc:', _hex(address.to_disc_address(), 8))