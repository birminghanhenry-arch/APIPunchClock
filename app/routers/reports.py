"""
app/routers/reports.py  —  C de MVC
Estadísticas, reporte diario y export CSV.
Delega al service, solo formatea la respuesta HTTP.
"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database  import get_db
from app.schemas        import StatsOut, DailyReportRow
from app.services       import get_today_stats, get_daily_report, generate_csv

router = APIRouter(tags=["Reports"])


@router.get("/stats/today", response_model=StatsOut)
def today_stats(db: Session = Depends(get_db)):
    return StatsOut(**get_today_stats(db))


@router.get("/reports/daily", response_model=list[DailyReportRow])
def daily_report(
    days: int = Query(default=7, ge=1, le=60),
    db:   Session = Depends(get_db),
):
    return [DailyReportRow(**row) for row in get_daily_report(db, days)]


@router.get("/export/csv")
def export_csv(
    since: str = Query(default=None),
    until: str = Query(default=None),
    db:    Session = Depends(get_db),
):
    buf, filename = generate_csv(db, since, until)
    return StreamingResponse(
        iter([buf.read()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
