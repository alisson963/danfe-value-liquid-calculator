from pathlib import Path
import shutil
import pandas as pd
from config import PASTA_DOCUMENTOS, PASTA_RESULTADOS, PASTA_LOGS, PASTA_PROCESSADOS, ARQUIVO_RESULTADO, ARQUIVO_ERROS, ARQUIVO_LOG, MOVER_PROCESSADOS
from utils import garantir_pastas, registrar_log
from calculadora import calcular_valor_liquido
from extrator_xml import extrair_itens_xml
from extrator_texto import detectar_tipo_arquivo, extrair_texto_pdf, extrair_texto_html, extrair_texto_txt, extrair_itens_texto, extrair_itens_pdf_por_posicao, arquivo_parece_pagina_consultadanfe_sem_nota
from exportador import salvar_excel
EXTENSOES_ACEITAS = {'.xml', '.pdf', '.html', '.htm', '.txt'}

def extrair_itens_documento(caminho: Path):
    if arquivo_parece_pagina_consultadanfe_sem_nota(caminho):
        raise ValueError('Este arquivo parece ser apenas a página do site Consulta DANFE, não o DANFE/PDF da nota. Abra a chave no site, clique em Imprimir DANFE/Visualizar e salve o PDF verdadeiro.')
    tipo = detectar_tipo_arquivo(caminho)
    if tipo == 'xml':
        return extrair_itens_xml(caminho)
    if tipo == 'pdf':
        itens = extrair_itens_pdf_por_posicao(caminho)
        if itens:
            return itens
        texto = extrair_texto_pdf(caminho)
        return extrair_itens_texto(caminho, texto, 'PDF')
    if tipo == 'html':
        texto = extrair_texto_html(caminho)
        return extrair_itens_texto(caminho, texto, 'HTML')
    if tipo == 'txt':
        texto = extrair_texto_txt(caminho)
        return extrair_itens_texto(caminho, texto, 'TXT')
    return []

def listar_documentos():
    arquivos = []
    for caminho in PASTA_DOCUMENTOS.rglob('*'):
        if not caminho.is_file():
            continue
        if caminho.name.startswith('~$'):
            continue
        if caminho.name.upper().startswith('COLOQUE_'):
            continue
        if caminho.suffix.lower() in EXTENSOES_ACEITAS:
            arquivos.append(caminho)
    return sorted(arquivos, key=lambda p: str(p).lower())

def processar_documentos():
    garantir_pastas(PASTA_DOCUMENTOS, PASTA_RESULTADOS, PASTA_LOGS, PASTA_PROCESSADOS)
    registrar_log(ARQUIVO_LOG, 'Iniciando processamento.')
    print('Iniciando processamento...')
    print(f'Pasta de entrada: {PASTA_DOCUMENTOS}')
    documentos = listar_documentos()
    if not documentos:
        mensagem = 'Nenhum documento encontrado. Coloque PDF, XML, HTML ou TXT na pasta 01_documentos_para_analisar.'
        print(mensagem)
        registrar_log(ARQUIVO_LOG, mensagem)
        return
    print(f'Documentos encontrados: {len(documentos)}')
    registrar_log(ARQUIVO_LOG, f'Documentos encontrados: {len(documentos)}')
    resultados = []
    erros = []
    status_documentos = []
    for documento in documentos:
        nome_relativo = str(documento.relative_to(PASTA_DOCUMENTOS))
        print(f'\nAnalisando: {nome_relativo}')
        registrar_log(ARQUIVO_LOG, f'Analisando: {nome_relativo}')
        try:
            itens = extrair_itens_documento(documento)
            if not itens:
                erro = 'Nenhum item foi encontrado automaticamente no documento. Pode ser layout diferente, PDF ilegível ou arquivo baixado errado.'
                print(f'  Atenção: {erro}')
                erros.append({'arquivo': nome_relativo, 'erro': erro})
                status_documentos.append({'arquivo': nome_relativo, 'status': 'ERRO', 'itens_encontrados': 0, 'detalhe': erro})
                registrar_log(ARQUIVO_LOG, f'Erro: {nome_relativo} - {erro}')
                continue
            primeiro_item = itens[0] if itens else {}
            for item in itens:
                item['arquivo'] = nome_relativo
                item['arquivo_origem'] = nome_relativo
                item_calculado = calcular_valor_liquido(item)
                resultados.append(item_calculado)
            print(f'  Itens encontrados: {len(itens)}')
            status_documentos.append({'arquivo': nome_relativo, 'status': 'OK', 'itens_encontrados': len(itens), 'documento_id': primeiro_item.get('documento_id', ''), 'chave_acesso': primeiro_item.get('chave_acesso', ''), 'numero_nfe': primeiro_item.get('numero_nfe', ''), 'serie_nfe': primeiro_item.get('serie_nfe', ''), 'data_emissao': primeiro_item.get('data_emissao', ''), 'emitente': primeiro_item.get('emitente', ''), 'destinatario': primeiro_item.get('destinatario', ''), 'valor_total_nota_documento': primeiro_item.get('valor_total_nota_documento', ''), 'detalhe': 'Processado com sucesso'})
            registrar_log(ARQUIVO_LOG, f'OK: {nome_relativo} - {len(itens)} itens encontrados.')
            if MOVER_PROCESSADOS:
                destino = PASTA_PROCESSADOS / nome_relativo
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(documento), str(destino))
                registrar_log(ARQUIVO_LOG, f'Documento movido para processados: {destino}')
        except Exception as exc:
            erro = str(exc)
            print(f'  Erro ao processar: {erro}')
            erros.append({'arquivo': nome_relativo, 'erro': erro})
            status_documentos.append({'arquivo': nome_relativo, 'status': 'ERRO', 'itens_encontrados': 0, 'detalhe': erro})
            registrar_log(ARQUIVO_LOG, f'Erro: {nome_relativo} - {erro}')
    if resultados or erros or status_documentos:
        caminho_gerado = salvar_excel(resultados, ARQUIVO_RESULTADO, erros=erros, documentos=status_documentos)
        print(f'\nPlanilha criada/atualizada com sucesso: {caminho_gerado}')
        if caminho_gerado.name != ARQUIVO_RESULTADO.name:
            print('Obs.: o arquivo padrão estava aberto ou bloqueado. Por isso o robô salvou uma nova cópia com data e hora no nome.')
        registrar_log(ARQUIVO_LOG, f'Planilha criada: {caminho_gerado}')
    else:
        print('\nNenhum resultado calculado.')
        registrar_log(ARQUIVO_LOG, 'Nenhum resultado calculado.')
    if erros:
        try:
            df_erros = pd.DataFrame(erros)
            df_erros.to_excel(ARQUIVO_ERROS, index=False)
            print(f'Arquivos com erro/atenção: {ARQUIVO_ERROS}')
            registrar_log(ARQUIVO_LOG, f'Arquivo de erros criado: {ARQUIVO_ERROS}')
        except PermissionError:
            print('Não consegui atualizar erros_processamento.xlsx porque ele está aberto no Excel. Feche o arquivo e rode novamente.')
    print(f'\nResumo: {len(resultados)} item(ns) calculado(s), {len(erros)} arquivo(s) com erro/atenção.')
    registrar_log(ARQUIVO_LOG, 'Processamento finalizado.')
    print('Processamento finalizado.')
if __name__ == '__main__':
    processar_documentos()
