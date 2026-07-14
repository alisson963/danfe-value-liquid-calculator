from decimal import Decimal, ROUND_HALF_UP
import re
from datetime import datetime
from pathlib import Path

def converter_numero(valor) -> Decimal:
    if valor is None:
        return Decimal('0')
    texto = str(valor).strip()
    texto = texto.replace('\xa0', ' ')
    texto = re.sub('[^\\d,\\.\\-]', '', texto)
    if texto in ('', '-', '.', ','):
        return Decimal('0')
    if ',' in texto and texto.rfind(',') > texto.rfind('.'):
        texto = texto.replace('.', '').replace(',', '.')
    elif ',' in texto and texto.rfind('.') > texto.rfind(','):
        texto = texto.replace(',', '')
    return Decimal(texto)

def arredondar(valor: Decimal, casas: int=2) -> Decimal:
    formato = '0.' + '0' * casas
    return valor.quantize(Decimal(formato), rounding=ROUND_HALF_UP)

def formatar_moeda_br(valor) -> str:
    valor = converter_numero(valor)
    texto = f'{valor:,.2f}'
    return 'R$ ' + texto.replace(',', 'X').replace('.', ',').replace('X', '.')

def garantir_pastas(*pastas: Path):
    for pasta in pastas:
        pasta.mkdir(parents=True, exist_ok=True)

def registrar_log(caminho_log: Path, mensagem: str):
    caminho_log.parent.mkdir(parents=True, exist_ok=True)
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    with caminho_log.open('a', encoding='utf-8') as arquivo:
        arquivo.write(f'[{agora}] {mensagem}\n')

def texto_limpo(texto: str) -> str:
    texto = texto or ''
    texto = texto.replace('\xa0', ' ')
    texto = re.sub('\\s+', ' ', texto)
    return texto.strip()
