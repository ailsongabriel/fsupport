import subprocess
import psutil
from models.security_info import AntivirusInfo, FirewallInfo, SecurityInfo
from services.system_service import SystemService

class SecurityService:

  KNOWN_AV_LINUX = [
    "clamav", "clamd", "freshclam",
    "sophos", "eset", "comodo",
    "avg", "avast", "bitdefender"
  ]

  def __init__(self):
    self.system_service = SystemService()
    self.os_type = self.system_service.get_os_type()

  def get_security_info(self) -> SecurityInfo:
    antivirus_list = self._get_antivirus()
    firewall = self._get_firewall()
    return SecurityInfo(antivirus_list, firewall)

# ---------------------------------------------------------------- antivírus

  def _get_antivirus(self) -> list:
    if self.os_type == "Windows":
      return self._get_antivirus_windows()
    if self.os_type == "Linux":
      return self._get_antivirus_linux()
    return []

  def _get_antivirus_windows(self) -> list:
    antivirus = {}
    try:
      result = subprocess.run(
        [
          "powershell", "-Command",
          "Get-CimInstance -Namespace root/SecurityCenter2 "
          "-ClassName AntiVirusProduct | "
          "Select-Object displayName, productState | "
          "ConvertTo-Json"
        ],
        capture_output=True, text=True, timeout=10
      )
      import json
      data = json.loads(result.stdout)
      if isinstance(data, dict):
        data = [data]
      for entry in data:
        name = entry.get("displayName", "Unknown")
        # productState: bit 12 indica se está ativo
        state = entry.get("productState", 0)
        active = (int(state) >> 12 & 0xF) != 0
        if name not in antivirus:
          antivirus[name] = AntivirusInfo(
            name=name,
            active=active
          )
        else:
          antivirus[name].active = (
            antivirus[name].active or active
          ) 
    except Exception as error:
      return [AntivirusInfo(
        name="Verificacao indisponivel",
        active=None,
        note=str(error)
      )]

    if not antivirus:
      return [AntivirusInfo(name="Nenhum detectado", active=False)]

    return list(antivirus.values())

  def _get_antivirus_linux(self) -> list:
    items = []
    running = {p.name().lower() for p in psutil.process_iter(["name"])}
    for av in self.KNOWN_AV_LINUX:
      if any(av in proc for proc in running):
        items.append(AntivirusInfo(name=av, active=True))
    if not items:
      items.append(AntivirusInfo(name="Nenhum detectado", active=False))
    return items

  # ---------------------------------------------------------------- firewall

  def _get_firewall(self) -> FirewallInfo:
    if self.os_type == "Windows":
      return self._get_firewall_windows()
    if self.os_type == "Linux":
      return self._get_firewall_linux()
    return FirewallInfo(active=None)

  def _get_firewall_windows(self) -> FirewallInfo:
    try:
      result = subprocess.run(
        ["netsh", "advfirewall", "show", "allprofiles", "state"],
        capture_output=True, text=True, timeout=10
      )
      if result.returncode != 0:
        return FirewallInfo(active=None, note=result.stderr.strip() or "Falha ao consultar netsh.")
      active = "ON" in result.stdout.upper()
      return FirewallInfo(active=active)
    except Exception as error:
      return FirewallInfo(active=None, note=str(error))

  def _get_firewall_linux(self) -> FirewallInfo:
    # Tenta ufw → firewalld → iptables
    for cmd, active_keyword in [
      (["ufw", "status"],          "active"),
      (["firewall-cmd", "--state"], "running"),
    ]:
      try:
        result = subprocess.run(
          cmd, capture_output=True, text=True, timeout=5
        )
        if active_keyword in result.stdout.lower():
          return FirewallInfo(active=True)
        return FirewallInfo(active=False)
      except FileNotFoundError:
        continue
      except Exception:
        continue
    # Fallback: iptables com regras = considera ativo
    try:
      result = subprocess.run(
        ["iptables", "-L"], capture_output=True, text=True, timeout=5
      )
      active = result.returncode == 0 and len(result.stdout.splitlines()) > 3
      return FirewallInfo(active=active)
    except Exception:
      return FirewallInfo(active=None)
