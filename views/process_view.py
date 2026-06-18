from views.base_view import BaseView


class ProcessView(BaseView):

  def show_process_scan(self, scan, latest_path, session_path):
    summary = scan["summary"]
    lines = [
      f"Coletado em             = {scan['collected_at']}",
      f"Processos analisados    = {summary['total_processes']}",
      f"Com conexoes de rede    = {summary['network_processes_count']}",
      f"Suspeitas reais         = {summary['suspicious_count']}",
      f"Dados para diagnostico  = {latest_path}",
      f"Historico da coleta     = {session_path}"
    ]

    width = self.get_width(lines)
    self.print_title("PROCESSOS EM DESTAQUE", width)
    for line in lines:
      print(line)

    self._print_process_table("Maior uso de CPU", scan["top_cpu"], width, mode="compact")
    self._print_process_table("Maior uso de RAM", scan["top_ram"], width, mode="compact")
    self._print_process_table("Processos com conexao de rede", scan["network_processes"], width, mode="network")
    self._print_process_table("Suspeitas para investigar", scan["suspicious_processes"], width, mode="risk")

  def _print_process_table(self, title, processes, width, mode="compact"):
    self.print_subtitle(title, width)

    if not processes:
      print("Nenhum processo encontrado.")
      return

    for process in processes[:10]:
      print("")
      print(
        f"PID {process['pid']:<7} "
        f"{self._shorten(process['name'], 24):<24} "
        f"CPU {process['cpu_percent']:>6.2f}% "
        f"RAM {process['memory_mb']:>8.2f} MB"
      )

      if process["activity_flags"]:
        print(f"  Atividade: {', '.join(process['activity_flags'])}")

      if mode == "risk":
        print(f"  Risco: {process['risk_score']}")
        if process["risk_flags"]:
          print(f"  Sinais: {', '.join(process['risk_flags'])}")

      if mode in {"network", "risk"} and process["exe"]:
        print(f"  Exe: {self._shorten(process['exe'], width - 7)}")

      if mode in {"network", "risk"} and process["connections"]:
        for connection in process["connections"][:3]:
          print(
            f"  Rede: {connection['local_address']} -> "
            f"{connection['remote_address']} ({connection['status']})"
          )

      if mode == "risk" and process["recommendation"]:
        print(f"  Sugestao: {process['recommendation']}")

  def _shorten(self, value, max_length):
    if value is None:
      return "N/A"

    if len(value) <= max_length:
      return value

    return value[:max_length - 3] + "..."
