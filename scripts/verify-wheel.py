#!/usr/bin/env python3
"""Static checks which reject host or malformed Android wheels."""

from __future__ import annotations

import re
import subprocess
import struct
import sys
import tempfile
import zipfile
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f"wheel verification failed: {message}")


wheel = Path(sys.argv[1])
if not re.fullmatch(
    r"unicorn-2\.1\.4-1-cp311-cp311-android_24_arm64_v8a\.whl", wheel.name
):
    fail(f"unexpected filename {wheel.name}")

with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
    libraries = [name for name in names if name.endswith("libunicorn.so.2")]
    if len(libraries) != 1:
        fail(f"expected one libunicorn.so.2, got {libraries}")
    elf = archive.read(libraries[0])
    metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
    if len(metadata_names) != 1:
        fail("missing or ambiguous METADATA")
    metadata = archive.read(metadata_names[0]).decode("utf-8", "strict")

if not elf.startswith(b"\x7fELF") or elf[4] != 2 or elf[5] != 1:
    fail("library is not a little-endian ELF64")
machine = struct.unpack_from("<H", elf, 18)[0]
if machine != 183:  # EM_AARCH64
    fail(f"ELF machine is {machine}, expected AArch64 (183)")

program_offset = struct.unpack_from("<Q", elf, 32)[0]
program_size = struct.unpack_from("<H", elf, 54)[0]
program_count = struct.unpack_from("<H", elf, 56)[0]
load_alignments = []
for index in range(program_count):
    offset = program_offset + index * program_size
    if struct.unpack_from("<I", elf, offset)[0] == 1:  # PT_LOAD
        load_alignments.append(struct.unpack_from("<Q", elf, offset + 48)[0])
if not load_alignments or any(alignment < 16384 for alignment in load_alignments):
    fail(f"PT_LOAD alignment is not 16 KiB safe: {load_alignments}")

with tempfile.TemporaryDirectory() as temporary:
    library = Path(temporary) / "libunicorn.so.2"
    library.write_bytes(elf)
    dynamic = subprocess.run(
        ["readelf", "--dynamic", str(library)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
needed = set(re.findall(r"Shared library: \[(.+?)\]", dynamic))
unexpected = needed - {"libc.so", "libdl.so", "libm.so", "liblog.so"}
if unexpected:
    fail(f"unexpected host/runtime dependencies: {sorted(unexpected)}")
if "Library soname: [libunicorn.so.2]" not in dynamic:
    fail("unexpected or missing SONAME")
if "Name: unicorn\n" not in metadata or "Version: 2.1.4\n" not in metadata:
    fail("package metadata does not match pinned source")

print(
    f"verified {wheel.name}: AArch64 ELF64, 16 KiB aligned, "
    f"SONAME/dependencies safe, pinned metadata"
)
