from services.startup_service import StartupService
from views.startup_view import StartupView
from core.utils import clear_screen

class StartupController():
  def __init__(self):
    self.service = StartupService()
    self.view = StartupView()

  def show_startup_items(self):
    self.view.show_message("\nColetando itens de inicialização...\n")
    startup_items = self.service.get_startup_items()
    clear_screen()
    self.view.show_startup_items(startup_items)