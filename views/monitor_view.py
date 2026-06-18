from views.base_view import BaseView


class MonitorView(BaseView):

  def show_dashboard(self, snapshot, session, interval):
    lines = self._build_dashboard_lines(snapshot, session)
    width = self.get_width(lines)

    self.print_title("MONITORAMENTO EM TEMPO REAL", width)
    print(f"Atualizado em       = {snapshot.timestamp.strftime('%H:%M:%S')}")

    self.print_subtitle("Uso atual", width)
    print(f"CPU                 = {snapshot.cpu_usage:.2f}%")
    print(f"RAM                 = {snapshot.ram_usage:.2f}%")
    print(f"RAM disponivel      = {self.format_size(snapshot.ram_available)}")

    self.print_subtitle("Disco", width)
    for disk in snapshot.disks:
      print(
        f"{disk.partition:<18} = {disk.percent:>6.2f}% "
        f"(livre: {self.format_size(disk.free)})"
      )

    self.print_subtitle("Rede", width)
    print(f"Download atual      = {self.format_size(snapshot.download_rate)}/s")
    print(f"Upload atual        = {self.format_size(snapshot.upload_rate)}/s")
    print(f"Download acumulado  = {self.format_size(snapshot.bytes_recv)}")
    print(f"Upload acumulado    = {self.format_size(snapshot.bytes_sent)}")

    self.print_subtitle("Picos da sessao", width)
    print(f"Pico CPU            = {session.peak_cpu:.2f}%")
    print(f"Pico RAM            = {session.peak_ram:.2f}%")
    if session.peak_ram_available is not None:
      print(f"Menor RAM livre     = {self.format_size(session.peak_ram_available)}")
    print(f"Pico download       = {self.format_size(session.peak_download_rate)}/s")
    print(f"Pico upload         = {self.format_size(session.peak_upload_rate)}/s")

    if snapshot.alerts:
      self.print_subtitle("Alertas atuais", width)
      for alert in snapshot.alerts:
        print(f"[{alert.level.upper()}] {alert.component}: {alert.value:.2f}%")
        print(f"  {alert.message}")

    print(f"\nAtualizando em {interval}s. Pressione CTRL+C para encerrar e salvar.")

  def show_session_summary(self, session_data, latest_path, session_path):
    peaks = session_data["peaks"]
    averages = session_data["averages"]
    lines = [
      f"Inicio              = {session_data['started_at']}",
      f"Fim                 = {session_data['finished_at']}",
      f"Duracao             = {session_data['duration_seconds']}s",
      f"Amostras            = {session_data['samples_count']}",
      f"CPU media           = {averages['cpu_usage']}%",
      f"CPU pico            = {peaks['cpu_usage']}%",
      f"RAM media           = {averages['ram_usage']}%",
      f"RAM pico            = {peaks['ram_usage']}%",
      f"Dados diagnostico   = {latest_path}",
      f"Historico sessao    = {session_path}"
    ]
    width = self.get_width(lines)

    self.print_title("RESUMO DO MONITORAMENTO", width)
    for line in lines:
      print(line)

    print(f"Menor RAM livre     = {self.format_size(peaks['lowest_ram_available'])}")
    print(f"Pico download       = {self.format_size(peaks['download_rate'])}/s")
    print(f"Pico upload         = {self.format_size(peaks['upload_rate'])}/s")

    if peaks["disk_usage"]:
      self.print_subtitle("Picos de disco", width)
      for partition, percent in peaks["disk_usage"].items():
        print(f"{partition:<18} = {percent:.2f}%")

    if session_data["alerts"]:
      self.print_subtitle("Alertas registrados", width)
      for alert in session_data["alerts"]:
        print(f"[{alert['level'].upper()}] {alert['component']}: {alert['value']}%")
        if alert["recommendation"]:
          print(f"  Sugestao: {alert['recommendation']}")

  def _build_dashboard_lines(self, snapshot, session):
    lines = [
      f"Atualizado em       = {snapshot.timestamp.strftime('%H:%M:%S')}",
      f"CPU                 = {snapshot.cpu_usage:.2f}%",
      f"RAM                 = {snapshot.ram_usage:.2f}%",
      f"RAM disponivel      = {self.format_size(snapshot.ram_available)}",
      f"Download atual      = {self.format_size(snapshot.download_rate)}/s",
      f"Upload atual        = {self.format_size(snapshot.upload_rate)}/s",
      f"Pico CPU            = {session.peak_cpu:.2f}%",
      f"Pico RAM            = {session.peak_ram:.2f}%"
    ]

    for disk in snapshot.disks:
      lines.append(f"{disk.partition} = {disk.percent:.2f}%")

    for alert in snapshot.alerts:
      lines.append(f"[{alert.level.upper()}] {alert.component}: {alert.value:.2f}%")

    return lines
