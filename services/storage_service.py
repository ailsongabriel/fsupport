import json
from pathlib import Path


class StorageService:

  def __init__(self, base_path="storage"):
    self.base_path = Path(base_path)

  def save_json(self, category, filename, data):
    directory = self.base_path / category
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
      json.dump(data, file, ensure_ascii=False, indent=2)

    return str(path)

  def save_snapshot(self, category, timestamp, data):
    safe_timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    session_path = self.save_json(category, f"scans/{safe_timestamp}.json", data)
    latest_path = self.save_json(category, "latest_scan.json", data)
    return latest_path, session_path

  def save_session(self, category, timestamp, data):
    safe_timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")
    session_path = self.save_json(category, f"sessions/{safe_timestamp}.json", data)
    latest_path = self.save_json(category, "latest_session.json", data)
    return latest_path, session_path

  def load_json(self, category, filename):
    path = self.base_path / category / filename
    if not path.exists():
      return None

    with path.open("r", encoding="utf-8") as file:
      return json.load(file)
