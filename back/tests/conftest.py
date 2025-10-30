# tests/conftest.py
import os

def pytest_sessionstart(session):
    # 1) Pakota SQLite testisessioon niin mikään ei yritä hostiin "db"
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    # dummy-avaimet, jos joltain moduulilta vaaditaan
    os.environ.setdefault("OPENAI_API_KEY", "test")
    os.environ.setdefault("TAVILY_API_KEY", "test")

    # 2) JSONB-polyfill SQLitea varten (vain jos käytätte postgresql.JSONB-tyyppiä malleissa)
    try:
        from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
        if not hasattr(SQLiteTypeCompiler, "visit_JSONB"):
            def visit_JSONB(self, type_, **kw):
                # “JSON”/”TEXT” kelpaa SQLitelle
                return "JSON"
            SQLiteTypeCompiler.visit_JSONB = visit_JSONB
    except Exception:
        # ei pakko onnistu, jatketaan
        pass
