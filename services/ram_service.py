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

  def _get_total(self): # Retorna a quantidade total de RAM
    return psutil.virtual_memory().total

  def _get_used(self): # Retorna a quantidade de RAM usada
    return psutil.virtual_memory().used

  def _get_available(self): # Retorna a quantidade de RAM disponível
    return psutil.virtual_memory().available

  def _get_usage(self): # Retorna o percentual de uso da RAM
    return round(psutil.virtual_memory().percent, 2)