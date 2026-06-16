from views.base_view import BaseView

class DiskView(BaseView):

  def show_disk_info(self, disk_info):

    lines = []

    for disk in disk_info:
      lines.extend([
        f"Partição    = {disk.partition}",
        f"Total       = {self.format_size(disk.total)}",
        f"Em uso      = {self.format_size(disk.used)}",
        f"Disponível  = {self.format_size(disk.free)}",
        f"Uso         = {disk.percent:.2f}%"
      ])

    width = self.get_width(lines)
    self.print_title("DISCO", width)
    for i, disk in enumerate(disk_info):
      print(f"Partição    = {disk.partition}")
      print(f"Total       = {self.format_size(disk.total)}")
      print(f"Em uso      = {self.format_size(disk.used)}")
      print(f"Disponível  = {self.format_size(disk.free)}")
      print(f"Uso         = {disk.percent:.2f}%")
      if i < len(disk_info) - 1:
        self.print_separator(width)