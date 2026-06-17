from views.base_view import BaseView
import os


class DuplicateView(BaseView):

    def ask_scope(self) -> str | None:
      self.print_title("ENCONTRAR DUPLICATAS", 50)
      print("\n1 - Diretório específico")
      print("2 - Disco/partição inteira")
      print("0 - Voltar")
      choice = input("\nEscolha: ").strip()
      if choice == "1":
        return "directory"
      if choice == "2":
        return "disk"
      return None

    def ask_path(self) -> str | None:
      path = input("\nCaminho do diretório: ").strip()
      if not os.path.exists(path):
        self.show_message(f"\nCaminho não encontrado: {path}")
        return None
      return path

    def show_report(self, groups: list):
      if not groups:
        self.show_message("\nNenhum arquivo duplicado encontrado.")
        return

      total_wasted = sum(g.total_wasted for g in groups)

      lines = [f"Grupos encontrados: {len(groups)}"]
      for g in groups:
        for f in g.files:
          lines.append(f"  {f.path}")

      width = self.get_width(lines)
      self.print_title("DUPLICATAS ENCONTRADAS", width)
      print(f"Grupos encontrados  = {len(groups)}")
      print(f"Espaço recuperável  = {self.format_size(total_wasted)}")

      for i, group in enumerate(groups):
        self.print_subtitle(f"Grupo {i + 1} — {self.format_size(group.files[0].size)} cada", width)
        for file in group.files:
          print(f"  {file.path}")

    def ask_action(self) -> str | None:
      print("\n1 - Exportar lista (CSV)")
      print("2 - Mover duplicatas para quarentena")
      print("0 - Voltar")
      choice = input("\nEscolha: ").strip()
      if choice == "1":
        return "export"
      if choice == "2":
        return "quarantine"
      return None

    def ask_export_path(self) -> str | None:
      path = input("\nDiretório para salvar o CSV: ").strip()
      if not os.path.isdir(path):
        self.show_message(f"\nDiretório inválido: {path}")
        return None
      return path

    def ask_quarantine_path(self) -> str | None:
      path = input("\nDiretório de quarentena: ").strip()
      if not path:
        self.show_message("\nCaminho não informado.")
        return None
      return path