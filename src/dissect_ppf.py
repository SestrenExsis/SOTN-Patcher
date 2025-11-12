# External libraries
import argparse
import os

# Local libraries
import sotn_address
import sotn_extractor

class ParsedPPF:
    def __init__(self, bin: sotn_extractor.BIN):
        self.bin = bin
        self.header = self.read_string(5)
        self.encoding_method = self.read_byte()
        self.description = self.read_string(50)
        self.image_type = self.read_byte()
        self.block_check = self.read_byte()
        self.undo_data = self.read_byte()
        self.dummy = self.read_byte()
        self.writes = []
        while True:
            address = self.read_u64()
            length = self.read_byte()
            chars = []
            for _ in range(length):
                char = self.read_byte()
                chars.append(char)
            write = (address, length, chars)
            if length < 1:
                break
            self.writes.append(write)
    
    def read(self, byte_count, endianness, sign):
        result = self.bin.read(self.bin.cursor.address, byte_count, endianness, sign)
        self.bin.cursor.address += byte_count
        return result
    
    def read_byte(self):
        result = self.read(1, 'little', False)
        return result
    
    def read_u64(self):
        result = self.read(8, 'little', False)
        return result
    
    def read_string(self, size: int):
        result = ''
        for _ in range(size):
            char_code = self.read(1, 'little', False)
            result += chr(char_code)
        return result

if __name__ == '__main__':
    '''
    Usage
    python dissect_ppf.py ppf
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('ppf', help='Input a filepath to the PPF binary file to be dissected', type=str)
    args = parser.parse_args()
    with open(os.path.join(os.path.normpath(args.ppf)), 'br') as ppf_file:
        bin = sotn_extractor.BIN(ppf_file, 0, False)
        ppf = PPF(bin)
        print('header:', ppf.header)
        print('encoding_method:', ppf.encoding_method)
        print('description:', ppf.description)
        print('image_type:', ppf.image_type)
        print('block_check:', ppf.block_check)
        print('undo_data:', ppf.undo_data)
        print('dummy:', ppf.dummy)
        print('writes:')
        for (address, length, chars) in ppf.writes:
            print(' -', (sotn_address._hex(address, 8), sotn_address._hex(length, 2), list(sotn_address._hex(char, 2) for char in chars)))
