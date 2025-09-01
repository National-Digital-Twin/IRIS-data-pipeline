#!/usr/bin/env python3
import os, io, sys

LIMIT = 700 * 1024        # <1 MB
infile = 'heating-wales.ttl'     # change as needed
header = []                # will collect any @prefix / base lines

out_idx, size = 0, 0
out = None

def new_file():
    global out_idx, size, out
    if out: out.close()
    fname = f"chunk_{out_idx:02d}.ttl"
    out   = open(fname, "w", encoding="utf-8")
    # add header block to every part
    out.writelines(header)
    out_idx += 1
    size = sum(len(line.encode('utf-8')) for line in header)

with open(infile, encoding="utf-8") as inp:
    for line in inp:
        if not header and (line.startswith('@prefix') or line.startswith('base') or line.lstrip().startswith('PREFIX')):
            header.append(line)
            continue

        if out is None:
            new_file()

        out.write(line)
        size += len(line.encode('utf-8'))

        if line.rstrip().endswith('.') and size >= LIMIT:
            new_file()

if out: out.close()
