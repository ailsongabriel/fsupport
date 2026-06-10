from views.base_view import BaseView

class MenuView(BaseView):

  def show_banner(self):
    print(r"""
__________   ________                                   _____ 
___  ____╱   __  ___╱___  ________________________________  ╱_
__  ╱_       _____ ╲_  ╱ ╱ ╱__  __ ╲__  __ ╲  __ ╲_  ___╱  __╱
_  __╱       ____╱ ╱╱ ╱_╱ ╱__  ╱_╱ ╱_  ╱_╱ ╱ ╱_╱ ╱  ╱   ╱ ╱_  
╱_╱          ╱____╱ ╲__,_╱ _  .___╱_  .___╱╲____╱╱_╱    ╲__╱  
                           ╱_╱     ╱_╱                        
""")

  def show_menu(self, opcoes):
    print("\n[ FS Support ] =======================\n")
    for opcao,nome in opcoes.items():
      self.show_message(f"{opcao} - {nome}")

  def get_option(self):
    opcao = int(input("\nDigite a opcao desejada:"))
    return opcao