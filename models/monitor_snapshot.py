class MonitorSnapshot:
  def __init__(
    self,
    timestamp,
    cpu_usage,
    ram_usage,
    ram_available,
    disks,
    bytes_sent,
    bytes_recv,
    upload_rate,
    download_rate,
    alerts=None
  ):
    self.timestamp = timestamp
    self.cpu_usage = cpu_usage
    self.ram_usage = ram_usage
    self.ram_available = ram_available
    self.disks = disks
    self.bytes_sent = bytes_sent
    self.bytes_recv = bytes_recv
    self.upload_rate = upload_rate
    self.download_rate = download_rate
    self.alerts = alerts if alerts is not None else []

  def to_dict(self):
    return {
      "timestamp": self.timestamp.isoformat(timespec="seconds"),
      "cpu_usage": self.cpu_usage,
      "ram_usage": self.ram_usage,
      "ram_available": self.ram_available,
      "disks": [
        {
          "partition": disk.partition,
          "total": disk.total,
          "used": disk.used,
          "free": disk.free,
          "percent": disk.percent
        }
        for disk in self.disks
      ],
      "bytes_sent": self.bytes_sent,
      "bytes_recv": self.bytes_recv,
      "upload_rate": self.upload_rate,
      "download_rate": self.download_rate,
      "alerts": [alert.to_dict() for alert in self.alerts]
    }
