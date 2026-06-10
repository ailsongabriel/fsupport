from models.disk_info import DiskInfo
from services.system_service import SystemService
import psutil

class DiskService:

  def __init__(self):
    self.system_service = SystemService()
  
  def get_disk_info(self):
    
    disk_info_list = []
    partitions = psutil.disk_partitions()

    for partition in partitions:
      usage = psutil.disk_usage(partition.mountpoint)
      total = usage.total
      used = usage.used
      free = usage.free
      percent = round(usage.percent, 2)

      disk_info = DiskInfo(partition.device, total, used, free, percent)
      disk_info_list.append(disk_info)

    return disk_info_list