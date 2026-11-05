import csv
import hashlib
import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from insight_vendas.__main__ import main
from insight_vendas.core import FIELDS, InputError, load_csv, parse_sale, payload, safe_cell, summarize
from insight_vendas.report import render_html


BASE = dict(zip(FIELDS, ("P-001", "2026-10-01", "Cliente fictício", "Produto teste", "Casa", "Sudeste", "3", "19,99", "10", "concluído")))


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_csv(self, rows, headers=FIELDS, name="input.csv"):
        path = self.root / name
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_decimal_calculation_and_rounding(self):
        sale = parse_sale(BASE)
        self.assertEqual(sale.total_centavos, 5397)
        self.assertEqual(sale.preco_unitario_centavos, 1999)
        self.assertEqual(sale.status, "concluido")

    def test_half_cent_rounds_up_per_order(self):
        self.assertEqual(parse_sale({**BASE, "quantidade": "1", "preco_unitario": "0.05", "desconto_pct": "50"}).total_centavos, 3)

    def test_full_discount(self):
        self.assertEqual(parse_sale({**BASE, "desconto_pct": "100"}).total_centavos, 0)

    def test_brazilian_date(self):
        self.assertEqual(parse_sale({**BASE, "data": "29/02/2024"}).data, "2024-02-29")

    def test_invalid_dates(self):
        for value in ("2026-02-29", "31/04/2026", "01-02-2026", "1999-12-31", "2100-01-01", "2026-1-1"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "data"):
                parse_sale({**BASE, "data": value})

    def test_invalid_money(self):
        for value in ("NaN", "Infinity", "-1", "1e5", "1.234,56", "1.234", "100001", "", "R$ 9,99"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "preco_unitario"):
                parse_sale({**BASE, "preco_unitario": value})

    def test_quantity_and_discount_bounds(self):
        for value in ("0", "-1", "1.5", "1001", "10000", "NaN"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "quantidade"):
                parse_sale({**BASE, "quantidade": value})
        for value in ("101", "-2", "10.001"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "desconto_pct"):
                parse_sale({**BASE, "desconto_pct": value})

    def test_required_and_control_characters(self):
        for field in ("pedido_id", "cliente", "produto", "categoria", "regiao"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                parse_sale({**BASE, field: "  "})
        with self.assertRaisesRegex(ValueError, "controle"):
            parse_sale({**BASE, "cliente": "Teste\nNome"})
        with self.assertRaisesRegex(ValueError, "limite"):
            parse_sale({**BASE, "cliente": "X" * 121})

    def test_status_whitelist(self):
        self.assertEqual(parse_sale({**BASE, "status": " CONCLUÍDO "}).status, "concluido")
        with self.assertRaisesRegex(ValueError, "status"):
            parse_sale({**BASE, "status": "pago"})

    def test_utf8_bom_and_decimal_dot(self):
        dataset = load_csv(self.write_csv([{**BASE, "preco_unitario": "19.99"}]))
        self.assertEqual(dataset.sales[0].total_centavos, 5397)
        self.assertEqual(dataset.input_rows, 1)

    def test_duplicate_rejected_and_invalid_first_does_not_reserve_id(self):
        dataset = load_csv(self.write_csv([{**BASE, "data": "bad"}, BASE, BASE]))
        self.assertEqual(len(dataset.sales), 1)
        self.assertEqual(len(dataset.issues), 2)
        self.assertIn("duplicado", dataset.issues[1].motivo)
        self.assertEqual(dataset.issues[1].linha, 4)

    def test_sorting_and_reordered_headers(self):
        dataset = load_csv(self.write_csv([{**BASE, "pedido_id": "B", "data": "2026-10-03"}, BASE], tuple(reversed(FIELDS))))
        self.assertEqual([sale.pedido_id for sale in dataset.sales], ["P-001", "B"])

    def test_missing_extra_and_duplicate_headers(self):
        for header in (FIELDS[:-1], (*FIELDS, "extra"), (*FIELDS, "status")):
            path = self.root / "headers.csv"
            path.write_text(";".join(header) + "\n", encoding="utf-8")
            with self.subTest(header=header), self.assertRaisesRegex(InputError, "Cabeçalho"):
                load_csv(path)

    def test_empty_and_only_invalid(self):
        with self.assertRaisesRegex(InputError, "Nenhum registro"):
            load_csv(self.write_csv([]))
        with self.assertRaisesRegex(InputError, "Primeiro problema"):
            load_csv(self.write_csv([{**BASE, "data": "bad"}]))

    def test_wrong_column_count(self):
        path = self.write_csv([BASE])
        with path.open("a", encoding="utf-8") as stream:
            stream.write("bad;too;short\n")
        dataset = load_csv(path)
        self.assertEqual(len(dataset.issues), 1)
        self.assertIn("colunas", dataset.issues[0].motivo)

    def test_invalid_encoding(self):
        path = self.root / "invalid.csv"
        path.write_bytes(b"\xff\xfe\xff")
        with self.assertRaisesRegex(InputError, "UTF-8"):
            load_csv(path)

    def test_limits(self):
        path = self.write_csv([BASE, {**BASE, "pedido_id": "P-002"}])
        with patch("insight_vendas.core.MAX_ROWS", 1), self.assertRaisesRegex(InputError, "10.000"):
            load_csv(path)
        with patch("insight_vendas.core.MAX_FILE_BYTES", 10), self.assertRaisesRegex(InputError, "10 MB"):
            load_csv(path)

    def test_malformed_quoted_csv_is_fatal(self):
        path = self.write_csv([BASE])
        with path.open("a", encoding="utf-8") as stream:
            stream.write('"unterminated')
        with self.assertRaisesRegex(InputError, "CSV malformado"):
            load_csv(path)

    def test_summary_uses_completed_only(self):
        completed = parse_sale(BASE)
        pending = parse_sale({**BASE, "pedido_id": "P-002", "status": "pendente"})
        canceled = parse_sale({**BASE, "pedido_id": "P-003", "status": "cancelado"})
        summary = summarize([completed, pending, canceled])
        self.assertEqual(summary["faturamento_centavos"], 5397)
        self.assertEqual(summary["ticket_medio_centavos"], 5397)
        self.assertEqual(summary["pendente_centavos"], 5397)
        self.assertEqual(summary["pedidos_concluidos"], 1)
        self.assertEqual(summary["pedidos_cancelados"], 1)
        self.assertEqual(summary["receita_por_categoria"], {"Casa": 5397})

    def test_zero_completed_summary(self):
        summary = summarize([parse_sale({**BASE, "status": "pendente"})])
        self.assertEqual(summary["ticket_medio_centavos"], 0)
        self.assertEqual(summary["faturamento_centavos"], 0)
        self.assertEqual(summarize([])["registros_validos"], 0)

    def test_csv_formula_guard(self):
        for value in ("=1+1", "+SUM(A1)", "-1", "@test", "  =2"):
            with self.subTest(value=value):
                self.assertTrue(safe_cell(value).startswith("'"))
        self.assertEqual(safe_cell("Cliente normal"), "Cliente normal")

    def test_html_json_cannot_escape_script(self):
        dangerous = '</script><script>alert("x")</script>&'
        data = payload(load_csv(self.write_csv([{**BASE, "cliente": dangerous}])))
        html = render_html(data)
        self.assertNotIn(dangerous, html)
        embedded = html.split('<script type="application/json" id="data">')[1].split("</script>")[0]
        self.assertEqual(json.loads(embedded)["vendas"][0]["cliente"], dangerous)
        script = html.split('<script id="app">')[1].split("</script>")[0]
        digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        self.assertIn(f"'sha256-{digest}'", html)

    def test_cli_outputs_and_reject_log(self):
        path = self.write_csv([BASE, {**BASE, "pedido_id": "=2+2", "data": "bad"}])
        output = self.root / "output"
        self.assertEqual(main([str(path), "--output", str(output)]), 0)
        self.assertEqual({p.name for p in output.iterdir()}, {"index.html", "resumo.json", "vendas_tratadas.csv", "erros.csv"})
        self.assertEqual(json.loads((output / "resumo.json").read_text())["linhas_rejeitadas"], 1)
        self.assertIn("'=2+2", (output / "erros.csv").read_text(encoding="utf-8-sig"))

    def test_strict_mode_does_not_write(self):
        path = self.write_csv([BASE, {**BASE, "data": "bad"}])
        output = self.root / "output"
        self.assertEqual(main([str(path), "--strict", "--output", str(output)]), 2)
        self.assertFalse(output.exists())

    def test_missing_input_is_friendly_error(self):
        self.assertEqual(main([str(self.root / "missing.csv")]), 2)

    def test_source_cannot_be_overwritten(self):
        path = self.write_csv([BASE], name="vendas_tratadas.csv")
        original = path.read_bytes()
        self.assertEqual(main([str(path), "--output", str(self.root)]), 2)
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse((self.root / "index.html").exists())

    def test_bad_destination_does_not_partially_overwrite(self):
        path = self.write_csv([BASE])
        output = self.root / "output"
        output.mkdir()
        (output / "index.html").write_text("original")
        (output / "erros.csv").mkdir()
        self.assertEqual(main([str(path), "--output", str(output)]), 2)
        self.assertEqual((output / "index.html").read_text(), "original")


if __name__ == "__main__":
    unittest.main()
