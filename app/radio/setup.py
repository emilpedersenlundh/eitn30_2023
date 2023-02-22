#!/usr/bin/env python3

from RF24 import RF24_PA_MAX, RF24_2MBPS, RF24_CRC_16

# Unused RF24 imports
# RF24,
# RF24_CRC_DISABLED,
# RF24_CRC_8,
# RF24_PA_LOW,

from app.radio.attributes import *


def setup(radio, mode):
    """
    Starts radio module and applies settings.
    """
    if not radio.begin():
        radio.printPrettyDetails()
        raise RuntimeError("Radio module is inactive.")

    # Set power amplifier level
    radio.setPALevel(RF24_PA_MAX)

    # Set payload size (dynamic/static)
    radio.enableDynamicPayloads()

    # Set CRC encoding
    radio.setCRCLength(RF24_CRC_16)

    # Set CRC enable/disable
    # radio.disableCRC()

    # Set auto-ACK (If false: CRC has to be disabled)
    radio.setAutoAck(True)

    # Set address A_WIDTH
    radio.setAddressWidth(A_WIDTH)

    # Set auto-retransmit delay & limit
    radio.setRetries(RT_DELAY, RT_LIMIT)

    # Set channel
    radio.setChannel(CHANNEL)

    # Set data rate
    radio.setDataRate(RF24_2MBPS)

    # Open pipes
    for pipe, address in enumerate(PIPE_ADDRESSES):
        if mode == "BASE":
            radio.openReadingPipe(pipe, address)
            # print("Opened reading pipe: {} with address: {}".format(pipe, address))
    radio.openWritingPipe(PIPE_ADDRESSES[0])
    # print("Opened writing pipe with address: {}".format(address))

    # Flush buffers
    radio.flush_rx()
    radio.flush_tx()
