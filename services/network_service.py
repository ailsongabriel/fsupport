from models.network_info import NetworkInfo
import psutil
import socket
from requests import get
import netifaces

class NetworkService:
  def get_network_info(self):
    ip_local = self._get_local_ip()
    hostname = socket.gethostname()
    gateway = self._get_gateway()
    interfaces = self._get_network_interfaces()
    download_bytes, upload_bytes = self._get_network_speed()
    public_ip = self._get_public_ip()

    return NetworkInfo(
      ip_local,
      hostname,
      gateway,
      interfaces,
      download_bytes,
      upload_bytes,
      public_ip
    )

  def _get_local_ip(self): # Obtém o IP local do dispositivo
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Cria um socket UDP
    s.connect(("8.8.8.8", 80)) # Conecta a um servidor DNS público (Google) para obter o IP local
    local_ip = s.getsockname()[0] # Obtém o IP local do socket
    s.close()
    return local_ip
  
  def _get_gateway(self):
    gateways = netifaces.gateways()
    return gateways["default"][netifaces.AF_INET][0]
  
  def _get_network_interfaces(self):
    interfaces = []
    for iface in psutil.net_if_addrs():
      interfaces.append(iface)
    return interfaces
  
  def _get_network_speed(self):
    net_io = psutil.net_io_counters()
    return net_io.bytes_recv, net_io.bytes_sent
  
  def _get_public_ip(self):
    public_ip = get('https://api.ipify.org').text
    return public_ip
  