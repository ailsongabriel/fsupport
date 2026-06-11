from services.network_service import NetworkService
from views.network_view import NetworkView
from core.utils import clear_screen

class NetworkController:

  def __init__(self):
    self.service = NetworkService()
    self.view = NetworkView()

  def show_info(self):
    self.view.show_message("\nColetando informações de rede...\n")
    network_info = self.service.get_network_info()
    clear_screen()
    self.view.show_network_info(network_info)