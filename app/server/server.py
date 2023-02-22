#!/usr/bin/env python3

import random

from app.interface.interface import Interface


class Server:
    """
    Starts a server in mode [BASE | NODE] with corresponding TUN device.
    """

    def __init__(self, mode: str):
        self.ip = "10.10.10.{}".format(random.randint(2, 254))
        self.mode = mode.upper()
        self.tun = Interface(self.ip, self.mode)
        if self.mode == "BASE":
            self.set_ip("10.10.10.1")
        print("Started server at {} as {}".format(self.ip, self.mode))

    def read(self) -> bytes:
        """
        Read from TUN interface.
        """
        return self.tun.read()

    def write(self, buffer: list[list]) -> bool:
        """
        Writes to TUN interface. If successful returns true, else false.
        """
        # Expect buffer[i, q: Queue]
        written = False
        for queue in buffer:
            try:
                if not queue:
                    continue
                data = queue.pop(0)
                return self.tun.write(data)
            except Exception as error:
                print("Server write(): \n{}".format(error.with_traceback))
        return written

    def set_ip(self, ip):
        """
        Sets IP of the Tun interface.
        """
        self.tun.set_ip(ip)
        self.ip = ip
