from core.utils import clear_screen
from services.report_service import ReportService
from views.report_view import ReportView


class ReportController:

  def __init__(self):
    self.service = ReportService()
    self.view = ReportView()

  def generate_report(self):
    self.view.show_message("\nGerando relatorio FSupport...\n")
    result = self.service.generate_latest_report()
    clear_screen()
    self.view.show_report_result(result)
