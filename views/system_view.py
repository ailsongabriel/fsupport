class SystemView:

  def show_system_info(self, system_info):
    print("\n=============== INFORMAÇÕES DO SISTEMA ===============")
    print(f"Hostname      = {system_info.hostname}")
    print(f"Username      = {system_info.username}")
    print(f"OS            = {system_info.os_name}")
    print(f"Architecture  = {system_info.architecture}")