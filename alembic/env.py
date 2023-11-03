
from alembic import context
from fhelp.alembic_env import run_migrations_offline,run_migrations_online


# Если Alembic запущен через 'stamped'
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
