from views.base_view import BaseView

class NetworkView(BaseView):

  def show_network_info(self, network_info):

    lines = [
      f"IP Local    = {network_info.ip_local}",
      f"Hostname    = {network_info.hostname}",
      f"Downloads   = {self.format_size(network_info.bytes_recv)}",
      f"Uploads     = {self.format_size(network_info.bytes_sent)}"
    ]

    if network_info.gateway:
      lines.append(f"Gateway     = {network_info.gateway}")
    if network_info.public_ip:
      lines.append(f"IP Público  = {network_info.public_ip}")
    for iface, ips in network_info.interfaces.items():
      lines.append(f"Interface: {iface}")
      for ip in ips:
        lines.append(f"  IPv4 -> {ip}")

    width = self.get_width(lines)
    self.print_title("NETWORK", width)

    print(f"IP Local    = {network_info.ip_local}")
    print(f"Hostname    = {network_info.hostname}")

    if network_info.gateway:
      print(f"Gateway     = {network_info.gateway}")

    print(f"Downloads   = {self.format_size(network_info.bytes_recv)}")
    print(f"Uploads     = {self.format_size(network_info.bytes_sent)}")

    if network_info.public_ip:
      print(f"IP Público  = {network_info.public_ip}")
    else:
      print("IP Público  = indisponível")

    self.print_subtitle("Interfaces de Rede", width)

    for iface, ips in network_info.interfaces.items():

      print(f"\nInterface: {iface}")

      for ip in ips:
        print(f"  IPv4 -> {ip}")
