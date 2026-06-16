from views.base_view import BaseView

class CpuView(BaseView):

  def show_cpu_info(self, cpu_info):

    frequency = cpu_info.frequency if cpu_info.frequency else "Unknown"
    lines = [
      f"CPU         = {cpu_info.model}",
      f"Uso         = {cpu_info.usage}%",
      f"Frequencia  = {frequency} GHz",
      f"Nucleos     = {cpu_info.cores}",
      f"Threads     = {cpu_info.threads}"
    ]

    if cpu_info.average_usage is not None:
      lines.append(f"Uso Médio   = {cpu_info.average_usage}%")
    if cpu_info.peak_usage is not None:
      lines.append(f"Pico de Uso = {cpu_info.peak_usage}%")

    width = self.get_width(lines)
    self.print_title("CPU", width)
    for line in lines:
      print(line)