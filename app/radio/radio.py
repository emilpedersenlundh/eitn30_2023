#!/usr/bin/env python3

import time
import struct
from RF24 import RF24
from app.radio.attributes import *
from app.radio.setup import setup
from app.utilities import fragment


class Radio:
    def __init__(self, mode):
        self.tx_radio = RF24(SPI0["ce"], SPI0["SPI"])
        self.rx_radio = RF24(SPI1["ce"], SPI1["SPI"])
        setup(self.tx_radio, mode)
        setup(self.rx_radio, mode)
        self.received: int = 0
        self.transmitted: int = 0
        self.dropped: int = 0

    def transmit(self, address, data) -> bool:
        if not data:
            return False

        self.tx_radio.openWritingPipe(address)
        # print("Opened writing pipe with address: {}".format(address))

        status = []
        chunks = []

        start = time.monotonic()

        # Fragment the data into chunks (n chunks * chunk size (30) matrix, each line is a chunk)
        if len(data) > 30:
            chunks = fragment(data)
            fragment_enabled = True

        else:
            chunks.append(data)
            fragment_enabled = False

        self.tx_radio.stopListening()

        if not fragment_enabled:
            id = 0

            buffer = bytes(chunks[0])
            buffer += struct.pack(">H", id)
            result = self.tx_radio.write(buffer, False)

            if not result:
                status.append(False)
                self.dropped += 1
                return False

            else:
                status.append(True)
                self.transmitted += 1

        # Otherwise send all available chunks and append id > 0
        else:
            id = 1
            nbr_chunks = len(chunks)

            # Data available to send
            for index, chunk in enumerate(chunks):
                # Last fragment part will have id 0
                if index == len(chunks) - 1:
                    id = 0

                buffer = bytes(chunk)
                buffer += struct.pack(">H", id)

                # Send all chunks one at a time
                result = self.tx_radio.write(buffer, False)

                if not result:
                    status.append(False)
                    return False

                else:
                    status.append(True)

                id += 1

        total_time = time.monotonic() - start

        if fragment_enabled:
            bps = nbr_chunks * len(chunks[0]) * 8 * len(status) / total_time
            # print('{} successful transmissions, {} failures, {} bps\n'.format(sum(status), len(status)-sum(status), bps), end='\r')

        else:
            bps = len(chunks[0]) * 8 * len(status) / total_time
            # print('{} successful transmissions, {} failures, {} bps\n'.format(sum(status), len(status)-sum(status), bps), end='\r')

        self.transmitted += sum(status)
        self.dropped += len(status) - sum(status)

        return True

    def receive(self, timeout, data_buffer) -> bool:
        # print('Rx NRF24L01+ started w/ power {}, SPI freq: {}hz'.format(self.rx_radio.getPALevel(), SPI_SPEED))

        nbr_pipes = 6  # len(ip_table)
        fragmented = [False for _ in range(nbr_pipes)]
        fragment_buffer = [[] for _ in range(nbr_pipes)]
        id_offset = 2  # 2bytes for id
        id = (0, 0)  # (cur, prev)

        self.rx_radio.startListening()
        start = time.time()

        while time.time() - start < timeout:
            # Checks if there are bytes available for read
            payload_available, pipe_nbr = self.rx_radio.available_pipe()
            payload = []

            if payload_available:
                payload_size = self.rx_radio.getDynamicPayloadSize()
                payload = self.rx_radio.read(payload_size)

                id = (
                    struct.unpack(
                        ">H", payload[payload_size - id_offset : payload_size]
                    )[0],
                    id[0],
                )

                if id[0] > 0:
                    if id[0] == 1:
                        # First fragment
                        fragmented[pipe_nbr] = True

                    if fragmented[pipe_nbr]:
                        if id[0] - id[1] == 1 or id[0] == 1:
                            fragment_buffer[pipe_nbr].append(
                                bytes(payload[: payload_size - id_offset])
                            )

                        else:
                            print(
                                "Fragmentation order corrupt (current id: {}, previous id: {}), discarding packet..".format(
                                    id[0], id[1]
                                )
                            )

                elif id[0] == 0:
                    if fragmented[pipe_nbr]:
                        # Last fragmented packet, remove id and padding
                        padding_size = payload[payload_size - id_offset - 1]
                        fragment_buffer[pipe_nbr].append(
                            bytes(payload[: payload_size - padding_size - id_offset])
                        )

                        # Add all fragments to one element in the buffer
                        data_buffer[pipe_nbr].append(
                            b"".join(fragment_buffer[pipe_nbr])
                        )
                        fragment_buffer[pipe_nbr].clear()
                        fragmented[pipe_nbr] = False

                    else:
                        # Single packet, not fragmented
                        data_buffer[pipe_nbr].append(
                            bytes(payload[: payload_size - id_offset - 1])
                        )

                    return True

                else:
                    print("Invalid id..")
                    return False

        # Timeout
        print("Timeout")
        self.rx_radio.stopListening()
        return False
