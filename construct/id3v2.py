import sys
from construct import *


def synchsafe(values):
    return values[0] << 21 | values[1] << 14 | values[2] << 7 | values[3]


frame_header = Struct(
    'frame_header',
    String('frame_identifier', 4),
    UBInt32('size'),
    Field('flags', 2))

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
    Value('length_of_tag', lambda ctx: synchsafe(ctx.unsynchronization_length)))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Usage: python id3v2.py [MP3 Filename]"
        sys.exit(1)

    f = open(sys.argv[1])
    id3 = id3v2_parser.parse(f.read())

    print id3