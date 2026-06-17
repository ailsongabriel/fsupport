from views.menu_view import MenuView
from core.utils import clear_screen
from controllers.system_controller import SystemController
from controllers.cpu_controller import CpuController
from controllers.ram_controller import RamController
from controllers.disk_controller import DiskController
from controllers.network_controller import NetworkController
from controllers.startup_controller import StartupController
from controllers.duplicate_controller import DuplicateController
from controllers.security_controller import SecurityController

class MenuController:
  
  def __init__(self):
    self.menu = MenuView()
    self.opcoes = { # Dic para visualizacao
      1: " Diagnóstico rápido",
      2: " Diagnóstico completo",
      3: " Ver processos pesados",
      4: " Ver uso de RAM",
      5: " Ver uso de CPU",
      6: " Ver uso de disco",
      7: " Ver rede",
      8: " Startup do sistema",
      9: " Encontrar arquivos duplicados",
      10: "Limpeza automática",
      11: "Segurança",
      12: "Gerar relatório",
      13: "Monitoramento em tempo real",
      14: "Informações do Sistema",
      0: " Sair"
    }
    self.acoes = { # Dic para os parametros
      0: self.sair,
      1: self.diagnostico_rapido,
      2: self.diagnostico_completo,
      3: self.processos_pesados,
      4: self.ram,
      5: self.cpu,
      6: self.disco,
      7: self.rede,
      8: self.startup,
      9: self.duplicados,
      10: self.limpeza,
      11: self.seguranca,
      12: self.relatorio,
      13: self.monitoramento,
      14: self.system_info
    }
    
    self.cpu_controller = CpuController()
    self.system_controller = SystemController()
    self.ram_controller = RamController()
    self.disk_controller = DiskController()
    self.network_controller = NetworkController()
    self.startup_controller = StartupController()
    self.duplicate_controller = DuplicateController()
    self.security_controller = SecurityController()

  def iniciar(self): # Loop do menu
    clear_screen()
    self.menu.show_banner()
    while True:
      self.menu.show_menu(self.opcoes)
      opcao = self.menu.get_option()

      if opcao == 0:
        self.sair()
        break

      self.processar_opcao(opcao)
      clear_screen()

  def processar_opcao(self, opcao): # Processa a opcao escolhida
    acao = self.acoes.get(opcao)

    if acao:
      acao()
      self.menu.pause()
    else:
      self.menu.show_message("Opção inválida")
      self.menu.pause()


  #Opcao 0
  def sair(self):
    clear_screen()
    self.menu.show_message("\n\tDesligando...")
    self.menu.close_banner()

  #Opcao 1
  def diagnostico_rapido(self):
    self.menu.show_message("Diagnóstico rápido em desenvolvimento")

  #Opcao 2
  def diagnostico_completo(self):
    self.menu.show_message("Diagnóstico completo em desenvolvimento")

  #Opcao 3
  def processos_pesados(self):
    self.menu.show_message("Ver processos pesados em desenvolvimento")

  #Opcao 4
  def ram(self):
    self.ram_controller.show_info()

  #Opcao 5
  def cpu(self):
    self.cpu_controller.show_info()

  #Opcao 6
  def disco(self):
    self.disk_controller.show_info()

  #Opcao 7
  def rede(self):
    self.network_controller.show_info()

  #Opcao 8
  def startup(self):
    self.startup_controller.show_startup_items()

  #Opcao 9
  def duplicados(self):
    self.duplicate_controller.show_duplicates()

  #Opcao 10
  def limpeza(self):
    self.menu.show_message("Limpeza automática em desenvolvimento")

  #Opcao 11
  def seguranca(self):
    self.security_controller.show_info()

  #Opcao 12
  def relatorio(self):
    self.menu.show_message("Gerar relatório em desenvolvimento")

  #Opcao 13
  def monitoramento(self):
    self.menu.show_message("Monitoramento em tempo real em desenvolvimento")
  
  #Opcao 14
  def system_info(self):
    self.system_controller.show_info()