from services.disk_service import DiskService
from views.disk_view import DiskView
from core.utils import clear_screen

class DiskController:

  def __init__(self):
    self.service = DiskService()
    self.view = DiskView()

  def show_info(self):
    self.view.show_message("\nColetando informações do disco...\n")
    disk_info = self.service.get_disk_info()
    clear_screen()
    self.view.show_disk_info(disk_info)