class MenuView:

  def show_menu(self, opcoes):
    for opcao,nome in opcoes.items():
      self.show_message(f"{opcao} - {nome}")

  def get_option(self):
    opcao = int(input("\nDigite a opcao desejada:"))
    return opcao

  def show_message(self, message):
    print(message)

  def pause(self):
    input("\nPressione ENTER para continuar...")