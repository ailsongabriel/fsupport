from views.base_view import BaseView


class ProcessView(BaseView):

  def show_process_scan(self, scan, latest_path, session_path):
    summary = scan["summary"]
    lines = [
      f"Coletado em             = {scan['collected_at']}",
      f"Processos analisados    = {summary['total_processes']}",
      f"Com conexoes de rede    = {summary['network_processes_count']}",
      f"Suspeitas sinalizadas   = {summary['suspicious_count']}",
      f"Arquivo latest          = {latest_path}",
      f"Arquivo da coleta       = {session_path}"
    ]

    width = self.get_width(lines)
    self.print_title("PROCESSOS PESADOS E SUSPEITOS", width)
    for line in lines:
      print(line)

    self._print_process_table("Top CPU", scan["top_cpu"], width, show_connections=False)
    self._print_process_table("Top RAM", scan["top_ram"], width, show_connections=False)
    self._print_process_table("Processos com rede", scan["network_processes"], width)
    self._print_process_table("Sinais de suspeita", scan["suspicious_processes"], width)

  def _print_process_table(self, title, processes, width, show_connections=True):
    self.print_subtitle(title, width)

    if not processes:
      print("Nenhum processo encontrado.")
      return

    for process in processes[:10]:
      print(
        f"PID {process['pid']:<7} "
        f"{self._shorten(process['name'], 24):<24} "
        f"CPU {process['cpu_percent']:>6.2f}% "
        f"RAM {process['memory_mb']:>8.2f} MB "
        f"Risco {process['risk_score']:>3}"
      )

      if process["risk_flags"]:
        print(f"  Sinais: {', '.join(process['risk_flags'])}")

      if process["exe"]:
        print(f"  Exe: {self._shorten(process['exe'], width - 7)}")

      if show_connections and process["connections"]:
        for connection in process["connections"][:3]:
          print(
            f"  Rede: {connection['local_address']} -> "
            f"{connection['remote_address']} ({connection['status']})"
          )

      if process["recommendation"]:
        print(f"  Sugestao: {process['recommendation']}")

  def _shorten(self, value, max_length):
    if value is None:
      return "N/A"

    if len(value) <= max_length:
      return value

    return value[:max_length - 3] + "..."
