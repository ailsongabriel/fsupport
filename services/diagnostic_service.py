from datetime import datetime

from services.cpu_service import CpuService
from services.disk_service import DiskService
from services.ram_service import RamService
from services.security_service import SecurityService
from services.startup_service import StartupService
from services.storage_service import StorageService
from services.system_service import SystemService
from services.windows_health_service import WindowsHealthService


class DiagnosticService:

  def __init__(self):
    self.storage = StorageService()
    self.cpu_service = CpuService()
    self.ram_service = RamService()
    self.disk_service = DiskService()
    self.security_service = SecurityService()
    self.startup_service = StartupService()
    self.system_service = SystemService()
    self.windows_health_service = WindowsHealthService()

  def run_quick(self):
    context = self._collect_context(include_current=True)
    findings = []

    findings.extend(self._analyze_monitoring(context["monitoring"], quick=True))
    findings.extend(self._analyze_processes(context["processes"], quick=True))
    findings.extend(self._analyze_current_resources(context["current"], quick=True))
    findings.extend(self._analyze_security(context["security"]))

    result = self._build_result("quick", context, findings)
    result["history_comparison"] = self._build_history_comparison("quick", result)
    self._refresh_report_ready(result, context)
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
    findings.extend(self._analyze_windows_health(context["windows_health"]))

    result = self._build_result("full", context, findings)
    result["history_comparison"] = self._build_history_comparison("full", result)
    self._refresh_report_ready(result, context)
    self._save_result(result)
    return result

  def _collect_context(self, include_current):
    context = {
      "monitoring": self.storage.load_json("monitoring", "latest_session.json"),
      "processes": self.storage.load_json("processes", "latest_scan.json"),
      "startup_scan": self.storage.load_json("startup", "latest_scan.json"),
      "current": None,
      "security": None,
      "startup": None,
      "system": None,
      "windows_health": None,
      "collection_errors": []
    }

    if not include_current:
      return context

    context["system"] = self._safe_collect("system", self._collect_system, context)
    context["current"] = self._safe_collect("current", self._collect_current_resources, context)
    context["security"] = self._safe_collect("security", self._collect_security, context)
    context["startup"] = context["startup_scan"]
    if context["startup"] is None:
      context["startup"] = self._safe_collect("startup", self._collect_startup, context)
    context["windows_health"] = self._safe_collect("windows_health", self._collect_windows_health, context)
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
          "up_to_date": antivirus.up_to_date,
          "note": antivirus.note
        }
        for antivirus in security.antivirus_list
      ],
      "firewall": {
        "active": security.firewall.active,
        "profiles": security.firewall.profiles,
        "note": security.firewall.note
      }
    }

  def _collect_startup(self):
    startup_items = self.startup_service.get_startup_items()
    items = [
      {
        "name": item.name,
        "command": item.command,
        "location": item.location,
        "enabled": item.enabled,
        "startup_flags": []
      }
      for item in startup_items
    ]
    enabled_items = [item for item in items if item["enabled"]]

    return {
      "collected_at": datetime.now().isoformat(timespec="seconds"),
      "summary": {
        "total_items": len(items),
        "enabled_count": len(enabled_items),
        "disabled_count": len(items) - len(enabled_items),
        "review_count": 0
      },
      "items": items,
      "enabled_items": enabled_items,
      "review_items": []
    }

  def _collect_windows_health(self):
    return self.windows_health_service.get_health_info()

  def _analyze_monitoring(self, monitoring, quick):
    if not monitoring:
      return [self._finding(
        "warning",
        "monitoring",
        "Sem dados de monitoramento",
        "Execute o monitoramento em tempo real antes do diagnostico para avaliar picos e medias.",
        "Rodar a opcao 4 por alguns minutos e repetir o diagnostico.",
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
        "Rodar a opcao 5 antes do diagnostico para identificar processos que pesam CPU, RAM ou rede.",
        "software"
      )]

    findings = []
    suspicious = processes.get("suspicious_processes", [])
    if suspicious:
      top = suspicious[0]
      evidence = self._build_process_evidence(top)
      findings.append(self._finding(
        "warning",
        "security",
        "Processos suspeitos para investigar",
        f"{len(suspicious)} processo(s) passaram do limiar de suspeita. Principal: {evidence}.",
        "Verificar assinatura digital, caminho do executavel, reputacao e necessidade do processo antes de remover.",
        "security"
      ))

    high_cpu = [
      process for process in processes.get("top_cpu", [])
      if process.get("cpu_percent", 0) >= 20
    ]
    if high_cpu:
      names = self._build_process_evidence_summary(high_cpu)
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
      names = self._build_process_evidence_summary(high_ram)
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
        names = self._build_process_evidence_summary(network_processes)
        findings.append(self._finding(
          "info",
          "network",
          "Processos com conexoes de rede",
          f"{network_count} processo(s) com conexoes de rede foram registrados. Principais: {names}.",
          "Verificar apenas processos desconhecidos ou fora do esperado; navegadores e apps de comunicacao podem ser normais.",
          "security"
        ))

    return findings

  def _build_process_evidence_summary(self, processes, limit=3):
    if not processes:
      return "nenhum processo detalhado"

    return "; ".join([
      self._build_process_evidence(process)
      for process in processes[:limit]
    ])

  def _build_process_evidence(self, process):
    parts = [
      f"{process.get('name', 'N/A')} PID {process.get('pid', 'N/A')}",
      f"CPU {process.get('cpu_percent', 0)}%",
      f"RAM {process.get('memory_mb', 0)} MB"
    ]

    remote_address = self._get_first_remote_address(process)
    if remote_address:
      parts.append(f"remoto {remote_address}")

    exe = process.get("exe")
    if exe and process.get("risk_score", 0) > 0:
      parts.append(f"exe {exe}")

    return ", ".join(parts)

  def _get_first_remote_address(self, process):
    connections = process.get("connections", [])
    if not connections:
      return None

    return connections[0].get("remote_address")

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
        "Cruzar com a opcao 5 para identificar o processo causador.",
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
    unavailable_av = [item for item in antivirus if item.get("active") is None]
    if unavailable_av:
      findings.append(self._finding(
        "warning",
        "security",
        "Verificacao de antivirus indisponivel",
        "Nao foi possivel confirmar o estado do antivirus nesta maquina.",
        "Executar a ferramenta com permissao adequada e validar manualmente o Windows Security ou solucao instalada.",
        "security"
      ))
      return findings

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
    if firewall.get("active") is None:
      findings.append(self._finding(
        "warning",
        "security",
        "Verificacao de firewall indisponivel",
        "Nao foi possivel confirmar o estado do firewall.",
        "Validar manualmente o firewall do sistema antes de concluir a revisao de seguranca.",
        "security"
      ))

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

    findings = []
    summary = startup.get("summary", {})
    enabled_items = startup.get("enabled_items", [])
    review_items = startup.get("review_items", [])
    enabled_count = summary.get("enabled_count", len(enabled_items))

    if enabled_count >= 10:
      names = self._build_startup_name_summary(enabled_items)
      findings.append(self._finding(
        "info",
        "startup",
        "Muitos itens iniciando com o sistema",
        f"{enabled_count} itens habilitados na inicializacao. Principais: {names}.",
        "Desabilitar itens nao essenciais para reduzir tempo de boot e consumo inicial de RAM.",
        "software"
      ))

    performance_items = [
      item for item in review_items
      if "review_performance_impact" in item.get("startup_flags", [])
    ]
    if performance_items:
      names = self._build_startup_name_summary(performance_items)
      findings.append(self._finding(
        "info",
        "startup",
        "Itens de inicializacao com possivel impacto",
        f"Itens que podem impactar desempenho inicial: {names}.",
        "Revisar se estes programas precisam iniciar com o Windows ou se podem ser abertos manualmente.",
        "software"
      ))

    unusual_items = [
      item for item in review_items
      if "review_unusual_startup_path" in item.get("startup_flags", [])
    ]
    if unusual_items:
      names = self._build_startup_name_summary(unusual_items)
      findings.append(self._finding(
        "warning",
        "security",
        "Itens de inicializacao em caminho incomum",
        f"Itens iniciando a partir de locais que merecem verificacao: {names}.",
        "Validar assinatura, caminho e reputacao antes de manter estes itens na inicializacao.",
        "security"
      ))

    return findings

  def _build_startup_name_summary(self, items, limit=5):
    names = []

    for item in items:
      name = item.get("name") or "N/A"
      if name in names:
        continue
      names.append(name)

      if len(names) >= limit:
        break

    if not names:
      return "nenhum item detalhado"

    return ", ".join(names)

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

  def _analyze_windows_health(self, windows_health):
    if not windows_health:
      return []

    findings = []
    uptime_days = windows_health.get("uptime_days")
    if uptime_days is not None and uptime_days >= 14:
      findings.append(self._finding(
        "info",
        "reliability",
        "Sistema sem reiniciar ha muitos dias",
        f"Uptime atual de {uptime_days} dia(s).",
        "Reiniciar em janela segura antes de investigar lentidao persistente ou atualizacoes pendentes.",
        "software"
      ))

    hotfix = windows_health.get("latest_hotfix") or {}
    hotfix_age = hotfix.get("age_days")
    if hotfix_age is not None and hotfix_age >= 45:
      findings.append(self._finding(
        "warning",
        "security",
        "Windows possivelmente desatualizado",
        f"Hotfix mais recente ha {hotfix_age} dia(s): {hotfix.get('id', 'N/A')}.",
        "Verificar Windows Update e aplicar atualizacoes pendentes conforme politica do ambiente.",
        "security"
      ))

    critical_events = windows_health.get("critical_events_7d")
    if critical_events:
      findings.append(self._finding(
        "warning",
        "reliability",
        "Eventos criticos recentes no Windows",
        f"{critical_events} evento(s) critico(s) no log System nos ultimos 7 dias.",
        "Abrir Visualizador de Eventos e revisar origem dos eventos criticos antes de concluir o atendimento.",
        "software"
      ))

    return findings

  def _build_result(self, diagnostic_type, context, findings):
    generated_at = datetime.now()
    findings = self._deduplicate_findings(findings)
    status = self._build_status(findings)
    actions = self._build_actions(findings)
    health_score = self._build_health_score(findings, context)
    result = {
      "type": diagnostic_type,
      "generated_at": generated_at.isoformat(timespec="seconds"),
      "status": status,
      "summary": self._build_summary(status, findings),
      "health_score": health_score,
      "findings": findings,
      "recommended_actions": actions,
      "support_checklist": self._build_support_checklist(status, findings),
      "data_sources": {
        "monitoring_latest_session": context["monitoring"] is not None,
        "processes_latest_scan": context["processes"] is not None,
        "startup_latest_scan": context["startup_scan"] is not None,
        "current_resources": context["current"] is not None,
        "security": context["security"] is not None,
        "startup": context["startup"] is not None,
        "system": context["system"] is not None,
        "windows_health": context["windows_health"] is not None
      },
      "collection_errors": context["collection_errors"],
      "report_ready": {
        "formats": ["pdf", "txt", "md"]
      }
    }
    result["report_ready"]["markdown"] = self._build_markdown(result, context)
    result["report_ready"]["text"] = self._build_text(result)
    return result

  def _refresh_report_ready(self, result, context):
    result["report_ready"]["markdown"] = self._build_markdown(result, context)
    result["report_ready"]["text"] = self._build_text(result)

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
    priority_order = {"critical": 0, "warning": 1, "info": 2}
    return sorted(actions, key=lambda action: priority_order.get(action["priority"], 3))

  def _build_health_score(self, findings, context):
    score = 100
    breakdown = {
      "performance": 100,
      "storage": 100,
      "security": 100,
      "reliability": 100
    }
    penalties = {
      "critical": 20,
      "warning": 10,
      "info": 4
    }
    category_map = {
      "performance": "performance",
      "cleanup": "storage",
      "security": "security",
      "monitoring": "reliability",
      "processes": "reliability",
      "startup": "performance",
      "hardware": "performance",
      "network": "reliability",
      "reliability": "reliability"
    }

    for finding in findings:
      penalty = penalties.get(finding["severity"], 0)
      score -= penalty
      area = category_map.get(finding["category"], "reliability")
      breakdown[area] = max(0, breakdown[area] - penalty)

    missing_sources = [
      available
      for available in [
        context.get("monitoring") is not None,
        context.get("processes") is not None,
        context.get("security") is not None
      ]
      if not available
    ]
    missing_penalty = len(missing_sources) * 3
    score -= missing_penalty
    breakdown["reliability"] = max(0, breakdown["reliability"] - missing_penalty)

    final_score = max(0, min(100, score))
    return {
      "score": final_score,
      "grade": self._grade_health_score(final_score),
      "breakdown": breakdown
    }

  def _grade_health_score(self, score):
    if score >= 90:
      return "excellent"
    if score >= 75:
      return "good"
    if score >= 60:
      return "attention"
    return "critical"

  def _build_support_checklist(self, status, findings):
    checklist = [
      {
        "item": "Confirmar com o usuario o sintoma principal, quando começou e se ocorre sempre.",
        "priority": "critical" if status == "attention_required" else "warning"
      },
      {
        "item": "Executar monitoramento por pelo menos 3 a 5 minutos durante o uso que gera lentidao.",
        "priority": "warning"
      },
      {
        "item": "Registrar processos de maior CPU/RAM antes de fechar programas ou reiniciar.",
        "priority": "warning"
      },
      {
        "item": "Validar backup antes de mover, remover ou limpar arquivos.",
        "priority": "critical"
      }
    ]

    if any(finding["category"] == "security" for finding in findings):
      checklist.append({
        "item": "Validar antivirus, firewall e reputacao de processos antes de remover qualquer executavel.",
        "priority": "critical"
      })

    if any(finding["category"] == "cleanup" for finding in findings):
      checklist.append({
        "item": "Revisar arquivos grandes com o usuario antes de limpar disco.",
        "priority": "warning"
      })

    return checklist

  def _build_history_comparison(self, diagnostic_type, result):
    previous = self.storage.load_json("diagnostics", f"latest_{diagnostic_type}.json")
    if not previous:
      return {
        "available": False,
        "summary": "Sem diagnostico anterior para comparacao."
      }

    previous_score = previous.get("health_score", {}).get("score")
    current_score = result.get("health_score", {}).get("score")
    previous_findings = len(previous.get("findings", []))
    current_findings = len(result.get("findings", []))
    score_delta = None
    if previous_score is not None and current_score is not None:
      score_delta = current_score - previous_score

    return {
      "available": True,
      "previous_generated_at": previous.get("generated_at"),
      "previous_status": previous.get("status"),
      "current_status": result.get("status"),
      "previous_score": previous_score,
      "current_score": current_score,
      "score_delta": score_delta,
      "previous_findings": previous_findings,
      "current_findings": current_findings,
      "findings_delta": current_findings - previous_findings,
      "summary": self._build_history_summary(score_delta, current_findings - previous_findings)
    }

  def _build_history_summary(self, score_delta, findings_delta):
    parts = []
    if score_delta is None:
      parts.append("Pontuacao anterior indisponivel.")
    elif score_delta > 0:
      parts.append(f"Pontuacao melhorou {score_delta} ponto(s).")
    elif score_delta < 0:
      parts.append(f"Pontuacao piorou {abs(score_delta)} ponto(s).")
    else:
      parts.append("Pontuacao ficou estavel.")

    if findings_delta > 0:
      parts.append(f"{findings_delta} achado(s) a mais.")
    elif findings_delta < 0:
      parts.append(f"{abs(findings_delta)} achado(s) a menos.")
    else:
      parts.append("Quantidade de achados estavel.")

    return " ".join(parts)

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
      f"Saude: {result['health_score']['score']}/100 ({result['health_score']['grade']})",
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
      "## Checklist de suporte",
      ""
    ])

    for item in result["support_checklist"]:
      lines.append(f"- [{item['priority']}] {item['item']}")

    comparison = result.get("history_comparison", {})
    lines.extend([
      "",
      "## Comparacao com diagnostico anterior",
      "",
      comparison.get("summary", "Sem comparacao disponivel."),
      "",
      "## Fontes de dados",
      "",
      f"- Monitoramento: {'sim' if result['data_sources']['monitoring_latest_session'] else 'nao'}",
      f"- Processos: {'sim' if result['data_sources']['processes_latest_scan'] else 'nao'}",
      f"- Startup salvo: {'sim' if result['data_sources']['startup_latest_scan'] else 'nao'}",
      f"- Recursos atuais: {'sim' if result['data_sources']['current_resources'] else 'nao'}",
      f"- Seguranca: {'sim' if result['data_sources']['security'] else 'nao'}",
      f"- Inicializacao: {'sim' if result['data_sources']['startup'] else 'nao'}",
      f"- Saude do Windows: {'sim' if result['data_sources']['windows_health'] else 'nao'}",
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
      f"Saude: {result['health_score']['score']}/100 ({result['health_score']['grade']})",
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
