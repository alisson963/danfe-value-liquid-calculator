from decimal import Decimal
from config import PIS_PADRAO, COFINS_PADRAO
from utils import converter_numero, arredondar

def calcular_valor_liquido(item: dict) -> dict:
    valor_total = converter_numero(item.get('valor_total'))
    quantidade = converter_numero(item.get('quantidade'))
    aliquota_icms = converter_numero(item.get('aliquota_icms'))
    aliquota_ipi = converter_numero(item.get('aliquota_ipi'))
    if quantidade <= 0:
        quantidade = Decimal('1')
    pis_decimal = converter_numero(PIS_PADRAO) / Decimal('100')
    cofins_decimal = converter_numero(COFINS_PADRAO) / Decimal('100')
    icms_decimal = aliquota_icms / Decimal('100')
    ipi_decimal = aliquota_ipi / Decimal('100')
    valor_ipi_calculado = valor_total * ipi_decimal
    valor_icms_calculado = (valor_total + valor_ipi_calculado) * icms_decimal
    base_pis_cofins = valor_total - valor_icms_calculado
    valor_pis = base_pis_cofins * pis_decimal
    valor_cofins = base_pis_cofins * cofins_decimal
    valor_liquido_total = valor_total - valor_icms_calculado - valor_pis - valor_cofins
    valor_liquido_unitario = valor_liquido_total / quantidade
    item['pis_percentual_usado'] = converter_numero(PIS_PADRAO)
    item['cofins_percentual_usado'] = converter_numero(COFINS_PADRAO)
    item['valor_ipi_calculado'] = arredondar(valor_ipi_calculado)
    item['valor_icms_calculado'] = arredondar(valor_icms_calculado)
    item['base_pis_cofins'] = arredondar(base_pis_cofins)
    item['valor_pis'] = arredondar(valor_pis)
    item['valor_cofins'] = arredondar(valor_cofins)
    item['valor_liquido_total'] = arredondar(valor_liquido_total)
    item['valor_liquido_unitario'] = arredondar(valor_liquido_unitario)
    return item
