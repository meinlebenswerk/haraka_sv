"""
Re-implementation of Haraka v2 (512-bit only) in python
"""

import itertools
import operator

# AES S-box
S = [[0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
     [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
     [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
     [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
     [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
     [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
     [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
     [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
     [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
     [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
     [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
     [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
     [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
     [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
     [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
     [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]]

RC = [
    int.to_bytes(c, 16, 'little') for c in [
        0x0684704ce620c00ab2c5fef075817b9d,
        0x8b66b4e188f3a06b640f6ba42f08f717,
        0x3402de2d53f28498cf029d609f029114,
        0x0ed6eae62e7b4f08bbf3bcaffd5b4f79,
        0xcbcfb0cb4872448b79eecd1cbe397044,
        0x7eeacdee6e9032b78d5335ed2b8a057b,
        0x67c28f435e2e7cd0e2412761da4fef1b,
        0x2924d9b0afcacc07675ffde21fc70b3b,
        0xab4d63f1e6867fe9ecdb8fcab9d465ee,
        0x1c30bf84d4b7cd645b2a404fad037e33,
        0xb2cc0bb9941723bf69028b2e8df69800,
        0xfa0478a6de6f55724aaa9ec85c9d2d8a,
        0xdfb49f2b6b772a120efa4f2e29129fd4,
        0x1ea10344f449a23632d611aebb6a12ee,
        0xaf0449884b0500845f9600c99ca8eca6,
        0x21025ed89d199c4f78a2c7e327e593ec,
        0xbf3aaaf8a759c9b7b9282ecd82d40173,
        0x6260700d6186b01737f2efd910307d6b,
        0x5aca45c22130044381c29153f6fc9ac6,
        0x9223973c226b68bb2caf92e836d1943a,
        0xd3bf9238225886eb6cbab958e51071b4,
        0xdb863ce5aef0c677933dfddd24e1128d,
        0xbb606268ffeba09c83e48de3cb2212b1,
        0x734bd3dce2e4d19c2db91a4ec72bf77d,
        0x43bb47c361301b434b1415c42cb3924e,
        0xdba775a8e707eff603b231dd16eb6899,
        0x6df3614b3c7559778e5e23027eca472c,
        0xcda75a17d6de7d776d1be5b9b88617f9,
        0xec6b43f06ba8e9aa9d6c069da946ee5d,
        0xcb1e6950f957332ba25311593bf327c1,
        0x2cee0c7500da619ce4ed0353600ed0d9,
        0xf0b1a5a196e90cab80bbbabc63a4a350,
        0xae3db1025e962988ab0dde30938dca39,
        0x17bb8f38d554a40b8814f3a82e75b442,
        0x34bb8a5b5f427fd7aeb6b779360a16f6,
        0x26f65241cbe5543843ce5918ffbaafde,
        0x4ce99a54b9f3026aa2ca9cf7839ec978,
        0xae51a51a1bdff7be40c06e2822901235,
        0xa0c1613cba7ed22bc173bc0f48a659cf,
        0x756acc03022882884ad6bdfde9c59da1,
    ]
]

# multiply by 2 over GF(2^128)
def xtime(x):
    if (x >> 7):
        return ((x << 1) ^ 0x1b) & 0xff
    else:
        return (x << 1) & 0xff

# xor two lists element-wise
def xor(msg1: bytes, msg2: bytes) -> bytes:
    """
    Perform xor between two buffers
    """
    return bytes(map(operator.xor, msg1, msg2))

# apply a single S-box
def sbox(x):
    return S[(x >> 4)][x & 0xF]

# AES SubBytes
def subbytes(s):
    return [sbox(x) for x in s]

# AES ShiftRows
def shiftrows(s):
    return [s[0], s[5], s[10], s[15], 
            s[4], s[9], s[14], s[3], 
            s[8], s[13], s[2], s[7], 
            s[12], s[1], s[6], s[11]]

# AES MixColumns
def mixcolumns(s):	
    return list(itertools.chain(*
        [[xtime(s[4*i]) ^ xtime(s[4*i+1]) ^ s[4*i+1] ^ s[4*i+2] ^ s[4*i+3],
        s[4*i] ^ xtime(s[4*i+1]) ^ xtime(s[4*i+2]) ^ s[4*i+2] ^ s[4*i+3],
        s[4*i] ^ s[4*i+1] ^ xtime(s[4*i+2]) ^ xtime(s[4*i+3]) ^ s[4*i+3],
        xtime(s[4*i]) ^ s[4*i] ^ s[4*i+1] ^ s[4*i+2] ^ xtime(s[4*i+3])] 
        for i in range(4)]))
    
# AES single regular round	
def haraka_aes_round(s: bytes, rk: bytes) -> bytes:
    s = subbytes(s)
    s = shiftrows(s)
    s = mixcolumns(s)
    s = xor(s, rk)
    return s

def haraka_aes_round_verbose(s: bytes, rk: bytes) -> tuple[bytes, bytes, bytes, bytes]:
    sub_out = subbytes(s)
    shift_out = shiftrows(sub_out)
    mix_out = mixcolumns(shift_out)
    s = xor(mix_out, rk)
    return bytes(sub_out), bytes(shift_out), bytes(mix_out), bytes(s)


""" Haraka v2 """

def haraka_mix256(state: bytes) -> bytes:
    mixed: list[int] = []
    for i in [0, 4, 1, 5, 2, 6, 3, 7]:
        mixed += state[i*4: (i+1)*4]
    return bytes(mixed)

def haraka_mix512(state: bytes) -> bytes:
    """
    Takes in a linear representation of the 512-bit state, permutes the columns according to:
    x_0, ..., x_15 -> x_3, x_11, x_7, x_15, x_8, x_0, x_12, x_4, x_9, x_1, x_13, x_5, x_2, x_10, x_6, x_14
    Note that for *some* reason the state is assumed to be transposed, or in column-major order.
    """

    mixed: list[int] = []
    for i in [3, 11, 7, 15, 8, 0, 12, 4, 9, 1, 13, 5, 2, 10, 6, 14]:
        mixed += state[i*4: (i+1)*4]
    return bytes(mixed)

def haraka256(msg: bytes) -> bytes:
    """
    Haraka v2 256-bit
    """
    m = 2 # Number of AES rounds per round of Haraka v2
    T = 5 # Number of rounds of Haraka v2

    state = bytes([e for e in msg])

    aes_states = []
    round_states = []

    for round in range(T):
        # Run the AES rounds on ea. slice of the state
        for aes_round in range(m):
            next_state = bytearray(32)
            aes_slices = []
            for slice_idx in range(2):
                next_state[slice_idx*16: (slice_idx+1)*16] = haraka_aes_round(
                    state[slice_idx*16: (slice_idx+1)*16],
                    RC[2 * round * m + 2 * aes_round + slice_idx] # 16 bytes, 4x4 matrix
                )
                aes_slices.append(next_state[slice_idx*16: (slice_idx+1)*16])
            aes_states.append(bytes(next_state))
            state = bytes(next_state)
        
        # Mix the columns
        state = haraka_mix256(state)
        round_states.append(bytes(state))
    
    # apply feed-forward, xor the final state against the message
    state = xor(state, msg)
    return state



def haraka512(msg: bytes) -> bytes:
    """
    Haraka-512 v2
    """
    m = 2 # Number of AES rounds per round of Haraka v2
    T = 5 # Number of rounds of Haraka v2

    state = bytes([e for e in msg])
    # print(state.hex())

    aes_states = []
    round_states = []

    for round in range(T):
        # Run the AES rounds on ea. slice of the state
        for aes_round in range(m):
            next_state = bytearray(64)
            aes_slices = []
            for slice_idx in range(4):
                next_state[slice_idx*16: (slice_idx+1)*16] = haraka_aes_round(
                    state[slice_idx*16: (slice_idx+1)*16],
                    RC[4 * round * m + 4 * aes_round + slice_idx] # 16 bytes, 4x4 matrix
                )
                aes_slices.append(next_state[slice_idx*16: (slice_idx+1)*16])
            aes_states.append(bytes(next_state))
            state = bytes(next_state)
        
        # Mix the columns
        state = haraka_mix512(state)
        round_states.append(bytes(state))
    
    # apply feed-forward, xor the final state against the message
    state = xor(state, msg)

    # truncate down to 256 bits
    truncated: list[int] = []
    for i in [2, 3, 6, 7, 8, 9, 12, 13]:
        truncated += state[i*4: (i+1)*4]
    return bytes(truncated)


""" Harakav2 (keyed) """

def haraka512_keyed(msg: bytes, key: list[bytes]) -> bytes:
    """
    Haraka-512 v2 with key (which just replaces the Round-keys)
    """
    m = 2 # Number of AES rounds per round of Haraka v2
    T = 5 # Number of rounds of Haraka v2

    state = bytes([e for e in msg])
    # print(state.hex())

    aes_states = []
    round_states = []

    for round in range(T):
        # Run the AES rounds on ea. slice of the state
        for aes_round in range(m):
            next_state = bytearray(64)
            aes_slices = []
            for slice_idx in range(4):
                next_state[slice_idx*16: (slice_idx+1)*16] = haraka_aes_round(
                    state[slice_idx*16: (slice_idx+1)*16],
                    key[4 * round * m + 4 * aes_round + slice_idx] # 16 bytes, 4x4 matrix
                )
                aes_slices.append(next_state[slice_idx*16: (slice_idx+1)*16])
            aes_states.append(bytes(next_state))
            state = bytes(next_state)
        
        # Mix the columns
        state = haraka_mix512(state)
        round_states.append(bytes(state))
    
    # apply feed-forward, xor the final state against the message
    state = xor(state, msg)

    # truncate down to 256 bits
    truncated: list[int] = []
    for i in [2, 3, 6, 7, 8, 9, 12, 13]:
        truncated += state[i*4: (i+1)*4]
    return bytes(truncated)



if __name__ == '__main__':
    testvector_haraka_512 = bytes([
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
        0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f
    ])
    testvector_haraka_512_output = bytes([
        0xbe, 0x7f, 0x72, 0x3b, 0x4e, 0x80, 0xa9, 0x98, 0x13, 0xb2, 0x92, 0x28, 0x7f, 0x30, 0x6f, 0x62,
        0x5a, 0x6d, 0x57, 0x33, 0x1c, 0xae, 0x5f, 0x34, 0xdd, 0x92, 0x77, 0xb0, 0x94, 0x5b, 0xe2, 0xaa
    ])

    out_test = haraka512(testvector_haraka_512).hex()
    assert out_test == testvector_haraka_512_output.hex(), f'Expected {testvector_haraka_512_output.hex()} but got {out_test}'
    print('Haraka-512 test passed!')


    testvector_haraka_256 = bytes([
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f
    ])
    testvector_haraka_256_output = bytes([
        0x80, 0x27, 0xcc, 0xb8, 0x79, 0x49, 0x77, 0x4b, 0x78, 0xd0, 0x54, 0x5f, 0xb7, 0x2b, 0xf7, 0x0c,
        0x69, 0x5c, 0x2a, 0x09, 0x23, 0xcb, 0xd4, 0x7b, 0xba, 0x11, 0x59, 0xef, 0xbf, 0x2b, 0x2c, 0x1c
    ])

    out_test = haraka256(testvector_haraka_256).hex()
    assert out_test == testvector_haraka_256_output.hex(), f'Expected {testvector_haraka_256_output.hex()} but got {out_test}'
    print('Haraka-256 test passed!')
