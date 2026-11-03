#!/usr/bin/env python3
"""Diagnóstico sem instalação ou alteração das configurações do host."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile


PROFILES = {
    "dev": {"base", "dev"},
    "core": {"base", "dev", "core"},
    "analysis": {"base", "analysis"},
    "all": {"base", "dev", "core", "analysis"},
}
ANALYSIS_PACKAGES = ("numpy", "pandas", "scipy", "matplotlib")
CORE_INSTALL = "Consulte docs/AMBIENTE.md e a instalação oficial do CORE."


def execute(argv, timeout=15, cwd=None):
    """Nunca usa shell; captura ausência, permissão, timeout e retorno não zero."""
    try:
        result = subprocess.run(
            argv, capture_output=True, text=True, errors="replace",
            timeout=timeout, check=False, cwd=cwd,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, "{}: {}".format(type(exc).__name__, exc)
    output = (result.stdout + "\n" + result.stderr).strip()
    if result.returncode:
        return False, "exit={}: {}".format(result.returncode, output[:600])
    return True, output


def find_tool(name):
    found = shutil.which(name)
    if found:
        return found
    if name in ("core-daemon", "core-gui"):
        candidate = Path("/opt/core/venv/bin") / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def command_result(name, arguments, hint, expected=None):
    path = find_tool(name)
    if not path:
        return "missing", "{} não encontrado no ambiente atual".format(name), hint
    ok, output = execute([path] + list(arguments))
    if not ok:
        return "error", "{}: {}".format(name, output), hint
    if expected and expected not in output:
        return "error", "{}: implementação incompatível ({})".format(name, output[:160]), hint
    return "ok", "{}: {}".format(path, next(iter(output.splitlines()), "sem versão informada")), ""


def compiler_probe():
    compiler = find_tool("gcc")
    if not compiler:
        return "missing", "Teste C/POSIX não executado: GCC ausente", "Instale build-essential."
    source = r'''#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <sys/socket.h>
#include <time.h>
#include <stdlib.h>
#include <unistd.h>
static void *worker(void *p) { return p; }
int main(void) {
    struct timespec now;
    pthread_t thread;
    char path[] = "probe-XXXXXX";
    int file = mkstemp(path);
    if (file < 0) return 1;
    close(file); unlink(path);
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) return 2;
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return 3;
    close(fd);
    if (pthread_create(&thread, NULL, worker, NULL) != 0) return 4;
    return pthread_join(thread, NULL) == 0 ? 0 : 5;
}
'''
    try:
        with tempfile.TemporaryDirectory(prefix="redes-env-") as folder:
            code = Path(folder) / "probe.c"
            binary = Path(folder) / "probe"
            code.write_text(source, encoding="utf-8")
            ok, output = execute(
                [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-pthread",
                 str(code), "-o", str(binary)], timeout=30,
            )
            if ok:
                ok, output = execute([str(binary)], cwd=folder)
            if not ok:
                return "error", "Teste C/POSIX falhou: " + output, "Verifique headers, libc, pthreads e permissões de execução."
    except OSError as exc:
        return "error", "Teste C/POSIX: " + str(exc), "Verifique acesso à pasta temporária."
    return "ok", "Compilação e execução de sockets, pthreads, relógio monotônico e mkstemp", ""


def core_interpreter(explicit=None):
    if explicit:
        return shutil.which(explicit) or (explicit if Path(explicit).is_file() else None)
    daemon = find_tool("core-daemon")
    if daemon:
        try:
            with Path(daemon).open(encoding="utf-8") as stream:
                first = stream.readline(1024).strip()
            parts = shlex.split(first[2:]) if first.startswith("#!") else []
            if len(parts) == 1 and Path(parts[0]).is_file():
                return parts[0]
            if parts and Path(parts[0]).name == "env" and len(parts) == 2:
                return shutil.which(parts[1])
        except (OSError, UnicodeError, ValueError):
            pass
    candidate = Path("/opt/core/venv/bin/python")
    return str(candidate) if candidate.is_file() else sys.executable


def package_results():
    # Subprocesso: falhas de DLL/importação são diagnosticadas, não só instalação.
    code = """import importlib, json
results = []
for name in ['numpy', 'pandas', 'scipy', 'matplotlib']:
    try:
        module = importlib.import_module(name)
        results.append([name, True, str(getattr(module, '__version__', 'desconhecida'))])
    except Exception as exc:
        results.append([name, False, type(exc).__name__ + ': ' + str(exc)])
print(json.dumps(results))
"""
    ok, output = execute([sys.executable, "-c", code], timeout=45)
    try:
        records = json.loads(output) if ok else []
        if {r[0] for r in records} != set(ANALYSIS_PACKAGES):
            raise ValueError("resposta de importação incompleta")
    except (ValueError, TypeError, IndexError):
        return [("analysis-imports", "error", output[:600], "Verifique o ambiente Python de análise.")]
    return [
        (name, "ok" if imported else "error", "{}: {}".format(name, detail),
         "" if imported else "No venv ativo: python -m pip install -r analysis/requirements.txt")
        for name, imported, detail in records
    ]


def collect(profile, core_python=None, require_docker=False):
    enabled = PROFILES[profile]
    checks = []

    def add(key, group, status, message, hint="", required=True):
        checks.append(dict(key=key, group=group, required=required,
                           status=status, message=message, hint=hint))

    add("python", "base", "ok" if sys.version_info >= (3, 10) else "error",
        "{} ({})".format(platform.python_version(), sys.executable),
        "Use Python 3.10 ou superior." if sys.version_info < (3, 10) else "")
    add("git", "base", *command_result("git", ["--version"], "Instale Git no ambiente que executa este script."))
    ok, detail = execute([sys.executable, "-m", "pip", "--version"])
    add("python-pip", "base", "ok" if ok else "error", detail,
        "Disponibilize pip no Python atual ou crie/ative um venv." if not ok else "")
    ok, detail = execute([sys.executable, "-c", "import venv, ensurepip; print('venv e ensurepip disponíveis')"])
    add("python-venv", "base", "ok" if ok else "error", detail,
        "No Ubuntu, instale python3-venv." if not ok else "")

    linux = platform.system() == "Linux"
    if "dev" in enabled:
        add("linux", "dev", "ok" if linux else "error", platform.platform(),
            "Execute no Linux, WSL2 ou contêiner CORE; Git Bash não substitui o Linux." if not linux else "")
        for name, flags, hint, expected in [
            ("bash", ["--version"], "Instale bash.", None),
            ("gcc", ["--version"], "No Ubuntu: sudo apt install build-essential", None),
            ("make", ["--version"], "Instale GNU Make (build-essential no Ubuntu).", "GNU Make"),
            ("sha256sum", ["--version"], "Instale coreutils.", None),
        ]:
            add(name, "dev", *command_result(name, flags, hint, expected))
        if linux:
            add("c-posix", "dev", *compiler_probe())
        else:
            add("c-posix", "dev", "error", "Teste C/POSIX exige Linux", "Repita o diagnóstico no Linux de execução.")

    if "core" in enabled:
        version = re.match(r"(\d+)\.(\d+)", platform.release())
        kernel_ok = linux and version and tuple(map(int, version.groups())) >= (3, 3)
        add("linux-kernel", "core", "ok" if kernel_ok else "error",
            "Kernel: " + platform.release(), "CORE precisa de kernel Linux compatível.")
        add("network-namespaces", "core", "ok" if linux and Path("/proc/self/ns/net").exists() else "error",
            "Disponibilidade da interface de namespaces de rede; privilégios não testados", CORE_INSTALL)
        for name, flags, hint in [
            ("ip", ["-V"], "Instale iproute2."),
            ("tc", ["-V"], "Instale iproute2."),
            ("ss", ["--version"], "Instale iproute2."),
            ("nft", ["--version"], "Instale nftables."),
            ("ping", ["-V"], "Instale iputils-ping."),
            ("traceroute", ["--version"], "Instale traceroute."),
            ("iperf3", ["--version"], "Instale iperf3; iperf2 não é substituto deste roteiro."),
            ("sysctl", ["--version"], "Instale procps."),
            ("top", ["-V"], "Instale procps."),
            ("vmstat", ["-V"], "Instale procps."),
            ("dd", ["--version"], "Instale coreutils."),
            ("cp", ["--version"], "Instale coreutils."),
        ]:
            status, message, remedy = command_result(name, flags, hint)
            if status == "ok" and name in ("ip", "tc"):
                match = re.search(r"iproute2[- ](\d+)\.(\d+)", message)
                if not match or tuple(map(int, match.groups())) < (4, 5):
                    status, remedy = "error", "Confirme iproute2 >= 4.5; versão não reconhecida ou antiga."
            add(name, "core", status, message, remedy)
        for name in ("core-daemon", "core-gui"):
            path = find_tool(name)
            add(name, "core", "ok" if path else "missing", path or name + " ausente", CORE_INSTALL if not path else "")
        interpreter = core_interpreter(core_python)
        if not interpreter:
            add("core-python", "core", "missing", "Interpretador CORE não encontrado", "Informe --core-python /caminho/python.")
        else:
            code = ("import sys\n"
                    "if sys.version_info < (3,10): raise SystemExit('CORE requer Python >= 3.10')\n"
                    "from core.emulator.coreemu import CoreEmu\n"
                    "import tkinter\n"
                    "print('CORE importável; Tcl ' + tkinter.Tcl().eval('info patchlevel'))\n")
            ok, detail = execute([interpreter, "-c", code])
            add("core-python", "core", "ok" if ok else "error", str(interpreter) + ": " + detail[:600],
                "Use --core-python para o Python do CORE; confira CORE e Tcl/Tk." if not ok else "")
        add("core-runtime", "core", "warning",
            "Pendente: criar sessão CORE, abrir nós, testar rotas, tc e tráfego nos dois sentidos.",
            "Ferramentas instaladas não provam permissões, GUI, forwarding ou calibração.", required=False)

    if "analysis" in enabled:
        for key, status, detail, hint in package_results():
            add(key, "analysis", status, detail, hint)

    if require_docker:
        add("docker-runtime", "runtime", *command_result(
            "docker", ["version", "--format", "{{.Server.Version}}"],
            "Instale/inicie Docker e verifique acesso ao daemon; no Windows, confira a integração WSL.",
        ))
    for name in ("docker", "vagrant", "VBoxManage", "curl"):
        path = find_tool(name)
        add(name, "optional", "ok" if path else "skipped",
            (path + " (somente localização; funcionamento não testado)") if path else "Não encontrado; depende da rota de instalação",
            required=False)
    return checks


def passed(checks):
    return all(not check["required"] or check["status"] == "ok" for check in checks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=PROFILES, default="all")
    parser.add_argument("--core-python", help="Python que contém o CORE (pode ser um venv separado)")
    parser.add_argument("--require-docker", action="store_true", help="Exige também cliente Docker e acesso ao daemon")
    parser.add_argument("--json", type=Path, help="Grava relatório local; não contém medições experimentais")
    args = parser.parse_args(argv)
    checks = collect(args.profile, args.core_python, args.require_docker)
    ready = passed(checks)
    labels = {"ok": "OK", "missing": "FALTA", "error": "ERRO", "warning": "AVISO", "skipped": "OPCIONAL"}
    print("Verificação de ferramentas: perfil {}\n".format(args.profile))
    for check in checks:
        print("[{}] {}: {}".format(labels[check["status"]], check["key"], check["message"]))
        if check["hint"] and check["status"] != "ok":
            print("  " + check["hint"])
    report = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),
                  profile=args.profile, system=platform.system(), python=sys.executable,
                  tools_ready=ready, core_runtime_validated=False, checks=checks)
    if args.json:
        try:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            print("ERRO ao gravar relatório: " + str(exc), file=sys.stderr)
            return 2
        print("\nRelatório local: " + str(args.json))
    print("\n" + ("Ferramentas do perfil disponíveis." if ready else "Existem ferramentas obrigatórias ausentes, incompatíveis ou sem execução permitida."))
    print("Nenhuma ferramenta foi instalada. A validação funcional do CORE continua separada.")
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
