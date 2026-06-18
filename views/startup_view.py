from views.base_view import BaseView

class StartupView(BaseView):

  def show_startup_items(self, startup_items, latest_path=None, session_path=None):

    lines = []

    for item in startup_items:
      lines.extend([
        f"Nome        = {item.name}",
        f"Comando     = {item.command}",
        f"Localização = {item.location}",
        f"Habilitado  = {'Sim' if item.enabled else 'Não'}"
      ])

    width = self.get_width(lines)

    self.print_title("ITENS DE INICIALIZAÇÃO", width)

    if latest_path and session_path:
      print(f"Dados diagnostico = {latest_path}")
      print(f"Historico coleta  = {session_path}")
      self.print_separator(width)

    for i, item in enumerate(startup_items):

      print(f"Nome        = {item.name}")
      print(f"Comando     = {item.command}")
      print(f"Localização = {item.location}")
      print(f"Habilitado  = {'Sim' if item.enabled else 'Não'}")

      if i < len(startup_items) - 1:
        self.print_separator(width)
