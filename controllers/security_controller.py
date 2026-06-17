from services.security_service import SecurityService
from views.security_view import SecurityView
from core.utils import clear_screen

class SecurityController:
  def __init__(self):
    self.service = SecurityService()
    self.view = SecurityView()

  def show_info(self):
    self.view.show_message("\nColetando informações de segurança...\n")
    security_info = self.service.get_security_info()
    clear_screen()
    self.view.show_security_info(security_info)