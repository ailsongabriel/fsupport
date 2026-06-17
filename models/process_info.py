class ProcessInfo:
  def __init__(
    self,
    pid,
    name,
    username,
    cpu_percent,
    memory_mb,
    memory_percent,
    exe,
    cmdline,
    create_time,
    connections=None,
    risk_flags=None,
    risk_score=0,
    recommendation=None
  ):
    self.pid = pid
    self.name = name
    self.username = username
    self.cpu_percent = cpu_percent
    self.memory_mb = memory_mb
    self.memory_percent = memory_percent
    self.exe = exe
    self.cmdline = cmdline
    self.create_time = create_time
    self.connections = connections if connections is not None else []
    self.risk_flags = risk_flags if risk_flags is not None else []
    self.risk_score = risk_score
    self.recommendation = recommendation

  def to_dict(self):
    return {
      "pid": self.pid,
      "name": self.name,
      "username": self.username,
      "cpu_percent": self.cpu_percent,
      "memory_mb": self.memory_mb,
      "memory_percent": self.memory_percent,
      "exe": self.exe,
      "cmdline": self.cmdline,
      "create_time": self.create_time,
      "connections": [connection.to_dict() for connection in self.connections],
      "risk_flags": self.risk_flags,
      "risk_score": self.risk_score,
      "recommendation": self.recommendation
    }
