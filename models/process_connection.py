class ProcessConnection:
  def __init__(self, local_address=None, remote_address=None, status=None):
    self.local_address = local_address
    self.remote_address = remote_address
    self.status = status

  def to_dict(self):
    return {
      "local_address": self.local_address,
      "remote_address": self.remote_address,
      "status": self.status
    }
