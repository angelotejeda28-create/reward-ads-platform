# RewardAds Platform - Sistema de Tareas, Anuncios y Recompensas (PTC)

Plataforma completa de publicidad remunerada y tareas para usuarios construida con **Python 3** (sin dependencias externas) y una base de datos relacional **SQLite**.

---

## 🚀 Cómo Iniciar la Plataforma

Para arrancar el servidor web y la API REST localmente:

```bash
cd /home/dilan/.gemini/antigravity/scratch/reward-ads-platform
python3 server.py
```

Luego abre tu navegador web en:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📁 Estructura del Proyecto

```
reward-ads-platform/
├── server.py              # Servidor HTTP + REST API con validación de seguridad
├── schema.sql             # Esquema relacional SQL (SQLite)
├── database.db            # Base de datos (se autogenera al iniciar)
├── README.md              # Documentación técnica y guía de uso
└── static/
    └── index.html         # Panel unificado (SPA) con los 4 módulos funcionales
```

---

## 🛠️ Módulos Integrados

1. **📺 Ver Anuncios (Ganar Dinero):**
   * Listado de campañas activas en la red.
   * Visor con temporizador regresivo de 15s, 30s o 60s.
   * Detección de pestaña activa (*Page Visibility API*) para evitar visualizaciones en segundo plano.
   * Reto de verificación anti-bot (Mini-Captcha) al finalizar.
   * Verificación estricta del tiempo transcurrido en el servidor backend antes de acreditar saldo.

2. **📢 Panel de Anunciante:**
   * Creación de nuevas campañas con título, enlace de destino y duración.
   * Calculadora automática de presupuesto en tiempo real.
   * Control de estado de campañas (pausar / reanudar).

3. **💰 Billetera y Retiros:**
   * Consulta de saldo acumulado por tareas.
   * Solicitud de retiros (USDT TRC-20, Binance Pay, PayPal) con cálculo dinámico de comisiones.
   * Historial de pagos en vivo.

4. **⚙️ SuperAdmin:**
   * Monitoreo del margen de ganancias de la plataforma.
   * Cola de retiros por aprobar o rechazar con reembolso automático en caso de cancelación.
   * Moderación de anuncios publicitarios entrantes.

---

## 🔒 Reglas de Seguridad en el Backend

* **Validación de Permanencia en el Servidor:** La API registra `started_at` con el reloj del servidor y rechaza cualquier solicitud de cobro en `/api/ads/claim` si el tiempo transcurrido es menor al contratado por el anunciante.
* **Transacciones Atómicas:** Las acreditaciones de saldo y el descuento de presupuesto de las campañas se ejecutan en transacciones de base de datos para garantizar la integridad contable.
