import struct
import SocketServer
from base64 import b64encode
from hashlib import sha1
from mimetools import Message
from StringIO import StringIO
import traceback

from servo import *

# Constants
CUR_LEFT_THRES = -0.3
CUR_LEFT_MAX = -1.2
CUR_RIGHT_THRES = 0.3
CUR_RIGHT_MAX = 1.2
CUR_MAX_PULSE = 0.1
CUR_MIN_PULSE = 0.5

FUTURE_LEFT_THRES = 0
FUTURE_LEFT_MAX = -4
FUTURE_RIGHT_THRES = 0
FUTURE_RIGHT_MAX = 4
FUTURE_MAX_PULSE = 0.1
FUTURE_MIN_PULSE = 0.7

CUR_LEFT_PIN = 2
CUR_RIGHT_PIN =0

FUTURE_LEFT_PIN = 8
FUTURE_RIGHT_PIN = 6

running = True

def process(input):

    # testing
    # pulse(1,0.2)

    try:
        cur = float(input.split(",")[0])
        future = float(input.split(",")[1])
        print "Current - %f, Future - %f" % (cur, future)
        # if(cur < -0.3):
        #     down(0)
        # else:
        #     up(0)

        # if(cur > 0.3):
        #     down(2)
        # else:
        #     up(2)

        if(True):
            if(cur < CUR_LEFT_THRES):
                pulse_v = ((((cur - CUR_LEFT_THRES)/(CUR_LEFT_MAX - CUR_LEFT_THRES))) * (CUR_MAX_PULSE-CUR_MIN_PULSE)) + CUR_MIN_PULSE
                print("left pulse - %f" % pulse_v)
                pulse(CUR_LEFT_PIN, pulse_v)
                pulse(CUR_RIGHT_PIN, 0)
            elif(cur > CUR_RIGHT_THRES):
                pulse_v = ((((cur - CUR_RIGHT_THRES)/(CUR_RIGHT_MAX - CUR_RIGHT_THRES))) * (CUR_MAX_PULSE-CUR_MIN_PULSE)) + CUR_MIN_PULSE
                print("right pulse - %f " % pulse_v)
                pulse(CUR_RIGHT_PIN, pulse_v)
                pulse(CUR_LEFT_PIN, 0)
            else:
                pulse(CUR_LEFT_PIN, 0)
                pulse(CUR_RIGHT_PIN, 0)

            if(future < FUTURE_LEFT_THRES):
                print "Future left"
                f_pulse_v = ((((future - FUTURE_LEFT_THRES)/(FUTURE_LEFT_MAX - FUTURE_LEFT_THRES))) * (FUTURE_MAX_PULSE-FUTURE_MIN_PULSE)) + FUTURE_MIN_PULSE
                print("future left pulse - %f" % f_pulse_v)
                pulse(FUTURE_LEFT_PIN, f_pulse_v)
                pulse(FUTURE_RIGHT_PIN, 0)
            elif(future > FUTURE_RIGHT_THRES):
                print "Future right"
                f_pulse_v = ((((future - FUTURE_RIGHT_THRES)/(FUTURE_RIGHT_MAX - FUTURE_RIGHT_THRES))) * (FUTURE_MAX_PULSE-FUTURE_MIN_PULSE)) + FUTURE_MIN_PULSE
                print("right pulse - %f " % f_pulse_v)
                pulse(FUTURE_RIGHT_PIN, f_pulse_v)
                pulse(FUTURE_LEFT_PIN, 0)
            else:
                print "Future null"
                pulse(FUTURE_LEFT_PIN, 0)
                pulse(FUTURE_RIGHT_PIN, 0)

    except Exception as e:
        print e
        traceback.print_exc()


class WebSocketsHandler(SocketServer.StreamRequestHandler):
    magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

    def setup(self):
        SocketServer.StreamRequestHandler.setup(self)
        print "connection established", self.client_address
        self.handshake_done = False

    def handle(self):
        while True:
            if not self.handshake_done:
                self.handshake()
            else:
                self.read_next_message()

    def read_next_message(self):
        length = ord(self.rfile.read(2)[1]) & 127
        if length == 126:
            length = struct.unpack(">H", self.rfile.read(2))[0]
        elif length == 127:
            length = struct.unpack(">Q", self.rfile.read(8))[0]
        masks = [ord(byte) for byte in self.rfile.read(4)]
        decoded = ""
        for char in self.rfile.read(length):
            decoded += chr(ord(char) ^ masks[len(decoded) % 4])
        self.on_message(decoded)

    def send_message(self, message):
        self.request.send(chr(129))
        length = len(message)
        if length <= 125:
            self.request.send(chr(length))
        elif length >= 126 and length <= 65535:
            self.request.send(126)
            self.request.send(struct.pack(">H", length))
        else:
            self.request.send(127)
            self.request.send(struct.pack(">Q", length))
        self.request.send(message)

    def handshake(self):
        data = self.request.recv(1024).strip()
        headers = Message(StringIO(data.split('\r\n', 1)[1]))
        if headers.get("Upgrade", None) != "websocket":
            return
        print 'Handshaking...'
        key = headers['Sec-WebSocket-Key']
        digest = b64encode(sha1(key + self.magic).hexdigest().decode('hex'))
        response = 'HTTP/1.1 101 Switching Protocols\r\n'
        response += 'Upgrade: websocket\r\n'
        response += 'Connection: Upgrade\r\n'
        response += 'Sec-WebSocket-Accept: %s\r\n\r\n' % digest
        self.handshake_done = self.request.send(response)

    def on_message(self, message):
        print "Message Received - ",message
        process(message)

if __name__ == "__main__":
    SocketServer.TCPServer.allow_reuse_address = True
    server = SocketServer.TCPServer(
        ("192.168.43.44", 9999), WebSocketsHandler)
    print "Serving..."
    server.serve_forever()
