from views.base_view import BaseView

class MenuView(BaseView):

  def show_menu(self, opcoes):
    for opcao,nome in opcoes.items():
      self.show_message(f"{opcao} - {nome}")

  def get_option(self):
    opcao = int(input("\nDigite a opcao desejada:"))
    return opcao