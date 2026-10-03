#!/usr/bin/env python3
"""
Servidor Backend para la Plataforma de Anuncios y Recompensas (PTC).
Construido exclusivamente con la biblioteca estándar de Python (sin dependencias externas).
"""

import http.server
import json
import os
import secrets
import sqlite3
import time
from urllib.parse import parse_qs, urlparse

PORT = 8000
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
        
    # Verificar si ya existen usuarios por defecto
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (id, username, email, role, balance_earnings, balance_advertiser)
            VALUES 
                (1, 'usuario_demo', 'usuario@demo.com', 'user', 3.4200, 0.0000),
                (2, 'anunciante_demo', 'anunciante@demo.com', 'advertiser', 0.0000, 85.0000),
                (3, 'admin_demo', 'admin@demo.com', 'admin', 0.0000, 0.0000)
        """)
        
        cursor.execute("""
            INSERT INTO ad_campaigns (id, advertiser_id, title, target_url, description, cost_per_view, user_reward, total_budget, remaining_budget, duration_seconds, views_delivered, total_views, status)
            VALUES 
                (1, 2, 'PaySecure: Solución de Pagos Globales', 'https://paysecure.example.com', 'Acepta pagos con bajas comisiones en más de 40 divisas.', 0.0200, 0.0150, 20.00, 16.50, 15, 175, 1000, 'active'),
                (2, 2, 'CryptoWallet Web3: App Móvil', 'https://cryptowallet.example.com', 'Billetera descentralizada con soporte multi-cadena.', 0.0350, 0.0250, 35.00, 28.00, 30, 200, 1000, 'active'),
                (3, 2, 'Hosting Cloud para Desarrolladores', 'https://cloudhost.example.com', 'Servidores VPS ultra-rápidos con discos NVMe.', 0.0600, 0.0450, 60.00, 60.00, 60, 0, 1000, 'pending')
        """)
        
        cursor.execute("""
            INSERT INTO withdrawals (id, user_id, amount, fee, net_amount, payment_method, destination_account, status, created_at)
            VALUES
                (1, 1, 10.00, 0.00, 10.00, 'Binance Pay', 'usuario@binance.id', 'approved', datetime('now', '-2 days')),
                (2, 1, 6.50, 1.00, 5.50, 'USDT TRC-20', 'TJ9x...84mK', 'pending', datetime('now', '-1 hours'))
        """)
        
        conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


class RewardPlatformHandler(http.server.BaseHTTPRequestHandler):

    def send_json(self, data, status_code=200):
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def parse_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(raw_body)
            except json.JSONDecodeError:
                return {}
        return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html")
            return

        if path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            file_path = os.path.join(STATIC_DIR, rel_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                content_type = "text/plain"
                if file_path.endswith(".html"):
                    content_type = "text/html"
                elif file_path.endswith(".css"):
                    content_type = "text/css"
                elif file_path.endswith(".js"):
                    content_type = "application/javascript"
                elif file_path.endswith(".json"):
                    content_type = "application/json"
                self.serve_file(file_path, content_type)
                return
            else:
                self.send_error(404, "Archivo no encontrado")
                return

        # Endpoints API
        if path == "/api/user":
            conn = get_db()
            user = conn.execute("SELECT id, username, email, role, balance_earnings, balance_advertiser FROM users WHERE id = 1").fetchone()
            advertiser = conn.execute("SELECT balance_advertiser FROM users WHERE id = 2").fetchone()
            conn.close()
            self.send_json({
                "user": dict(user),
                "advertiser_balance": advertiser["balance_advertiser"]
            })
            return

        if path == "/api/ads":
            conn = get_db()
            ads = conn.execute("""
                SELECT id, title, target_url, description, user_reward, duration_seconds, views_delivered, total_views
                FROM ad_campaigns
                WHERE status = 'active' AND remaining_budget >= user_reward
            """).fetchall()
            conn.close()
            self.send_json([dict(row) for row in ads])
            return

        if path == "/api/campaigns":
            conn = get_db()
            campaigns = conn.execute("SELECT * FROM ad_campaigns ORDER BY id DESC").fetchall()
            conn.close()
            self.send_json([dict(row) for row in campaigns])
            return

        if path == "/api/withdrawals":
            conn = get_db()
            withdrawals = conn.execute("SELECT * FROM withdrawals WHERE user_id = 1 ORDER BY id DESC").fetchall()
            conn.close()
            self.send_json([dict(row) for row in withdrawals])
            return

        if path == "/api/admin/metrics":
            conn = get_db()
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_views = conn.execute("SELECT COUNT(*) FROM ad_views WHERE status = 'completed'").fetchone()[0]
            
            # Margen ganado por la plataforma = (cost_per_view - user_reward) * views
            platform_margin = conn.execute("""
                SELECT COALESCE(SUM((c.cost_per_view - c.user_reward)), 0.0)
                FROM ad_views v
                JOIN ad_campaigns c ON v.campaign_id = c.id
                WHERE v.status = 'completed'
            """).fetchone()[0]

            pending_withdrawals = conn.execute("SELECT * FROM withdrawals WHERE status = 'pending' ORDER BY id DESC").fetchall()
            pending_ads = conn.execute("SELECT * FROM ad_campaigns WHERE status = 'pending' ORDER BY id DESC").fetchall()
            conn.close()

            self.send_json({
                "total_users": total_users,
                "total_views": total_views,
                "platform_margin": round(platform_margin, 4),
                "pending_withdrawals": [dict(w) for w in pending_withdrawals],
                "pending_ads": [dict(a) for a in pending_ads]
            })
            return

        self.send_error(404, "Ruta no encontrada")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.parse_body()

        # Iniciar visualización de anuncio (Genera token con timestamp del servidor)
        if path == "/api/ads/start":
            campaign_id = body.get("campaign_id")
            conn = get_db()
            campaign = conn.execute("SELECT * FROM ad_campaigns WHERE id = ? AND status = 'active'", (campaign_id,)).fetchone()
            
            if not campaign:
                conn.close()
                self.send_json({"error": "Campaña no disponible"}, 400)
                return

            token = secrets.token_hex(16)
            start_time = time.time()

            conn.execute("""
                INSERT INTO ad_views (campaign_id, user_id, session_token, started_at, reward_amount, status)
                VALUES (?, 1, ?, ?, ?, 'in_progress')
            """, (campaign_id, token, start_time, campaign["user_reward"]))
            conn.commit()
            conn.close()

            self.send_json({
                "session_token": token,
                "duration_seconds": campaign["duration_seconds"],
                "target_url": campaign["target_url"],
                "reward": campaign["user_reward"]
            })
            return

        # Reclamar recompensa (Validación estricta de tiempo transcurrido en el servidor)
        if path == "/api/ads/claim":
            token = body.get("session_token")
            conn = get_db()
            view = conn.execute("SELECT * FROM ad_views WHERE session_token = ? AND status = 'in_progress'", (token,)).fetchone()

            if not view:
                conn.close()
                self.send_json({"error": "Sesión inválida o ya reclamada"}, 400)
                return

            campaign = conn.execute("SELECT * FROM ad_campaigns WHERE id = ?", (view["campaign_id"],)).fetchone()
            elapsed_time = time.time() - view["started_at"]

            # Validación de tiempo en el backend: No confiar en el navegador
            if elapsed_time < (campaign["duration_seconds"] - 0.5):
                conn.execute("UPDATE ad_views SET status = 'invalid' WHERE id = ?", (view["id"],))
                conn.commit()
                conn.close()
                self.send_json({"error": "Tiempo insuficiente. Intento de omisión detectado."}, 403)
                return

            # Acreditar saldo al usuario y actualizar campaña en una transacción
            reward = view["reward_amount"]
            conn.execute("UPDATE users SET balance_earnings = balance_earnings + ? WHERE id = 1", (reward,))
            conn.execute("""
                UPDATE ad_campaigns 
                SET views_delivered = views_delivered + 1,
                    remaining_budget = remaining_budget - cost_per_view
                WHERE id = ?
            """, (campaign["id"],))
            conn.execute("UPDATE ad_views SET status = 'completed', completed_at = ? WHERE id = ?", (time.time(), view["id"]))

            # Obtener nuevo balance
            new_balance = conn.execute("SELECT balance_earnings FROM users WHERE id = 1").fetchone()[0]
            conn.commit()
            conn.close()

            self.send_json({
                "success": True,
                "reward_credited": reward,
                "new_balance": round(new_balance, 4)
            })
            return

        # Crear nueva campaña (Anunciante)
        if path == "/api/campaigns":
            title = body.get("title")
            target_url = body.get("target_url")
            duration = int(body.get("duration_seconds", 15))
            views = int(body.get("total_views", 100))

            price_map = {15: 0.020, 30: 0.035, 60: 0.060}
            reward_map = {15: 0.015, 30: 0.025, 60: 0.045}
            cost_per_view = price_map.get(duration, 0.020)
            user_reward = reward_map.get(duration, 0.015)
            total_budget = round(cost_per_view * views, 2)

            conn = get_db()
            advertiser = conn.execute("SELECT balance_advertiser FROM users WHERE id = 2").fetchone()

            if advertiser["balance_advertiser"] < total_budget:
                conn.close()
                self.send_json({"error": "Saldo publicitario insuficiente"}, 400)
                return

            # Descontar del balance publicitario
            conn.execute("UPDATE users SET balance_advertiser = balance_advertiser - ? WHERE id = 2", (total_budget,))
            cursor = conn.execute("""
                INSERT INTO ad_campaigns (advertiser_id, title, target_url, cost_per_view, user_reward, total_budget, remaining_budget, duration_seconds, total_views, status)
                VALUES (2, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (title, target_url, cost_per_view, user_reward, total_budget, total_budget, duration, views))
            
            new_balance = conn.execute("SELECT balance_advertiser FROM users WHERE id = 2").fetchone()[0]
            conn.commit()
            conn.close()

            self.send_json({
                "success": True,
                "campaign_id": cursor.lastrowid,
                "new_advertiser_balance": round(new_balance, 2)
            })
            return

        # Pausar o reanudar campaña
        if path == "/api/campaigns/toggle":
            campaign_id = body.get("campaign_id")
            conn = get_db()
            campaign = conn.execute("SELECT status FROM ad_campaigns WHERE id = ?", (campaign_id,)).fetchone()
            if campaign:
                new_status = "paused" if campaign["status"] == "active" else "active"
                conn.execute("UPDATE ad_campaigns SET status = ? WHERE id = ?", (new_status, campaign_id))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "new_status": new_status})
            else:
                conn.close()
                self.send_json({"error": "Campaña no encontrada"}, 404)
            return

        # Solicitar retiro de saldo
        if path == "/api/withdrawals":
            amount = float(body.get("amount", 0))
            method = body.get("payment_method")
            destination = body.get("destination_account")

            if amount < 5.0:
                self.send_json({"error": "El monto mínimo de retiro es $5.00 USD"}, 400)
                return

            conn = get_db()
            user = conn.execute("SELECT balance_earnings FROM users WHERE id = 1").fetchone()

            if user["balance_earnings"] < amount:
                conn.close()
                self.send_json({"error": "Saldo insuficiente"}, 400)
                return

            fee = 1.0 if "TRC-20" in method else round(amount * 0.02, 2)
            net_amount = round(amount - fee, 2)

            conn.execute("UPDATE users SET balance_earnings = balance_earnings - ? WHERE id = 1", (amount,))
            conn.execute("""
                INSERT INTO withdrawals (user_id, amount, fee, net_amount, payment_method, destination_account, status)
                VALUES (1, ?, ?, ?, ?, ?, 'pending')
            """, (amount, fee, net_amount, method, destination))

            new_balance = conn.execute("SELECT balance_earnings FROM users WHERE id = 1").fetchone()[0]
            conn.commit()
            conn.close()

            self.send_json({
                "success": True,
                "new_balance": round(new_balance, 4)
            })
            return

        # Acción de SuperAdmin sobre retiros (Aprobar / Rechazar)
        if path == "/api/admin/withdrawals/action":
            withdrawal_id = body.get("withdrawal_id")
            action = body.get("action") # 'approve' o 'reject'

            conn = get_db()
            withdrawal = conn.execute("SELECT * FROM withdrawals WHERE id = ?", (withdrawal_id,)).fetchone()
            if not withdrawal:
                conn.close()
                self.send_json({"error": "Retiro no encontrado"}, 404)
                return

            if action == "approve":
                conn.execute("UPDATE withdrawals SET status = 'approved' WHERE id = ?", (withdrawal_id,))
            elif action == "reject":
                conn.execute("UPDATE withdrawals SET status = 'rejected' WHERE id = ?", (withdrawal_id,))
                # Devolver el monto al saldo del usuario
                conn.execute("UPDATE users SET balance_earnings = balance_earnings + ? WHERE id = ?", (withdrawal["amount"], withdrawal["user_id"]))

            conn.commit()
            conn.close()
            self.send_json({"success": True})
            return

        # Acción de SuperAdmin sobre campañas (Aprobar / Rechazar)
        if path == "/api/admin/campaigns/action":
            campaign_id = body.get("campaign_id")
            action = body.get("action") # 'approve' o 'reject'

            conn = get_db()
            campaign = conn.execute("SELECT * FROM ad_campaigns WHERE id = ?", (campaign_id,)).fetchone()
            if not campaign:
                conn.close()
                self.send_json({"error": "Campaña no encontrada"}, 404)
                return

            if action == "approve":
                conn.execute("UPDATE ad_campaigns SET status = 'active' WHERE id = ?", (campaign_id,))
            elif action == "reject":
                conn.execute("UPDATE ad_campaigns SET status = 'rejected' WHERE id = ?", (campaign_id,))
                # Reembolsar presupuesto al anunciante
                conn.execute("UPDATE users SET balance_advertiser = balance_advertiser + ? WHERE id = ?", (campaign["total_budget"], campaign["advertiser_id"]))

            conn.commit()
            conn.close()
            self.send_json({"success": True})
            return

        self.send_error(404, "Endpoint no encontrado")

    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error leyendo archivo: {e}")


def run_server():
    init_db()
    server_address = ("", PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, RewardPlatformHandler)
    print(f"🚀 Servidor de Plataforma de Anuncios iniciado en: http://localhost:{PORT}")
    print(f"📁 Directorio de archivos: {STATIC_DIR}")
    print("Presiona Ctrl+C para detener el servidor.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando servidor...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
