-- Esquema de Base de Datos para Plataforma de Anuncios y Recompensas (SQLite)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user', -- 'user', 'advertiser', 'admin'
    balance_earnings REAL NOT NULL DEFAULT 0.0000,
    balance_advertiser REAL NOT NULL DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ad_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    advertiser_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    target_url TEXT NOT NULL,
    description TEXT,
    cost_per_view REAL NOT NULL,
    user_reward REAL NOT NULL,
    total_budget REAL NOT NULL,
    remaining_budget REAL NOT NULL,
    duration_seconds INTEGER NOT NULL DEFAULT 15,
    views_delivered INTEGER NOT NULL DEFAULT 0,
    total_views INTEGER NOT NULL DEFAULT 100,
    status TEXT NOT NULL DEFAULT 'active', -- 'pending', 'active', 'paused', 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(advertiser_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS ad_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    session_token TEXT UNIQUE NOT NULL,
    started_at REAL NOT NULL, -- Unix timestamp en segundos
    completed_at REAL,
    reward_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'in_progress', -- 'in_progress', 'completed', 'invalid'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES ad_campaigns(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    fee REAL NOT NULL DEFAULT 0.0,
    net_amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    destination_account TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'ad_reward', 'ad_deposit', 'withdrawal', 'refund'
    amount REAL NOT NULL,
    balance_after REAL NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
