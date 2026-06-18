# FSupport

FSupport é uma ferramenta de diagnóstico e suporte técnico para Windows e Linux, desenvolvida em Python com arquitetura MVC. O projeto coleta informações do sistema, monitora recursos, identifica pontos de atenção e gera relatórios técnicos em JSON, Markdown, TXT e PDF.

O objetivo é ajudar em atendimentos de suporte: transformar sinais técnicos de CPU, RAM, disco, rede, segurança, processos e inicialização em um diagnóstico mais claro, priorizado e acionável.

## Principais recursos

- Diagnóstico rápido e completo com resumo técnico.
- Pontuação de saúde da máquina, com classificação geral e detalhamento por área.
- Checklist de suporte para orientar próximos passos durante o atendimento.
- Comparação com o diagnóstico anterior para indicar melhora ou piora.
- Monitoramento em tempo real de CPU, RAM, disco e rede.
- Análise de processos por consumo, conexões de rede e sinais de risco.
- Verificação de antivírus, firewall e sinais de saúde do Windows.
- Leitura de itens de inicialização do sistema.
- Busca de arquivos duplicados com exportação CSV e quarentena protegida.
- Geração de relatório técnico em PDF, Markdown e TXT.

## Requisitos

- Python 3.9 ou superior.
- Dependências listadas em `requirements.txt`.

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Dependências atuais:

```text
py-cpuinfo
requests
netifaces
psutil
reportlab
```

## Como executar

Modo interativo:

```powershell
python app.py
```

Comandos diretos:

```powershell
python app.py --quick
python app.py --full
python app.py --report
```

Use `--quick` para um diagnóstico mais direto, `--full` para uma análise mais completa e `--report` para gerar o relatório a partir do último diagnóstico salvo.

## Fluxo recomendado de atendimento

1. Execute o monitoramento em tempo real por alguns minutos durante o uso que apresenta lentidão.
2. Rode a análise de processos pesados para salvar dados de CPU, RAM, rede e suspeitas.
3. Execute o diagnóstico completo.
4. Gere o relatório técnico.
5. Revise o checklist, os achados críticos e as ações recomendadas antes de fazer alterações na máquina.

No menu interativo, esse fluxo corresponde principalmente às opções:

```text
4  - Monitoramento em tempo real
5  - Processos pesados
2  - Diagnóstico completo
13 - Gerar relatório
```

## Menu de recursos

```text
1  - Diagnóstico rápido
2  - Diagnóstico completo
3  - Informações do sistema
4  - Monitoramento em tempo real
5  - Processos pesados
6  - Uso de CPU
7  - Uso de RAM
8  - Uso de disco
9  - Rede e conectividade
10 - Inicialização do sistema
11 - Segurança
12 - Arquivos duplicados
13 - Gerar relatório
0  - Sair
```

## Relatórios e dados gerados

O FSupport salva coletas e diagnósticos em diretórios locais do projeto:

- `storage/monitoring`: sessões de monitoramento.
- `storage/processes`: varreduras de processos.
- `storage/startup`: coletas de inicialização.
- `storage/diagnostics`: diagnósticos rápidos e completos.
- `reports`: relatórios finais em PDF, Markdown e TXT.

Esses arquivos são úteis para comparar atendimentos, revisar evidências e acompanhar a evolução da máquina.

## Segurança operacional

A busca de duplicados pode analisar muitos arquivos. Por segurança, o FSupport:

- ignora diretórios protegidos do sistema ao mover arquivos para quarentena;
- mantém um arquivo de cada grupo de duplicados;
- exige confirmação textual antes de mover arquivos;
- recomenda validar backup antes de qualquer limpeza.

Use a quarentena com cuidado, especialmente em discos inteiros.

## Arquitetura

O projeto usa uma separação simples por responsabilidade:

```text
controllers/  Orquestram ações do menu e chamadas de serviço
services/     Coletam dados, analisam e geram diagnósticos/relatórios
models/       Representam estruturas de dados do domínio
views/        Exibem informações no terminal
storage/      Guarda coletas e diagnósticos gerados
reports/      Guarda relatórios finais
tests/        Testes unitários
```

## Testes

Execute a suíte de testes:

```powershell
python -m unittest discover -s tests -v
```

## Observações

Algumas verificações dependem do sistema operacional e das permissões do terminal. No Windows, informações como antivírus, firewall, hotfixes e eventos críticos podem exigir permissões adequadas para retornar dados completos.
