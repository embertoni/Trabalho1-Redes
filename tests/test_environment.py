"""Testes do diagnóstico; subprocessos/ferramentas simulados não são medições."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import check_environment as env


class CommandTests(unittest.TestCase):
    def test_missing_command(self):
        with patch.object(env, "find_tool", return_value=None):
            self.assertEqual(env.command_result("gcc", ["--version"], "install")[0], "missing")

    def test_broken_command_does_not_pass(self):
        with patch.object(env, "find_tool", return_value="/fake/gcc"), \
             patch.object(env, "execute", return_value=(False, "permission denied")):
            self.assertEqual(env.command_result("gcc", ["--version"], "install")[0], "error")

    def test_non_gnu_make_does_not_pass(self):
        with patch.object(env, "find_tool", return_value="/fake/make"), \
             patch.object(env, "execute", return_value=(True, "BSD Make")):
            result = env.command_result("make", ["--version"], "GNU Make", "GNU Make")
            self.assertEqual(result[0], "error")

    def test_working_command(self):
        with patch.object(env, "find_tool", return_value="/fake/make"), \
             patch.object(env, "execute", return_value=(True, "GNU Make 4.3\nmore")):
            result = env.command_result("make", ["--version"], "GNU Make", "GNU Make")
            self.assertEqual(result[0], "ok")
            self.assertIn("4.3", result[1])

    def test_subprocess_missing_executable(self):
        with patch.object(env.subprocess, "run", side_effect=FileNotFoundError("missing")):
            self.assertFalse(env.execute(["missing"])[0])

    def test_subprocess_timeout(self):
        with patch.object(env.subprocess, "run", side_effect=subprocess.TimeoutExpired(["slow"], 15)):
            ok, message = env.execute(["slow"])
            self.assertFalse(ok)
            self.assertIn("TimeoutExpired", message)

    def test_nonzero_exit_and_stderr_are_preserved(self):
        result = subprocess.CompletedProcess(["broken"], 7, "", "bad runtime")
        with patch.object(env.subprocess, "run", return_value=result):
            ok, detail = env.execute(["broken"])
            self.assertFalse(ok)
            self.assertIn("exit=7", detail)
            self.assertIn("bad runtime", detail)

    def test_arguments_not_sent_to_shell(self):
        result = subprocess.CompletedProcess(["/path with spaces/tool"], 0, "ok", "")
        with patch.object(env.subprocess, "run", return_value=result) as run:
            self.assertTrue(env.execute(["/path with spaces/tool", "literal;argument"])[0])
            self.assertEqual(run.call_args.args[0], ["/path with spaces/tool", "literal;argument"])
            self.assertFalse(run.call_args.kwargs.get("shell", False))


class CompilerTests(unittest.TestCase):
    def test_no_compiler(self):
        with patch.object(env, "find_tool", return_value=None):
            self.assertEqual(env.compiler_probe()[0], "missing")

    def test_compile_failure_prevents_binary_execution(self):
        with patch.object(env, "find_tool", return_value="/fake/gcc"), \
             patch.object(env, "execute", return_value=(False, "pthread header missing")) as execute:
            result = env.compiler_probe()
            self.assertEqual(result[0], "error")
            self.assertEqual(execute.call_count, 1)

    def test_compiled_but_not_runnable_is_failure(self):
        with patch.object(env, "find_tool", return_value="/fake/gcc"), \
             patch.object(env, "execute", side_effect=[(True, ""), (False, "noexec")]):
            self.assertEqual(env.compiler_probe()[0], "error")

    def test_success_requires_compile_and_run(self):
        with patch.object(env, "find_tool", return_value="/fake/gcc"), \
             patch.object(env, "execute", return_value=(True, "")) as execute:
            self.assertEqual(env.compiler_probe()[0], "ok")
            self.assertEqual(execute.call_count, 2)


class ProfileTests(unittest.TestCase):
    def core_checks(self, ip_version="6.1.0", missing_gui=False):
        def command(name, *_args):
            return "ok", "iproute2-" + ip_version if name in ("ip", "tc") else "tool 1.0", ""

        def find(name):
            return None if missing_gui and name == "core-gui" else "/fake/" + name

        with patch.object(env.platform, "system", return_value="Linux"), \
             patch.object(env.platform, "release", return_value="6.1.0"), \
             patch.object(env, "execute", return_value=(True, "ok")), \
             patch.object(env, "command_result", side_effect=command), \
             patch.object(env, "find_tool", side_effect=find), \
             patch.object(env, "core_interpreter", return_value="/fake/python"), \
             patch.object(env.Path, "exists", return_value=True), \
             patch.object(env, "compiler_probe", return_value=("ok", "compiled and ran", "")):
            return env.collect("core")

    def test_core_complete_tools_keep_functional_runtime_pending(self):
        checks = self.core_checks()
        self.assertTrue(env.passed(checks))
        runtime = next(r for r in checks if r["key"] == "core-runtime")
        self.assertEqual(runtime["status"], "warning")
        self.assertFalse(runtime["required"])

    def test_old_iproute2_prevents_core_approval(self):
        self.assertFalse(env.passed(self.core_checks(ip_version="4.4.0")))

    def test_unknown_iproute2_version_requires_inspection(self):
        self.assertFalse(env.passed(self.core_checks(ip_version="unknown")))

    def test_missing_core_gui_prevents_approval(self):
        self.assertFalse(env.passed(self.core_checks(missing_gui=True)))

    def test_required_failure_controls_exit_even_if_optional_passes(self):
        self.assertFalse(env.passed([
            dict(required=True, status="missing"),
            dict(required=False, status="ok"),
        ]))

    def test_optional_warning_is_not_installation_failure(self):
        self.assertTrue(env.passed([
            dict(required=True, status="ok"),
            dict(required=False, status="warning"),
            dict(required=False, status="skipped"),
        ]))

    def test_analysis_on_windows_does_not_require_linux_or_compiler(self):
        with patch.object(env.platform, "system", return_value="Windows"), \
             patch.object(env, "execute", return_value=(True, "ok")), \
             patch.object(env, "command_result", return_value=("ok", "git", "")), \
             patch.object(env, "find_tool", return_value=None), \
             patch.object(env, "package_results", return_value=[("scipy", "ok", "available", "")]), \
             patch.object(env, "compiler_probe") as compiler:
            checks = env.collect("analysis")
            self.assertTrue(env.passed(checks))
            self.assertNotIn("linux", [r["key"] for r in checks])
            compiler.assert_not_called()

    def test_windows_dev_cannot_pass_with_native_tools(self):
        with patch.object(env.platform, "system", return_value="Windows"), \
             patch.object(env, "execute", return_value=(True, "ok")), \
             patch.object(env, "command_result", return_value=("ok", "tool", "")), \
             patch.object(env, "find_tool", return_value=None), \
             patch.object(env, "compiler_probe") as compiler:
            checks = env.collect("dev")
            self.assertFalse(env.passed(checks))
            compiler.assert_not_called()

    def test_dev_does_not_require_core_or_analysis(self):
        with patch.object(env.platform, "system", return_value="Linux"), \
             patch.object(env, "execute", return_value=(True, "ok")), \
             patch.object(env, "command_result", return_value=("ok", "tool", "")), \
             patch.object(env, "find_tool", return_value=None), \
             patch.object(env, "compiler_probe", return_value=("ok", "compiled and ran", "")), \
             patch.object(env, "package_results") as packages:
            checks = env.collect("dev")
            self.assertTrue(env.passed(checks))
            self.assertNotIn("core-daemon", [r["key"] for r in checks])
            packages.assert_not_called()

    def test_docker_daemon_failure_is_required_only_when_selected(self):
        def command(name, *_args):
            return ("error", "daemon unavailable", "start Docker") if name == "docker" else ("ok", "tool", "")

        with patch.object(env.platform, "system", return_value="Linux"), \
             patch.object(env, "execute", return_value=(True, "ok")), \
             patch.object(env, "command_result", side_effect=command), \
             patch.object(env, "find_tool", return_value=None), \
             patch.object(env, "compiler_probe", return_value=("ok", "ran", "")):
            self.assertTrue(env.passed(env.collect("dev")))
            self.assertFalse(env.passed(env.collect("dev", require_docker=True)))


class ImportsAndReportTests(unittest.TestCase):
    def test_unwritable_report_exits_two(self):
        checks = [dict(key="tool", group="base", required=True, status="ok", message="ok", hint="")]
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(env, "collect", return_value=checks), \
             patch.object(env.Path, "write_text", side_effect=PermissionError("denied")), \
             redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(env.main(["--json", str(Path(folder) / "report.json")]), 2)

    def test_broken_package_import_not_just_missing_metadata(self):
        values = [[name, name != "scipy", "DLL failed" if name == "scipy" else "1.0"]
                  for name in env.ANALYSIS_PACKAGES]
        with patch.object(env, "execute", return_value=(True, json.dumps(values))):
            results = {row[0]: row[1] for row in env.package_results()}
            self.assertEqual(results["scipy"], "error")
            self.assertEqual(results["numpy"], "ok")

    def test_incomplete_import_report_is_error(self):
        with patch.object(env, "execute", return_value=(True, "[]")):
            self.assertEqual(env.package_results()[0][1], "error")

    def test_explicit_core_python_is_used(self):
        with patch.object(env.shutil, "which", return_value="/other/venv/python"):
            self.assertEqual(env.core_interpreter("python-special"), "/other/venv/python")

    def test_cli_defaults_to_all_and_never_claims_core_validated(self):
        checks = [dict(key="tool", group="base", required=True, status="ok", message="ok", hint="")]
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(env, "collect", return_value=checks) as collect, \
             redirect_stdout(io.StringIO()):
            target = Path(folder) / "environment.json"
            self.assertEqual(env.main(["--json", str(target)]), 0)
            collect.assert_called_once_with("all", None, False)
            report = json.loads(target.read_text(encoding="utf-8"))
            self.assertTrue(report["tools_ready"])
            self.assertFalse(report["core_runtime_validated"])

    def test_cli_missing_tools_exit_one_and_report_failure(self):
        checks = [dict(key="tool", group="base", required=True, status="missing", message="absent", hint="install")]
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(env, "collect", return_value=checks), redirect_stdout(io.StringIO()):
            target = Path(folder) / "environment.json"
            self.assertEqual(env.main(["--profile", "dev", "--json", str(target)]), 1)
            self.assertFalse(json.loads(target.read_text(encoding="utf-8"))["tools_ready"])


if __name__ == "__main__":
    unittest.main()
