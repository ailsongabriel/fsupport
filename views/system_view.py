from views.base_view import BaseView

class SystemView(BaseView):

  def show_system_info(self, system_info):

    lines = [
      f"Hostname      = {system_info.hostname}",
      f"Username      = {system_info.username}",
      f"OS            = {system_info.os_name}",
      f"Arquitetura   = {system_info.architecture}"
    ]
    
    width = self.get_width(lines)
    self.print_title("INFORMAÇÕES DO SISTEMA", width)
    for line in lines:
      print(line)