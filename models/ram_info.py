class RamInfo:
  def __init__(self, total, used, available, usage, average_usage=None, peak_usage=None):
    self.total = total
    self.used = used
    self.available = available
    self.usage = usage

    self.average_usage = average_usage
    self.peak_usage = peak_usage