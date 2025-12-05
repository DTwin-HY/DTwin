# tests/conftest.py
import os


def pytest_sessionstart(session):
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("OPENAI_API_KEY", "test")
    os.environ.setdefault("TAVILY_API_KEY", "test")

    try:
        from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler

        if not hasattr(SQLiteTypeCompiler, "visit_JSONB"):

            def visit_JSONB(self, type_, **kw):
                return "JSON"

            SQLiteTypeCompiler.visit_JSONB = visit_JSONB
    except Exception:
        pass
