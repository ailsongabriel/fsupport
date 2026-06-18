from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from services.storage_service import StorageService


class ReportService:

  def __init__(self):
    self.storage = StorageService()
    self.output_path = Path("reports")

  def generate_latest_report(self):
    diagnostic = self._load_latest_diagnostic()
    if diagnostic is None:
      return {
        "success": False,
        "message": "Nenhum diagnostico encontrado. Execute a opcao 1 ou 2 antes de gerar o relatorio.",
        "paths": {}
      }

    report = self._build_report_data(diagnostic)
    timestamp = datetime.now()
    safe_timestamp = timestamp.strftime("%Y-%m-%d_%H-%M-%S")

    markdown = self._build_markdown(report)
    text = self._build_text(report)

    markdown_history = self._save_report_text(f"history/{safe_timestamp}.md", markdown)
    markdown_latest = self._save_report_text("latest_report.md", markdown)
    text_history = self._save_report_text(f"history/{safe_timestamp}.txt", text)
    text_latest = self._save_report_text("latest_report.txt", text)

    pdf_history = self._save_pdf(self.output_path / "history" / f"{safe_timestamp}.pdf", report)
    pdf_latest = self._save_pdf(self.output_path / "latest_report.pdf", report)

    return {
      "success": True,
      "message": "Relatorio FSupport gerado com sucesso.",
      "paths": {
        "markdown_latest": markdown_latest,
        "markdown_history": markdown_history,
        "text_latest": text_latest,
        "text_history": text_history,
        "pdf_latest": pdf_latest,
        "pdf_history": pdf_history
      },
      "diagnostic_type": diagnostic.get("type"),
      "status": diagnostic.get("status")
    }

  def _load_latest_diagnostic(self):
    full = self.storage.load_json("diagnostics", "latest_full.json")
    if full:
      return full

    return self.storage.load_json("diagnostics", "latest_quick.json")

  def _save_report_text(self, filename, content):
    path = self.output_path / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
      file.write(content)

    return str(path)

  def _build_report_data(self, diagnostic):
    findings = diagnostic.get("findings", [])
    actions = diagnostic.get("recommended_actions", [])
    data_sources = diagnostic.get("data_sources", {})
    report_ready = diagnostic.get("report_ready", {})

    return {
      "title": "Relatorio Tecnico FSupport",
      "diagnostic_type": "Completo" if diagnostic.get("type") == "full" else "Rapido",
      "generated_at": datetime.now().isoformat(timespec="seconds"),
      "diagnostic_generated_at": diagnostic.get("generated_at"),
      "status": diagnostic.get("status", "unknown"),
      "summary": diagnostic.get("summary", "Sem resumo disponivel."),
      "tasks_done": self._build_tasks_done(data_sources),
      "findings": findings,
      "actions": actions,
      "data_sources": data_sources,
      "collection_errors": diagnostic.get("collection_errors", []),
      "diagnostic_markdown": report_ready.get("markdown"),
      "diagnostic_text": report_ready.get("text")
    }

  def _build_tasks_done(self, data_sources):
    labels = {
      "monitoring_latest_session": "Analise do monitoramento em tempo real",
      "processes_latest_scan": "Analise de processos por CPU, RAM e rede",
      "startup_latest_scan": "Analise da coleta salva de inicializacao",
      "current_resources": "Verificacao atual de CPU, RAM e disco",
      "security": "Verificacao de antivirus e firewall",
      "startup": "Revisao de itens de inicializacao",
      "system": "Identificacao do sistema operacional e maquina"
    }

    tasks = []
    for key, label in labels.items():
      tasks.append({
        "label": label,
        "done": bool(data_sources.get(key))
      })

    return tasks

  def _build_markdown(self, report):
    lines = [
      "# FSupport - Relatorio Tecnico",
      "",
      f"Gerado em: {report['generated_at']}",
      f"Diagnostico usado: {report['diagnostic_type']}",
      f"Status: {report['status']}",
      "",
      "## Resumo",
      "",
      report["summary"],
      "",
      "## Tarefas feitas",
      ""
    ]

    for task in report["tasks_done"]:
      mark = "OK" if task["done"] else "Pendente"
      lines.append(f"- {mark}: {task['label']}")

    lines.extend(["", "## Achados", ""])
    if report["findings"]:
      for finding in report["findings"]:
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
      lines.extend([
        "Nenhum problema relevante foi encontrado. A maquina parece estar em nivel normal.",
        ""
      ])

    lines.extend(["## Sugestoes de melhoria", ""])
    if report["actions"]:
      for action in report["actions"]:
        lines.append(f"- [{action['priority']}] {action['action']}")
    else:
      lines.append("- Manter atualizacoes do sistema e softwares em dia.")
      lines.append("- Repetir monitoramento caso o usuario relate lentidao novamente.")

    if report["collection_errors"]:
      lines.extend(["", "## Observacoes", ""])
      for error in report["collection_errors"]:
        lines.append(f"- {error['source']}: {error['error']}")

    lines.extend([
      "",
      "## Arquivos",
      "",
      "Este relatorio tambem foi exportado em PDF, TXT e Markdown."
    ])

    return "\n".join(lines)

  def _build_text(self, report):
    lines = [
      "FSupport - Relatorio Tecnico",
      "=" * 30,
      f"Gerado em: {report['generated_at']}",
      f"Diagnostico usado: {report['diagnostic_type']}",
      f"Status: {report['status']}",
      "",
      "Resumo:",
      report["summary"],
      "",
      "Tarefas feitas:"
    ]

    for task in report["tasks_done"]:
      mark = "OK" if task["done"] else "Pendente"
      lines.append(f"- {mark}: {task['label']}")

    lines.extend(["", "Achados:"])
    if report["findings"]:
      for index, finding in enumerate(report["findings"], start=1):
        lines.extend([
          f"{index}. {finding['title']} ({finding['severity']})",
          f"   Evidencia: {finding['evidence']}",
          f"   Recomendacao: {finding['recommendation']}"
        ])
    else:
      lines.append("Nenhum problema relevante foi encontrado.")

    lines.extend(["", "Sugestoes de melhoria:"])
    if report["actions"]:
      for action in report["actions"]:
        lines.append(f"- [{action['priority']}] {action['action']}")
    else:
      lines.append("- Manter atualizacoes do sistema e softwares em dia.")
      lines.append("- Repetir monitoramento caso o usuario relate lentidao novamente.")

    return "\n".join(lines)

  def _save_pdf(self, filename, report):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
      str(path),
      pagesize=A4,
      rightMargin=1.7 * cm,
      leftMargin=1.7 * cm,
      topMargin=1.6 * cm,
      bottomMargin=1.6 * cm
    )

    styles = self._build_pdf_styles()
    story = []

    story.append(Paragraph("FSupport", styles["Brand"]))
    story.append(Paragraph("Relatorio Tecnico", styles["Title"]))
    story.append(Spacer(1, 0.25 * cm))
    story.append(Paragraph(f"Gerado em: {report['generated_at']}", styles["Small"]))
    story.append(Paragraph(f"Diagnostico usado: {report['diagnostic_type']}", styles["Small"]))
    story.append(Paragraph(f"Status: {report['status']}", styles["Small"]))
    story.append(Spacer(1, 0.45 * cm))

    story.extend(self._section("Resumo", [report["summary"]], styles))
    story.extend(self._tasks_section(report["tasks_done"], styles))
    story.extend(self._findings_section(report["findings"], styles))
    story.extend(self._actions_section(report["actions"], styles))

    if report["collection_errors"]:
      errors = [
        f"{error['source']}: {error['error']}"
        for error in report["collection_errors"]
      ]
      story.extend(self._section("Observacoes", errors, styles))

    doc.build(story, onFirstPage=self._draw_footer, onLaterPages=self._draw_footer)
    return str(path)

  def _build_pdf_styles(self):
    base = getSampleStyleSheet()
    return {
      "Brand": ParagraphStyle(
        "FSupportBrand",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1F4E79"),
        alignment=TA_CENTER,
        spaceAfter=4
      ),
      "Title": ParagraphStyle(
        "FSupportTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#333333"),
        alignment=TA_CENTER,
        spaceAfter=10
      ),
      "Heading": ParagraphStyle(
        "FSupportHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1F4E79"),
        spaceBefore=10,
        spaceAfter=6
      ),
      "Body": ParagraphStyle(
        "FSupportBody",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        spaceAfter=6
      ),
      "Small": ParagraphStyle(
        "FSupportSmall",
        parent=base["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#555555")
      )
    }

  def _section(self, title, paragraphs, styles):
    items = [Paragraph(title, styles["Heading"])]
    for paragraph in paragraphs:
      items.append(Paragraph(self._escape(paragraph), styles["Body"]))
    return items

  def _tasks_section(self, tasks, styles):
    items = [Paragraph("Tarefas feitas", styles["Heading"])]
    rows = [["Status", "Tarefa"]]
    for task in tasks:
      rows.append(["OK" if task["done"] else "Pendente", task["label"]])

    table = Table(rows, colWidths=[2.5 * cm, 13 * cm])
    table.setStyle(TableStyle([
      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
      ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
      ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
      ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
      ("FONTSIZE", (0, 0), (-1, -1), 8.5),
      ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D9E2EC")),
      ("VALIGN", (0, 0), (-1, -1), "TOP"),
      ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FB")])
    ]))
    items.append(table)
    return items

  def _findings_section(self, findings, styles):
    items = [Paragraph("Achados", styles["Heading"])]
    if not findings:
      items.append(Paragraph("Nenhum problema relevante foi encontrado.", styles["Body"]))
      return items

    for finding in findings:
      items.append(Paragraph(self._escape(f"{finding['title']} ({finding['severity']})"), styles["Body"]))
      items.append(Paragraph(self._escape(f"Evidencia: {finding['evidence']}"), styles["Small"]))
      items.append(Paragraph(self._escape(f"Recomendacao: {finding['recommendation']}"), styles["Small"]))
      items.append(Spacer(1, 0.15 * cm))

    return items

  def _actions_section(self, actions, styles):
    items = [Paragraph("Sugestoes de melhoria", styles["Heading"])]
    if not actions:
      actions = [
        {"priority": "info", "action": "Manter atualizacoes do sistema e softwares em dia."},
        {"priority": "info", "action": "Repetir monitoramento caso o usuario relate lentidao novamente."}
      ]

    for action in actions:
      items.append(Paragraph(self._escape(f"[{action['priority']}] {action['action']}"), styles["Body"]))

    return items

  def _draw_footer(self, canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(1.7 * cm, 1.0 * cm, "FSupport - Relatorio tecnico")
    canvas.drawRightString(A4[0] - 1.7 * cm, 1.0 * cm, f"Pagina {doc.page}")
    canvas.restoreState()

  def _escape(self, value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
