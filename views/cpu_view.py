from views.base_view import BaseView

class CpuView(BaseView):

  def show_cpu_info(self, cpu_info):

    frequency = cpu_info.frequency if cpu_info.frequency else "Unknown"

    print("\n======================== CPU =========================")
    print(f"CPU         = {cpu_info.model}")
    print(f"Uso         = {cpu_info.usage}%")
    print(f"Frequencia  = {frequency} GHz")
    print(f"Nucleos     = {cpu_info.cores}")
    print(f"Threads     = {cpu_info.threads}")

    if cpu_info.average_usage is not None:
      print(f"Uso Médio   = {cpu_info.average_usage}%")

    if cpu_info.peak_usage is not None:
      print(f"Pico de Uso = {cpu_info.peak_usage}%")