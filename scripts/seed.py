"""
scripts/seed.py
    python scripts/seed.py           # poblar
    python scripts/seed.py --reset   # borrar todo y repoblar
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.core.base     import Base
from app.models        import create_tables
from app.database.seeders import run_all


def main():
    if "--reset" in sys.argv:
        print("⚠  Reseteando base de datos...")
        Base.metadata.drop_all(bind=engine)
        print("✓  Tablas eliminadas")
    create_tables()
    with Session(engine) as session:
        run_all(session)


if __name__ == "__main__":
    main()
