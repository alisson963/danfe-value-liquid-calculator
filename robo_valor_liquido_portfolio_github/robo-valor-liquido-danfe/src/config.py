from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
PASTA_DOCUMENTOS = BASE_DIR / '01_documentos_para_analisar'
PASTA_RESULTADOS = BASE_DIR / '02_resultados'
PASTA_LOGS = BASE_DIR / '03_logs'
PASTA_PROCESSADOS = BASE_DIR / '04_documentos_processados'
ARQUIVO_RESULTADO = PASTA_RESULTADOS / 'resultado_valor_liquido.xlsx'
ARQUIVO_ERROS = PASTA_RESULTADOS / 'erros_processamento.xlsx'
ARQUIVO_LOG = PASTA_LOGS / 'log_processamento.txt'
PIS_PADRAO = '1.65'
COFINS_PADRAO = '7.60'
MOVER_PROCESSADOS = False
