#!/usr/bin/env python3
"""
Comprueba si hay nuevos commits en origin/main y, si los hay, hace pull y despliega.
Pensado para servidor con internet salida pero sin acceso entrante (no puede recibir webhooks).

Uso: python3 scripts/deploy-on-push-check.py

Para ejecutarlo como servicio cada 5 minutos: ver README, sección "Despliegue automático"
(systemd timer en scripts/systemd/ o cron).
"""

import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def run(cmd: list[str], timeout: int = 120) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (r.stdout or "").strip() + (r.stderr or "").strip()
        return r.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def main():
    # git fetch (el servidor tiene internet salida)
    ok, out = run(["git", "fetch", "origin", "main"])
    if not ok:
        print(f"git fetch failed: {out}")
        return 1

    # ¿Hay diferencias entre HEAD local y origin/main?
    ok, local = run(["git", "rev-parse", "HEAD"])
    if not ok:
        print("rev-parse HEAD failed")
        return 1
    ok, remote = run(["git", "rev-parse", "origin/main"])
    if not ok:
        print("rev-parse origin/main failed (¿existe origin/main?)")
        return 1

    if local.strip() == remote.strip():
        print("Nada nuevo en origin/main.")
        return 0

    print("Hay nuevos commits. Desplegando...")
    ok, out = run(["git", "pull", "origin", "main"])
    if not ok:
        print(f"git pull failed: {out}")
        return 1

    ok, out = run(["docker", "compose", "up", "--build", "-d"], timeout=600)
    if not ok:
        print(f"docker compose failed: {out}")
        return 1

    print("Deploy completado.")
    return 0


if __name__ == "__main__":
    exit(main())
