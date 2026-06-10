from models.cpu_info import CpuInfo
import psutil
from cpuinfo import get_cpu_info

class CpuService:

  def get_cpu_info(self):

    model = self._get_model()
    usage = self._get_usage()
    frequency = self._get_frequency()
    cores = self._get_cores()
    threads = self._get_threads()
    cpu_info = CpuInfo(model,usage,frequency,cores,threads)
    return cpu_info


  def _get_model(self):
    info = get_cpu_info()
    return info.get("brand_raw", "Unknown CPU")

  def _get_usage(self):
    return psutil.cpu_percent(interval=1)

  def _get_frequency(self):
    freq = psutil.cpu_freq()

    if freq:
      return round(freq.current / 1000, 2)

    return None

  def _get_cores(self):
    return psutil.cpu_count(logical=False)

  def _get_threads(self):
    return psutil.cpu_count(logical=True)