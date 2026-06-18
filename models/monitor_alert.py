class MonitorAlert:
  def __init__(self, level, component, metric, value, threshold, message, recommendation=None):
    self.level = level
    self.component = component
    self.metric = metric
    self.value = value
    self.threshold = threshold
    self.message = message
    self.recommendation = recommendation

  def to_dict(self):
    return {
      "level": self.level,
      "component": self.component,
      "metric": self.metric,
      "value": self.value,
      "threshold": self.threshold,
      "message": self.message,
      "recommendation": self.recommendation
    }
