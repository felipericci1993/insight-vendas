"""QA opcional: python tests/browser_smoke.py (requer Playwright + Chromium)."""

import csv
import io
import json
import os
from pathlib import Path
import sys
import tempfile

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from insight_vendas.report import render_html
REPORT = ROOT / "dist" / "index.html"
SHOTS = ROOT / "docs" / "screenshots"


def main():
    results = []
    SHOTS.mkdir(parents=True, exist_ok=True)
    model = json.loads((ROOT / "dist" / "resumo.json").read_text(encoding="utf-8"))
    with sync_playwright() as playwright:
        executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        browser = playwright.chromium.launch(headless=True, executable_path=executable)
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        errors, external = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        page.on("request", lambda request: external.append(request.url) if request.url.startswith(("https:", "http:")) else None)
        page.goto(REPORT.as_uri())
        assert page.title() == "Insight Vendas · Painel demonstrativo"
        assert page.locator("#period").input_value() == "2026-10"
        assert page.locator("#count").inner_text() == "72 registros"
        assert page.locator("#orders tr").count() == 8
        page.screenshot(path=str(SHOTS / "desktop.png"), full_page=True)
        results.append("Carregamento offline, mês mais recente e paginação inicial")

        def check_total(sales):
            completed = [sale for sale in sales if sale["status"] == "concluido"]
            cents = sum(sale["total_centavos"] for sale in completed)
            expected = page.evaluate("c => (c / 100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'})", cents)
            assert page.locator("#revenue").inner_text() == expected
            assert page.locator("#completed").inner_text() == str(len(completed))
            assert page.locator("#count").inner_text() == f"{len(sales)} registros"

        check_total([sale for sale in model["vendas"] if sale["data"].startswith("2026-10")])
        page.select_option("#category", "Tecnologia")
        page.select_option("#region", "Sudeste")
        selected = [sale for sale in model["vendas"] if sale["data"].startswith("2026-10") and sale["categoria"] == "Tecnologia" and sale["regiao"] == "Sudeste"]
        check_total(selected)
        results.append("Filtros combinados de período, categoria e região reconciliados com Python")

        page.fill("#search", "NENHUM-RESULTADO-XYZ")
        check_total([])
        assert page.locator("#export").is_disabled()
        assert "Nenhum pedido encontrado" in page.locator("#orders").inner_text()
        results.append("Estado vazio, zeragem dos indicadores e bloqueio de exportação vazia")

        page.click("#reset")
        check_total(model["vendas"])
        page.fill("#search", "luminaria")
        found = [sale for sale in model["vendas"] if sale["produto"] == "Luminária Horizonte"]
        check_total(found)
        results.append("Busca ignora acentos e limpar filtros recupera a base completa")

        page.click("#reset")
        page.click("#more")
        page.click("#more")
        assert page.locator("#orders tr").count() == 24
        page.select_option("#period", "2026-09")
        assert page.locator("#orders tr").count() == 8
        results.append("Cliques repetidos em mostrar mais e reinício da paginação ao filtrar")

        for trigger, exit_action in (("#method", "escape"), ("#quality-info", "button"), ("#method", "button")):
            history = page.evaluate("history.length")
            page.click(trigger)
            assert page.locator("#info").evaluate("element => element.open")
            if exit_action == "escape":
                page.keyboard.press("Escape")
            else:
                page.click("#close-info")
            assert not page.locator("#info").evaluate("element => element.open")
            assert page.evaluate("history.length") == history
            assert page.locator(trigger).evaluate("element => element === document.activeElement")
        results.append("Diálogo repetido, Escape, botão fechar, retorno de foco e histórico preservado")

        page.click("#reset")
        with page.expect_download() as event:
            page.click("#export")
        download = event.value
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / download.suggested_filename
            download.save_as(path)
            rows = list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")), delimiter=";"))
        assert len(rows) == 120
        assert len(rows) > page.locator("#orders tr").count()
        results.append("Download CSV com 120 registros, incluindo além das linhas visíveis")

        # Dados maliciosos são carregados em um relatório real e permanecem texto.
        malicious = '</script><img src=x onerror="window.XSS=1">'
        model["vendas"][0]["cliente"] = malicious
        model["vendas"][0]["produto"] = "=1+1"
        page.set_content(render_html(model))
        page.click("#reset")
        page.fill("#search", "window.XSS")
        assert page.locator("#orders tr").count() == 1
        assert malicious in page.locator("#orders").inner_text()
        assert page.locator("#orders img").count() == 0
        assert page.evaluate("typeof window.XSS") == "undefined"
        with page.expect_download() as event:
            page.click("#export")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "safe.csv"
            event.value.save_as(path)
            exported = list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")), delimiter=";"))
        assert exported[0]["produto"] == "'=1+1"
        results.append("Injeção HTML inerte e fórmula neutralizada no CSV baixado")

        page.goto(REPORT.as_uri())
        page.select_option("#period", "2026-10")
        for width in (320, 390, 768, 1440):
            page.set_viewport_size({"width": width, "height": 844})
            assert not page.evaluate("document.documentElement.scrollWidth > window.innerWidth"), f"Overflow em {width}px"
            assert page.locator("#export").is_visible()
            if width == 390:
                page.screenshot(path=str(SHOTS / "mobile.png"), full_page=True)
        results.append("Layout sem transbordamento horizontal em 320, 390, 768 e 1440 px")

        assert not errors, errors
        assert not external, external
        results.append("Zero erros JavaScript/CSP e zero requisições HTTP(S)")
        browser_version = browser.version
        browser.close()
    evidence = {"passed": len(results), "checks": results, "browser": browser_version, "javascript_errors": errors, "external_requests": external}
    (ROOT / "docs" / "browser-results.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
