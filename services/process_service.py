from datetime import datetime
import ipaddress
import time

import psutil

from models.process_connection import ProcessConnection
from models.process_info import ProcessInfo


class ProcessService:

  CPU_ACTIVITY_LIMIT = 10.0
  RAM_ACTIVITY_MB_LIMIT = 300.0
  SUSPICIOUS_SCORE_LIMIT = 50
  RISK_PATHS = [
    "\\temp\\",
    "\\downloads\\",
    "\\appdata\\roaming\\"
  ]
  TRUSTED_PATHS = [
    "\\appdata\\local\\programs\\",
    "\\appdata\\local\\python\\",
    "\\program files\\",
    "\\program files (x86)\\",
    "\\windows\\system32\\"
  ]
  TRUSTED_NETWORK_NAMES = {
    "brave.exe",
    "chrome.exe",
    "code.exe",
    "discord.exe",
    "firefox.exe",
    "msedge.exe",
    "onedrive.exe",
    "opera.exe",
    "python.exe",
    "pythonw.exe",
    "steam.exe",
    "teams.exe",
    "telegram.exe",
    "whatsapp.exe"
  }
  SYSTEM_NAMES = {
    "csrss.exe",
    "dwm.exe",
    "explorer.exe",
    "lsass.exe",
    "services.exe",
    "svchost.exe",
    "system",
    "wininit.exe",
    "winlogon.exe"
  }

  def scan_processes(self, limit=10, cpu_sample_interval=1):
    processes = self._collect_processes(cpu_sample_interval)
    top_cpu = sorted(processes, key=lambda item: item.cpu_percent, reverse=True)[:limit]
    top_ram = sorted(processes, key=lambda item: item.memory_mb, reverse=True)[:limit]
    network_processes = [
      process for process in processes
      if process.connections
    ]
    suspicious_processes = sorted(
      [process for process in processes if process.risk_score >= self.SUSPICIOUS_SCORE_LIMIT],
      key=lambda item: item.risk_score,
      reverse=True
    )

    collected_at = datetime.now()
    return {
      "collected_at": collected_at.isoformat(timespec="seconds"),
      "summary": {
        "total_processes": len(processes),
        "top_cpu_count": len(top_cpu),
        "top_ram_count": len(top_ram),
        "network_processes_count": len(network_processes),
        "suspicious_count": len(suspicious_processes)
      },
      "top_cpu": [process.to_dict() for process in top_cpu],
      "top_ram": [process.to_dict() for process in top_ram],
      "network_processes": [process.to_dict() for process in network_processes],
      "suspicious_processes": [process.to_dict() for process in suspicious_processes]
    }

  def _collect_processes(self, cpu_sample_interval):
    raw_processes = []

    for process in psutil.process_iter():
      try:
        process.cpu_percent(interval=None)
        raw_processes.append(process)
      except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

    time.sleep(cpu_sample_interval)

    processes = []
    for process in raw_processes:
      try:
        info = process.as_dict(attrs=[
          "pid",
          "name",
          "username",
          "memory_percent",
          "memory_info",
          "exe",
          "cmdline",
          "create_time"
        ])
        cpu_percent = round(process.cpu_percent(interval=None), 2)
        memory_mb = round(info["memory_info"].rss / 1024 / 1024, 2)
        connections = self._get_connections(process)
        activity_flags, risk_flags, risk_score, recommendation = self._analyze_process(
          info,
          cpu_percent,
          memory_mb,
          connections
        )

        processes.append(ProcessInfo(
          pid=info["pid"],
          name=info["name"],
          username=info["username"],
          cpu_percent=cpu_percent,
          memory_mb=memory_mb,
          memory_percent=round(info["memory_percent"], 2),
          exe=info["exe"],
          cmdline=" ".join(info["cmdline"]) if info["cmdline"] else None,
          create_time=info["create_time"],
          connections=connections,
          activity_flags=activity_flags,
          risk_flags=risk_flags,
          risk_score=risk_score,
          recommendation=recommendation
        ))
      except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

    return processes

  def _get_connections(self, process):
    connections = []

    try:
      if hasattr(process, "net_connections"):
        process_connections = process.net_connections(kind="inet")
      else:
        process_connections = process.connections(kind="inet")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
      return connections

    for connection in process_connections:
      local_address = self._format_address(connection.laddr)
      remote_address = self._format_address(connection.raddr)

      if not remote_address:
        continue

      connections.append(ProcessConnection(
        local_address=local_address,
        remote_address=remote_address,
        status=connection.status
      ))

    return connections

  def _analyze_process(self, info, cpu_percent, memory_mb, connections):
    activity_flags = []
    risk_flags = []
    score = 0
    name = (info["name"] or "").lower()
    exe = info["exe"] or ""
    exe_lower = exe.lower()

    if cpu_percent >= self.CPU_ACTIVITY_LIMIT:
      activity_flags.append("high_cpu")

    if memory_mb >= self.RAM_ACTIVITY_MB_LIMIT:
      activity_flags.append("high_ram")

    external_connections = [
      connection for connection in connections
      if self._is_external_address(connection.remote_address)
    ]
    if external_connections:
      activity_flags.append("external_network_connection")

    trusted_network_process = name in self.TRUSTED_NETWORK_NAMES
    trusted_path = exe and any(path in exe_lower for path in self.TRUSTED_PATHS)
    system_process = (
      name == "system" or
      (name in self.SYSTEM_NAMES and "\\windows\\system32\\" in exe_lower)
    )
    unusual_path = (
      exe and
      not trusted_path and
      any(path in exe_lower for path in self.RISK_PATHS)
    )
    unavailable_path = not exe

    if unusual_path:
      risk_flags.append("unusual_path")
      score += 30

    if unavailable_path and external_connections and not system_process:
      risk_flags.append("executable_path_unavailable")
      score += 25

    if external_connections and unusual_path and not trusted_network_process:
      risk_flags.append("external_network_from_unusual_path")
      score += 30

    if cpu_percent >= self.CPU_ACTIVITY_LIMIT and unusual_path:
      risk_flags.append("high_cpu_from_unusual_path")
      score += 20

    if memory_mb >= self.RAM_ACTIVITY_MB_LIMIT and unusual_path:
      risk_flags.append("high_ram_from_unusual_path")
      score += 15

    if (trusted_network_process and trusted_path) or system_process:
      score = 0
      risk_flags = []

    recommendation = None
    if score >= self.SUSPICIOUS_SCORE_LIMIT:
      recommendation = (
        "Investigar o caminho do executavel, assinatura digital e reputacao "
        "antes de qualquer acao corretiva."
      )

    return activity_flags, risk_flags, score, recommendation

  def _format_address(self, address):
    if not address:
      return None

    try:
      return f"{address.ip}:{address.port}"
    except AttributeError:
      return str(address)

  def _is_external_address(self, address):
    if not address:
      return False

    ip = address.split(":")[0]
    try:
      parsed_ip = ipaddress.ip_address(ip)
      return not (
        parsed_ip.is_private or
        parsed_ip.is_loopback or
        parsed_ip.is_link_local or
        parsed_ip.is_multicast
      )
    except ValueError:
      return False
