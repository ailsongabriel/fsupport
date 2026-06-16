from models.network_info import NetworkInfo
import psutil
import socket
import requests
import netifaces

class NetworkService:
  def get_network_info(self):
    ip_local = self._get_local_ip()
    hostname = socket.gethostname()
    gateway = self._get_gateway()
    interfaces = self._get_network_interfaces()
    bytes_recv, bytes_sent = self._get_total_network_usage()
    public_ip = self._get_public_ip()

    return NetworkInfo(
      ip_local,
      hostname,
      gateway,
      interfaces,
      bytes_recv,
      bytes_sent,
      public_ip
    )

  def _get_local_ip(self): # Obtém o IP local do dispositivo
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria um socket UDP
    s.connect(("8.8.8.8", 80)) # Conecta a um servidor DNS público (Google) para obter o IP local
    local_ip = s.getsockname()[0] # Obtém o IP local do socket
    s.close()
    return local_ip
  
  def _get_gateway(self):
    try:
      return netifaces.gateways()["default"][netifaces.AF_INET][0]
    except:
      return None

  def _get_network_interfaces(self):
    raw = psutil.net_if_addrs()

    interfaces = {}

    for iface, addrs in raw.items():
      ipv4s = [
        addr.address
        for addr in addrs
        if addr.family == socket.AF_INET
      ]

      interfaces[iface] = ipv4s

    return interfaces
  
  def _get_total_network_usage(self):
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent
  
  def _get_public_ip(self):
    try:
      return requests.get('https://api.ipify.org', timeout=3).text
    except:
      return None
