#!/usr/bin/env python3
"""Detecta señales de seguridad en un árbol de código o en una skill.

Uso:
    python3 security_scan.py --root <ruta> [--json] [--min-severity <nivel>]
                             [--exclude <patrón>]

Un hallazgo es una señal para revisar, no una vulnerabilidad confirmada. El
escáner no sustituye la lectura del código ni demuestra ausencia de defectos.

Códigos de salida:
    0  sin hallazgos con la severidad mínima
    1  al menos un hallazgo
    2  error de uso o de entorno
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SEVERITIES = ["low", "medium", "high", "critical"]
RANK = {name: index for index, name in enumerate(SEVERITIES)}

CODE_EXT = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".bash",
    ".zsh", ".ps1", ".rb", ".go", ".rs", ".java", ".kt", ".php", ".cs",
    ".swift", ".lua", ".pl", ".r", ".sql",
}
CONFIG_EXT = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".conf", ".properties", ".xml",
}
MD_EXT = {".md", ".markdown", ".txt"}
TEXT_EXT = CODE_EXT | CONFIG_EXT | MD_EXT

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", "dist",
    "build", "target", "__pycache__", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".tox", ".next", ".nuxt", "coverage", ".opencode",
    ".pi", ".atl", ".codegraph", ".worktrees", ".idea", ".vscode",
}

SUPPRESSION = "security-scan: ignore"
FILE_SUPPRESSION = "security-scan: ignore-file"
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    category: str
    message: str
    pattern: re.Pattern


@dataclass
class Finding:
    rule: str
    severity: str
    category: str
    path: str
    line: int
    message: str
    excerpt: str

    def as_dict(self):
        return {
            "rule": self.rule,
            "severity": self.severity,
            "category": self.category,
            "path": self.path,
            "line": self.line,
            "message": self.message,
            "excerpt": self.excerpt,
        }


def rule(rule_id, severity, category, message, pattern):
    return Rule(rule_id, severity, category, message, re.compile(pattern))


RULES = [
    rule("secret-private-key", "critical", "secretos",
         "clave privada en el árbol",
         r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    rule("secret-aws-access-key", "critical", "secretos",
         "clave de acceso de AWS",
         r"\bAKIA[0-9A-Z]{16}\b"),
    rule("secret-github-token", "critical", "secretos",
         "token de GitHub",
         r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    rule("secret-provider-key", "critical", "secretos",
         "clave de API con formato de proveedor",
         r"\b(?:sk|rk)-[A-Za-z0-9]{32,}\b"),
    rule("secret-google-key", "high", "secretos",
         "clave de API de Google",
         r"\bAIza[0-9A-Za-z_-]{35}\b"),
    rule("secret-slack-token", "high", "secretos",
         "token de Slack",
         r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    rule("prompt-injection", "high", "instrucciones",
         "intento de secuestro de instrucciones",  # security-scan: ignore prompt-injection
         r"(?i)\b(?:ignore|disregard|forget)\b[^.\n]{0,40}\b(?:previous|prior|above|earlier)\b"
         r"[^.\n]{0,30}\b(?:instructions?|prompts?|rules?|guidelines?)\b"),
    rule("stealth-directive", "high", "instrucciones",
         "directiva de ocultación al usuario",
         r"(?i)\b(?:do not|don't|never)\s+(?:tell|inform|mention|reveal|disclose)\b"
         r"[^.\n]{0,40}\b(?:user|human|operator)\b"),
    rule("safety-bypass", "high", "instrucciones",
         "intento de desactivar controles",
         r"(?i)\b(?:bypass|disable|turn off|ignore)\b[^.\n]{0,40}"
         r"\b(?:safety|security|guardrails?|content policy|filters?)\b"),
    rule("system-override", "high", "instrucciones",
         "anulación del mensaje de sistema",
         r"(?i)\b(?:system|developer)\s+(?:override|prompt)\b"),
    rule("dynamic-exec", "high", "ejecución",
         "ejecución dinámica de datos",
         r"(?:^|[^.\w])eval\s*\(|new\s+Function\s*\(|\bexec\s*\(\s*"
         r"(?:input|request|data|body|args|argv|user|payload)"),
    rule("shell-exec", "high", "ejecución",
         "shell del sistema con ejecución de comandos",
         r"\bos\.system\s*\(|subprocess\.(?:run|call|Popen|check_output|check_call)\([^)]*shell\s*=\s*True"
         r"|child_process\.(?:exec|execSync)\s*\(|Runtime\.getRuntime\(\)\.exec\s*\("),
    rule("remote-shell-pipe", "critical", "ejecución",
         "descarga ejecutada directamente en el shell",
         r"(?i)\b(?:curl|wget)\b[^\n|]{0,240}\|\s*(?:sudo\s+)?(?:ba|z|k|da)?sh\b"),
    rule("tls-verification-disabled", "high", "criptografía",
         "verificación TLS desactivada",
         r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0"),
    rule("cors-wildcard", "medium", "frontend",
         "CORS abierto a cualquier origen",
         r"(?i)access-control-allow-origin['\"]?\s*[:=]\s*['\"]?\*"),
    rule("credential-file-access", "high", "secretos",
         "acceso a ficheros de credenciales del usuario",
         r"\.ssh/(?:id_rsa|id_ed25519|id_ecdsa)|\.aws/credentials|\.npmrc|\.netrc"  # security-scan: ignore credential-file-access
         r"|\.docker/config\.json|\.kube/config"),  # security-scan: ignore credential-file-access
    rule("reverse-shell", "critical", "ejecución",
         "shell inverso o socket de control",
         r"(?i)(?:nc|ncat)\b[^\n]{0,40}\s-e\s+/bin/(?:ba)?sh|/dev/tcp/"  # security-scan: ignore reverse-shell
         r"|socket\.socket\([^)]*\)[^\n]{0,80}\.connect\("),  # security-scan: ignore reverse-shell
    rule("persistence-write", "medium", "persistencia",
         "escritura en un mecanismo de persistencia",
         r"(?i)(?:>>?|write_text|writeFile|open)\s*\([^)\n]*"
         r"(?:\.bashrc|\.zshrc|\.profile|crontab|/etc/systemd|LaunchAgents)"),
    rule("base64-blob", "medium", "ofuscación",
         "blob largo codificado en base64",
         r"[A-Za-z0-9+/]{200,}={0,2}"),
]

SECRET_ASSIGN = re.compile(
    r"""(?i)\b(api[_-]?key|secret|password|passwd|token|private[_-]?key|"""
    r"""access[_-]?key|client[_-]?secret)\b\s*[:=]\s*["']([^"'\n]{8,})["']"""
)
PLACEHOLDER = re.compile(
    r"(?i)^(?:example|sample|dummy|test|fake|changeme|change-me|placeholder"
    r"|redacted|your[-_]|\*+|x{4,}|\.{3})$"
)
ENV_HARVEST = re.compile(
    r"os\.environ\.(?:items|keys|values)\(\)|dict\(os\.environ\)"
    r"|Object\.entries\(process\.env\)|Object\.keys\(process\.env\)"
)
NETWORK = re.compile(
    r"\b(?:requests\.(?:post|put|patch)|httpx\.(?:post|put|patch)|fetch\s*\("
    r"|axios\.(?:post|put|patch)|urllib\.request|http\.client|socket\.connect)"
)
BASE64_DECODE = re.compile(
    r"b64decode|atob\s*\(|Buffer\.from\([^)]*['\"]base64['\"]"
)
EXECUTION = re.compile(r"(?:^|[^.\w])eval\s*\(|new\s+Function\s*\(|\bexec\s*\(")
BIDI = re.compile(r"[\u202a-\u202e\u2066-\u2069]")
INVISIBLE = re.compile(r"[\u200b-\u200f\u2060\ufeff]")
INSTALL_HOOKS = {"preinstall", "install", "postinstall", "prepare", "prepublish", "prepublishOnly"}


def is_text(path):
    return (
        path.suffix.lower() in TEXT_EXT
        or path.name in {".env", ".npmrc", ".netrc", ".gitconfig"}  # security-scan: ignore credential-file-access
        or path.name.startswith(".env.")
    )


def suppressed(lines, index, rule_id):
    for candidate in (lines[index], lines[index - 1] if index else ""):
        position = candidate.find(SUPPRESSION)
        if position < 0:
            continue
        tail = candidate[position + len(SUPPRESSION):].strip()
        if not tail or rule_id in tail:
            return True
    return False


def prose_lines(text):
    """Líneas fuera de bloques y código en línea para Markdown."""
    kept, fence = [], None
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)[0] * 3
                continue
            kept.append((number, INLINE_CODE_RE.sub("", line)))
        elif match and match.group(1).startswith(fence):
            fence = None
    return kept


def excerpt_of(line, category):
    if category == "secretos":
        return "[redactado]"
    return line.strip()[:160]


def add(findings, rule_obj, relative, number, line):
    findings.append(Finding(
        rule_obj.id, rule_obj.severity, rule_obj.category, relative, number,
        rule_obj.message, excerpt_of(line, rule_obj.category),
    ))


def scan_secrets(lines, relative, findings):
    for index, line in enumerate(lines):
        for match in SECRET_ASSIGN.finditer(line):
            value = match.group(2)
            if PLACEHOLDER.match(value) or "${" in value or "{{" in value:
                continue
            if any(token in value for token in ("os.environ", "process.env", "env(")):
                continue
            if suppressed(lines, index, "secret-assignment"):
                continue
            findings.append(Finding(
                "secret-assignment", "high", "secretos", relative, index + 1,
                "credencial asignada en el código", "[redactado]",
            ))
            break


def scan_install_hooks(path, text, relative, findings):
    if path.name == "package.json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return
        scripts = data.get("scripts") if isinstance(data, dict) else None
        if not isinstance(scripts, dict):
            return
        for hook, value in scripts.items():
            if hook in INSTALL_HOOKS and str(value).strip():
                findings.append(Finding(
                    "install-hook", "high", "cadena de suministro", relative, 1,
                    f"hook de instalación '{hook}' en package.json", str(value)[:160],
                ))
    elif path.name in {"setup.py", "setup.cfg"} and "cmdclass" in text:
        findings.append(Finding(
            "install-hook", "medium", "cadena de suministro", relative, 1,
            "comando de instalación personalizado en setup", "cmdclass",
        ))
    elif path.name == "composer.json":
        for hook in ("post-install-cmd", "post-update-cmd"):
            if hook in text:
                findings.append(Finding(
                    "install-hook", "high", "cadena de suministro", relative, 1,
                    f"hook de instalación '{hook}' en composer.json", hook,
                ))


def scan_combinations(text, relative, findings):
    if ENV_HARVEST.search(text) and NETWORK.search(text):
        line = text[: text.find("\n")] if "\n" in text else text
        findings.append(Finding(
            "env-exfiltration", "high", "exfiltración", relative, 1,
            "variables de entorno enumeradas y salida a red en el mismo fichero",
            excerpt_of(line, "exfiltración"),
        ))
    if BASE64_DECODE.search(text) and EXECUTION.search(text):
        findings.append(Finding(
            "encoded-execution", "high", "ofuscación", relative, 1,
            "datos decodificados y ejecutados en el mismo fichero",
            "[redactado]",
        ))


def scan_text(text, relative, is_markdown):
    findings, lines = [], []
    for number, line in (prose_lines(text) if is_markdown else enumerate(text.splitlines(), 1)):
        lines.append(line)
        for rule_obj in RULES:
            if suppressed(lines, len(lines) - 1, rule_obj.id):
                continue
            if rule_obj.pattern.search(line):
                add(findings, rule_obj, relative, number, line)
    return findings


def file_ignored(text):
    ignored = set()
    for line in text.splitlines()[:15]:
        position = line.find(FILE_SUPPRESSION)
        if position < 0:
            continue
        tail = line[position + len(FILE_SUPPRESSION):].strip()
        if not tail:
            ignored.add("*")
        else:
            ignored.update(re.findall(r"[a-z0-9-]+", tail))
    return ignored


def scan_file(path, relative, findings):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    local = []
    if path.suffix.lower() in MD_EXT:
        local.extend(scan_text(text, relative, True))
    elif path.suffix.lower() in (CODE_EXT | CONFIG_EXT) or is_text(path):
        local.extend(scan_text(text, relative, False))
        scan_secrets(text.splitlines(), relative, local)
        scan_install_hooks(path, text, relative, local)
        scan_combinations(text, relative, local)
    for match in BIDI.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        local.append(Finding(
            "bidi-control", "high", "ofuscación", relative, line,
            "carácter de control bidireccional", "[redactado]",
        ))
        break
    for match in INVISIBLE.finditer(text):
        if match.start() == 0 and match.group(0) == "\ufeff":
            continue
        line = text.count("\n", 0, match.start()) + 1
        local.append(Finding(
            "invisible-character", "medium", "ofuscación", relative, line,
            "carácter invisible en el texto", "[redactado]",
        ))
        break
    ignored = file_ignored(text)
    findings.extend(
        item for item in local
        if "*" not in ignored and item.rule not in ignored
    )


def iter_files(root, excludes):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if any(re.search(pattern, relative) for pattern in excludes):
            continue
        if is_text(path):
            yield path, relative


def scan(root, min_severity="low", excludes=()):
    root = Path(root)
    findings = []
    for path, relative in iter_files(root, excludes):
        scan_file(path, relative, findings)
    floor = RANK[min_severity]
    kept = [item for item in findings if RANK[item.severity] >= floor]
    kept.sort(key=lambda item: (-RANK[item.severity], item.path, item.line, item.rule))
    return kept


def counts_of(findings):
    counts = {name: 0 for name in SEVERITIES}
    for item in findings:
        counts[item.severity] += 1
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Detecta señales de seguridad en código, configuración y skills")
    parser.add_argument("--root", default=".", help="Raíz del árbol a escanear")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    parser.add_argument(
        "--min-severity", default="low", choices=SEVERITIES,
        help="Severidad mínima que se informa (por defecto: low)")
    parser.add_argument(
        "--exclude", action="append", default=[], metavar="REGEX",
        help="Patrón de ruta relativa que se omite; repetible")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: la raíz no es un directorio: {root}", file=sys.stderr)
        return 2
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    try:
        findings = scan(root, args.min_severity, args.exclude)
    except OSError as exc:
        print(f"ERROR: no se pudo escanear: {exc}", file=sys.stderr)
        return 2

    counts = counts_of(findings)
    if args.json:
        payload = {
            "ok": not findings,
            "root": str(root.resolve()),
            "minSeverity": args.min_severity,
            "counts": counts,
            "findings": [item.as_dict() for item in findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for item in findings:
            print(f"{item.severity.upper():8} {item.path}:{item.line} "
                  f"[{item.rule}] {item.message}")
            print(f"         {item.excerpt}")
        print(
            f"\n{len(findings)} hallazgos — críticos {counts['critical']}, "
            f"altos {counts['high']}, medios {counts['medium']}, "
            f"bajos {counts['low']} (mínimo: {args.min_severity})")
        print("Señales para revisar, no vulnerabilidades confirmadas.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
