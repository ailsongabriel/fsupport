from models.startup_item import StartupItem
from services.system_service import SystemService
import os

class StartupService():
  def __init__(self):
    self.system_service = SystemService()
    self.os_type = self.system_service.get_os_type()

  def get_startup_items(self):

    if self.os_type == "Windows":
      startup_items = self._get_windows_startup_items()
      return startup_items

    if self.os_type == "Linux":
      startup_items = self._get_linux_startup_items()
      return startup_items

    return []

  def _get_windows_startup_items(self):
    import winreg
    startup_items = []

    def get_enabled_status(name, startup_type="Run"):
      approved_locations = [
        (
          winreg.HKEY_CURRENT_USER,
          rf"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\{startup_type}"
        ),
        (
          winreg.HKEY_LOCAL_MACHINE,
          rf"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\{startup_type}"
        ),
      ]

      for hive, path in approved_locations:
          try:
              with winreg.OpenKey(hive, path) as key:
                  value, _ = winreg.QueryValueEx(key, name)

                  if isinstance(value, bytes) and len(value) > 0:
                      return value[0] == 0x02

          except (FileNotFoundError, OSError):
              pass

      # Se não existir em StartupApproved,
      # o Windows normalmente considera habilitado.
      return True

    registry_locations = [
      (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM\\Run"
      ),
      (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKLM\\RunOnce"
      ),
      (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU\\Run"
      ),
      (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU\\RunOnce"
      ),
    ]

    for hive, reg_path, location in registry_locations:
      try:
        with winreg.OpenKey(hive, reg_path) as key:
          i = 0

          while True:
            try:
              name, command, _ = winreg.EnumValue(key, i)

              enabled = get_enabled_status(
                name,
                "RunOnce" if "RunOnce" in reg_path else "Run"
              )

              startup_items.append(
                StartupItem(
                  name=name,
                  command=str(command),
                  location=location,
                  enabled=enabled
                )
              )

              i += 1

            except OSError:
                break

      except FileNotFoundError:
        continue
    
    startup_folders = []
    user_startup = os.getenv("APPDATA")
    all_users_startup = os.getenv("ProgramData")

    if user_startup:
      startup_folders.append(
        (
        os.path.join(
          user_startup,
          "Microsoft",
          "Windows",
          "Start Menu",
          "Programs",
          "Startup"
        ),
        "User Startup Folder"
      )
      )

    if all_users_startup:
      startup_folders.append(
        (
        os.path.join(
          all_users_startup,
          "Microsoft",
          "Windows",
          "Start Menu",
          "Programs",
          "Startup"
        ),
        "All Users Startup Folder"
      )
      )

    for folder, location in startup_folders:
      if os.path.exists(folder):

        for filename in os.listdir(folder):

          if filename.endswith((".lnk", ".exe")):

            enabled = get_enabled_status(
              filename,
              "StartupFolder"
            )

            startup_items.append(
              StartupItem(
                name=filename,
                command=os.path.join(folder, filename),
                location=location,
                enabled=enabled
              )
            )

    return startup_items
              
  def _get_linux_startup_items(self):
    startup_items = []

    autostart_dirs = [
      (
        os.path.expanduser("~/.config/autostart"),
        "User Autostart"
      ),
      (
        "/etc/xdg/autostart",
        "System Autostart"
      )
    ]

    for directory, location in autostart_dirs:

      if not os.path.isdir(directory):
        continue

      for filename in os.listdir(directory):

        if not filename.endswith(".desktop"):
          continue

        filepath = os.path.join(directory, filename)

        name = filename
        command = ""
        enabled = True

        try:
          with open(filepath, "r", encoding="utf-8") as f:

            for line in f:

              line = line.strip()

              if line.startswith("Name="):
                name = line.split("=", 1)[1]

              elif line.startswith("Exec="):
                command = line.split("=", 1)[1]

              elif line.startswith("Hidden="):
                value = line.split("=", 1)[1].lower()
                enabled = value != "true"

        except Exception:
          continue

        startup_items.append(
          StartupItem(
            name=name,
            command=command,
            location=location,
            enabled=enabled
          )
        )

    return startup_items