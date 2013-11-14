"""
ID3v2.3 Header reading script.

References:
    http://en.wikipedia.org/wiki/ID3
    http://wiki.kldp.org/wiki.php/ID3%20tag%20version%202.4.0%20structure%20%B9%F8%BF%AA (Korean)

Written by Chan Shik Lim. (chanshik@gmail.com)

"""

import sys
import six
from binascii import unhexlify

from construct import *
import pprint


class PrintContext(Construct):
    """
    Print current context structure.
    """
    def _parse(self, stream, context):
        print "\n# PrintContext ---"
        pprint.pprint(context)
        print "# --- PrintContent\n"


def synchsafe(values):
    return values[0] << 21 | values[1] << 14 | values[2] << 7 | values[3]


def int32(values):
    return values[0] << 24 | values[1] << 16 | values[2] << 8 | values[3]


def is_last_frame(obj, ctx):
    is_last = obj.frame_end_position >= ctx.header_start_position + ctx.length_of_tag
    is_padding_frame = obj.frame_identifier == '\x00\x00\x00\x00'
    is_valid_identifier = True

    for ch in obj.frame_identifier:
        if not ch.isalpha() and not ch.isdigit():
            print "Invalid: " + ch
            is_valid_identifier = False

    return is_last or is_padding_frame or not is_valid_identifier

frame_header = Struct(
    'frame_header',
    Anchor('frame_start_position'),
    String('frame_identifier', 4),
    Array(4, UBInt8('size')),
    IfThenElse(
        'length_of_frame',
        lambda ctx: ctx['_'].unsynchronisation is True,
        Value('length_of_frame', lambda ctx: synchsafe(ctx.size)),
        Value('length_of_frame', lambda ctx: int32(ctx.size))),
    Field('flags', 2),
    String('information', lambda ctx: ctx.length_of_frame),
    Anchor('frame_end_position'))

id3v2_parser = Struct(
    'id3v2',
    Magic('ID3'),
    UBInt8('major_version'),
    UBInt8('revision_number'),
    EmbeddedBitStruct(
        Flag('unsynchronisation'),
        Flag('extended_header'),
        Flag('experimental'),
        Flag('footer_present'),
        Padding(4)),
    Array(4, UBInt8('unsynchronization_length')),
    Value('length_of_tag', lambda ctx: synchsafe(ctx.unsynchronization_length)),
    Anchor('header_start_position'),
    RepeatUntil(
        lambda obj, ctx: is_last_frame(obj, ctx),
        frame_header))


if __name__ == '__main__':
    mp3_data = six.b(
        "49 44 33 04 00 00 00 00 03 2D 54 50 45 31 00 00 00 27 00 00 03 4D 61 72 69 "
        "61 6E 6E 65 20 54 68 6F 72 73 65 6E 20 2F 20 54 72 6F 6E 64 68 65 69 6D 53 "
        "6F 6C 69 73 74 65 6E 65 00 54 58 58 58 00 00 00 21 00 00 03 41 4C 42 55 4D "
        "20 41 52 54 49 53 54 00 54 72 6F 6E 64 68 65 69 6D 53 6F 6C 69 73 74 65 6E "
        "65 00 54 49 54 32 00 00 00 33 00 00 03 56 69 6F 6C 69 6E 20 43 6F 6E 63 65 "
        "72 74 6F 20 6E 6F 2E 20 34 20 69 6E 20 44 20 6D 61 6A 6F 72 20 4B 56 20 32 "
        "31 38 20 2D 20 41 6C 6C 65 67 72 6F 00 54 58 58 58 00 00 00 23 00 00 03 43 "
        "4F 4D 4D 45 4E 54 00 32 30 30 36 20 C2 A9 20 32 4C 20 28 4C 69 6E 64 62 65 "
        "72 67 20 4C 79 64 29 00 54 43 4F 4D 00 00 00 25 00 00 03 57 4F 4C 46 47 41 "
        "4E 47 20 41 4D 41 44 45 55 53 20 4D 4F 5A 41 52 54 20 31 37 35 36 E2 80 93 "
        "31 37 39 31 00 54 44 52 4C 00 00 00 06 00 00 03 32 30 30 38 00 54 50 4F 53 "
        "00 00 00 03 00 00 03 31 00 54 43 4F 4E 00 00 00 0B 00 00 03 43 6C 61 73 73 "
        "69 63 61 6C 00 54 50 45 33 00 00 00 14 00 00 03 54 72 6F 6E 64 68 65 69 6D "
        "53 6F 6C 69 73 74 65 6E 65 00 54 41 4C 42 00 00 00 08 00 00 03 4D 4F 5A 41 "
        "52 54 00 54 58 58 58 00 00 00 0E 00 00 03 54 4F 54 41 4C 44 49 53 43 53 00 "
        "31 00 54 58 58 58 00 00 00 0F 00 00 03 54 4F 54 41 4C 54 52 41 43 4B 53 00 "
        "39 00 54 52 43 4B 00 00 00 03 00 00 03 31 00 54 53 53 45 00 00 00 0E 00 00 "
        "03 4C 61 76 66 35 34 2E 36 2E 31 30 31 00 FF FB E4 00 00 00 00 00 00 00 00 "
        "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
        "49 6E 66 6F 00 00 00 07 00 00 5A 52 01 52 B7 40 00 02 05 07 0A 0D 0F 12 14 "
        "17 1A 1C 1F 21 24 26 29 2B 2E 30 33 35 38 3B 3D 40 42 45 48 4A 4D 4F 52 55 "
        "57 59 5C 5E 61 63 66 69 6B 6E 70 73 76 78 7B 7D 80 83 85 88 8A 8D 8F 91 94 "
        "96 99 9C 9E A1 A4 A6 A9 AB AE B1 B3 B6 B8 BB BD C0 C2 C4 C7 CA CC CF D2 D4 "
        "D7 D9 DC DF E1 E4 E6 E9 EB EE F0 F3 F5 F8 FA FD 00 00 00 00 00 00 00 00 00 ")

    mp3_data = unhexlify(mp3_data.replace(' ', ''))

    if len(sys.argv) == 1:
        id3 = id3v2_parser.parse(mp3_data)
    else:
        f = open(sys.argv[1])
        id3 = id3v2_parser.parse(f.read())

    for frame_header in id3.frame_header:
        print frame_header.frame_identifier, frame_header.information