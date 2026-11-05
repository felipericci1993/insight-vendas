"""Interface de linha de comando: python -m insight_vendas arquivo.csv."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .core import FIELDS, InputError, load_csv, normalized_rows, payload, safe_cell
from .report import render_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Transforma um CSV de vendas em um painel HTML offline. Projeto demonstrativo.")
    parser.add_argument("arquivo", type=Path, help="CSV UTF-8, separado por ponto e vírgula")
    parser.add_argument("--output", type=Path, default=Path("dist"), help="pasta de saída (padrão: dist)")
    parser.add_argument("--strict", action="store_true", help="não gera arquivos se alguma linha for rejeitada")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    try:
        dataset = load_csv(args.arquivo)
        if args.strict and dataset.issues:
            raise InputError(f"Modo estrito: {len(dataset.issues)} registro(s) inválido(s). Primeiro problema na linha {dataset.issues[0].linha}: {dataset.issues[0].motivo}")
        # Toda validação e renderização acontece antes de escrever a saída.
        data = payload(dataset)
        report = render_html(data)
        filenames = ("index.html", "resumo.json", "vendas_tratadas.csv", "erros.csv")
        for filename in filenames:
            destination = args.output / filename
            if destination.resolve() == args.arquivo.resolve():
                raise InputError("A pasta de saída substituiria o arquivo de entrada. Escolha outra pasta.")
            if destination.is_symlink() or (destination.exists() and not destination.is_file()):
                raise InputError(f"Destino não é um arquivo regular: {destination}")
        args.output.mkdir(parents=True, exist_ok=True)
        # Uma falha de gravação na preparação não altera relatórios existentes.
        # As substituições finais são atômicas por arquivo, não por conjunto.
        with tempfile.TemporaryDirectory(prefix=".insight-", dir=args.output) as temporary:
            staging = Path(temporary)
            (staging / "index.html").write_text(report, encoding="utf-8")
            (staging / "resumo.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            with (staging / "vendas_tratadas.csv").open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle, delimiter=";")
                writer.writerow((*FIELDS, "total_liquido"))
                writer.writerows([safe_cell(value) for value in row] for row in normalized_rows(dataset))
            with (staging / "erros.csv").open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.writer(handle, delimiter=";")
                writer.writerow(("linha", "pedido_id", "motivo"))
                writer.writerows([safe_cell(value) for value in asdict(issue).values()] for issue in dataset.issues)
            for filename in filenames:
                os.replace(staging / filename, args.output / filename)
    except (InputError, OSError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    print(f"Pronto: {len(dataset.sales)} registro(s) válido(s), {len(dataset.issues)} rejeitado(s).")
    print(f"Abra {args.output / 'index.html'} no navegador. Todos os dados permanecem locais.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
