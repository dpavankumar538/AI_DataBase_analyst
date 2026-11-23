
import sqlglot
from sqlglot import exp


SUPPORTED_DIALECTS = {
    "mysql": "mysql",
    "postgresql": "postgres",
    "postgres": "postgres",
}


def get_sql_dialect(database_type: str) -> str:
    dialect = SUPPORTED_DIALECTS.get(database_type)

    if dialect is None:
        raise ValueError("Unsupported database type.")

    return dialect


def validate_read_only_sql(query: str, database_type: str) -> str:
    """Validate exactly one read-only SELECT statement."""

    dialect = get_sql_dialect(database_type)

    if not query or not query.strip():
        raise ValueError("SQL query cannot be empty.")

    try:
        statements = sqlglot.parse(query, read=dialect)
    except sqlglot.errors.ParseError:
        raise ValueError("Invalid SQL query.") from None

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")

    if statement.args.get("into"):
        raise ValueError("SELECT INTO is not allowed.")

    if statement.find(exp.Lock):
        raise ValueError("Locking queries are not allowed.")

    return statement.sql(dialect=dialect)


def validate_allowed_tables(
    query: str,
    database_type: str,
    allowed_tables: set[str],
) -> None:
    """Reject queries that reference unauthorized tables."""

    dialect = get_sql_dialect(database_type)

    try:
        statements = sqlglot.parse(query, read=dialect)
    except sqlglot.errors.ParseError:
        raise ValueError("Invalid SQL query.") from None

    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    referenced_tables = {
        table.name.lower()
        for table in statements[0].find_all(exp.Table)
    }

    allowed = {name.lower() for name in allowed_tables}

    if not referenced_tables:
        raise ValueError("The query must reference an allowed table.")

    if referenced_tables - allowed:
        raise ValueError("The query references an unauthorized table.")
