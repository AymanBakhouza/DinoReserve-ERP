# DinoReserve-ERP
<div align="center">

# 🦖 DinoReserve ERP

### Sistema de Gestión Integral para Parque Temático Jurásico

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-FF6B35?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**Reserva Jurásica Inteligente · Control predictivo de biomas, seguridad, inventario y ventas**

</div>

---

## 📖 Descripción

**DinoReserve ERP** es una aplicación de escritorio completa para la administración de un parque temático de dinosaurios. Permite gestionar recintos, especies, empleados, inventario, venta de tickets y generación de reportes — todo desde una interfaz gráfica moderna y sin dependencias externas.

Construido con una arquitectura **MVC limpia y modular**, ofrece una experiencia tipo "Centro de Comando" inspirada en el universo Jurassic Park, con telemetría en vivo, alertas predictivas y trazabilidad completa de operaciones.

---

## ✨ Características principales

- 🦕 **Gestión de Dinosaurios** — Catálogo de especies, estados de salud, asignación a recintos
- 🏞️ **Control de Recintos (Biomas)** — Capacidad, seguridad de vallas, monitoreo en tiempo real
- 🎫 **Taquilla Inteligente** — Venta de entradas (Normal, Infantil, VIP, Pase Rápido) con cálculo automático de IVA (21%) y generación de recibos con localizador único `DR-XXXXXXXX`
- 👥 **Sistema de Personal** — Plantilla operativa: roles, salarios, zonas asignadas, niveles técnicos
- 📦 **Inventario y Logística** — Control de existencias (comida carnívora/herbívora, mercancía, médico, logística) con alertas de stock mínimo
- 🔧 **Mantenimiento** — Cola de reparaciones y seguimiento de incidentes
- 📊 **Reportes** — Generación de informes operativos y financieros
- 🎉 **Eventos** — Programación y simulación de eventos del parque
- 📜 **Registros** — Auditoría completa de todas las operaciones (transacciones atómicas)
- 🔐 **Autenticación por roles** — Administrador / Operador con credenciales biométricas

---

## 🖼️ Capturas de pantalla

### 🔐 Acceso al Centro de Comando
Pantalla de login con estética jurásica y credenciales biométricas.

### 🎯 Centro de Misión (Dashboard)
Telemetría predictiva del parque en vivo: ingresos, entradas registradas, alertas de suministros, biomas activos, señales de riesgo biológico y cola de reparaciones.

### 👥 Equipo del Parque
Gestión completa de plantilla operativa con filtros, roles, salarios y asignación a zonas.

### 📦 Inventario y Logística
Control de existencias con categorías, proveedores y alertas de stock bajo.

### 🎫 Taquilla de Entradas
Venta con cálculo automático de IVA y emisión de recibos con localizador único.

> 📁 *Las capturas completas se encuentran en la carpeta `/docs/screenshots/`*

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.10+ |
| Interfaz Gráfica | Tkinter / CustomTkinter |
| Base de Datos | SQLite 3 |
| Arquitectura | MVC (Model-View-Controller) |
| Patrón de acceso a datos | Repository Pattern |

---

## 📂 Estructura del proyecto

DinoReserve-ERP/
│
├── 📁 assets/              # Imágenes, iconos y recursos gráficos
├── 📁 controllers/         # Lógica de control (MVC)
├── 📁 database/            # Scripts SQL y conexión BD
├── 📁 docs/                # Documentación y diagramas
├── 📁 models/              # Modelos de datos (entidades)
├── 📁 repositories/        # Acceso a datos (Repository Pattern)
├── 📁 services/            # Lógica de negocio
├── 📁 utils/               # Utilidades y helpers
├── 📁 views/               # Interfaces gráficas (Tkinter)
│
├── 📄 main.py              # Punto de entrada de la aplicación
├── 📄 requirements.txt     # Dependencias del proyecto
├── 📄 DinoReserve ERP DATABASE.db  # Base de datos SQLite
└── 📄 README.md            # Este archivo


---

## 🚀 Instalación y ejecución

### Requisitos previos
- Python **3.10** o superior
- pip (gestor de paquetes de Python)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/AymanBakhouza/DinoReserve-ERP.git
cd DinoReserve-ERP

# 2. (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate     # Linux/Mac
venv\Scripts\activate        # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python main.py
```

---

## 🔑 Credenciales DEMO

| Usuario   | Contraseña   | Rol            |
|-----------|--------------|----------------|
| `admin`   | `admin123`   | Administrador  |
| `operador`| `operador123`| Operador       |

---

## 🎨 Diseño y UX

La interfaz se inspira en una **consola de comando jurásica**, con:
- Paleta de colores: verde fluorescente (`#00FF88`) y naranja jurásico (`#FF8C42`) sobre fondo oscuro
- Tipografía monoespaciada para terminales y datos técnicos
- Componentes con estética HUD militar/científica
- Iconografía inspirada en Jurassic Park

---

## 🗺️ Diagrama de Flujo

El diagrama de arquitectura completo está disponible en `/DIAGRAMA DE FLUJO/`.

---

## 🧪 Funcionalidades destacadas

- ✅ **Transacciones atómicas** en venta de tickets
- ✅ **Localizadores únicos** generados automáticamente (`DR-XXXXXXXX`)
- ✅ **Cálculo automático de IVA** español (21%)
- ✅ **Alertas predictivas** de stock bajo y mantenimiento
- ✅ **Multi-rol** con permisos diferenciados
- ✅ **Sin dependencias externas** — funciona offline al 100%

---

## 📸 Versión

**v2.0.0** — Versión de Comando

---

## 👨‍💻 Autor

**Ayman Bakhouza**

- 🎓 Proyecto Final de Estudios (PFE)
- 💼 [LinkedIn](https://www.linkedin.com/in/aymanbakhouza)
- 📧 Contacto: bk.ayman04@com.com
- 🐙 [GitHub](https://github.com/AymanBakhouza)

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

### 🦖 *"Life finds a way... and so does good code."* 🦖

**Biocomando DinoReserve · © 2026**

</div>
