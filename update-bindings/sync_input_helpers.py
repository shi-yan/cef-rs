#!/usr/bin/env python3
"""Regenerate scalar CEF 158 input helpers on a Linux host for every target.

Usage: python3 update-bindings/sync_input_helpers.py /path/to/update-bindings
Set CEF_PATH_linux_x86_64 and BINDGEN_EXTRA_CLANG_ARGS as needed.
Only platform-invariant uint32_t/int signatures are propagated. Other platform
APIs still require normal bindgen runs on their native SDKs.
"""
import re
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
generator = str(Path(sys.argv[1]).resolve())
subprocess.run([generator, '--bindgen', '--target', 'x86_64-unknown-linux-gnu'], check=True)
directory = root / 'sys/src/bindings'
source = (directory / 'x86_64_unknown_linux_gnu.rs').read_text()
names = ['cef_windows_key_code_from_dom_code_and_key', 'cef_non_printable_dom_key_from_xkeysym']
blocks = re.findall(r'(?:unsafe )?extern "C" \{\n.*?\n\}', source, re.S)
helpers = {name: next(block for block in blocks if f'pub fn {name}(' in block) for name in names}
for name, block in helpers.items():
    signature = block[block.index('pub fn'):]
    expected = (f'pub fn {name}(dom_code: u32, dom_key: u32) -> ::std::os::raw::c_int;' if name == names[0]
                else f'pub fn {name}(keysym: u32) -> u32;')
    if re.sub(r'\s+', '', signature.removesuffix('\n}')).replace(',)', ')') != re.sub(r'\s+', '', expected):
        raise RuntimeError(f'Review changed ABI before propagating {name}: {signature}')
for path in sorted(directory.glob('*.rs')):
    if path.name == 'mod.rs':
        continue
    original = path.read_bytes()
    text = original.decode()
    for name, block in helpers.items():
        if name == names[1] and 'linux' not in path.name:
            continue
        pattern = r'(?:unsafe )?extern \"C\" \{\r?\n.*?\r?\n\}'
        existing = next((m for m in re.finditer(pattern, text, re.S) if f'pub fn {name}(' in m[0]), None)
        if existing:
            text = text[:existing.start()] + block + text[existing.end():]
        else:
            text += '\n' + block + '\n'
    path.write_bytes(text.encode())
    subprocess.run([generator, '--target', path.stem.replace('x86_64', 'x86-64').replace('_', '-').replace('x86-64', 'x86_64')], check=True)
