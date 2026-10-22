#!/usr/bin/env python3
"""
M3 SDK (4A Engine) BC7 OpenCL fix.

Исправляет ошибку "#bc7::opencl_program_context::initialize: failed to build the program!"
Патчится OpenCL kernel в uEditor_m.dll.

Использование:
    python patch_bc7.py [path\\to\\uEditor_m.dll]                   применить патч
    python patch_bc7.py [path\\to\\uEditor_m.dll] --restore         восстановить бэкап

Перед патчем закрой SDK, запусти скрипт от Администратора.
"""
import os
import shutil
import sys

MARKER = b"// Copyright (c) 2012 THQ Inc."
OLD = b"(float2x4 const*)&gd_subset_results[0]"
NEW = b"(float2x4 const __private*)&gd_subset_results[0]"


def find_kernel(data):
    pos = data.find(MARKER)
    while pos != -1:
        end = data.find(b"\x00", pos)
        region = data[pos:end]
        if b"bc7_kernel" in region and b"__kernel" in region:
            return pos, end
        pos = data.find(MARKER, pos + 1)
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dll = args[0] if args else "uEditor_m.dll"
    bak = dll + ".bak"

    if "--restore" in sys.argv:
        if not os.path.exists(bak):
            sys.exit("Backup not found: " + bak)
        shutil.copyfile(bak, dll)
        print("Restored from", bak)
        return

    if not os.path.exists(dll):
        sys.exit("File not found: " + dll)

    data = open(dll, "rb").read()
    found = find_kernel(data)
    if not found:
        sys.exit("BC7 kernel source not found in this DLL. Maybe different SDK build?")
    start, end = found
    length = end - start
    region = data[start:end]
    print("Kernel found: offset %d, length %d" % (start, length))

    if NEW in region:
        print("Already patched. Nothing to do ¯\_(ツ)_/¯.")
        return
    if region.count(OLD) != 1:
        sys.exit("Expected code line not found exactly once (found %d). Different SDK build?"
                 % region.count(OLD))

    patched = region.replace(OLD, NEW)
    patched = b"\n".join(l.rstrip(b" \t\r") for l in patched.split(b"\n"))
    if len(patched) > length:
        sys.exit("Patched source is %d bytes longer than the original. Aborting." % (len(patched) - length))
    patched = patched.ljust(length, b" ")

    if not os.path.exists(bak):
        shutil.copyfile(dll, bak)
        print("Backup created:", bak)

    try:
        with open(dll, "r+b") as f:
            f.seek(start)
            f.write(patched)
    except PermissionError:
        sys.exit("Permission denied. Close the editor/SDK processes and run as administrator.")

    ok = NEW in open(dll, "rb").read()
    print("Patch applied." if ok else "Something went wrong: patch not found after writing.")


if __name__ == "__main__":
    main()