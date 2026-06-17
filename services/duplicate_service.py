from models.duplicate_info import DuplicateInfo, DuplicateGroup
from services.system_service import SystemService
import os
import hashlib
import csv
import shutil
from collections import defaultdict


class DuplicateService:
  # Filtros Linux — mesmo padrão do DiskService
  SKIP_FS_PREFIXES = ("/proc", "/sys", "/dev/loop", "/snap")

  def __init__(self):
    self.system_service = SystemService()
    self.os_type = self.system_service.get_os_type()

  # ------------------------------------------------------------------ público

  def find_duplicates(self, root: str) -> list:
    """Retorna lista de DuplicateGroup com arquivos duplicados."""
    records = self._scan(root)
    return self._group_by_hash(records)

  def export_csv(self, groups: list, dest_path: str) -> str:
    """Exporta os grupos de duplicatas para CSV. Retorna o path gravado."""
    filepath = os.path.join(dest_path, "duplicatas.csv")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
      writer = csv.writer(f)
      writer.writerow(["hash", "caminho", "tamanho_bytes", "modificado_em"])
      for group in groups:
        for file in group.files:
          writer.writerow([
            group.hash,
            file.path,
            file.size,
            file.modified_at
          ])
    return filepath

  def move_to_quarantine(self, groups: list, quarantine_path: str) -> list:
    """
    Move os arquivos duplicados para quarentena, mantendo o primeiro de cada grupo.
    Retorna lista de paths movidos.
    """
    os.makedirs(quarantine_path, exist_ok=True)
    moved = []

    for group in groups:
      # Mantém o mais recente (maior modified_at), move os demais
      sorted_files = sorted(group.files, key=lambda f: f.modified_at, reverse=True)
      to_move = sorted_files[1:]

      for file in to_move:
        filename = os.path.basename(file.path)
        dest = os.path.join(quarantine_path, filename)
        dest = self._safe_dest(dest)  # evita colisão de nomes
        try:
          shutil.move(file.path, dest)
          moved.append(dest)
        except OSError:
          continue

    return moved
  
  def get_default_root(self) -> str:
    if self.os_type == "Windows":
      return "C:\\"
    return "/"

  # ------------------------------------------------------------------ privado

  def _scan(self, root: str) -> list:
    """Walk no diretório, retorna DuplicateInfo sem hash (apenas size)."""
    records = []
    for dirpath, _, filenames in os.walk(root):
      if self.os_type == "Linux" and self._should_skip(dirpath):
        continue
      for fname in filenames:
        path = os.path.join(dirpath, fname)
        try:
          size = os.path.getsize(path)
          modified_at = os.path.getmtime(path)
          records.append(DuplicateInfo(path, size, None, modified_at))
        except OSError:
          continue
    return records

  def _group_by_hash(self, records: list) -> list:
    """Agrupa por tamanho primeiro, depois calcula hash apenas nos candidatos."""
    by_size = defaultdict(list)
    for record in records:
      by_size[record.size].append(record)

    by_hash = defaultdict(list)
    for size_group in by_size.values():
      if len(size_group) < 2:
        continue
      for record in size_group:
        file_hash = self._hash_file(record.path)
        if file_hash is None:
          continue
        record.hash = file_hash
        by_hash[file_hash].append(record)

    return [
      DuplicateGroup(h, files)
      for h, files in by_hash.items()
      if len(files) >= 2
    ]

  def _hash_file(self, path: str, chunk_size: int = 65536) -> str | None:
    """SHA256 do arquivo. Retorna None em caso de erro de leitura."""
    h = hashlib.sha256()
    try:
      with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
          h.update(chunk)
      return h.hexdigest()
    except OSError:
      return None

  def _should_skip(self, dirpath: str) -> bool:
    return any(dirpath.startswith(prefix) for prefix in self.SKIP_FS_PREFIXES)

  def _safe_dest(self, dest: str) -> str:
    """Evita sobrescrever arquivos na quarentena com mesmo nome."""
    if not os.path.exists(dest):
      return dest
    base, ext = os.path.splitext(dest)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
      counter += 1
    return f"{base}_{counter}{ext}"