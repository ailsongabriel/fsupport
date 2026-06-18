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
from controllers.process_controller import ProcessController
from controllers.monitor_controller import MonitorController
from controllers.diagnostic_controller import DiagnosticController
from controllers.report_controller import ReportController

class MenuController:
  
  def __init__(self):
    self.menu = MenuView()
    self.opcoes = { # Dic para visualizacao
      1: " Diagnóstico rápido",
      2: " Diagnóstico completo",
      3: " Informações do sistema",
      4: " Monitoramento em tempo real",
      5: " Processos pesados",
      6: " Uso de CPU",
      7: " Uso de RAM",
      8: " Uso de disco",
      9: " Rede e conectividade",
      10: "Inicialização do sistema",
      11: "Segurança",
      12: "Arquivos duplicados",
      13: "Gerar relatório",
      0: " Sair"
    }
    self.acoes = { # Dic para os parametros
      0: self.sair,
      1: self.diagnostico_rapido,
      2: self.diagnostico_completo,
      3: self.system_info,
      4: self.monitoramento,
      5: self.processos_pesados,
      6: self.cpu,
      7: self.ram,
      8: self.disco,
      9: self.rede,
      10: self.startup,
      11: self.seguranca,
      12: self.duplicados,
      13: self.relatorio
    }
    
    self.cpu_controller = CpuController()
    self.system_controller = SystemController()
    self.ram_controller = RamController()
    self.disk_controller = DiskController()
    self.network_controller = NetworkController()
    self.startup_controller = StartupController()
    self.duplicate_controller = DuplicateController()
    self.security_controller = SecurityController()
    self.process_controller = ProcessController()
    self.monitor_controller = MonitorController()
    self.diagnostic_controller = DiagnosticController()
    self.report_controller = ReportController()

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
    if opcao is None:
      self.menu.show_message("Opção inválida. Digite apenas o número da opção.")
      self.menu.pause()
      return

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
    self.diagnostic_controller.show_quick_diagnostic()

  #Opcao 2
  def diagnostico_completo(self):
    self.diagnostic_controller.show_full_diagnostic()

  #Opcao 3
  def system_info(self):
    self.system_controller.show_info()

  #Opcao 4
  def monitoramento(self):
    self.monitor_controller.start()

  #Opcao 5
  def processos_pesados(self):
    self.process_controller.show_heavy_processes()

  #Opcao 6
  def cpu(self):
    self.cpu_controller.show_info()

  #Opcao 7
  def ram(self):
    self.ram_controller.show_info()

  #Opcao 8
  def disco(self):
    self.disk_controller.show_info()

  #Opcao 9
  def rede(self):
    self.network_controller.show_info()

  #Opcao 10
  def startup(self):
    self.startup_controller.show_startup_items()

  #Opcao 11
  def seguranca(self):
    self.security_controller.show_info()

  #Opcao 12
  def duplicados(self):
    self.duplicate_controller.show_duplicates()

  #Opcao 13
  def relatorio(self):
    self.report_controller.generate_report()
