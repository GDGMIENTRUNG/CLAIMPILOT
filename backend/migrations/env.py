from alembic import context
from app.config import settings
from app.database import Base, engine
from app import models
if context.is_offline_mode():
    context.configure(url=settings.database_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    def run(connection):
        context.configure(connection=connection, target_metadata=Base.metadata,
                          compare_type=True, compare_server_default=True)
        with context.begin_transaction():
            context.run_migrations()

    # Tests can supply a connection to their own throwaway database. Production
    # CLI continues to use DATABASE_URL; no app startup DDL is introduced.
    supplied = context.config.attributes.get('connection')
    if supplied is not None:
        run(supplied)
    else:
        with engine.connect() as connection:
            run(connection)
