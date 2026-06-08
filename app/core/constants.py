"""
app/core/constants.py
Constantes de dominio compartidas entre services y routers.

Fuente única de verdad para los mapas de IDs ↔ nombres
de eventos y estados de marcaje.
"""

EVENT_NAME_TO_ID: dict[str, int] = {"check_in": 1, "check_out": 2}
EVENT_ID_TO_NAME: dict[int, str] = {1: "check_in",  2: "check_out"}

STATUS_NAME_TO_ID: dict[str, int] = {"on_time": 1, "late": 2, "flexible": 3}
STATUS_ID_TO_NAME: dict[int, str] = {1: "on_time",  2: "late",   3: "flexible"}
