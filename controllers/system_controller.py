from services.system_service import SystemService
from views.system_view import SystemView

class SystemController:

  def __init__(self):
    self.service = SystemService()
    self.view = SystemView()

  def show_info(self):
    system_info = self.service.get_system_info()
    self.view.show_system_info(system_info)