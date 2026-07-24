#!/usr/bin/env python3
"""Read-only deployment inventory for a local web project."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


SKIP_DIRS = {
    ".git",
    ".next",
    ".nuxt",
    ".output",
    ".venv",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "venv",
}
MANIFESTS = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    "go.mod",
    "Cargo.toml",
    "composer.json",
}
DEPLOY_FILES = {
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "Procfile",
    "vercel.json",
    "netlify.toml",
    "nginx.conf",
}
LOCK_FILES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.sum",
}


def run_git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=8,
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def safe_remote(url: str | None) -> str:
    if not url:
        return "(未配置)"
    if "://" not in url:
        return url
    parts = urlsplit(url)
    hostname = parts.hostname or ""
    if parts.port:
        hostname += f":{parts.port}"
    return urlunsplit((parts.scheme, hostname, parts.path, "", ""))


def walk_shallow(root: Path, max_depth: int = 2):
    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        dirs[:] = [
            name
            for name in dirs
            if name not in SKIP_DIRS and not name.startswith(".")
        ]
        if depth >= max_depth:
            dirs[:] = []
        yield current_path, files


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def package_details(root: Path, package_files: list[Path]) -> list[str]:
    output: list[str] = []
    for path in package_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            output.append(f"- `{rel(root, path)}`：无法解析")
            continue
        scripts = data.get("scripts", {})
        script_text = "、".join(
            f"`{name}`" for name in ("dev", "test", "build", "start", "preview")
            if name in scripts
        )
        dependencies = {
            **data.get("dependencies", {}),
            **data.get("devDependencies", {}),
        }
        frameworks = [
            name
            for name in (
                "next",
                "nuxt",
                "vite",
                "react",
                "vue",
                "svelte",
                "express",
                "fastify",
                "nestjs",
            )
            if name in dependencies
        ]
        output.append(
            f"- `{rel(root, path)}`：脚本 {script_text or '未识别'}；"
            f"框架 {('、'.join(frameworks) or '未识别')}"
        )
    return output


def env_template_names(root: Path) -> list[str]:
    names: set[str] = set()
    template_names = {".env.example", ".env.sample", ".env.template"}
    for current, files in walk_shallow(root):
        for filename in template_names.intersection(files):
            path = current / filename
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", line)
                    if match:
                        names.add(match.group(1))
            except (OSError, UnicodeDecodeError):
                pass
    return sorted(names)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="只读检查 Web 项目的部署线索，不读取实际 .env 值。"
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"目录不存在：{root}")

    manifests: list[Path] = []
    package_files: list[Path] = []
    locks: list[Path] = []
    deploy_files: list[Path] = []
    for current, files in walk_shallow(root):
        for name in files:
            path = current / name
            if name in MANIFESTS:
                manifests.append(path)
            if name == "package.json":
                package_files.append(path)
            if name in LOCK_FILES:
                locks.append(path)
            if name in DEPLOY_FILES or "nginx" in name.lower():
                deploy_files.append(path)

    branch = run_git(root, "branch", "--show-current")
    commit = run_git(root, "rev-parse", "--short", "HEAD")
    remote = safe_remote(run_git(root, "remote", "get-url", "origin"))
    status = run_git(root, "status", "--porcelain")
    changed = len(status.splitlines()) if status else 0

    print("# 项目部署盘点")
    print(f"\n- 项目目录：`{root}`")
    print(f"- Git 分支：`{branch or '(非 Git 仓库或无分支)'}`")
    print(f"- 当前提交：`{commit or '(无)'}`")
    print(f"- origin：`{remote}`")
    print(f"- 工作区改动条目：{changed}")

    print("\n## 技术与构建线索")
    if package_files:
        print("\n".join(package_details(root, sorted(package_files))))
    elif manifests:
        for path in sorted(manifests):
            print(f"- `{rel(root, path)}`")
    else:
        print("- 未在两层目录内发现常见项目清单；需要人工识别。")

    print("\n## 可复现与部署线索")
    print(
        "- 锁文件：" + (
            "、".join(f"`{rel(root, p)}`" for p in sorted(locks)) or "未发现"
        )
    )
    print(
        "- 部署文件：" + (
            "、".join(f"`{rel(root, p)}`" for p in sorted(deploy_files)) or "未发现"
        )
    )
    names = env_template_names(root)
    print("- 环境变量模板名称：" + ("、".join(f"`{n}`" for n in names) or "未发现"))
    print("\n> 本脚本不会运行构建、读取真实 `.env` 值或判断线上合规。")
    print("> 下一步仍需确认国内/国外路线、产物目录、健康检查、持久化数据、托管方式、目标区域和正式域名。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
