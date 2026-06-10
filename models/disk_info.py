class DiskInfo:
  def __init__(self, partition, total, used, free, percent):
    self.partition = partition
    self.total = total
    self.used = used
    self.free = free
    self.percent = percent