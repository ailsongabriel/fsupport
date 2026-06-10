from services.system_service import SystemService
from views.system_view import SystemView
from core.utils import clear_screen

class SystemController:

  def __init__(self):
    self.service = SystemService()
    self.view = SystemView()

  def show_info(self):
    system_info = self.service.get_system_info()
    clear_screen()
    self.view.show_system_info(system_info)