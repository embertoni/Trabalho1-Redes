#!/usr/bin/env python3
"""Executa a matriz experimental do Trabalho 1 dentro do nó Cliente.

O script não troca a topologia CORE. O operador deve abrir o perfil correto
(A ou B), iniciar o servidor no nó Servidor e então executar este programa no
nó Cliente.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


EXPECTED_COLUMNS = {
    "scenario_id",
    "profile",
    "bandwidth_mbps",
    "delay_oneway_ms",
    "operation",
    "workload",
    "file_size_bytes",
    "concurrency",
    "repetitions",
}


class CampaignError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe_name(value: str) -> str:
    return "".join(
        char if char.isalnum() or char in "._-" else "_"
        for char in value
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_plan(path: Path, profile: str | None) -> list[dict[str, str]]:
    if not path.is_file():
        raise CampaignError(f"matriz inexistente: {path}")

    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns = set(reader.fieldnames or [])
        missing = EXPECTED_COLUMNS - columns
        if missing:
            raise CampaignError(
                "colunas ausentes na matriz: " + ", ".join(sorted(missing))
            )

        rows = []
        for row in reader:
            if profile is None or row["profile"] == profile:
                rows.append(row)

    return rows


def check_row(row: dict[str, str]) -> None:
    if row["operation"] not in {"GET", "PUT", "HEAD"}:
        raise CampaignError(f"operação inválida em {row['scenario_id']}")

    for field in ("file_size_bytes", "concurrency", "repetitions"):
        try:
            value = int(row[field])
        except ValueError as exc:
            raise CampaignError(
                f"{field} inválido em {row['scenario_id']}"
            ) from exc
        if value <= 0:
            raise CampaignError(f"{field} não positivo em {row['scenario_id']}")


def workload_path(input_dir: Path, row: dict[str, str]) -> Path:
    size = int(row["file_size_bytes"])
    if size == 2 * 1024 * 1024:
        return input_dir / "workload-2MiB.bin"
    if size == 10 * 1024 * 1024:
        return input_dir / "workload-10MiB.bin"
    raise CampaignError(
        f"tamanho sem arquivo de carga conhecido: {size} em {row['scenario_id']}"
    )


def expected_bytes(row: dict[str, str]) -> int:
    return int(row["file_size_bytes"]) if row["operation"] != "HEAD" else 0


def run_one(
    *,
    row: dict[str, str],
    repeat: int,
    worker: int,
    client_bin: Path,
    server_host: str,
    server_port: int,
    input_file: Path,
    raw_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    scenario = safe_name(row["scenario_id"])
    operation = row["operation"]
    identifier = f"{scenario}-r{repeat:02d}-w{worker:02d}"
    json_dir = raw_root / "json"
    log_dir = raw_root / "logs"
    hash_dir = raw_root / "hashes"
    output_dir = output_root / scenario / f"r{repeat:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    hash_dir.mkdir(parents=True, exist_ok=True)

    json_path = json_dir / f"{identifier}.json"
    log_path = log_dir / f"{identifier}.log"
    output_path = output_dir / f"{identifier}.bin"

    if operation == "PUT":
        remote = f"/campaign-{identifier}.bin"
    else:
        remote = f"/workload-{'2MiB' if int(row['file_size_bytes']) == 2 * 1024 * 1024 else '10MiB'}.bin"

    command = [
        str(client_bin),
        "--host", server_host,
        "--port", str(server_port),
        "--method", operation,
        "--remote", remote,
        "--io-timeout", "60",
    ]

    if operation == "PUT":
        command += ["--input", str(input_file)]
    elif operation == "GET":
        command += ["--output", str(output_path)]

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        elapsed_process = time.monotonic() - started
    except OSError as exc:
        completed = None
        elapsed_process = time.monotonic() - started
        stdout = ""
        stderr = f"execução falhou: {exc}\n"
        return write_failure(
            row, repeat, worker, identifier, command, stdout, stderr,
            elapsed_process, json_path, log_path, hash_dir, input_file,
        )

    stdout = completed.stdout.strip()
    stderr = completed.stderr
    lines = stdout.splitlines()
    parsed: dict[str, Any] | None = None
    parse_error = None

    if len(lines) == 1:
        try:
            candidate = json.loads(lines[0])
            if isinstance(candidate, dict):
                parsed = candidate
            else:
                parse_error = "saída JSON não é objeto"
        except json.JSONDecodeError as exc:
            parse_error = f"JSON inválido: {exc}"
    else:
        parse_error = f"esperada uma linha JSON, obtidas {len(lines)}"

    if parsed is None:
        parsed = {
            "status": "error",
            "method": operation,
            "remote": remote,
            "status_code": 0,
            "bytes": 0,
            "elapsed_ms": round(elapsed_process * 1000.0, 3),
            "throughput_mbps": None,
            "error": "invalid_client_output",
        }

    metadata = {
        "scenario_id": row["scenario_id"],
        "profile": row["profile"],
        "bandwidth_mbps": int(row["bandwidth_mbps"]),
        "delay_oneway_ms": int(row["delay_oneway_ms"]),
        "workload": row["workload"],
        "file_size_bytes": int(row["file_size_bytes"]),
        "concurrency": int(row["concurrency"]),
        "repetition": repeat,
        "worker": worker,
        "identifier": identifier,
        "started_utc": utc_now(),
        "client_exit_code": completed.returncode,
        "command": command,
        "client_result": parsed,
    }

    if parse_error:
        metadata["collector_error"] = parse_error

    json_path.write_text(
        json.dumps(metadata, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    log_path.write_text(
        "COMMAND: " + " ".join(command) + "\n"
        + "STDOUT:\n" + completed.stdout
        + "STDERR:\n" + stderr,
        encoding="utf-8",
    )

    hash_lines = []
    if input_file.is_file():
        hash_lines.append(f"input {sha256_file(input_file)} {input_file}")
    if operation == "GET" and output_path.is_file():
        hash_lines.append(f"output {sha256_file(output_path)} {output_path}")
    (hash_dir / f"{identifier}.sha256").write_text(
        "\n".join(hash_lines) + ("\n" if hash_lines else ""),
        encoding="utf-8",
    )

    return metadata


def write_failure(
    row: dict[str, str], repeat: int, worker: int, identifier: str,
    command: list[str], stdout: str, stderr: str, elapsed: float,
    json_path: Path, log_path: Path, hash_dir: Path, input_file: Path,
) -> dict[str, Any]:
    result = {
        "scenario_id": row["scenario_id"],
        "profile": row["profile"],
        "file_size_bytes": int(row["file_size_bytes"]),
        "concurrency": int(row["concurrency"]),
        "repetition": repeat,
        "worker": worker,
        "identifier": identifier,
        "client_exit_code": None,
        "command": command,
        "client_result": {
            "status": "error",
            "method": row["operation"],
            "remote": None,
            "status_code": 0,
            "bytes": 0,
            "elapsed_ms": round(elapsed * 1000.0, 3),
            "throughput_mbps": None,
            "error": "client_exec_failed",
        },
        "collector_error": stderr.strip(),
    }
    json_path.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    log_path.write_text(
        "COMMAND: " + " ".join(command) + "\n"
        + "STDOUT:\n" + stdout + "\nSTDERR:\n" + stderr,
        encoding="utf-8",
    )
    if input_file.is_file():
        (hash_dir / f"{identifier}.sha256").write_text(
            f"input {sha256_file(input_file)} {input_file}\n",
            encoding="utf-8",
        )
    return result


def execute_row(
    row: dict[str, str],
    *,
    client_bin: Path,
    server_host: str,
    server_port: int,
    input_dir: Path,
    raw_root: Path,
    output_root: Path,
    repetitions_override: int | None,
) -> list[dict[str, Any]]:
    check_row(row)
    input_file = workload_path(input_dir, row)
    if not input_file.is_file():
        raise CampaignError(f"arquivo de carga inexistente: {input_file}")
    if input_file.stat().st_size != int(row["file_size_bytes"]):
        raise CampaignError(
            f"tamanho incorreto de {input_file}: "
            f"{input_file.stat().st_size} != {row['file_size_bytes']}"
        )

    repetitions = repetitions_override or int(row["repetitions"])
    concurrency = int(row["concurrency"])
    results: list[dict[str, Any]] = []

    for repeat in range(1, repetitions + 1):
        print(
            f"[{utc_now()}] {row['scenario_id']} "
            f"repetição {repeat}/{repetitions} "
            f"op={row['operation']} c={concurrency}",
            flush=True,
        )
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [
                pool.submit(
                    run_one,
                    row=row,
                    repeat=repeat,
                    worker=worker,
                    client_bin=client_bin,
                    server_host=server_host,
                    server_port=server_port,
                    input_file=input_file,
                    raw_root=raw_root,
                    output_root=output_root,
                )
                for worker in range(1, concurrency + 1)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        write_manifest(row, repeat, raw_root)

    return results


def write_manifest(row: dict[str, str], repeat: int, raw_root: Path) -> None:
    manifest_dir = raw_root / "manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / f"{safe_name(row['scenario_id'])}-r{repeat:02d}.txt"
    path.write_text(
        "scenario_id=" + row["scenario_id"] + "\n"
        + "profile=" + row["profile"] + "\n"
        + "bandwidth_mbps=" + row["bandwidth_mbps"] + "\n"
        + "delay_oneway_ms=" + row["delay_oneway_ms"] + "\n"
        + "operation=" + row["operation"] + "\n"
        + "workload=" + row["workload"] + "\n"
        + "file_size_bytes=" + row["file_size_bytes"] + "\n"
        + "concurrency=" + row["concurrency"] + "\n"
        + "repetition=" + str(repeat) + "\n"
        + "collected_utc=" + utc_now() + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=Path("configs/experiment_plan.csv"))
    parser.add_argument("--profile", choices=["A", "B"], required=True)
    parser.add_argument("--scenario", help="executa somente este scenario_id")
    parser.add_argument("--max-scenarios", type=int)
    parser.add_argument("--repetitions", type=int, help="sobrescreve repetições; use 1 no piloto")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--client", type=Path, default=Path("build/client"))
    parser.add_argument("--server-host", default="10.10.5.10")
    parser.add_argument("--server-port", type=int, default=9000)
    parser.add_argument("--input-dir", type=Path, default=Path("/tmp/trabalho1-core/client-data"))
    parser.add_argument("--raw-root", type=Path, default=Path("experiments/raw"))
    parser.add_argument("--output-root", type=Path, default=Path("/tmp/trabalho1-core/client-output/campaign"))
    args = parser.parse_args()

    if args.repetitions is not None and args.repetitions <= 0:
        parser.error("--repetitions deve ser positivo")
    if args.max_scenarios is not None and args.max_scenarios <= 0:
        parser.error("--max-scenarios deve ser positivo")
    if not args.client.is_file() and not args.dry_run:
        raise CampaignError(f"cliente inexistente: {args.client}")

    rows = load_plan(args.plan, args.profile)
    if args.scenario:
        rows = [row for row in rows if row["scenario_id"] == args.scenario]
    if args.max_scenarios:
        rows = rows[:args.max_scenarios]
    if not rows:
        raise CampaignError("nenhum cenário selecionado")

    for row in rows:
        check_row(row)
        print(
            f"PLANO {row['scenario_id']}: perfil={row['profile']} "
            f"op={row['operation']} tamanho={row['file_size_bytes']} "
            f"concorrência={row['concurrency']} "
            f"repetições={args.repetitions or row['repetitions']}",
        )

    if args.dry_run:
        print(f"cenários selecionados: {len(rows)}")
        return 0

    args.raw_root.mkdir(parents=True, exist_ok=True)
    args.output_root.mkdir(parents=True, exist_ok=True)
    all_results: list[dict[str, Any]] = []

    for row in rows:
        try:
            results = execute_row(
                row,
                client_bin=args.client,
                server_host=args.server_host,
                server_port=args.server_port,
                input_dir=args.input_dir,
                raw_root=args.raw_root,
                output_root=args.output_root,
                repetitions_override=args.repetitions,
            )
            all_results.extend(results)
        except Exception as exc:
            print(
                f"ERRO no cenário {row['scenario_id']}: {exc}",
                file=sys.stderr,
            )
            return 2

    summary = {
        "profile": args.profile,
        "scenarios": len(rows),
        "observations": len(all_results),
        "successful": sum(
            1 for item in all_results
            if item.get("client_result", {}).get("status") == "ok"
        ),
        "failed": sum(
            1 for item in all_results
            if item.get("client_result", {}).get("status") != "ok"
        ),
        "finished_utc": utc_now(),
    }
    (args.raw_root / f"summary-profile-{args.profile}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CampaignError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(2)
