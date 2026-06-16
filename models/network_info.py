class NetworkInfo:
    def __init__(
        self,
        ip_local,
        hostname,
        gateway,
        interfaces,  # dict[str, list[str]]
        bytes_recv,
        bytes_sent,
        public_ip=None,
        primary_interface=None,
        vpn_status=None
    ):
        self.ip_local = ip_local
        self.hostname = hostname
        self.gateway = gateway

        self.interfaces = interfaces

        self.bytes_recv = bytes_recv
        self.bytes_sent = bytes_sent

        self.public_ip = public_ip
        self.primary_interface = primary_interface
        self.vpn_status = vpn_status