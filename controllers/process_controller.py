from datetime import datetime

from core.utils import clear_screen
from services.process_service import ProcessService
from services.storage_service import StorageService
from views.process_view import ProcessView


class ProcessController:

  def __init__(self):
    self.service = ProcessService()
    self.storage = StorageService()
    self.view = ProcessView()

  def show_heavy_processes(self):
    self.view.show_message("\nColetando processos, uso de CPU/RAM e conexoes de rede...\n")
    scan = self.service.scan_processes()
    collected_at = datetime.fromisoformat(scan["collected_at"])
    latest_path, session_path = self.storage.save_snapshot("processes", collected_at, scan)

    clear_screen()
    self.view.show_process_scan(scan, latest_path, session_path)
