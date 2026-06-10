from models.ram_info import RamInfo
import psutil

class RamService:
  
  def get_ram_info(self):
    total = self._get_total()
    used = self._get_used()
    available = self._get_available()
    usage = self._get_usage()
    ram_info = RamInfo(total, used, available, usage)
    return ram_info
  
  def _bytes_to_gb(self, value): # Converte bytes para gigabytes
    return round(value / (1024 ** 3), 2)

  def _get_total(self): # Retorna a quantidade total de RAM
    return self._bytes_to_gb(psutil.virtual_memory().total)

  def _get_used(self): # Retorna a quantidade de RAM usada
    return self._bytes_to_gb(psutil.virtual_memory().used)

  def _get_available(self): # Retorna a quantidade de RAM disponível
    return self._bytes_to_gb(psutil.virtual_memory().available)

  def _get_usage(self): # Retorna o percentual de uso da RAM
    return round(psutil.virtual_memory().percent, 2)