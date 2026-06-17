class AntivirusInfo:
  def __init__(self, name, active, up_to_date=None):
    self.name = name
    self.active = active
    self.up_to_date = up_to_date  # Futuro

class FirewallInfo:
  def __init__(self, active, profiles=None):
    self.active = active
    self.profiles = profiles  # Futuro (Domain/Private/Public)

class SecurityInfo:
  def __init__(self, antivirus_list, firewall):
    self.antivirus_list = antivirus_list  # list[AntivirusInfo]
    self.firewall = firewall              # FirewallInfo