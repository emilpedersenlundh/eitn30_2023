SPI0 = {"SPI": 0, "MOSI": 10, "MISO": 9, "clock": 11, "ce": 17, "csn": 8}
SPI1 = {"SPI": 10, "MOSI": 20, "MISO": 19, "clock": 21, "ce": 27, "csn": 18}

PIPE_ADDRESSES = [
    b"\xE7\xD3\xF0\x35\x77",
    b"\xC2\xC2\xC2\xC2\xC2",
    b"\xC2\xC2\xC2\xC2\xC3",
    b"\xC2\xC2\xC2\xC2\xC4",
    b"\xC2\xC2\xC2\xC2\xC5",
    b"\xC2\xC2\xC2\xC2\xC6",
]

SPI_SPEED = 10000000  # Hz
CHANNEL = 76  # 2.4G + channel Hz
A_WIDTH = 5  # 2-5 bytes
RT_DELAY = 0  # 0-15 (250-4000 microseconds)
RT_LIMIT = 15  # 0-15 (0 = Disabled)
