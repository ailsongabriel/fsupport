from views.base_view import BaseView

class SecurityView(BaseView):

  def show_security_info(self, security_info):
    lines = self._build_lines(security_info)
    width = self.get_width(lines)
    self.print_title("SEGURANÇA", width)

    self.print_subtitle("Antivírus instalados", width)
    print("")
    for i, av in enumerate(security_info.antivirus_list):
      status = self._format_status(av.active)
      print(f"Nome        = {av.name}")
      print(f"Status      = {status}")
      if av.up_to_date is not None:
        print(f"Atualizado  = {'Sim' if av.up_to_date else 'Não'}")
      if av.note:
        print(f"Observação  = {av.note}")
      if i < len(security_info.antivirus_list) - 1:
        self.print_separator(width)

    self.print_subtitle("Firewall", width)
    fw_status = self._format_status(security_info.firewall.active)
    print(f"Status      = {fw_status}")
    if security_info.firewall.note:
      print(f"Observação  = {security_info.firewall.note}")
    self.print_separator(width)

  def _build_lines(self, security_info) -> list:
    lines = []
    for av in security_info.antivirus_list:
      lines.append(f"Nome        = {av.name}")
      lines.append(f"Status      = {self._format_status(av.active)}")
      if av.note:
        lines.append(f"Observação  = {av.note}")
    lines.append(f"Firewall    = {self._format_status(security_info.firewall.active)}")
    return lines

  def _format_status(self, value) -> str:
    if value is True:
      return "Ativo"
    if value is False:
      return "Inativo"
    return "Não detectado"
