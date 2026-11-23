
from sqlalchemy.exc import ProgrammingError

from app.ai.llm.gemini import GeminiLLMProvider
from app.services.external_database_query import execute_external_query
from app.services.external_database import (
    get_database_url_from_config,
    discover_database_schema,
)
from app.models.data_source import DataSource


MAX_SQL_RETRIES = 2


def analyze_external_database(
    db,
    user_id: int,
    data_source_id: int,
    question: str,
) -> dict:
    """Generate, validate, and execute SQL with limited correction retries."""

    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == data_source_id,
            DataSource.user_id == user_id,
            DataSource.source_type.in_(["mysql", "postgresql"]),
        )
        .first()
    )

    if data_source is None:
        raise ValueError("External data source not found.")

    if data_source.connection_status != "connected":
        raise ValueError(
            "This database is disconnected. Reconnect before running analysis."
        )

    if not data_source.connection_config:
        raise ValueError("External database configuration is missing.")

    database_type = data_source.source_type

    database_url = get_database_url_from_config(
        data_source.connection_config
    )

    ssl_enabled = data_source.connection_config.get(
        "ssl_enabled", False
    )

    schema = discover_database_schema(
        database_url,
        database_type=database_type,
        ssl_enabled=ssl_enabled,
    )

    if not schema:
        raise ValueError("No tables found in the external database.")

    provider = GeminiLLMProvider()

    allowed_tables = set(schema.keys())

    generated_sql = provider.generate_sql(
        question=question,
        schema=schema,
        database_type=database_type,
    )

    for attempt in range(MAX_SQL_RETRIES + 1):
        try:
            result = execute_external_query(
                db=db,
                user_id=user_id,
                data_source_id=data_source_id,
                query=generated_sql,
                allowed_tables=allowed_tables,
            )

            return {
                "question": question,
                "generated_sql": generated_sql,
                "result": result,
                "attempts": attempt + 1,
            }

        except ValueError:
            # Validation, ownership, and security failures must stop immediately.
            raise

        except ProgrammingError:
            if attempt == MAX_SQL_RETRIES:
                raise ValueError(
                    "Unable to generate a valid SQL query after 2 retries."
                ) from None

            error_message = (
                "The SQL query could not be executed because of a "
                "database syntax or schema compatibility issue."
            )

        correction_prompt = f"""
You are an expert SQL developer.

The previous SQL query failed during database execution.

User question:
{question}

Database type:
{database_type}

Available schema:
{schema}

Previous SQL:
{generated_sql}

Validation feedback:
{error_message}

Generate a corrected, read-only SELECT query.

Rules:
1. Use only the supplied tables and columns.
2. Generate exactly one SELECT statement.
3. Do not use INSERT, UPDATE, DELETE, DROP, ALTER or CREATE.
4. Do not use SELECT INTO or locking clauses.
5. Return only SQL without Markdown fences or explanations.
"""

        generated_sql = provider.generate_response(
            correction_prompt
        ).strip()

    raise ValueError("SQL analysis could not be completed.")
