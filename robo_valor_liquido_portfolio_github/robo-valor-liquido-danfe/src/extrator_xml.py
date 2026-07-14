import xml.etree.ElementTree as ET

def nome_tag(elemento) -> str:
    return elemento.tag.split('}')[-1]

def buscar_primeiro(elemento, tag):
    if elemento is None:
        return None
    for filho in elemento.iter():
        if nome_tag(filho) == tag:
            return filho
    return None

def buscar_texto(elemento, tag, padrao='') -> str:
    encontrado = buscar_primeiro(elemento, tag)
    if encontrado is None or encontrado.text is None:
        return padrao
    return encontrado.text.strip()

def extrair_chave_acesso(root) -> str:
    for elemento in root.iter():
        if nome_tag(elemento) == 'infNFe':
            return elemento.attrib.get('Id', '').replace('NFe', '')
    return ''

def extrair_metadados_xml(root, arquivo: str) -> dict:
    chave_acesso = extrair_chave_acesso(root)
    ide = buscar_primeiro(root, 'ide')
    emit = buscar_primeiro(root, 'emit')
    dest = buscar_primeiro(root, 'dest')
    total = buscar_primeiro(root, 'ICMSTot')
    numero_nfe = buscar_texto(ide, 'nNF', '')
    serie_nfe = buscar_texto(ide, 'serie', '')
    data_emissao = buscar_texto(ide, 'dhEmi', '') or buscar_texto(ide, 'dEmi', '')
    emitente = buscar_texto(emit, 'xNome', '')
    destinatario = buscar_texto(dest, 'xNome', '')
    valor_total_nota = buscar_texto(total, 'vNF', '')
    documento_id = chave_acesso or arquivo
    if numero_nfe:
        documento_id = f'NF {numero_nfe} - {arquivo}'
    if chave_acesso and numero_nfe:
        documento_id = f'NF {numero_nfe} - Chave {chave_acesso}'
    return {'documento_id': documento_id, 'arquivo_origem': arquivo, 'chave_acesso': chave_acesso, 'numero_nfe': numero_nfe, 'serie_nfe': serie_nfe, 'data_emissao': data_emissao, 'emitente': emitente, 'destinatario': destinatario, 'valor_total_nota_documento': valor_total_nota}

def extrair_itens_xml(caminho):
    tree = ET.parse(caminho)
    root = tree.getroot()
    metadados = extrair_metadados_xml(root, caminho.name)
    itens = []
    for det in root.iter():
        if nome_tag(det) != 'det':
            continue
        prod = buscar_primeiro(det, 'prod')
        imposto = buscar_primeiro(det, 'imposto')
        numero_item = det.attrib.get('nItem', '')
        item = {'arquivo': caminho.name, 'tipo_arquivo': 'XML', **metadados, 'numero_item': numero_item, 'codigo_produto': buscar_texto(prod, 'cProd', ''), 'descricao': buscar_texto(prod, 'xProd', ''), 'ncm': buscar_texto(prod, 'NCM', ''), 'cst': buscar_texto(imposto, 'CST', ''), 'cfop': buscar_texto(prod, 'CFOP', ''), 'unidade': buscar_texto(prod, 'uCom', ''), 'quantidade': buscar_texto(prod, 'qCom', '0'), 'valor_unitario': buscar_texto(prod, 'vUnCom', '0'), 'valor_total': buscar_texto(prod, 'vProd', '0'), 'base_icms_documento': buscar_texto(imposto, 'vBC', '0'), 'valor_icms_documento': buscar_texto(imposto, 'vICMS', '0'), 'valor_ipi_documento': buscar_texto(imposto, 'vIPI', '0'), 'aliquota_icms': buscar_texto(imposto, 'pICMS', '0'), 'aliquota_ipi': buscar_texto(imposto, 'pIPI', '0')}
        itens.append(item)
    return itens
