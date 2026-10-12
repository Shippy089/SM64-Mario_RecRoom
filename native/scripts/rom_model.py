"""Rebuilds libsm64's Mario model source (src/decomp/mario/model.inc.c) from a ROM's own Mario model block.

libsm64 compiles Mario's shape and colours in from the SM64 decomp; only his textures, animations and sounds come from the
ROM at run time. A ROM hack that redraws Mario in place (Super Luigi 64 does: same block, same size, same layout) can still
change his shape and colours, so this reads them from that ROM:

  * every vertex array and light (colour) group, found in the vanilla block by its exact bytes, is read back from the
    same place in the hack's block;
  * every geometry display list made only of vertex loads and triangles is re-read the same way, so a hack that draws a
    part with other triangles (Super Luigi's head) keeps them.
Anything else that differs is reported and left as in the decomp. Nothing here leaves the user's PC: the output is
written next to the native build cache and compiled into that PC's own library.

  python rom_model.py <vanilla model.inc.c> <clean USA rom.z64> <hacked rom.z64> <out model.inc.c>

The native library does the same at start-up from a table of offsets (body-fit/native-pose/mario_model_offsets.json, read by
build_native.py). This writes that table again from the decomp's model and the clean ROM:

  python rom_model.py --offsets <vanilla model.inc.c> <clean USA rom.z64> <out mario_model_offsets.json>
"""
from __future__ import annotations

import json
import re
import struct
import sys

MARIO_MIO0 = 1132368  # libsm64 MARIO_TEX_ROM_OFFSET: Mario's segment 4 block
SEGMENT = 0x04


def mio0(buf: bytes, at: int) -> bytes:
    if at < 0 or buf[at:at + 4] != b"MIO0" or at + 16 > len(buf):
        raise ValueError("no MIO0 block at %#x" % at)
    size, comp, unc = struct.unpack(">III", buf[at + 4:at + 16])
    if size > 1 << 24:
        raise ValueError("the MIO0 block at %#x claims %d bytes" % (at, size))
    out = bytearray()
    bit_i, ci, ui = at + 16, at + comp, at + unc
    bits = nbits = 0
    try:
        while len(out) < size:
            if nbits == 0:
                bits, nbits, bit_i = struct.unpack(">I", buf[bit_i:bit_i + 4])[0], 32, bit_i + 4
            literal = bits & 0x80000000
            bits, nbits = (bits << 1) & 0xFFFFFFFF, nbits - 1
            if literal:
                out.append(buf[ui])
                ui += 1
            else:
                v = struct.unpack(">H", buf[ci:ci + 2])[0]
                ci += 2
                for _ in range((v >> 12) + 3):
                    out.append(out[-((v & 0xFFF) + 1)])
    except (IndexError, struct.error):
        raise ValueError("the MIO0 block at %#x is cut short or damaged" % at) from None
    return bytes(out[:size])  # a last copy can run a few bytes over


NUM = r"(-?(?:0x[0-9a-fA-F]+|\d+))"


def ints(s):
    return [int(x, 0) for x in re.findall(NUM, s)]


def vtx_bytes(body):
    out = bytearray()
    for v in re.findall(r"\{\{\{(.*?)\}\}\}", body, re.S):
        n = ints(v)
        out += struct.pack(">hhhHhhBBBB", n[0], n[1], n[2], n[3] & 0xFFFF, n[4], n[5], *[c & 0xFF for c in n[6:10]])
    return bytes(out)


def vtx_text(data):
    rows = []
    for i in range(0, len(data), 16):
        x, y, z, f, s, t, a, b, c, d = struct.unpack(">hhhHhhBBBB", data[i:i + 16])
        rows.append("    {{{%6d, %6d, %6d}, %d, {%6d, %6d}, {0x%02x, 0x%02x, 0x%02x, 0x%02x}}}," % (x, y, z, f, s, t, a, b, c, d))
    return "\n".join(rows)


def light_bytes(args):
    ar, ag, ab, r, g, b, x, y, z = ints(args)
    return bytes([ar, ag, ab, 0, ar, ag, ab, 0, r, g, b, 0, r, g, b, 0, x & 0xFF, y & 0xFF, z & 0xFF, 0])


def light_text(d):
    return "\n    0x%02x, 0x%02x, 0x%02x,\n    0x%02x, 0x%02x, 0x%02x, 0x%02x, 0x%02x, 0x%02x\n" % (
        d[0], d[1], d[2], d[8], d[9], d[10], d[16], d[17], d[18])


class Model:
    def __init__(self, text: str, vanilla: bytes):
        self.text, self.vanilla = text, vanilla
        self.vtx = {}  # name -> (offset, length)
        for m in re.finditer(r"static const Vtx (\w+)\[\] = \{(.*?)\n\};", text, re.S):
            data = vtx_bytes(m.group(2))
            at = vanilla.find(data)
            if at < 0:
                raise ValueError("vertex array %s is not in the vanilla block" % m.group(1))
            self.vtx[m.group(1)] = (at, len(data))
        self.lights = {}
        for m in re.finditer(r"static const Lights1 (\w+) = gdSPDefLights1\((.*?)\);", text, re.S):
            data = light_bytes(m.group(2))
            at = vanilla.find(data)
            if at < 0:
                raise ValueError("light group %s is not in the vanilla block" % m.group(1))
            self.lights[m.group(1)] = (at, len(data))

    def vertex_ref(self, addr: int) -> str:
        if addr >> 24 != SEGMENT:
            raise ValueError("vertex address %#x outside segment 4" % addr)
        off = addr & 0xFFFFFF
        for name, (at, length) in self.vtx.items():
            if at <= off < at + length and (off - at) % 16 == 0:
                return name if off == at else "%s + %d" % (name, (off - at) // 16)
        raise ValueError("vertex address %#x is in no known vertex array" % addr)

    def geometry_lists(self):
        """Gfx arrays made only of vertex loads, triangles and an end: (name, body span, F3D bytes)."""
        for m in re.finditer(r"const Gfx (\w+)\[\] = \{(.*?)\n\};", self.text, re.S):
            calls = re.findall(r"(gs\w+)\((.*?)\),", m.group(2), re.S)
            if not calls or any(c not in ("gsSPVertex", "gsSP1Triangle", "gsSP2Triangles", "gsSPEndDisplayList") for c, _ in calls):
                continue
            out = bytearray()
            for c, a in calls:
                parts = [p.strip() for p in a.split(",")]
                if c == "gsSPVertex":
                    name, plus = (parts[0].split("+") + ["0"])[:2]
                    if name.strip() not in self.vtx:
                        raise ValueError("display list %s loads %s, which is not a vertex array of the model" % (m.group(1), name.strip()))
                    at = self.vtx[name.strip()][0] + int(plus.strip(), 0) * 16
                    n, v0 = int(parts[1], 0), int(parts[2], 0)
                    out += struct.pack(">BBHI", 0x04, ((n - 1) << 4) | v0, n * 16, (SEGMENT << 24) | at)
                elif c == "gsSP1Triangle":
                    v = [int(p, 0) for p in parts[:4]]
                    out += struct.pack(">BBHBBBB", 0xBF, 0, 0, v[3], v[0] * 10, v[1] * 10, v[2] * 10)
                elif c == "gsSP2Triangles":
                    v = [int(p, 0) for p in parts[:8]]
                    out += struct.pack(">BBHBBBB", 0xBF, 0, 0, v[3], v[0] * 10, v[1] * 10, v[2] * 10)
                    out += struct.pack(">BBHBBBB", 0xBF, 0, 0, v[7], v[4] * 10, v[5] * 10, v[6] * 10)
                else:
                    out += bytes([0xB8, 0, 0, 0, 0, 0, 0, 0])
            yield m.group(1), m.span(2), bytes(out)

    def list_text(self, data: bytes) -> str:
        rows = []
        for i in range(0, len(data), 8):
            op = data[i]
            if op == 0x04:
                b1, length, addr = struct.unpack(">BHI", data[i + 1:i + 8])
                rows.append("    gsSPVertex(%s, %d, %d)," % (self.vertex_ref(addr), length // 16, b1 & 0xF))
            elif op == 0xBF:
                flag, a, b, c = data[i + 4], data[i + 5] // 10, data[i + 6] // 10, data[i + 7] // 10
                rows.append("    gsSP1Triangle(%d, %d, %d, 0x%x)," % (a, b, c, flag))
            elif op == 0xB8:
                rows.append("    gsSPEndDisplayList(),")
            else:
                raise ValueError("unexpected display list command %#x" % op)
        return "\n" + "\n".join(rows)


def rebuild(text: str, vanilla: bytes, hacked: bytes) -> tuple[str, dict]:
    if len(vanilla) != len(hacked):
        raise ValueError("the hack's Mario block has another size (%d vs %d): its layout moved" % (len(hacked), len(vanilla)))
    model = Model(text, vanilla)
    changed = set(i for i in range(len(vanilla)) if vanilla[i] != hacked[i])
    explained, edits, report = set(), [], {"vertex_arrays": 0, "lights": 0, "lists": 0}

    for m in re.finditer(r"static const Vtx (\w+)\[\] = \{(.*?)\n\};", text, re.S):
        at, length = model.vtx[m.group(1)]
        if hacked[at:at + length] != vanilla[at:at + length]:
            edits.append((m.span(2), "\n" + vtx_text(hacked[at:at + length])))
            report["vertex_arrays"] += 1
        explained.update(range(at, at + length))
    for m in re.finditer(r"static const Lights1 (\w+) = gdSPDefLights1\((.*?)\);", text, re.S):
        at, length = model.lights[m.group(1)]
        if hacked[at:at + length] != vanilla[at:at + length]:
            edits.append((m.span(2), light_text(hacked[at:at + length])))
            report["lights"] += 1
        explained.update(range(at, at + length))
    for name, span, data in model.geometry_lists():
        at = vanilla.find(data)
        if at < 0:
            continue
        if hacked[at:at + len(data)] != data:
            edits.append((span, model.list_text(hacked[at:at + len(data)])))
            report["lists"] += 1
        explained.update(range(at, at + len(data)))
    report["other_bytes"] = len(changed - explained)  # textures (read from the ROM at run time anyway) and the rest
    for (a, b), new in sorted(edits, reverse=True):
        text = text[:a] + new + text[b:]
    return text, report


def write_offsets(model_c, clean_rom, out):
    with open(clean_rom, "rb") as f:
        vanilla = mio0(f.read(), MARIO_MIO0)
    with open(model_c, encoding="utf-8") as f:
        model = Model(f.read(), vanilla)
    table = {
        "note": "Where each of libsm64's Mario vertex arrays and light groups sits in the USA ROM's Mario block (segment 4, "
                "decompressed). Offsets only, generated by scripts/rom_model.py.",
        "segmentSize": len(vanilla),
        "vertices": {name: at for name, (at, _) in model.vtx.items()},
        "lights": {name: at for name, (at, _) in model.lights.items()},
    }
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(table, f, indent=1)
    print("%d vertex arrays and %d light groups written to %s" % (len(table["vertices"]), len(table["lights"]), out))
    return 0


def main(argv):
    if len(argv) == 4 and argv[0] == "--offsets":
        return write_offsets(*argv[1:])
    if len(argv) != 4:
        print(__doc__)
        return 2
    model_c, clean_rom, hacked_rom, out = argv
    with open(clean_rom, "rb") as f:
        vanilla = mio0(f.read(), MARIO_MIO0)
    with open(hacked_rom, "rb") as f:
        hacked = mio0(f.read(), MARIO_MIO0)
    with open(model_c, encoding="utf-8") as f:
        text = f.read()
    text, report = rebuild(text, vanilla, hacked)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("model rebuilt: %(vertex_arrays)d vertex arrays, %(lights)d colours, %(lists)d triangle lists; "
          "%(other_bytes)d other changed bytes left to the ROM (textures)" % report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
