from construct import *
from io import BytesIO
from binascii import unhexlify
import six


byte_stream = BytesIO(
    unhexlify(
        six.b(
            "0102030405060708090a"
        )
    )
)

byte_parser = Struct(
    'byte_stream',
    UBInt8('v1'),
    UBInt8('v2')
)

while True:
    try:
        v = byte_parser.parse_stream(byte_stream)

        print v
    except FieldError, e:
        break
