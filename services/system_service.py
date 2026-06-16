from models.system_info import SystemInfo
import socket
import getpass
import platform

class SystemService:

  def get_system_info(self):

    hostname = self._get_hostname()
    username = self._get_username()
    os_name = self._get_os_name()
    architecture = self._get_architecture()
    system = SystemInfo(hostname, username, os_name, architecture)
    return system

  def _get_hostname(self):
    return socket.gethostname()

  def _get_username(self):
    return getpass.getuser()

  def _get_os_name(self):
    return f"{platform.system()} {platform.release()}"

  def _get_architecture(self):
    return platform.architecture()[0]
  
  def get_os_type(self):
    return platform.system()
  