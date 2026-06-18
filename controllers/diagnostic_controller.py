from core.utils import clear_screen
from services.diagnostic_service import DiagnosticService
from views.diagnostic_view import DiagnosticView


class DiagnosticController:

  def __init__(self):
    self.service = DiagnosticService()
    self.view = DiagnosticView()

  def show_quick_diagnostic(self):
    self.view.show_message("\nExecutando diagnostico rapido...\n")
    result = self.service.run_quick()
    clear_screen()
    self.view.show_diagnostic_result(result)

  def show_full_diagnostic(self):
    self.view.show_message("\nExecutando diagnostico completo...\n")
    result = self.service.run_full()
    clear_screen()
    self.view.show_diagnostic_result(result)
