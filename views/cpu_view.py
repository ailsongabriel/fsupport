from views.base_view import BaseView

class CpuView(BaseView):

  def show_cpu_info(self, cpu_info):

    frequency = cpu_info.frequency if cpu_info.frequency else "Unknown"

    print("\n======================== CPU =========================")
    print(f"CPU       = {cpu_info.model}")
    print(f"Usage     = {cpu_info.usage}%")
    print(f"Frequency = {frequency} GHz")
    print(f"Cores     = {cpu_info.cores}")
    print(f"Threads   = {cpu_info.threads}")