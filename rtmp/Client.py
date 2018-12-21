# -*- coding: utf-8 -*-
from rtmp import Message
import time

class Client:
    _sock = None
    
    def __init__(self, sock):
        self._sock = sock
        
    def do_handshake(self):
        sock = self._sock 
        # send c0c1
        c0 = Message.C0S0()
        c1 = Message.C1S1(int(time.time()))
        sock.sendall(c0.get_message() + c1.get_message())
        # recv s0
        s0 = sock.recv(1)

        # recv s1
        s1_time = sock.recv(4)
        s1_zero = sock.recv(4)
        s1_random = sock.recv(1528)

        # recv s2
        s2_time = sock.recv(4)
        #print('  time: %s' % int(s2_time.hex(), 16))
        s2_time2 = sock.recv(4)
        #print('  time2: %s' % int(s2_time2.hex(), 16))
        s2_random = sock.recv(1528)
        
        # send c2
        sock.sendall(s2_time + s2_time + s2_random)
        return True
        
    def do_connect(self):
        sock = self._sock
        connect_message = Message.ConnectMessage({
            b'app':b'live',
            b'tcUrl': b'rtmp://localhost:1935/live',
            b'flashVer': b'FMLE/3.0 (compatible; Lavf58.20.100)'
        })
        sock.sendall(connect_message.get_message())
        
        # result
        self._recv(sock)
        self._recv(sock)
        self._recv(sock)
        #result = amf0Parse(self._recv(sock)).get()[3]
        self._recv(sock)
        #return result[b'code'] == b'NetConnection.Connect.Success'

    def do_createstream(self):
        sock = self._sock
        createstream_message = Message.CreateStreamMessage()
        sock.sendall(createstream_message.get_message())
        self._recv(sock)

    def do_publish(self):
        sock = self._sock
        publish_message = Message.PublishMessage(b'live', b'test')
        sock.sendall(publish_message.get_message())
        self._recv(sock)

    def do_send_anydata(self, data):
        sock = self._sock
        rtmp_body = data

        chunk_stream_id = (0x06).to_bytes(1,'big')
        timestamp = (0).to_bytes(3, 'big')
        message_length = len(rtmp_body).to_bytes(3, 'big')
        message_type = (9).to_bytes(1,'big') # audio data type
        message_stream_id = (1).to_bytes(4, 'little')

        chunk_header = timestamp + message_length + message_type + message_stream_id

        sock.sendall(chunk_stream_id + chunk_header + rtmp_body)

    def do_set_chunk_size(self, sock, size):
        rtmp_body = size.to_bytes(4,'big')

        chunk_stream_id = (0x02).to_bytes(1,'big')
        timestamp = (0).to_bytes(3,'big')
        message_length = len(rtmp_body).to_bytes(3, 'big')
        message_type = (1).to_bytes(1,'big')
        message_stream_id = (0).to_bytes(4, 'little')
        
        chunk_header = timestamp + message_length + message_type + message_stream_id

        sock.sendall(chunk_stream_id + chunk_header + rtmp_body)

    def do_play(self):
        sock = self._sock

        play_message = Message.PlayMessage()

        sock.sendall(play_message.get_message())
        status = self._recv(sock)
        sampleaccess = self._recv(sock)
    
    def _recv(self,sock):
        chunk_stream_id = sock.recv(1) # TODO fmt!=0
        timestamp = sock.recv(3)
        message_length = sock.recv(3)
        message_type_id = sock.recv(1)
        message_stream_id = sock.recv(4)
        body = sock.recv(int(message_length.hex(), 16))
        return body
    
