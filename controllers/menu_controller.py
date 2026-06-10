from views.menu_view import MenuView
from core.utils import clear_screen
from controllers.system_controller import SystemController
from controllers.cpu_controller import CpuController
from controllers.ram_controller import RamController
from controllers.disk_controller import DiskController

class MenuController:
  
  def __init__(self):
    self.menu = MenuView() # View do menu

    # Dicionários para opções e ações
    self.opcoes = { # Dic para visualizacao
      1: " Diagnóstico rápido",
      2: " Diagnóstico completo",
      3: " Ver processos pesados",
      4: " Ver uso de RAM",
      5: " Ver uso de CPU",
      6: " Ver uso de disco",
      7: " Ver rede",
      8: " Ver temperatura",
      9: " Encontrar arquivos duplicados",
      10: "Limpeza automática",
      11: "Startup do sistema",
      12: "Segurança",
      13: "Benchmark",
      14: "Gerar relatório",
      15: "Monitoramento em tempo real",
      16: "Informações do Sistema",
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
      8: self.temperatura,
      9: self.duplicados,
      10: self.limpeza,
      11: self.startup,
      12: self.seguranca,
      13: self.benchmark,
      14: self.relatorio,
      15: self.monitoramento,
      16: self.system_info
    }
    
    # Controladores para cada funcionalidade
    self.cpu_controller = CpuController() # Controlador de CPU
    self.system_controller = SystemController() # Controlador de sistema
    self.ram_controller = RamController() # Controlador de RAM
    self.disk_controller = DiskController() # Controlador de disco

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
    self.menu.show_message("Saindo do sistema")

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
    self.menu.show_message("Ver rede em desenvolvimento")

  #Opcao 8
  def temperatura(self):
    self.menu.show_message("Ver temperatura em desenvolvimento")

  #Opcao 9
  def duplicados(self):
    self.menu.show_message("Encontrar arquivos duplicados em desenvolvimento")

  #Opcao 10
  def limpeza(self):
    self.menu.show_message("Limpeza automática em desenvolvimento")

  #Opcao 11
  def startup(self):
    self.menu.show_message("Startup do sistema em desenvolvimento")

  #Opcao 12
  def seguranca(self):
    self.menu.show_message("Segurança em desenvolvimento")

  #Opcao 13
  def benchmark(self):
    self.menu.show_message("Benchmark em desenvolvimento")

  #Opcao 14
  def relatorio(self):
    self.menu.show_message("Gerar relatório em desenvolvimento")

  #Opcao 15
  def monitoramento(self):
    self.menu.show_message("Monitoramento em tempo real em desenvolvimento")
  
  #Opcao 16
  def system_info(self):
    self.system_controller.show_info()