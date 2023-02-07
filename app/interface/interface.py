"""Contains code for generating, and controlling a network interface in RPi OS using TUN."""

import os
import fcntl
import struct
import subprocess


class Interface:
    """An interface object representing a virtual network interface."""

    def __init__(self, ip_address, mode):
        # Tun Attributes
        self.iface = "longge"
        self.mode = mode
        self.mtu = 1500
        self.ip_address = ip_address

        # Tun byte shorthands
        TUNSETIFF = 0x400454CA
        TUNSETOWNER = TUNSETIFF + 2
        IFF_TUN = 0x0001
        IFF_NO_PI = 0x1000

        # Opens already existing TUN interface
        self.tun = open("/dev/net/tun", "r+b", 0)
        ifr = struct.pack("16sH", bytes(self.iface, "utf-8"), IFF_TUN | IFF_NO_PI)
        fcntl.ioctl(self.tun, TUNSETIFF, ifr)
        fcntl.ioctl(self.tun, TUNSETOWNER, 1000)

        # Sets default values for TUN interface
        self.__set_interface(self.ip_address)

    def __del__(self):
        self.tun.close()
        subprocess.check_call("ip link delete dev {}".format(self.iface))

    def read(self):
        """Reads the data in the interface pipe."""
        packet = os.read(self.tun.fileno(), self.mtu)
        return packet

    def write(self, data) -> bool:
        """Writes to the interface data pipe."""
        written = os.write(self.tun.fileno(), data)
        if written != 0:
            return True
        return False

    def set_ip(self, ip_address):
        """
        Sets the IP address of the server and TUN interface.
        """
        cmd_remove = "ip addr del {}/24 dev {}".format(self.ip_address, self.iface)
        cmd_add = "ip addr add {}/24 dev {}".format(ip_address, self.iface)
        cmd_route_remove = "ip route delete default via {}/24 dev {}".format(
            ip_address, self.iface
        )
        cmd_route_add = "ip route add default via {}/24 dev {}".format(
            ip_address, self.iface
        )
        subprocess.check_call(cmd_remove, shell=True)
        subprocess.check_call(cmd_add, shell=True)
        if self.mode == "NODE":
            subprocess.check_call(cmd_route_remove, shell=True)
            subprocess.check_call(cmd_route_add, shell=True)
        self.ip_address = ip_address

    def __set_interface(self, ip_address):
        """
        Applies settings to the TUN interface.
        """
        cmd_mtu = "mtu {}".format(self.mtu)
        cmd = "ip link set {} {}".format(self.iface, cmd_mtu)
        cmd_ip = "ip addr add {}/24 dev {}".format(ip_address, self.iface)
        cmd_up = "ip link set {} up".format(self.iface)
        subprocess.check_call(cmd_ip, shell=True)
        subprocess.check_call(cmd, shell=True)
        subprocess.check_call(cmd_up, shell=True)
        self.ip_address = ip_address
        self.__routing_init()

    def __routing_init(self):
        """
        Applies routing rules depending on operating mode.
        """
        cmd_base_a = "iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"
        cmd_base_b = "iptables -A FORWARD -i eth0 -o {} -m state --state RELATED,ESTABLISHED -j ACCEPT".format(
            self.iface
        )
        cmd_base_c = "iptables -A FORWARD -i {} -o eth0 -j ACCEPT".format(self.iface)

        cmd_node = "ip route add 8.8.8.8 via {} dev {}".format(
            self.ip_address, self.iface
        )

        self.__enable_forwarding()

        if self.mode == "BASE":
            try:
                subprocess.check_call(cmd_base_a, shell=True)
                subprocess.check_call(cmd_base_b, shell=True)
                subprocess.check_call(cmd_base_c, shell=True)
            except subprocess.CalledProcessError as error:
                print(error.output)
        else:
            try:
                subprocess.check_call(cmd_node, shell=True)
            except subprocess.CalledProcessError as error:
                print(error.output)

    def __enable_forwarding(self):
        old = "#net.ipv4.ip_forward=1"
        new = "net.ipv4.ip_forward=1"
        cmd = "sed -i 's/{}/{}/g' /etc/sysctl.conf".format(old, new)
        subprocess.check_call(cmd, shell=True)
        subprocess.check_call("sysctl -p", shell=True, stdout=subprocess.DEVNULL)
