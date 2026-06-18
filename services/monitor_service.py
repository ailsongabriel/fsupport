from datetime import datetime
import psutil

from models.disk_info import DiskInfo
from models.monitor_alert import MonitorAlert
from models.monitor_session import MonitorSession
from models.monitor_snapshot import MonitorSnapshot
from services.disk_service import DiskService


class MonitorService:

  THRESHOLDS = {
    "cpu": {"warning": 75.0, "critical": 90.0},
    "ram": {"warning": 80.0, "critical": 95.0},
    "disk": {"warning": 85.0, "critical": 95.0}
  }

  def __init__(self, max_snapshots=120):
    self.disk_service = DiskService()
    self.session = MonitorSession(max_snapshots=max_snapshots)
    self.last_bytes_recv = None
    self.last_bytes_sent = None
    self.last_network_timestamp = None

  def collect_snapshot(self):
    timestamp = datetime.now()
    cpu_usage = round(psutil.cpu_percent(interval=None), 2)
    ram = psutil.virtual_memory()
    disks = self._get_disks()
    net = psutil.net_io_counters()
    download_rate, upload_rate = self._calculate_network_rates(
      timestamp,
      net.bytes_recv,
      net.bytes_sent
    )
    alerts = self._check_alerts(cpu_usage, ram.percent, disks)

    snapshot = MonitorSnapshot(
      timestamp=timestamp,
      cpu_usage=cpu_usage,
      ram_usage=round(ram.percent, 2),
      ram_available=ram.available,
      disks=disks,
      bytes_sent=net.bytes_sent,
      bytes_recv=net.bytes_recv,
      upload_rate=upload_rate,
      download_rate=download_rate,
      alerts=alerts
    )

    self.session.add_snapshot(snapshot)
    return snapshot

  def get_session(self):
    return self.session

  def build_session_data(self):
    return self.session.to_dict()

  def _get_disks(self):
    disks = []

    for disk in self.disk_service.get_disk_info():
      disks.append(DiskInfo(
        disk.partition,
        disk.total,
        disk.used,
        disk.free,
        disk.percent
      ))

    return disks

  def _calculate_network_rates(self, timestamp, bytes_recv, bytes_sent):
    if self.last_network_timestamp is None:
      self.last_network_timestamp = timestamp
      self.last_bytes_recv = bytes_recv
      self.last_bytes_sent = bytes_sent
      return 0, 0

    elapsed = max((timestamp - self.last_network_timestamp).total_seconds(), 1)
    download_rate = max(int((bytes_recv - self.last_bytes_recv) / elapsed), 0)
    upload_rate = max(int((bytes_sent - self.last_bytes_sent) / elapsed), 0)

    self.last_network_timestamp = timestamp
    self.last_bytes_recv = bytes_recv
    self.last_bytes_sent = bytes_sent

    return download_rate, upload_rate

  def _check_alerts(self, cpu_usage, ram_usage, disks):
    alerts = []
    alerts.extend(self._check_metric(
      "cpu",
      "CPU",
      "usage_percent",
      cpu_usage,
      "CPU com uso elevado por periodo de monitoramento.",
      "Verificar processos no topo de CPU e temperatura do processador."
    ))
    alerts.extend(self._check_metric(
      "ram",
      "RAM",
      "usage_percent",
      ram_usage,
      "RAM com uso elevado por periodo de monitoramento.",
      "Verificar processos no topo de RAM e programas iniciando com o sistema."
    ))

    for disk in disks:
      alerts.extend(self._check_metric(
        "disk",
        f"Disco {disk.partition}",
        "usage_percent",
        disk.percent,
        f"Disco {disk.partition} com pouco espaco livre.",
        "Liberar espaco, revisar arquivos grandes e validar saude do disco."
      ))

    return alerts

  def _check_metric(self, threshold_key, component, metric, value, message, recommendation):
    thresholds = self.THRESHOLDS[threshold_key]

    if value >= thresholds["critical"]:
      return [MonitorAlert(
        "critical",
        component,
        metric,
        value,
        thresholds["critical"],
        message,
        recommendation
      )]

    if value >= thresholds["warning"]:
      return [MonitorAlert(
        "warning",
        component,
        metric,
        value,
        thresholds["warning"],
        message,
        recommendation
      )]

    return []
