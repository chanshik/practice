from construct import *
from binascii import unhexlify
import sys
import six
import pprint


class PrintContext(Construct):
    """
    Print current context structure.
    """
    def _parse(self, stream, context):
        print "\n# PrintContext ---"
        pprint.pprint(context)
        print "# --- PrintContent\n"


def enum_block_type(block_type):
    return Enum(block_type,
                STREAMINFO=0,
                PADDING=1,
                APPLICATION=2,
                SEEKTABLE=3,
                VORBIS_COMMENT=4,
                CUESHEET=5,
                PICTURE=6,
                INVALID=127)

metadata_block_header = BitStruct('metadata_block_header',
                                  Flag('last_metadata_block'),
                                  enum_block_type(BitField('block_type', 7)),
                                  BitField('length', 24))

metadata_streaminfo = BitStruct('streaminfo',
                                BitField('minimum_block_size', 16),
                                BitField('maximum_block_size', 16),
                                BitField('minimum_frame_size', 24),
                                BitField('maximum_frame_size', 24),
                                BitField('sample_rate', 20),
                                BitField('number_of_channels_minus_1', 3),
                                Value('number_of_channels', lambda ctx: ctx.number_of_channels_minus_1 + 1),
                                BitField('bits_per_sample_minus_1', 5),
                                Value('bits_per_sample', lambda ctx: ctx.bits_per_sample_minus_1 + 1),
                                BitField('total_samples', 36),
                                BitField('md5_signature', 128))

metadata_vorbis_comment = Struct('vorbis_comment',
                                 PascalString('vendor_string',
                                              length_field=ULInt32('vendor_length')),
                                 ULInt32('user_comment_list_length'),
                                 Array(lambda ctx: ctx.user_comment_list_length,
                                       PascalString('user_comment',
                                                    length_field=ULInt32('user_comment_length'))))

metadata_padding = Struct('padding',
                          Padding(lambda ctx: ctx['_'].header.length))

metadata_application = Struct('application',
                              UBInt32('registered_application_id'),
                              Field('application_data', lambda ctx: ctx['_'].header.length))

seekpoint = Struct('seekpoint',
                   UBInt64('sample_number_of_first_sample'),
                   UBInt64('offset'),
                   UBInt16('number_of_samples'))

metadata_seektable = Struct('seektable',
                            Array(lambda ctx: ctx['_'].header.length / 8,
                                  seekpoint))

cuesheet_track_index = Struct('cuesheet_track_index',
                              UBInt64('offset_in_samples'),
                              UBInt8('index_point_number'),
                              Padding(3))

cuesheet_track = Struct('cuesheet_track',
                        UBInt64('track_offset'),
                        UBInt8('track_number'),
                        String('ISRC', 12),
                        EmbeddedBitStruct(
                            Flag('track_type'),
                            Flag('pre-emphasis'),
                            Padding(6)
                        ),
                        Padding(13),
                        UBInt8('number_of_track_index_points'),
                        Array(lambda ctx: ctx.number_of_track_index_points,
                              cuesheet_track_index))

metadata_cuesheet = Struct('cuesheet',
                           String('media_catalog_number', 128),
                           UBInt64('number_of_lead_in_samples'),
                           EmbeddedBitStruct(
                               Flag('is_compact_disc'),
                               Padding(7)),
                           Padding(258),
                           UBInt8('number_of_tracks'),
                           Array(lambda ctx: ctx.number_of_tracks,
                                 cuesheet_track)
                           )

metadata_picture = Struct('picture',
                          UBInt32('picture_type'),
                          UBInt32('length_of_mime'),
                          String('mime', lambda ctx: ctx.length_of_mime),
                          UBInt32('length_of_description'),
                          String('description', lambda ctx: ctx.length_of_description),
                          UBInt32('width'),
                          UBInt32('height'),
                          UBInt32('bits_per_pixel'),
                          UBInt32('number_of_colors'),
                          UBInt32('length_of_picture'),
                          Field('picture_data', lambda ctx: ctx.length_of_picture)
                          )

metadata_block = Struct('metadata_block',
                        Rename('header', metadata_block_header),
                        Switch('metadata', lambda ctx: ctx['header'].block_type,
                               {
                                   'STREAMINFO': metadata_streaminfo,
                                   'VORBIS_COMMENT': metadata_vorbis_comment,
                                   'PADDING': metadata_padding,
                                   'APPLICATION': metadata_application,
                                   'SEEKTABLE': metadata_seektable,
                                   'CUESHEET': metadata_cuesheet,
                                   'PICTURE': metadata_picture
                               }
                        ))

flac = Struct('flac',
              Magic('fLaC'),
              RepeatUntil(
                  lambda obj, ctx: obj.header.last_metadata_block is True,
                  metadata_block
              ))

if __name__ == '__main__':
    flac_data = "66 4C 61 43 00 00 00 22 10 00 10 00 00 0D 2E 00 44 E7 17 70 03 " \
                "70 03 2C D5 00 60 54 95 D1 1E DB 8E DA 81 C5 61 34 6B BA F8 77 " \
                "04 00 01 9D 20 00 00 00 72 65 66 65 72 65 6E 63 65 20 6C 69 62 " \
                "46 4C 41 43 20 31 2E 32 2E 31 20 32 30 30 37 30 39 31 37 0D 00 " \
                "00 00 0C 00 00 00 41 4C 42 55 4D 3D 4D 4F 5A 41 52 54 1F 00 00 " \
                "00 41 4C 42 55 4D 20 41 52 54 49 53 54 3D 54 72 6F 6E 64 68 65 " \
                "69 6D 53 6F 6C 69 73 74 65 6E 65 2C 00 00 00 41 52 54 49 53 54 " \
                "3D 4D 61 72 69 61 6E 6E 65 20 54 68 6F 72 73 65 6E 20 2F 20 54 " \
                "72 6F 6E 64 68 65 69 6D 53 6F 6C 69 73 74 65 6E 65 21 00 00 00 " \
                "43 4F 4D 4D 45 4E 54 3D 32 30 30 36 20 C2 A9 20 32 4C 20 28 4C " \
                "69 6E 64 62 65 72 67 20 4C 79 64 29 2C 00 00 00 43 4F 4D 50 4F " \
                "53 45 52 3D 57 4F 4C 46 47 41 4E 47 20 41 4D 41 44 45 55 53 20 " \
                "4D 4F 5A 41 52 54 20 31 37 35 36 E2 80 93 31 37 39 31 09 00 00 " \
                "00 44 41 54 45 3D 32 30 30 38 0C 00 00 00 44 49 53 43 4E 55 4D " \
                "42 45 52 3D 31 0F 00 00 00 47 45 4E 52 45 3D 43 6C 61 73 73 69 " \
                "63 61 6C 1C 00 00 00 50 45 52 46 4F 52 4D 45 52 3D 54 72 6F 6E " \
                "64 68 65 69 6D 53 6F 6C 69 73 74 65 6E 65 37 00 00 00 54 49 54 " \
                "4C 45 3D 56 69 6F 6C 69 6E 20 43 6F 6E 63 65 72 74 6F 20 6E 6F " \
                "2E 20 34 20 69 6E 20 44 20 6D 61 6A 6F 72 20 4B 56 20 32 31 38 " \
                "20 2D 20 41 6C 6C 65 67 72 6F 0C 00 00 00 54 4F 54 41 4C 44 49 " \
                "53 43 53 3D 31 0D 00 00 00 54 4F 54 41 4C 54 52 41 43 4B 53 3D " \
                "39 0D 00 00 00 54 52 41 43 4B 4E 55 4D 42 45 52 3D 31 81 00 00 " \
                "14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 "
    flac_data = six.b(flac_data).replace(' ', '')

    try:
        if len(sys.argv) == 1:
            f = flac.parse(unhexlify(flac_data))
        else:
            f = flac.parse(open(sys.argv[1]).read())
    except SwitchError:
        pass

    print f.metadata_block[0]  # May be 'STREAMINFO'
    print f.metadata_block[1]  # May be 'VORBIS_COMMENT'