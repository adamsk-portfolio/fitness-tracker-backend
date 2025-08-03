"""Alembic migration environment for fitness-tracker."""

from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool
from alembic import context

# ───────────────────────────────────────────────
# 1)  ŚCIEŻKA – dodaj katalog projektu
#    ( .. / .. = dwa poziomy w górę od migrations/ )
# ───────────────────────────────────────────────
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_DIR)

# ───────────────────────────────────────────────
# 2)  IMPORTUJ JAKO PAKIET  backend.…
# ───────────────────────────────────────────────
from backend.extensions import db           # noqa: E402
from backend import models                  # noqa: F401, E402  (side-effect: rejestruje tabele)

# ───────────────────────────────────────────────
# 3)  KONFIGURACJA ALEMBIC
# ───────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = db.Model.metadata


# ╭──────────────────────── helpery ───────────────────────╮
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
# ╰─────────────────────────────────────────────────────────╯


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
