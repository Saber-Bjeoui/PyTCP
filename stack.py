#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack simulation version 0.1 - 2020, Sebastian Majewski
stack.py - main TCP/IP stack program

"""

import os
import sys
import fcntl
import time
import struct
import loguru
import threading

from udp_socket import UdpSocket
from arp_cache import ArpCache
from rx_ring import RxRing
from tx_ring import TxRing

from service_udp_echo import ServiceUdpEcho


TUNSETIFF = 0x400454CA
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

STACK_INTERFACE = b"tap7"
STACK_IP_ADDRESS = "192.168.9.7"
STACK_MAC_ADDRESS = "02:00:00:77:77:77"


class PacketHandler:
    """ Pick up and respond to incoming packets """

    from stack_ether import ether_packet_handler
    from stack_arp import arp_packet_handler
    from stack_ip import ip_packet_handler
    from stack_icmp import icmp_packet_handler
    from stack_udp import udp_packet_handler
    from stack_tcp import tcp_packet_handler

    def __init__(self, stack_mac_address, stack_ip_address, rx_ring, tx_ring, arp_cache):
        """ Class constructor """

        self.stack_ip_address = stack_ip_address
        self.stack_mac_address = stack_mac_address
        self.tx_ring = tx_ring
        self.rx_ring = rx_ring
        self.arp_cache = arp_cache
        self.logger = loguru.logger.bind(object_name="packet_handler.")

        threading.Thread(target=self.__packet_handler).start()
        self.logger.debug("Started packet handler")

    def __packet_handler(self):
        """ Thread that picks up incoming packets from RX ring and process them """

        while True:
            self.ether_packet_handler(self.rx_ring.dequeue())


def main():
    """ Main function """

    loguru.logger.remove(0)
    loguru.logger.add(
        sys.stdout,
        colorize=True,
        level="DEBUG",
        format="<green>{time:YY-MM-DD HH:mm:ss}</green> <level>| {level:7} "
        + "|</level> <level> <normal><cyan>{extra[object_name]}{function}:</cyan></normal> {message}</level>",
    )

    tap = os.open("/dev/net/tun", os.O_RDWR)
    fcntl.ioctl(tap, TUNSETIFF, struct.pack("16sH", STACK_INTERFACE, IFF_TAP | IFF_NO_PI))

    arp_cache = ArpCache(STACK_MAC_ADDRESS, STACK_IP_ADDRESS)
    rx_ring = RxRing(tap, STACK_MAC_ADDRESS)
    tx_ring = TxRing(tap, STACK_MAC_ADDRESS, arp_cache)
    PacketHandler(STACK_MAC_ADDRESS, STACK_IP_ADDRESS, rx_ring, tx_ring, arp_cache)
    UdpSocket.set_tx_ring(tx_ring)
    ServiceUdpEcho()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    sys.exit(main())
