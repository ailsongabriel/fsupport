class BaseView:

  def show_message(self, message):
    print(message)

  def pause(self):
    input("\nPressione ENTER para continuar...")

  def format_size(self, size): # Formata o tamanho do disco para uma unidade legível

    if size is None: # Se o valor for None, retorna "N/A"
      return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']: # Converte o tamanho para a unidade apropriada
      if size < 1024: # Se o tamanho for menor que 1024, retorna o valor formatado com a unidade
        return f"{size:.2f} {unit}" # Formata o valor com 2 casas decimais
      size /= 1024 # Divide o tamanho por 1024 para converter para a próxima unidade
    return f"{size:.2f} PB" # Se o tamanho for maior que 1024 TB, retorna o valor em PB