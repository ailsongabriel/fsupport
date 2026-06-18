import unittest
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

sys.modules.setdefault("cpuinfo", SimpleNamespace(get_cpu_info=lambda: {}))
sys.modules.setdefault("psutil", SimpleNamespace(
  cpu_count=lambda logical=True: 4,
  cpu_percent=lambda interval=None: 0,
  cpu_freq=lambda: SimpleNamespace(current=0),
  virtual_memory=lambda: SimpleNamespace(total=0, used=0, available=0, percent=0),
  disk_partitions=lambda: [],
  boot_time=lambda: 0,
  process_iter=lambda attrs=None: [],
  net_io_counters=lambda: SimpleNamespace(bytes_recv=0, bytes_sent=0),
  NoSuchProcess=Exception,
  AccessDenied=Exception
))
sys.modules.setdefault("netifaces", SimpleNamespace(gateways=lambda: {}, AF_INET=2))

reportlab = MagicMock()
sys.modules.setdefault("reportlab", reportlab)
sys.modules.setdefault("reportlab.lib", MagicMock())
sys.modules.setdefault("reportlab.lib.colors", MagicMock())
sys.modules.setdefault("reportlab.lib.enums", SimpleNamespace(TA_CENTER=1))
sys.modules.setdefault("reportlab.lib.pagesizes", SimpleNamespace(A4=(595, 842)))
sys.modules.setdefault("reportlab.lib.styles", SimpleNamespace(
  ParagraphStyle=MagicMock(),
  getSampleStyleSheet=lambda: {"Title": object(), "Heading2": object(), "BodyText": object()}
))
sys.modules.setdefault("reportlab.lib.units", SimpleNamespace(cm=28.35))
sys.modules.setdefault("reportlab.platypus", SimpleNamespace(
  Paragraph=MagicMock(),
  SimpleDocTemplate=MagicMock(),
  Spacer=MagicMock(),
  Table=MagicMock(),
  TableStyle=MagicMock()
))

from services.diagnostic_service import DiagnosticService


class DiagnosticServiceTest(unittest.TestCase):

  def test_actions_are_prioritized_by_severity(self):
    service = DiagnosticService()
    findings = [
      service._finding("info", "startup", "Info", "e", "info action", "software"),
      service._finding("critical", "security", "Critical", "e", "critical action", "security"),
      service._finding("warning", "performance", "Warning", "e", "warning action", "hardware")
    ]

    actions = service._build_actions(findings)

    self.assertEqual([action["priority"] for action in actions], ["critical", "warning", "info"])

  def test_health_score_penalizes_findings_and_missing_sources(self):
    service = DiagnosticService()
    findings = [
      service._finding("critical", "security", "Critical", "e", "r", "security"),
      service._finding("warning", "performance", "Warning", "e", "r", "hardware")
    ]
    context = {
      "monitoring": None,
      "processes": {},
      "security": {},
      "current": {},
      "startup": {},
      "startup_scan": None,
      "system": {},
      "windows_health": None,
      "collection_errors": []
    }

    health = service._build_health_score(findings, context)

    self.assertEqual(health["score"], 67)
    self.assertEqual(health["grade"], "attention")
    self.assertLess(health["breakdown"]["security"], 100)

  def test_windows_health_findings_include_update_and_events(self):
    service = DiagnosticService()
    findings = service._analyze_windows_health({
      "uptime_days": 20,
      "latest_hotfix": {"id": "KB123", "age_days": 60},
      "critical_events_7d": 2
    })

    titles = [finding["title"] for finding in findings]
    self.assertIn("Sistema sem reiniciar ha muitos dias", titles)
    self.assertIn("Windows possivelmente desatualizado", titles)
    self.assertIn("Eventos criticos recentes no Windows", titles)


if __name__ == "__main__":
  unittest.main()
