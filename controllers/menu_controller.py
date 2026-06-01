from views.menu_view import MenuView
from core.utils import clear_screen

class MenuController:

  def __init__(self):
    self.menu = MenuView()
    self.opcoes = {
      1:"Diagnóstico rápido",
      2:"Diagnóstico completo",
      3: "Ver processos pesados",
      4:"Ver uso de RAM",
      5: "Ver uso de CPU",
      6: "Ver uso de disco",
      7: "Ver rede",
      8: "Ver temperatura",
      9: "Encontrar arquivos duplicados",
      10: "Limpeza automática",
      11: "Startup do sistema",
      12: "Segurança",
      13: "Benchmark",
      14: "Gerar relatório",
      15: "Monitoramento em tempo real",
      0: "Sair"
    }

  def iniciar(self):
    self.menu.show_menu(self.opcoes)
    self.processar_opcao()

  def processar_opcao(self):
    opcao = 1
    while opcao != 0:
      clear_screen()
      self.menu.show_menu(self.opcoes)
      opcao = self.menu.get_option()
      if opcao not in self.opcoes:
        self.menu.show_message("Opcao inválida")
        self.menu.pause()
      else: 
        if opcao == 0: self.sair()
        else: self.menu.show_message(f"{self.opcoes[opcao]} esta em desenvolvimento")

  def sair(self):
    self.menu.show_message("Saindo do sistema")


