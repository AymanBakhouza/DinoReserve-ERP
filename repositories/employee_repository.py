# repositories/employee_repository.py
 
from typing import List, Optional

from models.employee import Employee
from repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository):
    def list_all(self) -> List[Employee]:
        rows = self._fetch_all("SELECT * FROM employees ORDER BY id ASC")
        return [Employee.from_row(r) for r in rows]

    def get(self, emp_id: int) -> Optional[Employee]:
        row = self._fetch_one("SELECT * FROM employees WHERE id = ?", (emp_id,))
        return Employee.from_row(row) if row else None

    def create(self, emp: Employee) -> int:
        return self._execute(
            """INSERT INTO employees (name, role, salary, assigned_zone,
                                       technical_level, status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (emp.name, emp.role, emp.salary, emp.assigned_zone,
             emp.technical_level, emp.status),
        )

    def update(self, emp: Employee) -> None:
        self._execute(
            """UPDATE employees
                  SET name=?, role=?, salary=?, assigned_zone=?,
                      technical_level=?, status=?
                WHERE id=?""",
            (emp.name, emp.role, emp.salary, emp.assigned_zone,
             emp.technical_level, emp.status, emp.id),
        )

    def delete(self, emp_id: int) -> None:
        self._execute("DELETE FROM employees WHERE id = ?", (emp_id,))
