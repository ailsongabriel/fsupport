from datetime import datetime
import ipaddress
import time

import psutil

from models.process_connection import ProcessConnection
from models.process_info import ProcessInfo


class ProcessService:

  CPU_LIMIT = 10.0
  RAM_MB_LIMIT = 300.0
  RISK_PATHS = [
    "\\appdata\\",
    "\\temp\\",
    "\\downloads\\",
    "\\programdata\\"
  ]

  def scan_processes(self, limit=10, cpu_sample_interval=1):
    processes = self._collect_processes(cpu_sample_interval)
    top_cpu = sorted(processes, key=lambda item: item.cpu_percent, reverse=True)[:limit]
    top_ram = sorted(processes, key=lambda item: item.memory_mb, reverse=True)[:limit]
    network_processes = [
      process for process in processes
      if process.connections
    ]
    suspicious_processes = sorted(
      [process for process in processes if process.risk_score > 0],
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
        risk_flags, risk_score, recommendation = self._analyze_risk(
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

  def _analyze_risk(self, info, cpu_percent, memory_mb, connections):
    risk_flags = []
    score = 0
    exe = info["exe"] or ""
    exe_lower = exe.lower()

    if cpu_percent >= self.CPU_LIMIT:
      risk_flags.append("high_cpu")
      score += 20

    if memory_mb >= self.RAM_MB_LIMIT:
      risk_flags.append("high_ram")
      score += 15

    external_connections = [
      connection for connection in connections
      if self._is_external_address(connection.remote_address)
    ]
    if external_connections:
      risk_flags.append("external_network_connection")
      score += 25

    if exe and any(path in exe_lower for path in self.RISK_PATHS):
      risk_flags.append("unusual_path")
      score += 20

    if not exe:
      risk_flags.append("executable_path_unavailable")
      score += 10

    recommendation = None
    if score > 0:
      recommendation = (
        "Verificar assinatura, caminho do executavel e reputacao do processo "
        "antes de qualquer acao corretiva."
      )

    return risk_flags, score, recommendation

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
