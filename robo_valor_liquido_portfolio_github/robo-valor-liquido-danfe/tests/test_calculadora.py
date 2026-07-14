from decimal import Decimal
from calculadora import calcular_valor_liquido


def test_calculo_valor_liquido_exemplo_base():
    item = {
        "valor_total": "9958736.47",
        "quantidade": "1",
        "aliquota_icms": "12",
        "aliquota_ipi": "0",
    }

    resultado = calcular_valor_liquido(item)

    assert resultado["valor_liquido_unitario"] == Decimal("7953046.94")
    assert resultado["valor_liquido_total"] == Decimal("7953046.94")
