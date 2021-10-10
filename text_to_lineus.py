#!/usr/bin/python3
import os
import re
import socket
import time
import logging
from typing import Union
from text_to_gcode import readLetters, textToGcode
logging.basicConfig(level="DEBUG")
LETTERS_DIR = os.path.join(os.path.dirname(__file__), "ascii_gcode")
SCALE = 20.0
START = 800, 600

def text_to_lineus_gcode(text="hello", directory=LETTERS_DIR, line_length=1000):
    letters = readLetters(directory)
    gcode = textToGcode(letters, text, line_length/SCALE, 8.0, 1.5)
    new_gcode = []
    for line in (l.strip() for l in gcode.splitlines()):
        if line == "":
            continue
        m = re.match(r"G([01]) X(-?[0-9]+\.[0-9]+) Y(-?[0-9]+\.[0-9]+)",line)
        assert m is not None
        t,x,y = m.groups()
        X, Y = [float(a)*SCALE + s for a, s in zip([x, y], START)]
        if t == "0":
            new_gcode.append(f"G01 X{X} Y{Y} Z1000")
        new_gcode.append(f"G01 X{X} Y{Y} Z0")
    return "\n".join(new_gcode)

class LineUs:
    """An example class to show how to use the Line-us API"""

    def __init__(self, line_us_name: str):
        self.__line_us = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__line_us.connect((line_us_name, 1337))
        self.__connected = True
        self.__hello_message = self.__read_response()
        time.sleep(0.5)

    def get_hello_string(self):
        if self.__connected:
            return self.__hello_message.decode()
        return 'Not connected'

    def disconnect(self):
        """Close the connection to the Line-us"""
        self.__line_us.close()
        self.__connected = False

    def g01(self, x: Union[float, str], y: Union[float, str], z: Union[float, str]):
        """Send a G01 (interpolated move), and wait for the response before returning"""
        self.__send_command(f"G01 X{x} Y{y} Z{z}".encode())
        logging.info(self.__read_response())

    def __read_response(self):
        """Read from the socket one byte at a time until we get a null"""
        line = b''
        while len(line)==0 or line[-1] != 0:
            line += self.__line_us.recv(1)
        logging.info(f"Response: {line}")
        return line[:-1]

    def __send_command(self, command: bytes):
        """Send the command to Line-us"""
        self.__line_us.send(command + b"\x00")

    def send_gcode(self, gcode: str):
        for line in gcode.splitlines():
            cmd = line.strip().upper().encode()
            if cmd == b"":
                continue
            logging.info(f"Sending: {cmd}")
            self.__send_command(cmd)
            logging.info(self.__read_response())

    def write_msg(self,text="hello"):
        gcode = text_to_lineus_gcode(text=text)
        self.send_gcode(gcode)




if __name__ == "__main__":
    pass
    gcode = text_to_lineus_gcode(text="hello")
    lineus = LineUs("192.168.1.212")
    lineus.send_gcode(gcode)
