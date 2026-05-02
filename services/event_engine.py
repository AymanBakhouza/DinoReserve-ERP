# services/event_engine.py
# Motor de eventos aleatorios para simular situaciones inesperadas en el parque.


import random
from dataclasses import dataclass

from repositories.base_repository import BaseRepository
from repositories.dinosaur_repository import DinosaurRepository
from repositories.enclosure_repository import EnclosureRepository
from repositories.inventory_repository import InventoryRepository
from utils.constants import RANDOM_EVENTS
from utils.logger import get_logger


@dataclass
class EventResult:
    """Resultado de un evento aleatorio para mostrar en la GUI."""
    event_type: str
    title: str
    description: str
    severity: str  # info | warning | error
    affected_id: int | None = None


class RandomEventEngine(BaseRepository):
    def __init__(self):
        super().__init__()
        self._log = get_logger()
        self._dinos = DinosaurRepository()
        self._encs = EnclosureRepository()
        self._inv = InventoryRepository()

    # ------------------------------------------------------------
    def trigger_random_event(self) -> EventResult:
        """Punto de entrada: elige un evento por probabilidad y lo aplica."""
        events, weights = zip(*RANDOM_EVENTS)
        chosen = random.choices(events, weights=weights, k=1)[0]
        handler = getattr(self, f"_event_{chosen}")
        result = handler()
        self._persist(result)
        return result

    # ------------------------------------------------------------
    def _persist(self, ev: EventResult):
        self._execute(
            """INSERT INTO random_events (event_type, description, severity, affected_id)
               VALUES (?, ?, ?, ?)""",
            (ev.event_type, ev.description, ev.severity, ev.affected_id),
        )
        log_method = {
            "info": self._log.info,
            "warning": self._log.warning,
            "error": self._log.error,
        }.get(ev.severity, self._log.info)
        log_method("EVENTO[%s] %s", ev.event_type, ev.description)

    # ------------------------------------------------------------ Eventos
    def _event_tropical_storm(self) -> EventResult:
        carns = [e for e in self._encs.list_all()
                 if e.zone_type == "carnivore_zone" and e.status == "active"]
        if not carns:
            return EventResult(
                "tropical_storm", "Tormenta tropical",
                "Tormenta detectada. Sin recintos carnívoros activos afectados.",
                "info",
            )
        affected = random.choice(carns)
        new_voltage = max(0, affected.fence_voltage - random.randint(2000, 5000))
        self._encs.update_voltage(affected.id, new_voltage)
        return EventResult(
            "tropical_storm",
            "⚡ Tormenta tropical",
            f"Voltaje en '{affected.name}' bajó a {new_voltage:.0f}V.",
            "warning",
            affected.id,
        )

    def _event_feeding_delay(self) -> EventResult:
        dinos = self._dinos.list_all()
        if not dinos:
            return EventResult(
                "feeding_delay", "Retraso de alimentación",
                "No hay dinosaurios registrados.", "info",
            )
        sample = random.sample(dinos, min(3, len(dinos)))
        for d in sample:
            self._dinos.update_feeding(d.id, max(0, d.feeding_level - random.randint(10, 25)))
        names = ", ".join(d.name for d in sample)
        return EventResult(
            "feeding_delay",
            "🍖 Retraso de alimentación",
            f"Niveles de alimentación reducidos en: {names}.",
            "warning",
        )

    def _event_stock_variation(self) -> EventResult:
        items = self._inv.list_all()
        if not items:
            return EventResult(
                "stock_variation", "Variación de existencias",
                "Inventario vacío.", "info",
            )
        item = random.choice(items)
        delta = random.randint(5, 30)
        new_qty = max(0, item.quantity - delta)
        self._inv.update_quantity(item.id, new_qty)
        sev = "warning" if new_qty < item.minimum_stock else "info"
        return EventResult(
            "stock_variation",
            "📦 Variación de existencias",
            f"'{item.item_name}' redujo en {delta} unidades (quedan {new_qty}).",
            sev,
            item.id,
        )

    def _event_fence_malfunction(self) -> EventResult:
        actives = [e for e in self._encs.list_all() if e.status == "active"]
        if not actives:
            return EventResult(
                "fence_malfunction", "Fallo de valla",
                "Sin recintos activos para inspeccionar.", "info",
            )
        target = random.choice(actives)
        self._encs.update_status(target.id, "maintenance")
        return EventResult(
            "fence_malfunction",
            "🛠️ Fallo de valla",
            f"Recinto '{target.name}' pasó a mantenimiento.",
            "error",
            target.id,
        )

    def _event_dinosaur_health_alert(self) -> EventResult:
        dinos = self._dinos.list_all()
        if not dinos:
            return EventResult(
                "dinosaur_health_alert", "Alerta sanitaria",
                "No hay dinosaurios registrados.", "info",
            )
        target = random.choice(dinos)
        new_status = random.choice(["observation", "sick", "critical"])
        self._dinos.update_health(target.id, new_status)
        status_labels = {
            "observation": "observación",
            "sick": "enfermo",
            "critical": "crítico",
        }
        return EventResult(
            "dinosaur_health_alert",
            "🩺 Alerta sanitaria",
            f"'{target.name}' cambió a estado de salud '{status_labels.get(new_status, new_status)}'.",
            "warning" if new_status != "critical" else "error",
            target.id,
        )

    def _event_calm_day(self) -> EventResult:
        return EventResult(
            "calm_day",
            "🌤️ Día tranquilo",
            "Sin incidentes en el parque. Operaciones normales.",
            "info",
        )
