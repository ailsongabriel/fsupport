class NetworkInfo:
    def __init__(
        self,
        ip_local,
        hostname,
        gateway,
        interfaces,  # list[NetworkInterface]
        download_bytes,
        upload_bytes,
        public_ip=None,
        primary_interface=None,
        vpn_status=None
    ):
        self.ip_local = ip_local
        self.hostname = hostname
        self.gateway = gateway

        self.interfaces = interfaces

        self.download_bytes = download_bytes
        self.upload_bytes = upload_bytes

        self.public_ip = public_ip
        self.primary_interface = primary_interface
        self.vpn_status = vpn_status