from services.cpu_service import CpuService
from views.cpu_view import CpuView
from core.utils import clear_screen

class CpuController:

  def __init__(self):
    self.service = CpuService()
    self.view = CpuView()

  def show_info(self):
    self.view.show_message("\nColetando informações da CPU...\n")
    cpu_info = self.service.get_cpu_info()
    clear_screen()
    self.view.show_cpu_info(cpu_info)