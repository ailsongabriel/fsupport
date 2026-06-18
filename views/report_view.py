from views.base_view import BaseView


class ReportView(BaseView):

  def show_report_result(self, result):
    if not result["success"]:
      self.show_message(result["message"])
      return

    lines = [
      result["message"],
      f"Diagnostico = {result['diagnostic_type']}",
      f"Status      = {result['status']}",
      f"PDF         = {result['paths']['pdf_latest']}",
      f"Markdown    = {result['paths']['markdown_latest']}",
      f"Texto       = {result['paths']['text_latest']}"
    ]
    width = self.get_width(lines, min_width=70)

    self.print_title("RELATORIO FSUPPORT", width)
    for line in lines:
      print(line)

    self.print_subtitle("Historico", width)
    print(f"PDF         = {result['paths']['pdf_history']}")
    print(f"Markdown    = {result['paths']['markdown_history']}")
    print(f"Texto       = {result['paths']['text_history']}")
