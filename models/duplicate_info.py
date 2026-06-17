class DuplicateInfo:
  def __init__(self, path, size, hash, modified_at):
    self.path = path
    self.size = size
    self.hash = hash
    self.modified_at = modified_at  # float (os.path.getmtime)


class DuplicateGroup:
  def __init__(self, hash, files):
    self.hash = hash
    self.files = files                              # list[DuplicateInfo]
    self.total_wasted = (len(files) - 1) * files[0].size  # espaço recuperável