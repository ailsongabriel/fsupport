from datetime import datetime, timedelta
import platform
import subprocess

import psutil


class WindowsHealthService:

  def is_supported(self):
    return platform.system() == "Windows"

  def get_health_info(self):
    if not self.is_supported():
      return None

    boot_time = datetime.fromtimestamp(psutil.boot_time())
    return {
      "boot_time": boot_time.isoformat(timespec="seconds"),
      "uptime_days": (datetime.now() - boot_time).days,
      "latest_hotfix": self._get_latest_hotfix(),
      "critical_events_7d": self._count_recent_critical_events()
    }

  def _get_latest_hotfix(self):
    command = (
      "Get-HotFix | Sort-Object InstalledOn -Descending | "
      "Select-Object -First 1 HotFixID, InstalledOn | ConvertTo-Json"
    )
    result = subprocess.run(
      ["powershell", "-NoProfile", "-Command", command],
      capture_output=True,
      text=True,
      timeout=15
    )
    if result.returncode != 0 or not result.stdout.strip():
      return None

    import json
    data = json.loads(result.stdout)
    installed_at = self._parse_powershell_date(data.get("InstalledOn"))
    age_days = (datetime.now() - installed_at).days if installed_at else None
    return {
      "id": data.get("HotFixID"),
      "installed_on": installed_at.isoformat(timespec="seconds") if installed_at else str(data.get("InstalledOn")),
      "age_days": age_days
    }

  def _count_recent_critical_events(self):
    start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    command = (
      "$events = Get-WinEvent -FilterHashtable "
      f"@{{LogName='System'; Level=1; StartTime='{start_time}'}} -ErrorAction SilentlyContinue; "
      "if ($events) { $events.Count } else { 0 }"
    )
    result = subprocess.run(
      ["powershell", "-NoProfile", "-Command", command],
      capture_output=True,
      text=True,
      timeout=15
    )
    if result.returncode != 0:
      return None

    try:
      return int(result.stdout.strip() or "0")
    except ValueError:
      return None

  def _parse_powershell_date(self, value):
    if not isinstance(value, str):
      return None

    normalized = value.replace("/Date(", "").replace(")/", "")
    if normalized.isdigit():
      return datetime.fromtimestamp(int(normalized[:10]))

    for fmt in ("%Y-%m-%dT%H:%M:%S", "%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
      try:
        return datetime.strptime(value[:19], fmt)
      except ValueError:
        continue
    return None
