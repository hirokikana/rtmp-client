# -*- coding: utf-8 -*-

class amf0Parse():
    def __init__(self, binary):
        result = []
        byteio = io.BytesIO(binary)
        while(True):
            message_type = byteio.read(1)
            if (message_type == b''):
                break
            if (int(message_type.hex(),16) == 2):
                length = byteio.read(2)
                body = byteio.read(int(length.hex(), 16))
            elif (int(message_type.hex(),16) == 3):
                body = self._object_parse(byteio)
            else:
                body = byteio.read(8)
            result.append(body)
        self.parsed = result

    def get(self):
        return self.parsed
        
    def _object_parse(self, byteio):
        result = {}
        while(True):
            key_length = byteio.read(2)
            if (int(key_length.hex(),16) == 0 and int(byteio.read(1).hex(),16) == 9):
                break
            key_body = byteio.read(int(key_length.hex(), 16))
            value_amf0_type = byteio.read(1)
            if (int(value_amf0_type.hex(), 16) == 2):
                # string
                value_length = byteio.read(2)
                value_body = byteio.read(int(value_length.hex(), 16))
            else:
                value_body = byteio.read(8)

            result[key_body] = value_body
        return result

class amf0():
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
