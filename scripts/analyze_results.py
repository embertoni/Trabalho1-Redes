#!/usr/bin/env python3
"""Consolida experiments/raw/json em tabelas, relatório e gráficos.

A unidade experimental é scenario_id + repetition. Os workers concorrentes
são preservados em dados individuais e agregados por rodada.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any


def read_jsons(root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(root.glob("S*.json")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) != 1:
            raise ValueError(f"{path}: esperado 1 JSON por arquivo")
        data = json.loads(lines[0])
        data["_file"] = str(path)
        result = data.get("client_result", {})
        data["status"] = result.get("status", "error")
        data["status_code"] = result.get("status_code", 0)
        data["elapsed_ms"] = result.get("elapsed_ms")
        data["throughput_mbps"] = result.get("throughput_mbps")
        data["bytes"] = result.get("bytes", 0)
        records.append(data)
    return records


def ci95(values: list[float]) -> float | None:
    n = len(values)
    if n < 2:
        return None
    return 1.96 * stdev(values) / math.sqrt(n)


def clean_num(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def aggregate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for record in records:
        key = (str(record["scenario_id"]), int(record["repetition"]))
        groups.setdefault(key, []).append(record)

    rows = []
    for (scenario, repetition), items in sorted(groups.items()):
        first = items[0]
        ok_items = [item for item in items if item["status"] == "ok"]
        times = [clean_num(item["elapsed_ms"]) for item in ok_items]
        times = [value for value in times if value is not None]
        throughputs = [clean_num(item["throughput_mbps"]) for item in ok_items]
        throughputs = [value for value in throughputs if value is not None]
        bytes_values = [int(item.get("bytes", 0) or 0) for item in ok_items]
        rows.append({
            "scenario_id": scenario,
            "profile": first.get("profile"),
            "bandwidth_mbps": first.get("bandwidth_mbps"),
            "delay_oneway_ms": first.get("delay_oneway_ms"),
            "operation": first.get("client_result", {}).get("method", ""),
            "workload": first.get("workload"),
            "file_size_bytes": first.get("file_size_bytes"),
            "concurrency": first.get("concurrency"),
            "repetition": repetition,
            "workers_expected": int(first.get("concurrency", len(items))),
            "workers_observed": len(items),
            "workers_ok": len(ok_items),
            "workers_failed": len(items) - len(ok_items),
            "round_status": "ok" if items and len(ok_items) == len(items) else "partial_or_failed",
            "time_mean_ms": mean(times) if times else None,
            "time_median_ms": median(times) if times else None,
            "time_min_ms": min(times) if times else None,
            "time_max_ms": max(times) if times else None,
            "time_ci95_ms": ci95(times),
            "throughput_mean_mbps": mean(throughputs) if throughputs else None,
            "throughput_median_mbps": median(throughputs) if throughputs else None,
            "throughput_ci95_mbps": ci95(throughputs),
            "throughput_aggregate_mbps": sum(throughputs) if throughputs else None,
            "bytes_ok": sum(bytes_values),
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from collections import defaultdict
    groups = defaultdict(list)
    for row in rows:
        key = (
            row["profile"], row["bandwidth_mbps"], row["delay_oneway_ms"],
            row["operation"], row["workload"], row["file_size_bytes"],
            row["concurrency"],
        )
        groups[key].append(row)

    output = []
    for key, items in sorted(groups.items(), key=lambda pair: str(pair[0])):
        times = [row["time_mean_ms"] for row in items if row["time_mean_ms"] is not None]
        rates = [row["throughput_mean_mbps"] for row in items if row["throughput_mean_mbps"] is not None]
        output.append({
            "profile": key[0], "bandwidth_mbps": key[1],
            "delay_oneway_ms": key[2], "operation": key[3],
            "workload": key[4], "file_size_bytes": key[5],
            "concurrency": key[6], "repetitions": len(items),
            "valid_rounds": sum(row["round_status"] == "ok" for row in items),
            "failed_or_partial_rounds": sum(row["round_status"] != "ok" for row in items),
            "time_mean_ms": mean(times) if times else None,
            "time_median_ms": median(times) if times else None,
            "time_ci95_ms": ci95(times),
            "throughput_mean_mbps": mean(rates) if rates else None,
            "throughput_median_mbps": median(rates) if rates else None,
            "throughput_ci95_mbps": ci95(rates),
        })
    return output


def write_report(path: Path, records: list[dict[str, Any]], rounds: list[dict[str, Any]], cells: list[dict[str, Any]]) -> None:
    ok = sum(record["status"] == "ok" for record in records)
    failed = len(records) - ok
    lines = [
        "# Relatório inicial da campanha experimental", "",
        "## Escopo", "",
        "Os dados foram consolidados a partir de `experiments/raw/json`. A unidade estatística usada nas comparações é a rodada `(scenario_id, repetition)`; workers concorrentes não são contados como repetições independentes.", "",
        "## Cobertura", "",
        f"- Observações individuais: {len(records)}",
        f"- Observações individuais válidas: {ok}",
        f"- Observações individuais com falha: {failed}",
        f"- Rodadas agregadas: {len(rounds)}",
        f"- Células da matriz: {len(cells)}", "",
        "## Interpretação", "",
        "`time_mean_ms` e `throughput_mean_mbps` são médias dos workers bem-sucedidos da rodada. `throughput_aggregate_mbps` é a soma das vazões individuais e deve ser usada separadamente para discutir saturação. HEAD é mantido na tabela, mas sua vazão de conteúdo é não aplicável.", "",
        "## Arquivos gerados", "",
        "- `analysis/data/individual.csv`: uma linha por worker.",
        "- `analysis/data/rounds.csv`: uma linha por rodada independente.",
        "- `analysis/tables/cells.csv`: estatísticas por célula da matriz.",
        "- `analysis/reports/analysis_report.md`: este relatório.",
        "- `analysis/figures/`: gráficos gerados, quando matplotlib estiver disponível.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_figures(cells: list[dict[str, Any]], figure_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Aviso: matplotlib não instalado; gráficos não foram gerados.")
        return
    figure_dir.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[dict[str, Any]]] = {}
    for cell in cells:
        key = f"{cell['operation']} | {cell['file_size_bytes']} B"
        groups.setdefault(key, []).append(cell)
    for title, items in groups.items():
        plt.figure(figsize=(9, 5))
        for profile in ("A", "B"):
            subset = [item for item in items if item["profile"] == profile and item["throughput_mean_mbps"] is not None]
            subset.sort(key=lambda item: int(item["concurrency"]))
            if subset:
                x = [int(item["concurrency"]) for item in subset]
                y = [float(item["throughput_mean_mbps"]) for item in subset]
                plt.plot(x, y, marker="o", label=f"Perfil {profile}")
        plt.title(f"Vazão média por concorrência — {title}")
        plt.xlabel("Concorrência")
        plt.ylabel("Vazão média individual (Mbit/s)")
        plt.xticks([1, 8, 32])
        plt.grid(True, alpha=0.3)
        plt.legend()
        filename = "throughput_" + "_".join(title.lower().replace("|", "").split()) + ".png"
        plt.tight_layout()
        plt.savefig(figure_dir / filename, dpi=160)
        plt.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=Path("experiments/raw/json"))
    parser.add_argument("--out", type=Path, default=Path("analysis"))
    args = parser.parse_args()
    records = read_jsons(args.raw)
    if not records:
        raise SystemExit(f"nenhum JSON encontrado em {args.raw}")
    rounds = aggregate(records)
    cells = summary(rounds)
    write_csv(args.out / "data/individual.csv", records)
    write_csv(args.out / "data/rounds.csv", rounds)
    write_csv(args.out / "tables/cells.csv", cells)
    write_report(args.out / "reports/analysis_report.md", records, rounds, cells)
    make_figures(cells, args.out / "figures")
    print(f"observações individuais: {len(records)}")
    print(f"rodadas agregadas: {len(rounds)}")
    print(f"células resumidas: {len(cells)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
