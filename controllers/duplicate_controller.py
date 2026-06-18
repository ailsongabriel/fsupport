from services.duplicate_service import DuplicateService
from views.duplicate_view import DuplicateView
from core.utils import clear_screen


class DuplicateController:
  def __init__(self):
    self.service = DuplicateService()
    self.view = DuplicateView()

  def show_duplicates(self):
    scope = self.view.ask_scope()
    if scope is None:
      return

    if scope == "directory":
      root = self.view.ask_path()
      if root is None:
        return
    else:
      root = self.service.get_default_root()  # C:\ ou /

    self.view.show_message(f"\nAnalisando: {root}\nIsso pode levar alguns instantes...\n")
    groups = self.service.find_duplicates(root)
    clear_screen()

    self.view.show_report(groups)

    if not groups:
      return

    action = self.view.ask_action()

    if action == "export":
      dest = self.view.ask_export_path()
      if dest:
        filepath = self.service.export_csv(groups, dest)
        self.view.show_message(f"\nRelatório exportado: {filepath}")

    elif action == "quarantine":
      dest = self.view.ask_quarantine_path()
      if dest:
        if not self.view.confirm_quarantine():
          self.view.show_message("\nOperação cancelada.")
          return
        moved = self.service.move_to_quarantine(groups, dest)
        self.view.show_message(f"\n{len(moved)} arquivo(s) movido(s) para quarentena: {dest}")
