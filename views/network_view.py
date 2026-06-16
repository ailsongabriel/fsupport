from views.base_view import BaseView

class NetworkView(BaseView):
  def show_network_info(self, network_info):
    print("\n======================== Network =========================")
    print(f"IP Local    = {network_info.ip_local}")
    print(f"Hostname    = {network_info.hostname}")

    if network_info.gateway is not None:
      print(f"Gateway     = {network_info.gateway}")

    print(f"Downloads   = {self.format_size(network_info.bytes_recv)}")
    print(f"Uploads     = {self.format_size(network_info.bytes_sent)}")

    if network_info.public_ip is not None: 
      print(f"IP Público  = {network_info.public_ip}")

    if network_info.primary_interface is not None:
      print(f"Interface de Rede Principal = {network_info.primary_interface}")

    if network_info.vpn_status is not None:
      print(f"VPN Status                  = {network_info.vpn_status}")

    print("\n------------------ Interfaces de Rede: ------------------")
    for iface, ips in network_info.interfaces.items():
      print(f"\nInterface: {iface}")
      for ip in ips:
        print(f"  IPv4 -> {ip}")
    print("-----------------------------------------------------------")