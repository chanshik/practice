from construct import *
from binascii import unhexlify
import six


# from construct/protocol/layer3/ipv4.py
class IpAddressAdapter(Adapter):
    def _encode(self, obj, context):
        if bytes is str:
            return "".join(chr(int(b)) for b in obj.split("."))
        else:
            return bytes(int(b) for b in obj.split("."))
    def _decode(self, obj, context):
        if bytes is str:
            return ".".join(str(ord(b)) for b in obj)
        else:
            return ".".join("%d" % (b,) for b in obj)


def ip_address(name):
    return IpAddressAdapter(Bytes(name, 4))

ip_packet = Struct(
    'ip_packet',
    Embed(
        Union(
            'ip_group',
            SBInt32('signed_ip'),
            UBInt32('unsigned_ip'),
            ip_address('ip')
        )
    ))


packet = ip_packet.parse(unhexlify(six.b('c0a80001')))

print packet