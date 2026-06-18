from datetime import datetime

from services.cpu_service import CpuService
from services.disk_service import DiskService
from services.ram_service import RamService
from services.security_service import SecurityService
from services.startup_service import StartupService
from services.storage_service import StorageService
from services.system_service import SystemService


class DiagnosticService:

  def __init__(self):
    self.storage = StorageService()
    self.cpu_service = CpuService()
    self.ram_service = RamService()
    self.disk_service = DiskService()
    self.security_service = SecurityService()
    self.startup_service = StartupService()
    self.system_service = SystemService()

  def run_quick(self):
    context = self._collect_context(include_current=True)
    findings = []

    findings.extend(self._analyze_monitoring(context["monitoring"], quick=True))
    findings.extend(self._analyze_processes(context["processes"], quick=True))
    findings.extend(self._analyze_current_resources(context["current"], quick=True))
    findings.extend(self._analyze_security(context["security"]))

    result = self._build_result("quick", context, findings)
    self._save_result(result)
    return result

  def run_full(self):
    context = self._collect_context(include_current=True)
    findings = []

    findings.extend(self._analyze_monitoring(context["monitoring"], quick=False))
    findings.extend(self._analyze_processes(context["processes"], quick=False))
    findings.extend(self._analyze_current_resources(context["current"], quick=False))
    findings.extend(self._analyze_security(context["security"]))
    findings.extend(self._analyze_startup(context["startup"]))
    findings.extend(self._analyze_software_and_hardware(context))

    result = self._build_result("full", context, findings)
    self._save_result(result)
    return result

  def _collect_context(self, include_current):
    context = {
      "monitoring": self.storage.load_json("monitoring", "latest_session.json"),
      "processes": self.storage.load_json("processes", "latest_scan.json"),
      "current": None,
      "security": None,
      "startup": None,
      "system": None,
      "collection_errors": []
    }

    if not include_current:
      return context

    context["system"] = self._safe_collect("system", self._collect_system, context)
    context["current"] = self._safe_collect("current", self._collect_current_resources, context)
    context["security"] = self._safe_collect("security", self._collect_security, context)
    context["startup"] = self._safe_collect("startup", self._collect_startup, context)
    return context

  def _safe_collect(self, name, collector, context):
    try:
      return collector()
    except Exception as error:
      context["collection_errors"].append({
        "source": name,
        "error": str(error)
      })
      return None

  def _collect_system(self):
    system = self.system_service.get_system_info()
    return {
      "hostname": system.hostname,
      "username": system.username,
      "os_name": system.os_name,
      "architecture": system.architecture
    }

  def _collect_current_resources(self):
    cpu = self.cpu_service.get_cpu_info()
    ram = self.ram_service.get_ram_info()
    disks = self.disk_service.get_disk_info()

    return {
      "cpu": {
        "model": cpu.model,
        "usage": cpu.usage,
        "frequency": cpu.frequency,
        "cores": cpu.cores,
        "threads": cpu.threads
      },
      "ram": {
        "total": ram.total,
        "used": ram.used,
        "available": ram.available,
        "usage": ram.usage
      },
      "disks": [
        {
          "partition": disk.partition,
          "total": disk.total,
          "used": disk.used,
          "free": disk.free,
          "percent": disk.percent
        }
        for disk in disks
      ]
    }

  def _collect_security(self):
    security = self.security_service.get_security_info()
    return {
      "antivirus": [
        {
          "name": antivirus.name,
          "active": antivirus.active,
          "up_to_date": antivirus.up_to_date
        }
        for antivirus in security.antivirus_list
      ],
      "firewall": {
        "active": security.firewall.active,
        "profiles": security.firewall.profiles
      }
    }

  def _collect_startup(self):
    startup_items = self.startup_service.get_startup_items()
    return [
      {
        "name": item.name,
        "command": item.command,
        "location": item.location,
        "enabled": item.enabled
      }
      for item in startup_items
    ]

  def _analyze_monitoring(self, monitoring, quick):
    if not monitoring:
      return [self._finding(
        "warning",
        "monitoring",
        "Sem dados de monitoramento",
        "Execute o monitoramento em tempo real antes do diagnostico para avaliar picos e medias.",
        "Rodar a opcao 12 por alguns minutos e repetir o diagnostico.",
        "software"
      )]

    findings = []
    peaks = monitoring.get("peaks", {})
    averages = monitoring.get("averages", {})

    peak_cpu = peaks.get("cpu_usage", 0) or 0
    avg_cpu = averages.get("cpu_usage", 0) or 0
    if peak_cpu >= 90 or avg_cpu >= 75:
      findings.append(self._finding(
        "critical" if peak_cpu >= 90 else "warning",
        "performance",
        "CPU sob carga alta",
        f"CPU media {avg_cpu}% e pico {peak_cpu}% durante o monitoramento.",
        "Verificar processos no topo de CPU; se persistir em tarefas normais, avaliar CPU mais forte ou gargalo termico.",
        "hardware"
      ))

    peak_ram = peaks.get("ram_usage", 0) or 0
    avg_ram = averages.get("ram_usage", 0) or 0
    if peak_ram >= 90 or avg_ram >= 80:
      findings.append(self._finding(
        "critical" if peak_ram >= 95 else "warning",
        "performance",
        "RAM sob pressao",
        f"RAM media {avg_ram}% e pico {peak_ram}% durante o monitoramento.",
        "Fechar programas pesados, reduzir inicializacao automatica e avaliar aumento de RAM.",
        "hardware"
      ))

    disk_usage = peaks.get("disk_usage", {}) or {}
    for partition, percent in disk_usage.items():
      if percent >= 85:
        findings.append(self._finding(
          "critical" if percent >= 95 else "warning",
          "cleanup",
          f"Pouco espaco no disco {partition}",
          f"O disco {partition} chegou a {percent}% de uso.",
          "Remover arquivos grandes/desnecessarios, revisar downloads e considerar disco maior se o uso for recorrente.",
          "storage"
        ))

    if not quick:
      alerts = monitoring.get("alerts", [])
      for alert in alerts:
        findings.append(self._finding(
          alert.get("level", "warning"),
          "monitoring",
          alert.get("component", "Alerta de monitoramento"),
          alert.get("message", "Alerta registrado durante o monitoramento."),
          alert.get("recommendation") or "Cruzar este alerta com processos e estado atual da maquina.",
          "software"
        ))

    return findings

  def _analyze_processes(self, processes, quick):
    if not processes:
      return [self._finding(
        "warning",
        "processes",
        "Sem varredura de processos",
        "Nao ha coleta salva de processos pesados/suspeitos.",
        "Rodar a opcao 3 antes do diagnostico para identificar processos que pesam CPU, RAM ou rede.",
        "software"
      )]

    findings = []
    suspicious = processes.get("suspicious_processes", [])
    if suspicious:
      top = suspicious[0]
      findings.append(self._finding(
        "warning",
        "security",
        "Processos suspeitos para investigar",
        f"{len(suspicious)} processo(s) passaram do limiar de suspeita. Principal: {top.get('name')} PID {top.get('pid')}.",
        "Verificar assinatura digital, caminho do executavel, reputacao e necessidade do processo antes de remover.",
        "security"
      ))

    high_cpu = [
      process for process in processes.get("top_cpu", [])
      if process.get("cpu_percent", 0) >= 20
    ]
    if high_cpu:
      names = ", ".join(process.get("name", "N/A") for process in high_cpu[:3])
      findings.append(self._finding(
        "warning",
        "performance",
        "Processos consumindo CPU",
        f"Processos em destaque por CPU: {names}.",
        "Confirmar se estes processos fazem parte da atividade esperada do usuario e fechar/otimizar se necessario.",
        "software"
      ))

    high_ram = [
      process for process in processes.get("top_ram", [])
      if process.get("memory_mb", 0) >= 500
    ]
    if high_ram:
      names = ", ".join(process.get("name", "N/A") for process in high_ram[:3])
      findings.append(self._finding(
        "warning",
        "performance",
        "Processos consumindo RAM",
        f"Processos em destaque por RAM: {names}.",
        "Reduzir abas/programas abertos, revisar extensoes e avaliar aumento de RAM se o uso for comum.",
        "hardware"
      ))

    if not quick:
      network_count = processes.get("summary", {}).get("network_processes_count", 0)
      if network_count:
        network_processes = processes.get("network_processes", [])
        names = self._build_process_name_summary(network_processes)
        findings.append(self._finding(
          "info",
          "network",
          "Processos com conexoes de rede",
          f"{network_count} processo(s) com conexoes de rede foram registrados. Principais: {names}.",
          "Verificar apenas processos desconhecidos ou fora do esperado; navegadores e apps de comunicacao podem ser normais.",
          "security"
        ))

    return findings

  def _build_process_name_summary(self, processes, limit=5):
    names = []

    for process in processes:
      name = process.get("name") or "N/A"
      if name in names:
        continue
      names.append(name)

      if len(names) >= limit:
        break

    if not names:
      return "nenhum processo detalhado"

    return ", ".join(names)

  def _analyze_current_resources(self, current, quick):
    if not current:
      return []

    findings = []
    cpu = current.get("cpu", {})
    ram = current.get("ram", {})
    disks = current.get("disks", [])

    if cpu.get("usage", 0) >= 85:
      findings.append(self._finding(
        "warning",
        "performance",
        "CPU alta no momento do diagnostico",
        f"Uso atual de CPU em {cpu.get('usage')}%.",
        "Cruzar com a opcao 3 para identificar o processo causador.",
        "software"
      ))

    if ram.get("usage", 0) >= 85:
      findings.append(self._finding(
        "warning",
        "performance",
        "RAM alta no momento do diagnostico",
        f"Uso atual de RAM em {ram.get('usage')}%.",
        "Fechar programas desnecessarios e avaliar upgrade de RAM se recorrente.",
        "hardware"
      ))

    for disk in disks:
      if disk.get("percent", 0) >= 85:
        findings.append(self._finding(
          "warning",
          "cleanup",
          f"Disco {disk.get('partition')} com uso elevado",
          f"Uso atual em {disk.get('percent')}%.",
          "Liberar espaco e revisar arquivos grandes antes de instalar novos softwares.",
          "storage"
        ))

    return findings

  def _analyze_security(self, security):
    if not security:
      return []

    findings = []
    antivirus = security.get("antivirus", [])
    active_av = [item for item in antivirus if item.get("active")]
    if not active_av:
      findings.append(self._finding(
        "warning",
        "security",
        "Antivirus nao detectado ou inativo",
        "Nenhum antivirus ativo foi confirmado.",
        "Ativar Windows Defender ou solucao confiavel e executar verificacao completa.",
        "security"
      ))

    firewall = security.get("firewall", {})
    if firewall.get("active") is False:
      findings.append(self._finding(
        "warning",
        "security",
        "Firewall desativado",
        "O firewall parece estar desativado.",
        "Ativar o firewall antes de usar a maquina em redes externas.",
        "security"
      ))

    return findings

  def _analyze_startup(self, startup):
    if not startup:
      return []

    enabled_items = [item for item in startup if item.get("enabled")]
    if len(enabled_items) < 10:
      return []

    return [self._finding(
      "info",
      "startup",
      "Muitos itens iniciando com o sistema",
      f"{len(enabled_items)} itens habilitados na inicializacao.",
      "Desabilitar itens nao essenciais para reduzir tempo de boot e consumo inicial de RAM.",
      "software"
    )]

  def _analyze_software_and_hardware(self, context):
    findings = []
    current = context.get("current") or {}
    ram = current.get("ram", {})
    cpu = current.get("cpu", {})

    total_ram = ram.get("total")
    if total_ram and total_ram < 8 * 1024 * 1024 * 1024:
      findings.append(self._finding(
        "info",
        "hardware",
        "RAM abaixo do recomendado",
        "A maquina possui menos de 8 GB de RAM.",
        "Para uso atual de navegador, escritorio e suporte remoto, avaliar upgrade para 8 GB ou 16 GB.",
        "hardware"
      ))

    cpu_threads = cpu.get("threads")
    if cpu_threads and cpu_threads <= 4:
      findings.append(self._finding(
        "info",
        "hardware",
        "CPU limitada para multitarefa",
        f"CPU com {cpu_threads} threads logicas.",
        "Se houver lentidao recorrente com CPU alta, avaliar troca de CPU/maquina conforme compatibilidade.",
        "hardware"
      ))

    return findings

  def _build_result(self, diagnostic_type, context, findings):
    generated_at = datetime.now()
    findings = self._deduplicate_findings(findings)
    status = self._build_status(findings)
    actions = self._build_actions(findings)
    result = {
      "type": diagnostic_type,
      "generated_at": generated_at.isoformat(timespec="seconds"),
      "status": status,
      "summary": self._build_summary(status, findings),
      "findings": findings,
      "recommended_actions": actions,
      "data_sources": {
        "monitoring_latest_session": context["monitoring"] is not None,
        "processes_latest_scan": context["processes"] is not None,
        "current_resources": context["current"] is not None,
        "security": context["security"] is not None,
        "startup": context["startup"] is not None,
        "system": context["system"] is not None
      },
      "collection_errors": context["collection_errors"],
      "report_ready": {
        "formats": ["pdf", "txt", "md"]
      }
    }
    result["report_ready"]["markdown"] = self._build_markdown(result, context)
    result["report_ready"]["text"] = self._build_text(result)
    return result

  def _build_status(self, findings):
    severities = [finding["severity"] for finding in findings]
    if "critical" in severities:
      return "attention_required"
    if "warning" in severities:
      return "review_recommended"
    return "normal"

  def _build_summary(self, status, findings):
    if not findings:
      return "Nenhum problema relevante foi encontrado. A maquina parece estar em nivel normal."
    if status == "attention_required":
      return "Foram encontrados pontos criticos que podem afetar desempenho, seguranca ou estabilidade."
    return "Foram encontrados pontos de melhoria, mas sem indicio critico no momento."

  def _build_actions(self, findings):
    actions = []
    for finding in findings:
      actions.append({
        "category": finding["recommendation_type"],
        "priority": finding["severity"],
        "action": finding["recommendation"]
      })
    return actions

  def _deduplicate_findings(self, findings):
    unique = []
    seen = set()
    for finding in findings:
      key = (finding["severity"], finding["category"], finding["title"])
      if key in seen:
        continue
      seen.add(key)
      unique.append(finding)
    return unique

  def _finding(self, severity, category, title, evidence, recommendation, recommendation_type):
    return {
      "severity": severity,
      "category": category,
      "title": title,
      "evidence": evidence,
      "recommendation": recommendation,
      "recommendation_type": recommendation_type
    }

  def _save_result(self, result):
    generated_at = datetime.fromisoformat(result["generated_at"])
    prefix = "quick" if result["type"] == "quick" else "full"
    safe_timestamp = generated_at.strftime("%Y-%m-%d_%H-%M-%S")
    history_filename = f"{prefix}/{safe_timestamp}.json"
    latest_filename = f"latest_{prefix}.json"
    history_markdown_filename = f"{prefix}/{safe_timestamp}.md"
    latest_markdown_filename = f"latest_{prefix}.md"
    history_text_filename = f"{prefix}/{safe_timestamp}.txt"
    latest_text_filename = f"latest_{prefix}.txt"

    run_path = self.storage.save_json("diagnostics", history_filename, result)
    latest_path = self.storage.save_json("diagnostics", latest_filename, result)
    markdown_history_path = self.storage.save_text(
      "diagnostics",
      history_markdown_filename,
      result["report_ready"]["markdown"]
    )
    markdown_latest_path = self.storage.save_text(
      "diagnostics",
      latest_markdown_filename,
      result["report_ready"]["markdown"]
    )
    text_history_path = self.storage.save_text(
      "diagnostics",
      history_text_filename,
      result["report_ready"]["text"]
    )
    text_latest_path = self.storage.save_text(
      "diagnostics",
      latest_text_filename,
      result["report_ready"]["text"]
    )

    result["saved_paths"] = {
      "latest": latest_path,
      "history": run_path,
      "markdown_latest": markdown_latest_path,
      "markdown_history": markdown_history_path,
      "text_latest": text_latest_path,
      "text_history": text_history_path
    }
    self.storage.save_json("diagnostics", history_filename, result)
    self.storage.save_json("diagnostics", latest_filename, result)

  def _build_markdown(self, result, context):
    title = "Diagnostico rapido" if result["type"] == "quick" else "Diagnostico completo"
    lines = [
      f"# {title}",
      "",
      f"Gerado em: {result['generated_at']}",
      f"Status: {result['status']}",
      "",
      "## Resumo",
      "",
      result["summary"],
      "",
      "## Achados",
      ""
    ]

    if result["findings"]:
      for finding in result["findings"]:
        lines.extend([
          f"### {finding['title']}",
          "",
          f"- Severidade: {finding['severity']}",
          f"- Categoria: {finding['category']}",
          f"- Evidencia: {finding['evidence']}",
          f"- Recomendacao: {finding['recommendation']}",
          ""
        ])
    else:
      lines.extend(["Nenhum achado relevante.", ""])

    lines.extend([
      "## Fontes de dados",
      "",
      f"- Monitoramento: {'sim' if result['data_sources']['monitoring_latest_session'] else 'nao'}",
      f"- Processos: {'sim' if result['data_sources']['processes_latest_scan'] else 'nao'}",
      f"- Recursos atuais: {'sim' if result['data_sources']['current_resources'] else 'nao'}",
      f"- Seguranca: {'sim' if result['data_sources']['security'] else 'nao'}",
      f"- Inicializacao: {'sim' if result['data_sources']['startup'] else 'nao'}",
      ""
    ])

    system = context.get("system")
    if system:
      lines.extend([
        "## Maquina",
        "",
        f"- Hostname: {system['hostname']}",
        f"- Usuario: {system['username']}",
        f"- Sistema: {system['os_name']}",
        f"- Arquitetura: {system['architecture']}",
        ""
      ])

    return "\n".join(lines)

  def _build_text(self, result):
    lines = [
      result["summary"],
      "",
      "Achados:"
    ]

    if result["findings"]:
      for index, finding in enumerate(result["findings"], start=1):
        lines.extend([
          f"{index}. {finding['title']} ({finding['severity']})",
          f"   Evidencia: {finding['evidence']}",
          f"   Recomendacao: {finding['recommendation']}"
        ])
    else:
      lines.append("Nenhum achado relevante.")

    return "\n".join(lines)
