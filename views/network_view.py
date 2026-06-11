from views.base_view import BaseView

class NetworkView(BaseView):
  def show_network_info(self, network_info):
    print("\n======================== Network =========================")
    print(f"IP Local            = {network_info.ip_local}")
    print(f"Hostname            = {network_info.hostname}")
    print(f"Gateway             = {network_info.gateway}")
    for i, interface in enumerate(network_info.interfaces):
        print(f"Interface {i}         = {interface}")
    print(f"Downloads           = {self.format_size(network_info.download_bytes)}")
    print(f"Uploads             = {self.format_size(network_info.upload_bytes)}")
    print(f"IP Público          = {network_info.public_ip}")
  