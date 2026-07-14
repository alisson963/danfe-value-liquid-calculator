from pathlib import Path
import re
from bs4 import BeautifulSoup
from utils import texto_limpo
NUMERO_2_CASAS = '\\d{1,3}(?:\\.\\d{3})*,\\d{2}|\\d+,\\d{2}|\\d+\\.\\d{2}'
NUMERO_4_CASAS = '\\d{1,3}(?:\\.\\d{3})*,\\d{4}|\\d+,\\d{4}|\\d+\\.\\d{4}'
PADRAO_NUMEROS_DANFE = re.compile(f'(?P<quantidade>{NUMERO_4_CASAS})\\s*(?P<valor_unitario>{NUMERO_4_CASAS})\\s*(?P<valor_total>{NUMERO_2_CASAS})\\s*(?P<base_icms>{NUMERO_2_CASAS})\\s*(?P<valor_icms>{NUMERO_2_CASAS})(?:\\s*(?P<valor_ipi>{NUMERO_2_CASAS}))?\\s*(?P<aliquota_icms>{NUMERO_2_CASAS})(?:\\s*(?P<aliquota_ipi>{NUMERO_2_CASAS}))?$', re.IGNORECASE)

def detectar_tipo_arquivo(caminho: Path) -> str:
    sufixo = caminho.suffix.lower()
    try:
        inicio_bytes = caminho.read_bytes()[:500]
        inicio = inicio_bytes.decode('utf-8', errors='ignore').lower().strip()
    except Exception:
        inicio = ''
    if sufixo == '.xml' or inicio.startswith('<?xml'):
        return 'xml'
    if '<html' in inicio or '<!doctype html' in inicio:
        return 'html'
    if sufixo == '.pdf' or inicio.startswith('%pdf'):
        return 'pdf'
    if sufixo == '.txt':
        return 'txt'
    return 'desconhecido'

def arquivo_parece_pagina_consultadanfe_sem_nota(caminho: Path) -> bool:
    try:
        inicio = caminho.read_bytes()[:20000].decode('utf-8', errors='ignore').lower()
    except Exception:
        return False
    eh_html = '<html' in inicio or '<!doctype html' in inicio
    tem_sinais_site = eh_html and 'consultadanfe' in inicio and ('gerar danfe online' in inicio or 'digite a chave de acesso' in inicio or 'favicon' in inicio)
    tem_sinais_nota_real = 'dados dos produtos' in inicio or 'recebemos de' in inicio
    return bool(tem_sinais_site and (not tem_sinais_nota_real))

def extrair_texto_html(caminho: Path) -> str:
    html = caminho.read_text(encoding='utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text('\n')

def extrair_texto_txt(caminho: Path) -> str:
    return caminho.read_text(encoding='utf-8', errors='ignore')

def extrair_texto_pdf(caminho: Path) -> str:
    import pdfplumber
    textos = []
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            textos.append(pagina.extract_text() or '')
    return '\n'.join(textos)

def extrair_chave_acesso_texto(texto: str) -> str:
    texto = texto or ''
    match = re.search('CHAVE\\s+DE\\s+ACESSO\\s*((?:\\d{4}\\s*){11}|\\d{44})', texto, re.IGNORECASE)
    if match:
        chave = re.sub('\\D', '', match.group(1))
        if len(chave) == 44:
            return chave
    match = re.search('\\b(\\d{44})\\b', texto)
    if match:
        return match.group(1)
    match = re.search('((?:\\d{4}\\s*){11})', texto)
    if match:
        chave = re.sub('\\D', '', match.group(1))
        if len(chave) == 44:
            return chave
    return ''

def _primeiro_grupo(padroes, texto: str, padrao='') -> str:
    for padrao_regex in padroes:
        match = re.search(padrao_regex, texto, re.IGNORECASE | re.DOTALL)
        if match:
            for grupo in match.groups():
                if grupo:
                    return texto_limpo(grupo)
    return padrao

def extrair_metadados_texto(texto: str, arquivo: str='') -> dict:
    texto_original = texto or ''
    texto_uma_linha = texto_limpo(texto_original)
    chave = extrair_chave_acesso_texto(texto_original)
    numero_nf = _primeiro_grupo(['NF-e\\s*N[ºo°\\.\\s]*([0-9][0-9\\.]+)', 'N[ºo°\\.\\s]*([0-9][0-9\\.]+)\\s*S[ée]rie', 'N[ºo°\\.\\s]*([0-9][0-9\\.]+)'], texto_uma_linha)
    serie = _primeiro_grupo(['S[ée]rie\\s*(\\d+)', 'S[ée]rie\\s*([A-Z0-9]+)'], texto_uma_linha)
    data_emissao = _primeiro_grupo(['EMISS[ÃA]O:\\s*(\\d{2}/\\d{2}/\\d{4})', 'DATA\\s+DA\\s+EMISS[ÃA]O\\s*(\\d{2}/\\d{2}/\\d{4})'], texto_uma_linha)
    valor_total_nota = _primeiro_grupo(['VALOR\\s+TOTAL:\\s*R\\$\\s*([\\d\\.]+,\\d{2})', 'V\\.\\s*TOTAL\\s+DA\\s+NOTA\\s*([\\d\\.]+,\\d{2})'], texto_uma_linha)
    emitente = _primeiro_grupo(['RECEBEMOS\\s+DE\\s+(.+?)\\s+OS\\s+PRODUTOS', 'IDENTIFICA[ÇC][ÃA]O\\s+DO\\s+EMITENTE\\s+(.+?)(?:\\s+DANFE|\\s+Documento\\s+Auxiliar)'], texto_uma_linha)
    if ' LTDA ' in emitente.upper():
        pos = emitente.upper().find(' LTDA') + len(' LTDA')
        emitente = emitente[:pos].strip()
    elif ' S.A ' in emitente.upper():
        pos = emitente.upper().find(' S.A') + len(' S.A')
        emitente = emitente[:pos].strip()
    destinatario = _primeiro_grupo(['DESTINAT[ÁA]RIO:\\s*(.+?)\\s+-\\s+', 'NOME\\s*/\\s*RAZ[ÃA]O\\s+SOCIAL\\s+(.+?)\\s+CNPJ\\s*/\\s*CPF'], texto_uma_linha)
    documento_id = chave or f'{arquivo}'
    if numero_nf:
        documento_id = f'NF {numero_nf} - {arquivo}'
    if chave and numero_nf:
        documento_id = f'NF {numero_nf} - Chave {chave}'
    return {'documento_id': documento_id, 'arquivo_origem': arquivo, 'chave_acesso': chave, 'numero_nfe': numero_nf, 'serie_nfe': serie, 'data_emissao': data_emissao, 'emitente': emitente, 'destinatario': destinatario, 'valor_total_nota_documento': valor_total_nota}

def agrupar_palavras_por_linha(words, tolerancia=2.0):
    linhas = []
    for word in sorted(words, key=lambda w: (round(w['top'], 1), w['x0'])):
        colocado = False
        for linha in linhas:
            if abs(linha['top'] - word['top']) <= tolerancia:
                linha['words'].append(word)
                linha['top'] = (linha['top'] + word['top']) / 2
                colocado = True
                break
        if not colocado:
            linhas.append({'top': word['top'], 'words': [word]})
    for linha in linhas:
        linha['words'].sort(key=lambda w: w['x0'])
    return linhas

def juntar_textos(words):
    return ' '.join((w['text'] for w in words)).strip()

def extrair_numeros_danfe(texto_numerico: str):
    texto_numerico = texto_limpo(texto_numerico)
    match = PADRAO_NUMEROS_DANFE.search(texto_numerico)
    if not match:
        return None
    dados = match.groupdict()
    if not dados.get('valor_ipi'):
        dados['valor_ipi'] = '0,00'
    if not dados.get('aliquota_ipi'):
        dados['aliquota_ipi'] = '0,00'
    return dados

def _aplicar_metadados(item: dict, metadados: dict):
    for chave, valor in metadados.items():
        if chave == 'chave_acesso' and item.get('chave_acesso'):
            continue
        item[chave] = valor
    if not item.get('chave_acesso'):
        item['chave_acesso'] = metadados.get('chave_acesso', '')
    return item

def extrair_itens_pdf_por_posicao(caminho: Path):
    import pdfplumber
    itens = []
    texto_completo = ''
    numero_item = 1
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            texto_completo += '\n' + (pagina.extract_text() or '')
            words = pagina.extract_words(use_text_flow=False, x_tolerance=1, y_tolerance=2, keep_blank_chars=False)
            linhas = agrupar_palavras_por_linha(words, tolerancia=2.0)
            for linha in linhas:
                palavras = linha['words']
                linha_texto = juntar_textos(palavras)
                if not re.search('\\b\\d{8}\\b', linha_texto):
                    continue
                if not re.search('\\b\\d{4}\\b', linha_texto):
                    continue
                codigo = juntar_textos([w for w in palavras if w['x0'] < 60])
                descricao = juntar_textos([w for w in palavras if 60 <= w['x0'] < 226])
                ncm = juntar_textos([w for w in palavras if 226 <= w['x0'] < 263])
                cst = juntar_textos([w for w in palavras if 263 <= w['x0'] < 287])
                cfop = juntar_textos([w for w in palavras if 287 <= w['x0'] < 309])
                unidade = juntar_textos([w for w in palavras if 309 <= w['x0'] < 331])
                numeros_texto = juntar_textos([w for w in palavras if w['x0'] >= 331])
                if not re.fullmatch('\\d{8}', re.sub('\\D', '', ncm or '')):
                    continue
                if not re.fullmatch('\\d{2,4}', re.sub('\\D', '', cst or '')):
                    continue
                if not re.fullmatch('\\d{4}', re.sub('\\D', '', cfop or '')):
                    continue
                numeros = extrair_numeros_danfe(numeros_texto)
                if not numeros:
                    continue
                item = {'arquivo': caminho.name, 'tipo_arquivo': 'PDF', 'chave_acesso': '', 'numero_item': numero_item, 'codigo_produto': codigo, 'descricao': descricao, 'ncm': re.sub('\\D', '', ncm), 'cst': re.sub('\\D', '', cst), 'cfop': re.sub('\\D', '', cfop), 'unidade': unidade, 'quantidade': numeros['quantidade'], 'valor_unitario': numeros['valor_unitario'], 'valor_total': numeros['valor_total'], 'base_icms_documento': numeros['base_icms'], 'valor_icms_documento': numeros['valor_icms'], 'valor_ipi_documento': numeros['valor_ipi'], 'aliquota_icms': numeros['aliquota_icms'], 'aliquota_ipi': numeros['aliquota_ipi']}
                itens.append(item)
                numero_item += 1
    metadados = extrair_metadados_texto(texto_completo, caminho.name)
    for item in itens:
        _aplicar_metadados(item, metadados)
    return itens

def extrair_itens_texto(caminho: Path, texto: str, tipo_arquivo: str):
    texto_original = texto or ''
    texto = texto_limpo(texto_original)
    metadados = extrair_metadados_texto(texto_original, caminho.name)
    itens = []
    padrao_item = re.compile(f'(?P<codigo>[A-Z0-9\\.\\-\\/]{{1,40}})\\s+(?P<descricao>.+?)\\s+(?P<ncm>\\d{{8}})\\s+(?P<cst>\\d{{2,4}})\\s+(?P<cfop>\\d{{4}})\\s+(?P<unidade>[A-ZÇ]{{1,8}})\\s+(?P<restante>{NUMERO_4_CASAS}.*?)(?=(?:[A-Z0-9\\.\\-\\/]{{1,40}}\\s+.+?\\s+\\d{{8}}\\s+\\d{{2,4}}\\s+\\d{{4}}\\s+[A-ZÇ]{{1,8}}\\s+{NUMERO_4_CASAS})|DADOS ADICIONAIS|$)', re.IGNORECASE)
    for numero_item, match in enumerate(padrao_item.finditer(texto), start=1):
        dados = match.groupdict()
        numeros = extrair_numeros_danfe(dados.get('restante', ''))
        if not numeros:
            continue
        item = {'arquivo': caminho.name, 'tipo_arquivo': tipo_arquivo.upper(), 'chave_acesso': metadados.get('chave_acesso', ''), 'numero_item': numero_item, 'codigo_produto': dados.get('codigo', '').strip(), 'descricao': dados.get('descricao', '').strip(), 'ncm': dados.get('ncm', ''), 'cst': dados.get('cst', ''), 'cfop': dados.get('cfop', ''), 'unidade': dados.get('unidade', ''), 'quantidade': numeros['quantidade'], 'valor_unitario': numeros['valor_unitario'], 'valor_total': numeros['valor_total'], 'base_icms_documento': numeros['base_icms'], 'valor_icms_documento': numeros['valor_icms'], 'valor_ipi_documento': numeros['valor_ipi'], 'aliquota_icms': numeros['aliquota_icms'], 'aliquota_ipi': numeros['aliquota_ipi']}
        itens.append(_aplicar_metadados(item, metadados))
    return itens
