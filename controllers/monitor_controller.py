from datetime import datetime
import time

from core.utils import clear_screen
from services.monitor_service import MonitorService
from services.storage_service import StorageService
from views.monitor_view import MonitorView


class MonitorController:

  def __init__(self, interval=5, max_snapshots=120):
    self.interval = interval
    self.max_snapshots = max_snapshots
    self.service = None
    self.storage = StorageService()
    self.view = MonitorView()

  def start(self):
    self.service = MonitorService(max_snapshots=self.max_snapshots)
    self.view.show_message("\nIniciando monitoramento em tempo real...")
    self.view.show_message("Pressione CTRL+C para encerrar e salvar a sessao.\n")

    try:
      time.sleep(1)
      while True:
        snapshot = self.service.collect_snapshot()
        clear_screen()
        self.view.show_dashboard(snapshot, self.service.get_session(), self.interval)
        time.sleep(self.interval)
    except KeyboardInterrupt:
      return self._finish_session()

  def _finish_session(self):
    clear_screen()
    session_data = self.service.build_session_data()

    if session_data["samples_count"] == 0:
      self.view.show_message("Nenhum dado de monitoramento foi coletado.")
      return session_data

    timestamp = datetime.fromisoformat(session_data["started_at"])
    latest_path, session_path = self.storage.save_session("monitoring", timestamp, session_data)
    self.view.show_session_summary(session_data, latest_path, session_path)
    return session_data
