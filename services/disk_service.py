from models.disk_info import DiskInfo
from services.system_service import SystemService
import psutil

class DiskService:

  def __init__(self):
    self.system_service = SystemService()
    self.os_type = self.system_service.get_os_type()
  
  def get_disk_info(self):
    
    disk_info_list = []
    partitions = psutil.disk_partitions()

    for partition in partitions:
      if not self._is_valid_partition(partition): # Se a partição não for válida, continue para a próxima
        continue
      try:
        usage = psutil.disk_usage(partition.mountpoint)
      except Exception:
          continue
      usage = psutil.disk_usage(partition.mountpoint)
      total = usage.total
      used = usage.used
      free = usage.free
      percent = round(usage.percent, 2)

      disk_info = DiskInfo(partition.device, total, used, free, percent)
      disk_info_list.append(disk_info)

    return disk_info_list
  
  def _is_valid_partition(self, partition):

    if self.os_type == "Windows":
        return self._is_valid_windows_partition(partition)

    if self.os_type == "Linux":
        return self._is_valid_linux_partition(partition)

    return True
  
  def _is_valid_linux_partition(self, partition):

    if partition.device.startswith("/dev/loop"):
        return False

    if partition.device.startswith("/dev/sr"):
        return False

    if partition.fstype in {
        "squashfs",
        "tmpfs",
        "devtmpfs",
        "proc",
        "sysfs"
    }:
        return False

    return True
  
  def _is_valid_windows_partition(self, partition):
    if partition.fstype == "":
        return False
    return True