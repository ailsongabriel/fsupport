from views.base_view import BaseView

class DiskView(BaseView):

  def format_size(self, size): # Formata o tamanho do disco para uma unidade legível

    if size is None: # Se o valor for None, retorna "N/A"
      return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']: # Converte o tamanho para a unidade apropriada
      if size < 1024: # Se o tamanho for menor que 1024, retorna o valor formatado com a unidade
        return f"{size:.2f} {unit}" # Formata o valor com 2 casas decimais
      size /= 1024 # Divide o tamanho por 1024 para converter para a próxima unidade
    return f"{size:.2f} PB" # Se o tamanho for maior que 1024 TB, retorna o valor em PB

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