from views.base_view import BaseView

class RamView(BaseView):

  def show_ram_info(self, ram_info):
    print("\n======================== RAM =========================")
    print(f"Total       = {self.format_size(ram_info.total)}")
    print(f"Em uso      = {self.format_size(ram_info.used)}")
    print(f"Disponível  = {self.format_size(ram_info.available)}")
    print(f"Uso         = {ram_info.usage}%")

    if ram_info.average_usage is not None:
      print(f"Uso Médio   = {ram_info.average_usage}%")

    if ram_info.peak_usage is not None:
      print(f"Pico de Uso = {ram_info.peak_usage}%")