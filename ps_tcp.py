#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack simulation version 0.1 - 2020, Sebastian Majewski
ps_tct.py - protocol support libary for TCP

"""


import struct

from tracker import Tracker


"""

   TCP packet header (RFC 793)

   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                        Sequence Number                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Acknowledgment Number                      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Data |           |U|A|P|R|S|F|                               |
   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
   |       |           |G|K|H|T|N|N|                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Checksum            |         Urgent Pointer        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                             data                              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

"""


TCP_HEADER_LEN = 20


class TcpPacket:
    """ TCP packet support class """

    protocol = "TCP"

    def __init__(
        self,
        parent_packet=None,
        tcp_sport=None,
        tcp_dport=None,
        tcp_seq_num=0,
        tcp_ack_num=0,
        tcp_flag_ns=False,
        tcp_flag_crw=False,
        tcp_flag_ece=False,
        tcp_flag_urg=False,
        tcp_flag_ack=False,
        tcp_flag_psh=False,
        tcp_flag_rst=False,
        tcp_flag_syn=False,
        tcp_flag_fin=False,
        tcp_win=0,
        tcp_urp=0,
        tcp_options=[],
        raw_data=b"",
        echo_tracker=None,
    ):
        """ Class constructor """

        # Packet parsing
        if parent_packet:
            self.tracker = parent_packet.tracker

            raw_packet = parent_packet.raw_data
            raw_header = raw_packet[:TCP_HEADER_LEN]
            raw_options = raw_packet[TCP_HEADER_LEN : (raw_header[12] & 0b11110000) >> 2]

            self.raw_data = raw_packet[(raw_header[12] & 0b11110000) >> 2 :]
            self.ip_pseudo_header = parent_packet.ip_pseudo_header

            self.tcp_sport = struct.unpack("!H", raw_header[0:2])[0]
            self.tcp_dport = struct.unpack("!H", raw_header[2:4])[0]
            self.tcp_seq_num = struct.unpack("!L", raw_header[4:8])[0]
            self.tcp_ack_num = struct.unpack("!L", raw_header[8:12])[0]
            self.tcp_hlen = (raw_header[12] & 0b11110000) >> 2
            self.tcp_flag_ns = bool(raw_header[12] & 0b00000001)
            self.tcp_flag_crw = bool(raw_header[13] & 0b10000000)
            self.tcp_flag_ece = bool(raw_header[13] & 0b01000000)
            self.tcp_flag_urg = bool(raw_header[13] & 0b00100000)
            self.tcp_flag_ack = bool(raw_header[13] & 0b00010000)
            self.tcp_flag_psh = bool(raw_header[13] & 0b00001000)
            self.tcp_flag_rst = bool(raw_header[13] & 0b00000100)
            self.tcp_flag_syn = bool(raw_header[13] & 0b00000010)
            self.tcp_flag_fin = bool(raw_header[13] & 0b00000001)
            self.tcp_win = struct.unpack("!H", raw_header[14:16])[0]
            self.tcp_cksum = struct.unpack("!H", raw_header[16:18])[0]
            self.tcp_urp = struct.unpack("!H", raw_header[18:20])[0]

            self.tcp_options = []

            i = 0

            while i < len(raw_options):
                if raw_options[i] == TCP_OPT_EOL:
                    self.tcp_options.append(TcpOptEol(raw_options[i : i + TCP_OPT_EOL_LEN]))
                    break

                elif raw_options[i] == TCP_OPT_NOP:
                    self.tcp_options.append(TcpOptNop(raw_options[i : i + TCP_OPT_NOP_LEN]))
                    i += TCP_OPT_NOP_LEN

                elif raw_options[i] == TCP_OPT_MSS:
                    self.tcp_options.append(TcpOptMss(raw_options[i : i + raw_options[i + 1]]))
                    i += self.raw_options[i + 1]

                elif raw_options[i] == TCP_OPT_WSCALE:
                    self.tcp_options.append(TcpOptWscale(raw_options[i : i + raw_options[i + 1]]))
                    i += self.raw_options[i + 1]

                elif raw_options[i] == TCP_OPT_TIMESTAMP:
                    self.tcp_options.append(TcpOptTimestamp(raw_options[i : i + raw_options[i + 1]]))
                    i += self.raw_options[i + 1]

                else:
                    self.tcp_options.append(TcpOptUnk(raw_options[i : i + raw_options[i + 1]]))
                    i += self.raw_options[i + 1]

        # Packet building
        else:
            self.tracker = Tracker("TX", echo_tracker)

            self.tcp_sport = tcp_sport
            self.tcp_dport = tcp_dport
            self.tcp_seq_num = tcp_seq_num
            self.tcp_ack_num = tcp_ack_num
            self.tcp_flag_ns = tcp_flag_ns
            self.tcp_flag_crw = tcp_flag_crw
            self.tcp_flag_ece = tcp_flag_ece
            self.tcp_flag_urg = tcp_flag_urg
            self.tcp_flag_ack = tcp_flag_ack
            self.tcp_flag_psh = tcp_flag_psh
            self.tcp_flag_rst = tcp_flag_rst
            self.tcp_flag_syn = tcp_flag_syn
            self.tcp_flag_fin = tcp_flag_fin
            self.tcp_win = tcp_win
            self.tcp_cksum = 0
            self.tcp_urp = tcp_urp

            self.tcp_options = tcp_options

            self.raw_data = raw_data

            self.tcp_hlen = TCP_HEADER_LEN + len(self.raw_options)

            assert self.tcp_hlen % 4 == 0, "TCP header len is not multiplcation of 4 bytes, check options"

    @property
    def raw_header(self):
        """ Packet header in raw format """

        return struct.pack(
            "! HH L L BBH HH",
            self.tcp_sport,
            self.tcp_dport,
            self.tcp_seq_num,
            self.tcp_ack_num,
            self.tcp_hlen << 2 | self.tcp_flag_ns,
            self.tcp_flag_crw << 7
            | self.tcp_flag_ece << 6
            | self.tcp_flag_urg << 5
            | self.tcp_flag_ack << 4
            | self.tcp_flag_psh << 3
            | self.tcp_flag_rst << 2
            | self.tcp_flag_syn << 1
            | self.tcp_flag_fin,
            self.tcp_win,
            self.tcp_cksum,
            self.tcp_urp,
        )

    def __str__(self):
        """ Short packet log string """

        log = (
            f"TCP {self.tcp_sport} > {self.tcp_dport}, {'N' if self.tcp_flag_ns else ''}{'C' if self.tcp_flag_crw else ''}"
            + f"{'E' if self.tcp_flag_ece else ''}{'U' if self.tcp_flag_urg else ''}{'A' if self.tcp_flag_ack else ''}"
            + f"{'P' if self.tcp_flag_psh else ''}{'R' if self.tcp_flag_rst else ''}{'S' if self.tcp_flag_syn else ''}"
            + f"{'F' if self.tcp_flag_fin else ''}, seq {self.tcp_seq_num}, ack {self.tcp_ack_num}, win {self.tcp_win}"
        )

        for option in self.tcp_options:
            log += ", " + str(option)

        return log

    def __len__(self):
        """ Length of the packet """

        return len(self.raw_packet)

    def compute_cksum(self, ip_pseudo_header):
        """ Compute checksum of IP pseudo header + TCP packet """

        cksum_data = ip_pseudo_header + self.raw_packet + (b"\0" if len(self.raw_packet) & 1 else b"")
        cksum_data = list(struct.unpack(f"! {len(cksum_data) >> 1}H", cksum_data))
        cksum_data[6 + 8] = 0
        cksum = sum(cksum_data)
        return ~((cksum & 0xFFFF) + (cksum >> 16)) & 0xFFFF

    @property
    def raw_options(self):
        """ Packet options in raw format """

        raw_options = b""

        for option in self.tcp_options:
            raw_options += option.raw_option

        return raw_options

    @property
    def raw_packet(self):
        """ Packet in raw format """

        return self.raw_header + self.raw_options + self.raw_data

    def get_raw_packet(self, ip_pseudo_header):
        """ Get packet in raw format ready to be processed by lower level protocol """

        self.tcp_cksum = self.compute_cksum(ip_pseudo_header)

        return self.raw_packet

    def get_option(self, name):
        """ Find specific option by its name """

        for option in self.tcp_options:
            if option.name == name:
                return option


"""

   TCP options

"""


TCP_OPT_EOL = 0
TCP_OPT_EOL_LEN = 1
TCP_OPT_NOP = 1
TCP_OPT_NOP_LEN = 1
TCP_OPT_MSS = 2
TCP_OPT_MSS_LEN = 4
TCP_OPT_WSCALE = 3
TCP_OPT_WSCALE_LEN = 3
TCP_OPT_SACKPERM = 4
TCP_OPT_SACKPERM_LEN = 2
TCP_OPT_TIMESTAMP = 8
TCP_OPT_TIMESTAMP_LEN = 10


class TcpOptEol:
    """ TCP option End of Option List """

    name = "EOL"

    def __init__(self, raw_option=None):
        if raw_option:
            self.opt_kind = raw_option[0]
        else:
            self.opt_kind = TCP_OPT_EOL

    @property
    def raw_option(self):
        return struct.pack("!B", self.opt_kind)

    def __str__(self):
        return "eol"


class TcpOptNop:
    """ TCP option No Operation """

    name = "NOP"

    def __init__(self, raw_option=None):
        if raw_option:
            self.opt_kind = raw_option[0]
        else:
            self.opt_kind = TCP_OPT_NOP

    @property
    def raw_option(self):
        return struct.pack("!B", self.opt_kind)

    def __str__(self):
        return "nop"


class TcpOptMss:
    """ TCP option Maximum Segment Size """

    name = "MSS"

    def __init__(self, raw_option=None, opt_size=None):
        if raw_option:
            self.opt_kind = raw_option[0]
            self.opt_len = raw_option[1]
            self.opt_size = struct.unpack("!H", raw_option[2:4])[0]
        else:
            self.opt_kind = TCP_OPT_MSS
            self.opt_len = TCP_OPT_MSS_LEN
            self.opt_size = opt_size

    @property
    def raw_option(self):
        return struct.pack("! BB H", self.opt_kind, self.opt_len, self.opt_size)

    def __str__(self):
        return f"mss {self.opt_size}"


class TcpOptSackperm:
    """ TCP option Sack Permit """

    name = "SACKPERM"

    def __init__(self, raw_option=None):
        if raw_option:
            self.opt_kind = raw_option[0]
            self.opt_len = raw_option[1]
        else:
            self.opt_kind = TCP_OPT_SACKPERM
            self.opt_len = TCP_OPT_SACKPERM_LEN

    @property
    def raw_option(self):
        return struct.pack("! BB", self.opt_kind, self.opt_len)

    def __str__(self):
        return "sckp"


class TcpOptWscale:
    """ TCP option Window Scale """

    name = "WSCALE"

    def __init__(self, raw_option=None, opt_scale=None):
        if raw_option:
            self.opt_kind = raw_option[0]
            self.opt_len = raw_option[1]
            self.opt_scale = raw_option[2]
        else:
            self.opt_kind = TCP_OPT_MSS
            self.opt_len = TCP_OPT_MSS_LEN
            self.opt_scale = opt_scale

    @property
    def raw_option(self):
        return struct.pack("! BB B", self.opt_kind, self.opt_len, self.opt_scale)

    def __str__(self):
        return f"wscale {self.opt_scale}"


class TcpOptTimestamp:
    """ TCP option Timestamp """

    name = "TIMESTAMP"

    def __init__(self, raw_option=None, opt_tsval=None, opt_tsecr=None):
        if raw_option:
            self.opt_kind = raw_option[0]
            self.opt_len = raw_option[1]
            self.opt_tsval = struct.unpack("!L", raw_option[2:6])[0]
            self.opt_tsecr = struct.unpack("!L", raw_option[6:10])[0]
        else:
            self.opt_kind = TCP_OPT_MSS
            self.opt_len = TCP_OPT_MSS_LEN
            self.opt_tsval = opt_tsval
            self.opt_tsecr = opt_tsecr

    @property
    def raw_option(self):
        return struct.pack("! BB LL", self.opt_kind, self.opt_len, self.opt_tsval, self.opt_tsecr)

    def __str__(self):
        return f"ts {self.opt_tsval}/{self.opt_tsecr}"


class TcpOptUnk:
    """ TCP not supported by this stack """

    name = "UNKNOWN"

    def __init__(self, raw_option=None):
        self.opt_kind = raw_option[0]
        self.opt_len = raw_option[1]
        self.raw_data = raw_option[2 : self.opt_len - 2]

    @property
    def raw_option(self):
        return struct.pack("! BB", self.opt_kind, self.opt_len) + self.raw_data

    def __str__(self):
        return "unk"