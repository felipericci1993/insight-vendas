"""Validação e cálculos financeiros determinísticos, sem acesso à rede."""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


FIELDS = (
    "pedido_id", "data", "cliente", "produto", "categoria", "regiao",
    "quantidade", "preco_unitario", "desconto_pct", "status",
)
MAX_ROWS = 10_000
MAX_FILE_BYTES = 10_000_000


class InputError(ValueError):
    """Problema de arquivo ou de formato que impede um relatório confiável."""


@dataclass(frozen=True)
class Sale:
    pedido_id: str
    data: str
    cliente: str
    produto: str
    categoria: str
    regiao: str
    quantidade: int
    preco_unitario_centavos: int
    desconto_pct: str
    status: str
    total_centavos: int


@dataclass(frozen=True)
class Issue:
    linha: int
    pedido_id: str
    motivo: str


@dataclass(frozen=True)
class Dataset:
    sales: tuple[Sale, ...]
    issues: tuple[Issue, ...]
    source_name: str
    input_rows: int


def _text(value: str | None, name: str, limit: int = 120) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{name}: campo obrigatório")
    if len(value) > limit:
        raise ValueError(f"{name}: limite de {limit} caracteres")
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f"{name}: contém caractere de controle")
    return value


def _number(value: str | None, name: str, maximum: Decimal, places: int = 2) -> Decimal:
    raw = (value or "").strip()
    # Sem separador de milhar: 1234,56 e 1234.56 são aceitos, 1.234,56 não.
    if not re.fullmatch(rf"\d+(?:[.,]\d{{1,{places}}})?", raw):
        raise ValueError(f"{name}: use número não negativo, sem milhar, com até {places} casas")
    try:
        parsed = Decimal(raw.replace(",", "."))
    except InvalidOperation as exc:
        raise ValueError(f"{name}: número inválido") from exc
    if parsed > maximum:
        raise ValueError(f"{name}: máximo permitido {maximum}")
    return parsed


def _date(value: str | None) -> str:
    raw = (value or "").strip()
    for pattern, fmt in ((r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"), (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y")):
        if re.fullmatch(pattern, raw):
            try:
                parsed = datetime.strptime(raw, fmt).date()
                if not date(2000, 1, 1) <= parsed <= date(2099, 12, 31):
                    break
                return parsed.isoformat()
            except ValueError:
                break
    raise ValueError("data: use uma data válida entre 2000 e 2099 em AAAA-MM-DD ou DD/MM/AAAA")


def _status(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", (value or "").strip().lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    if text not in {"concluido", "pendente", "cancelado"}:
        raise ValueError("status: use concluido, pendente ou cancelado")
    return text


def parse_sale(row: dict[str, str | None]) -> Sale:
    identifier = _text(row.get("pedido_id"), "pedido_id", 50)
    day = _date(row.get("data"))
    fields = {name: _text(row.get(name), name) for name in ("cliente", "produto", "categoria", "regiao")}
    quantity = (row.get("quantidade") or "").strip()
    if not re.fullmatch(r"\d{1,4}", quantity) or not 1 <= int(quantity) <= 1000:
        raise ValueError("quantidade: use um inteiro entre 1 e 1000")
    price = _number(row.get("preco_unitario"), "preco_unitario", Decimal("100000"))
    discount = _number(row.get("desconto_pct"), "desconto_pct", Decimal("100"))
    status = _status(row.get("status"))
    total = (int(quantity) * price * (1 - discount / 100)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Sale(identifier, day, **fields, quantidade=int(quantity),
                preco_unitario_centavos=int(price * 100), desconto_pct=format(discount, "f"),
                status=status, total_centavos=int(total * 100))


def load_csv(path: str | Path) -> Dataset:
    path = Path(path)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise InputError("Arquivo maior que 10 MB. Divida a base antes de continuar.")
    sales: list[Sale] = []
    issues: list[Issue] = []
    seen: set[str] = set()
    input_rows = 0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";", strict=True)
            headers = reader.fieldnames
            if not headers or len(headers) != len(set(headers)) or set(headers) != set(FIELDS):
                raise InputError("Cabeçalho inválido. Use exatamente estas colunas, separadas por ponto e vírgula: " + ";".join(FIELDS))
            for row in reader:
                input_rows += 1
                if input_rows > MAX_ROWS:
                    raise InputError("Limite de 10.000 registros excedido. Divida a base antes de continuar.")
                line = reader.line_num
                identifier = (row.get("pedido_id") or "").strip()[:50]
                try:
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError("quantidade de colunas diferente do cabeçalho")
                    sale = parse_sale(row)
                    if sale.pedido_id in seen:
                        raise ValueError("pedido_id duplicado: a primeira ocorrência válida foi mantida")
                    seen.add(sale.pedido_id)
                    sales.append(sale)
                except ValueError as exc:
                    issues.append(Issue(line, identifier, str(exc)))
    except UnicodeDecodeError as exc:
        raise InputError("Codificação inválida. Salve o CSV como UTF-8.") from exc
    except csv.Error as exc:
        raise InputError(f"CSV malformado: {exc}") from exc
    if not sales:
        detail = f" {len(issues)} registro(s) rejeitado(s). Primeiro problema: {issues[0].motivo}." if issues else ""
        raise InputError("Nenhum registro válido encontrado." + detail)
    return Dataset(tuple(sorted(sales, key=lambda sale: (sale.data, sale.pedido_id))), tuple(issues), path.name, input_rows)


def summarize(sales: tuple[Sale, ...] | list[Sale]) -> dict:
    completed = [sale for sale in sales if sale.status == "concluido"]
    revenue = sum(sale.total_centavos for sale in completed)
    ticket = int((Decimal(revenue) / len(completed)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) if completed else 0
    by_category: dict[str, int] = {}
    by_day: dict[str, int] = {}
    for sale in completed:
        by_category[sale.categoria] = by_category.get(sale.categoria, 0) + sale.total_centavos
        by_day[sale.data] = by_day.get(sale.data, 0) + sale.total_centavos
    return {
        "registros_validos": len(sales), "pedidos_concluidos": len(completed),
        "faturamento_centavos": revenue, "ticket_medio_centavos": ticket,
        "pendente_centavos": sum(sale.total_centavos for sale in sales if sale.status == "pendente"),
        "pedidos_cancelados": sum(sale.status == "cancelado" for sale in sales),
        "receita_por_categoria": dict(sorted(by_category.items())),
        "receita_por_dia": dict(sorted(by_day.items())),
    }


def payload(dataset: Dataset) -> dict:
    return {"demonstracao": True, "moeda": "BRL", "fonte": dataset.source_name,
            "linhas_lidas": dataset.input_rows, "linhas_rejeitadas": len(dataset.issues),
            "resumo": summarize(dataset.sales), "vendas": [asdict(sale) for sale in dataset.sales]}


def safe_cell(value: object) -> str:
    """Reduz risco de fórmula ao abrir exportações em apps de planilha."""
    text = str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else text


def normalized_rows(dataset: Dataset):
    for sale in dataset.sales:
        yield (sale.pedido_id, sale.data, sale.cliente, sale.produto, sale.categoria, sale.regiao,
               sale.quantidade, f"{sale.preco_unitario_centavos / 100:.2f}".replace(".", ","),
               sale.desconto_pct.replace(".", ","), sale.status,
               f"{sale.total_centavos / 100:.2f}".replace(".", ","))
