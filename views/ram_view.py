from views.base_view import BaseView

class RamView(BaseView):

  def show_ram_info(self, ram_info):
    print("\n======================== RAM =========================")
    print(f"Total       = {ram_info.total} GB")
    print(f"Em uso      = {ram_info.used} GB")
    print(f"Disponível  = {ram_info.available} GB")
    print(f"Uso         = {ram_info.usage}%")

    if ram_info.average_usage is not None:
      print(f"Uso Médio   = {ram_info.average_usage}%")

    if ram_info.peak_usage is not None:
      print(f"Pico de Uso = {ram_info.peak_usage}%")