#!/usr/bin/env python3

from pwn import *

# pass in path to x86_64 libEncryptionKeyStore.so
# tested with sha-1 84126efbb85bec19dec85f17c1c8a2298f3ca9af
elf = ELF(sys.argv[1], checksec=False)

# main key generation function
off = elf.sym['Java_com_ubivelox_security_EncryptionKeyStore_getSecretKeyEx']
lines = elf.disasm(off, (12 * 32 * 4) * 4).split('\n')

# find sbox offset
for line in lines:
    # first lea is likely the sbox, disassembler calculates the offset for us
    if ' # 0x' in line:
        sbox_off = int(line.split()[-1], 16)
        break
else:
    raise ValueError('sbox not found')

# extract sbox
sbox = list(map(u32, group(4, elf.read(sbox_off, 12 * 4))))
# lookup is like sbox[month+1 % 12], so rotate left
sbox = rol(sbox, 1)

success(f'sbox: {sbox}')

# read keys
keys = []
for line in lines:
    if 'BYTE PTR' not in line:
        continue

    try:
        n = int(line.split()[-1], 16)
    except ValueError:
        continue

    if not (ord('0') <= n <= ord('9') or ord('A') <= n <= ord('F')):
        continue

    keys.append(chr(n))

# jumptable is like 11, 0 .. 10, so rotate left
keys = rol(group(32, keys[:12 * 32]), 1)
keys = list(map(''.join, keys))

success('keys:')
for key in keys:
    info(f'\t{key}')

with open('keys.txt', 'w') as f:
    for i in range(12):
        f.write(keys[sbox[i]] + '\n')
success('wrote keys.txt')
