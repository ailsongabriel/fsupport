from views.base_view import BaseView

class DiskView(BaseView):

  def show_disk_info(self, disk_info):

    print("\n======================== Disco =========================")
    for i, disk in enumerate(disk_info):
      print(f"Partição    = {disk.partition}")
      print(f"Total       = {self.format_size(disk.total)}")
      print(f"Em uso      = {self.format_size(disk.used)}")
      print(f"Disponível  = {self.format_size(disk.free)}")
      print(f"Uso         = {disk.percent:.2f}%")
      if len(disk_info) > 1 and i < len(disk_info) - 1: # Se houver mais de um disco e não for o último, imprime uma linha de separação
        print("------------------------------------------------------")