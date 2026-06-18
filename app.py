import argparse


def main():
  parser = argparse.ArgumentParser(description="FSupport - diagnostico e suporte tecnico")
  parser.add_argument("--quick", action="store_true", help="executa diagnostico rapido")
  parser.add_argument("--full", action="store_true", help="executa diagnostico completo")
  parser.add_argument("--report", action="store_true", help="gera relatorio do ultimo diagnostico")
  args = parser.parse_args()

  if args.quick:
    from services.diagnostic_service import DiagnosticService

    result = DiagnosticService().run_quick()
    print(result["summary"])
    print(f"Status: {result['status']}")
    print(f"Saude: {result['health_score']['score']}/100")
    print(f"Arquivo: {result['saved_paths']['latest']}")
    return

  if args.full:
    from services.diagnostic_service import DiagnosticService

    result = DiagnosticService().run_full()
    print(result["summary"])
    print(f"Status: {result['status']}")
    print(f"Saude: {result['health_score']['score']}/100")
    print(f"Arquivo: {result['saved_paths']['latest']}")
    return

  if args.report:
    from services.report_service import ReportService

    result = ReportService().generate_latest_report()
    print(result["message"])
    if result["success"]:
      print(f"PDF: {result['paths']['pdf_latest']}")
    return

  from controllers.menu_controller import MenuController

  controller = MenuController()
  controller.iniciar()

if __name__ == "__main__":
  main()
