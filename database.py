"""Módulo de conexión y configuración de la base de datos SQLite."""

import sqlite3

DB_NAME = "happy_burger.db"


def get_connection():
    """Retorna una conexión activa a la base de datos happy_burger.db."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Crea tablas y aplica migraciones necesarias."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Tabla Clientes ────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Clientes (
            id_cliente         INTEGER PRIMARY KEY AUTOINCREMENT,
            clave              TEXT    NOT NULL UNIQUE,
            nombre             TEXT    NOT NULL,
            direccion          TEXT,
            correo_electronico TEXT,
            telefono           TEXT
        )
    """)

    # ── Tabla Productos ───────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            clave       TEXT    NOT NULL UNIQUE,
            nombre      TEXT    NOT NULL,
            precio      REAL    NOT NULL
        )
    """)

    # ── Migración: reconstruir Pedidos con columnas opcionales ─
    cursor.execute("PRAGMA table_info(Pedidos)")
    cols = {row["name"]: dict(row) for row in cursor.fetchall()}

    if cols and cols.get("id_producto", {}).get("notnull", 0) == 1:
        cursor.executescript("""
            PRAGMA foreign_keys = OFF;

            CREATE TABLE IF NOT EXISTS _Pedidos_tmp (
                id_pedido     INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido TEXT    NOT NULL UNIQUE,
                id_cliente    INTEGER NOT NULL,
                id_producto   INTEGER,
                cantidad      INTEGER,
                precio        REAL,
                subtotal      REAL    NOT NULL DEFAULT 0,
                fecha         TEXT    NOT NULL,
                estado        TEXT    DEFAULT 'pendiente',
                FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
            );

            INSERT INTO _Pedidos_tmp
            SELECT id_pedido, numero_pedido, id_cliente, id_producto,
                   cantidad, precio, subtotal, fecha,
                   COALESCE(estado, 'pendiente')
            FROM Pedidos;

            DROP TABLE Pedidos;
            ALTER TABLE _Pedidos_tmp RENAME TO Pedidos;

            PRAGMA foreign_keys = ON;
        """)
        conn.commit()

    # ── Tabla Pedidos (nueva o ya migrada) ────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pedidos (
            id_pedido     INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_pedido TEXT    NOT NULL UNIQUE,
            id_cliente    INTEGER NOT NULL,
            id_producto   INTEGER,
            cantidad      INTEGER,
            precio        REAL,
            subtotal      REAL    NOT NULL DEFAULT 0,
            fecha         TEXT    NOT NULL,
            estado        TEXT    DEFAULT 'pendiente',
            FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
        )
    """)

    # ── Tabla DetallePedido (líneas por pedido) ───────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DetallePedido (
            id_detalle  INTEGER PRIMARY KEY AUTOINCREMENT,
            id_pedido   INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad    INTEGER NOT NULL,
            precio      REAL    NOT NULL,
            subtotal    REAL    NOT NULL,
            FOREIGN KEY (id_pedido)   REFERENCES Pedidos(id_pedido),
            FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
        )
    """)

    # ── Migrar pedidos legados a DetallePedido ─────────────────
    try:
        cursor.execute("""
            INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, precio, subtotal)
            SELECT p.id_pedido, p.id_producto, p.cantidad, p.precio, p.subtotal
            FROM   Pedidos p
            WHERE  p.id_producto IS NOT NULL
            AND    p.id_pedido NOT IN (SELECT DISTINCT id_pedido FROM DetallePedido)
        """)
    except Exception:
        pass

    # ── Agregar columna estado si falta ───────────────────────
    try:
        cursor.execute("ALTER TABLE Pedidos ADD COLUMN estado TEXT DEFAULT 'pendiente'")
    except Exception:
        pass

    conn.commit()
    conn.close()
