class MonitorSession:
  def __init__(self, max_snapshots=120):
    self.max_snapshots = max_snapshots
    self.snapshots = []
    self.started_at = None
    self.finished_at = None
    self.peak_cpu = 0.0
    self.peak_ram = 0.0
    self.peak_download_rate = 0
    self.peak_upload_rate = 0
    self.peak_ram_available = None
    self.peak_disks = {}

  def add_snapshot(self, snapshot):
    if self.started_at is None:
      self.started_at = snapshot.timestamp

    self.finished_at = snapshot.timestamp
    self.snapshots.append(snapshot)

    if len(self.snapshots) > self.max_snapshots:
      self.snapshots.pop(0)

    self._update_peaks(snapshot)

  def to_dict(self):
    samples_count = len(self.snapshots)
    duration_seconds = 0
    if self.started_at and self.finished_at:
      duration_seconds = int((self.finished_at - self.started_at).total_seconds())

    return {
      "started_at": self.started_at.isoformat(timespec="seconds") if self.started_at else None,
      "finished_at": self.finished_at.isoformat(timespec="seconds") if self.finished_at else None,
      "duration_seconds": duration_seconds,
      "samples_count": samples_count,
      "averages": self._build_averages(),
      "peaks": {
        "cpu_usage": self.peak_cpu,
        "ram_usage": self.peak_ram,
        "lowest_ram_available": self.peak_ram_available,
        "download_rate": self.peak_download_rate,
        "upload_rate": self.peak_upload_rate,
        "disk_usage": self.peak_disks
      },
      "alerts": self._build_unique_alerts(),
      "snapshots": [snapshot.to_dict() for snapshot in self.snapshots]
    }

  def _update_peaks(self, snapshot):
    self.peak_cpu = max(self.peak_cpu, snapshot.cpu_usage)
    self.peak_ram = max(self.peak_ram, snapshot.ram_usage)
    self.peak_download_rate = max(self.peak_download_rate, snapshot.download_rate)
    self.peak_upload_rate = max(self.peak_upload_rate, snapshot.upload_rate)

    if self.peak_ram_available is None or snapshot.ram_available < self.peak_ram_available:
      self.peak_ram_available = snapshot.ram_available

    for disk in snapshot.disks:
      current_peak = self.peak_disks.get(disk.partition, 0)
      self.peak_disks[disk.partition] = max(current_peak, disk.percent)

  def _build_averages(self):
    if not self.snapshots:
      return {
        "cpu_usage": 0,
        "ram_usage": 0,
        "download_rate": 0,
        "upload_rate": 0
      }

    total = len(self.snapshots)
    return {
      "cpu_usage": round(sum(snapshot.cpu_usage for snapshot in self.snapshots) / total, 2),
      "ram_usage": round(sum(snapshot.ram_usage for snapshot in self.snapshots) / total, 2),
      "download_rate": round(sum(snapshot.download_rate for snapshot in self.snapshots) / total, 2),
      "upload_rate": round(sum(snapshot.upload_rate for snapshot in self.snapshots) / total, 2)
    }

  def _build_unique_alerts(self):
    alerts = []
    seen = set()

    for snapshot in self.snapshots:
      for alert in snapshot.alerts:
        key = (alert.level, alert.component, alert.metric, alert.message)
        if key in seen:
          continue

        seen.add(key)
        alerts.append(alert.to_dict())

    return alerts
