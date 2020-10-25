#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack simulation version 0.1 - 2020, Sebastian Majewski
ph.py - protocol support for incoming and outgoing packets

"""

import loguru
import threading


class PacketHandler:
    """ Pick up and respond to incoming packets """

    from phrx_ether import phrx_ether
    from phrx_arp import phrx_arp
    from phrx_ip import phrx_ip
    from phrx_icmp import phrx_icmp
    from phrx_udp import phrx_udp
    from phrx_tcp import phrx_tcp

    from phtx_ether import phtx_ether
    from phtx_arp import phtx_arp
    from phtx_ip import phtx_ip
    from phtx_icmp import phtx_icmp
    from phtx_udp import phtx_udp
    from phtx_tcp import phtx_tcp

    def __init__(self, stack_mac_address, stack_ip_address, rx_ring, tx_ring, arp_cache):
        """ Class constructor """

        self.stack_mac_address = stack_mac_address
        self.stack_ip_address = stack_ip_address
        self.tx_ring = tx_ring
        self.rx_ring = rx_ring
        self.arp_cache = arp_cache
        self.logger = loguru.logger.bind(object_name="packet_handler.")

        # Update ARP cache object with reference to this packet handler so ARP cache can send out ARP requests
        self.arp_cache.packet_handler = self

        threading.Thread(target=self.__packet_handler).start()
        self.logger.debug("Started packet handler")

    def __packet_handler(self):
        """ Thread that picks up incoming packets from RX ring and process them """

        while True:
            self.phrx_ether(self.rx_ring.dequeue())