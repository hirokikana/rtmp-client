#-*- coding: utf-8 -*-
import random
import time
import struct

class AMF0():
    def __init__(self, message_type, message):
        self.type_mapping = {
            'string' : 2,
            'number' : 0,
            'object' : 3
        }
        self.message_type = message_type
        self.message = message
        
    def get_byte(self):
        # type(1byte) + length(2byte) + value(length)
        if (self.message_type == 'number'):
            body = struct.pack('>d', self.message)
            byte_message = (self.type_mapping[self.message_type]).to_bytes(1,'big') + body
        elif(self.message_type == 'object'):
            byte_message = (self.type_mapping[self.message_type]).to_bytes(1,'big')
            for object_key in self.message:
                byte_message += (len(object_key)).to_bytes(2,'big') + object_key
                byte_message += (0x02).to_bytes(1,'big') + (len(self.message[object_key])).to_bytes(2,'big')  + self.message[object_key] # TODO string type
        else:
            body = self.message
            byte_message = (self.type_mapping[self.message_type]).to_bytes(1,'big') + (len(body)).to_bytes(2,'big')  + body
        return byte_message


class HandshakeMessage():
    _message = ''
    def get_message(self):
        return self._message

class RTMPHeader():
    _header_binary = None
    def __init__(self, rtmp_body, chunk_stream_id, message_type, fmt):
        if fmt == 0:
            basic_header = chunk_stream_id.to_bytes(1, 'big')
        elif fmt == 1:
            basic_header = chunk_stream_id.to_bytes(1, 'big')

        timestamp = (0).to_bytes(3,'big')
        message_length = rtmp_body.get_length()
        message_type = message_type.to_bytes(1,'big')
        if fmt == 0:
            message_stream_id = (0).to_bytes(4, 'little')
            self._header_binary = basic_header + timestamp + message_length + message_type + message_stream_id
        else:
            self._header_binary = basic_header + timestamp + message_length + message_type


    def get(self):
        return self._header_binary

class RTMPBody():
    _body_binary = None
    def __init__(self, body_binary):
        self._body_binary = body_binary

    def get_length(self):
        return len(self._body_binary).to_bytes(3, 'big')

    def get(self):
        return self._body_binary

class ConnectMessage():
    _header = None
    _body = None
    def __init__(self, connect_param):
        self._body = RTMPBody(AMF0('string', b'connect').get_byte() + AMF0('number', 1).get_byte() + AMF0('object', connect_param).get_byte() + 0x09.to_bytes(3,'big'))
        self._header = RTMPHeader(self._body, 0x03, 0x14, 0)

    def get_message(self):
        return self._header.get() + self._body.get()

class PlayMessage():
    _header = None
    _body = None
    
    def __init__(self):
        self._body = RTMPBody(AMF0('string', b'play').get_byte() + AMF0('number', 5).get_byte() + (0x05).to_bytes(1,'big') + AMF0('string', b'test').get_byte())
        self._header = RTMPHeader(self._body, 0x08, 0x14, 0)

    def get_message(self):
        return self._header.get() + self._body.get()

class CreateStreamMessage():
    _header = None
    _body = None

    def __init__(self):
        self._body = RTMPBody(AMF0('string', b'createStream').get_byte() + AMF0('number', 4).get_byte() + (0x05).to_bytes(1,'big'))
        self._header = RTMPHeader(self._body, 0x43, 0x14, 1)

    def get_message(self):
        return self._header.get() + self._body.get()

class PublishMessage():
    _header = None
    _body = None

    def __init__(self, app, stream):
        self._body = RTMPBody(AMF0('string', b'publish').get_byte() +
                              AMF0('number', 5).get_byte() +
                              (0x05).to_bytes(1,'big') + 
                              AMF0('string', stream).get_byte() +
                              AMF0('string', app).get_byte()
                              )
        self._header = RTMPHeader(self._body, 0x8, 0x14, 0)

    def get_message(self):
        return self._header.get() + self._body.get()
                              
    
class C0S0():
    _version = 3
    def __init__(self):
        self._message = self._version.to_bytes(1, 'little')
    
    def get_version(self):
        return self._version

    def get_message(self):
        return self._message

class C1S1():
    _timestamp = 0
    _random = 0
    _zero = 0
    def __init__(self, timestamp):
        self._timestamp = timestamp
        self._random = random.getrandbits(1528 * 8)
        self._zero = 0
        self._message = self._timestamp.to_bytes(4, 'big') + self._zero.to_bytes(4, 'little') + self._random.to_bytes(1528, 'little')

    def get_time(self):
        return self._timestamp

    def get_message(self):
        return self._message

