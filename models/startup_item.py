class StartupItem():
  def __init__(self, name, command, location, enabled=True):
    self.name = name
    self.command = command
    self.location = location
    self.enabled = enabled