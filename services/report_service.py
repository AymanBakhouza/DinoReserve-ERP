# services/report_service.py
# Servicio de lógica de negocio para generar reportes y estadísticas.


from repositories.base_repository import BaseRepository


class ReportService(BaseRepository):
    """Genera estadísticas para la vista de Reportes."""

    # ----- Tickets -----
    def daily_revenue(self) -> float:
        row = self._fetch_one(
            """SELECT COALESCE(SUM(total), 0) AS revenue
                 FROM tickets
                WHERE DATE(sale_date) = DATE('now')"""
        )
        return float(row["revenue"]) if row else 0.0

    def daily_tickets_count(self) -> int:
        row = self._fetch_one(
            """SELECT COUNT(*) AS c
                 FROM tickets
                WHERE DATE(sale_date) = DATE('now')"""
        )
        return int(row["c"]) if row else 0

    def revenue_by_type(self) -> list:
        return self._fetch_all(
            """SELECT ticket_type,
                      COUNT(*)         AS quantity,
                      SUM(total)       AS revenue
                 FROM tickets
                WHERE DATE(sale_date) = DATE('now')
                GROUP BY ticket_type
                ORDER BY revenue DESC"""
        )

    # ----- Recintos / Dinosaurios -----
    def occupation_by_zone(self) -> list:
        return self._fetch_all(
            """SELECT e.id, e.name, e.zone_type, e.max_capacity,
                      COUNT(d.id) AS occupancy
                 FROM enclosures e
            LEFT JOIN dinosaurs d ON d.enclosure_id = e.id
                GROUP BY e.id
                ORDER BY e.id"""
        )

    def avg_danger_by_enclosure(self) -> list:
        return self._fetch_all(
            """SELECT e.name AS enclosure_name,
                      ROUND(AVG(d.danger_level), 2) AS avg_danger,
                      COUNT(d.id) AS dinos
                 FROM enclosures e
            LEFT JOIN dinosaurs d ON d.enclosure_id = e.id
                GROUP BY e.id
                ORDER BY avg_danger IS NULL, avg_danger DESC"""
        )

    # ----- Inventario -----
    def low_stock_items(self) -> list:
        return self._fetch_all(
            """SELECT item_name, category, quantity, minimum_stock, supplier
                 FROM inventory
                WHERE quantity < minimum_stock
                ORDER BY (minimum_stock - quantity) DESC"""
        )

    # ----- Mantenimiento -----
    def maintenance_by_status(self) -> list:
        return self._fetch_all(
            """SELECT status, COUNT(*) AS quantity
                 FROM maintenance_tasks
                GROUP BY status
                ORDER BY quantity DESC"""
        )

    # ----- Empleados -----
    def employees_by_role(self) -> list:
        return self._fetch_all(
            """SELECT role, COUNT(*) AS quantity, ROUND(AVG(salary), 2) AS avg_salary
                 FROM employees
                WHERE status = 'active'
                GROUP BY role
                ORDER BY quantity DESC"""
        )
