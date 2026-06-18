from views.base_view import BaseView


class DiagnosticView(BaseView):

  def show_diagnostic_result(self, result):
    title = "DIAGNOSTICO RAPIDO" if result["type"] == "quick" else "DIAGNOSTICO COMPLETO"
    lines = [
      f"Gerado em        = {result['generated_at']}",
      f"Status           = {result['status']}",
      f"Saude            = {result['health_score']['score']}/100 ({result['health_score']['grade']})",
      f"Resumo           = {result['summary']}",
      f"Arquivo latest   = {result['saved_paths']['latest']}",
      f"Historico        = {result['saved_paths']['history']}"
    ]
    width = self.get_width(lines, min_width=70)

    self.print_title(title, width)
    print(f"Gerado em        = {result['generated_at']}")
    print(f"Status           = {result['status']}")
    print(f"Saude            = {result['health_score']['score']}/100 ({result['health_score']['grade']})")
    print(f"Resumo           = {result['summary']}")

    self.print_subtitle("Comparacao historica", width)
    print(result.get("history_comparison", {}).get("summary", "Sem comparacao disponivel."))

    self.print_subtitle("Fontes usadas", width)
    for source, available in result["data_sources"].items():
      print(f"{source:<24} = {'sim' if available else 'nao'}")

    self.print_subtitle("Achados", width)
    if result["findings"]:
      for finding in result["findings"]:
        print(f"[{finding['severity'].upper()}] {finding['title']}")
        print(f"  Evidencia     = {finding['evidence']}")
        print(f"  Recomendacao  = {finding['recommendation']}")
    else:
      print("Nenhum problema relevante encontrado.")

    if result["collection_errors"]:
      self.print_subtitle("Coletas nao realizadas", width)
      for error in result["collection_errors"]:
        print(f"{error['source']} = {error['error']}")

    self.print_subtitle("Checklist de suporte", width)
    for item in result["support_checklist"]:
      print(f"[{item['priority'].upper()}] {item['item']}")

    self.print_subtitle("Pronto para relatorio", width)
    print(f"JSON latest      = {result['saved_paths']['latest']}")
    print(f"JSON historico   = {result['saved_paths']['history']}")
    print(f"Markdown latest  = {result['saved_paths']['markdown_latest']}")
    print(f"Texto latest     = {result['saved_paths']['text_latest']}")
    print("O PDF podera ser gerado pela opcao 13 a partir do diagnostico salvo.")
