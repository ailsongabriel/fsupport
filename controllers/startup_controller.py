from datetime import datetime

from services.startup_service import StartupService
from services.storage_service import StorageService
from views.startup_view import StartupView
from core.utils import clear_screen

class StartupController():
  def __init__(self):
    self.service = StartupService()
    self.storage = StorageService()
    self.view = StartupView()

  def show_startup_items(self):
    self.view.show_message("\nColetando itens de inicialização...\n")
    startup_items = self.service.get_startup_items()
    scan = self._build_scan(startup_items)
    collected_at = datetime.fromisoformat(scan["collected_at"])
    latest_path, session_path = self.storage.save_snapshot("startup", collected_at, scan)

    clear_screen()
    self.view.show_startup_items(startup_items, latest_path, session_path)

  def _build_scan(self, startup_items):
    collected_at = datetime.now()
    items = [self._item_to_dict(item) for item in startup_items]
    enabled_items = [item for item in items if item["enabled"]]
    review_items = [item for item in enabled_items if item["startup_flags"]]

    return {
      "collected_at": collected_at.isoformat(timespec="seconds"),
      "summary": {
        "total_items": len(items),
        "enabled_count": len(enabled_items),
        "disabled_count": len(items) - len(enabled_items),
        "review_count": len(review_items)
      },
      "items": items,
      "enabled_items": enabled_items,
      "review_items": review_items
    }

  def _item_to_dict(self, item):
    command = item.command or ""
    command_lower = command.lower()
    name_lower = (item.name or "").lower()
    flags = []

    heavy_keywords = [
      "adobe",
      "discord",
      "dropbox",
      "launcher",
      "onedrive",
      "steam",
      "teams",
      "updater"
    ]
    unusual_paths = [
      "\\appdata\\local\\temp\\",
      "\\appdata\\roaming\\",
      "\\downloads\\",
      "\\temp\\"
    ]

    if any(keyword in name_lower or keyword in command_lower for keyword in heavy_keywords):
      flags.append("review_performance_impact")

    if any(path in command_lower for path in unusual_paths):
      flags.append("review_unusual_startup_path")

    if "runonce" in (item.location or "").lower():
      flags.append("review_runonce_entry")

    return {
      "name": item.name,
      "command": item.command,
      "location": item.location,
      "enabled": item.enabled,
      "startup_flags": flags
    }
