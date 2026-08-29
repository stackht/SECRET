"""SECRET backend launcher (Phase 10).

Applies pending Alembic migrations, then starts uvicorn. Provides:
  python run.py            -> migrate + run
  python run.py --no-migrate
  python run.py --check    -> verify DB/graph connectivity and exit
"""
from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
import sys


def run_migrations() -> None:
    """Run alembic upgrade head in a subprocess (blocking)."""
    print("[deploy] Applying database migrations...")
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=os.path.dirname(__file__))
    if result.returncode != 0:
        print("[deploy] Migration failed; continuing with existing schema.", file=sys.stderr)


async def check_connections() -> bool:
    from app.core.dbcheck import check_database_connection
    from app.core.graphcheck import check_graph_connection

    db = await check_database_connection()
    graph = await check_graph_connection()
    print(f"[deploy] PostgreSQL: {db['status']}")
    print(f"[deploy] Neo4j:      {graph['status']}")
    return db["status"] == "ok" and graph["status"] == "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="SECRET backend launcher")
    parser.add_argument("--no-migrate", action="store_true", help="Skip Alembic migrations")
    parser.add_argument("--check", action="store_true", help="Check connectivity and exit")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.check:
        ok = asyncio.run(check_connections())
        return 0 if ok else 1

    if not args.no_migrate:
        run_migrations()

    print(f"[deploy] Starting SECRET API on {args.host}:{args.port}")
    os.execvp(
        sys.executable,
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", args.host, "--port", str(args.port)],
    )
    return 0  # unreachable


if __name__ == "__main__":
    raise SystemExit(main())
