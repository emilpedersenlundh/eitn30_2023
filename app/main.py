#!/usr/bin/env python3

from app.radio.radio import Radio
from app.server.server import Server
from app.utilities import define_mode


def main():
    pass
    # TODO:
    # Start server (which starts an interface)
    # Start radio
    #
    # If mode is base:
    # Listen on radio until data is received
    # Write data to server
    # Wait for response from server
    # Transmit response through radio
    #
    # If mode is node:
    # Read server until non-zero data is retrieved
    # Transmit data through radio
    # Listen on radio until data is received
    # Write data to server


if __name__ == "__main__":
    main()
