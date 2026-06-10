from services.ram_service import RamService
from views.ram_view import RamView
from core.utils import clear_screen

class RamController:

  def __init__(self):
    self.service = RamService()
    self.view = RamView()

  def show_info(self):
    self.view.show_message("\nColetando informações da RAM...\n")
    ram_info = self.service.get_ram_info()
    clear_screen()
    self.view.show_ram_info(ram_info)