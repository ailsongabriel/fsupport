from views.base_view import BaseView

class RamView(BaseView):

  def show_ram_info(self, ram_info):

    lines =[
      f"Total       = {self.format_size(ram_info.total)}",
      f"Em uso      = {self.format_size(ram_info.used)}",
      f"Disponível  = {self.format_size(ram_info.available)}",
      f"Uso         = {ram_info.usage}%",
    ]

    if ram_info.average_usage is not None:
      lines.append(f"Uso Médio   = {ram_info.average_usage}%")
    if ram_info.peak_usage is not None:
      lines.append(f"Pico de Uso = {ram_info.peak_usage}%")

    width = self.get_width(lines)
    self.print_title("RAM", width)
    for line in lines:
      print(line)
