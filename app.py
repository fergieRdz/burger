"""Interfaz web Flask para el sistema administrativo Happy Burger."""

import json
import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort

from database import initialize_db, get_connection
from cliente import Cliente
from producto import Producto
from pedido import Pedido

app = Flask(__name__)
app.secret_key = "happyburger_admin_2026"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _stats():
    """Retorna métricas globales del sistema."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) AS n FROM Clientes")
    tc = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) AS n FROM Productos")
    tp = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) AS n FROM Pedidos")
    tped = c.fetchone()["n"]
    c.execute("SELECT COALESCE(SUM(subtotal),0) AS s FROM Pedidos")
    tv = c.fetchone()["s"]
    conn.close()
    return tc, tp, tped, tv


def _ultimos_pedidos(limit=5):
    """Retorna los últimos pedidos con resumen de productos."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.numero_pedido, p.fecha, p.subtotal, p.estado,
               cl.nombre AS cliente,
               GROUP_CONCAT(pr.nombre || ' x' || dp.cantidad, ' | ') AS productos_resumen
        FROM Pedidos p
        JOIN Clientes cl ON p.id_cliente = cl.id_cliente
        JOIN DetallePedido dp ON p.id_pedido = dp.id_pedido
        JOIN Productos pr ON dp.id_producto = pr.id_producto
        GROUP BY p.id_pedido
        ORDER BY p.id_pedido DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def _todos_pedidos_con_detalle(estado=None, fecha=None):
    """Retorna pedidos con resumen de productos, opcionalmente filtrados."""
    conn = get_connection()
    c = conn.cursor()
    sql = """
        SELECT p.numero_pedido, p.fecha, p.subtotal, p.estado,
               cl.nombre AS cliente,
               GROUP_CONCAT(pr.nombre || ' x' || dp.cantidad, ' | ') AS productos_resumen,
               COUNT(dp.id_detalle) AS num_productos
        FROM Pedidos p
        JOIN Clientes cl ON p.id_cliente = cl.id_cliente
        JOIN DetallePedido dp ON p.id_pedido = dp.id_pedido
        JOIN Productos pr ON dp.id_producto = pr.id_producto
        WHERE 1=1
    """
    params = []
    if estado in ("pendiente", "completado"):
        sql += " AND p.estado = ?"
        params.append(estado)
    if fecha:
        sql += " AND DATE(p.fecha) = ?"
        params.append(fecha)
    sql += " GROUP BY p.id_pedido ORDER BY p.id_pedido DESC"
    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()
    return rows


def _get_cliente(id_cliente):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Clientes WHERE id_cliente=?", (id_cliente,))
    row = c.fetchone()
    conn.close()
    return row


def _get_producto(id_producto):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Productos WHERE id_producto=?", (id_producto,))
    row = c.fetchone()
    conn.close()
    return row


def _siguiente_numero_pedido():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) AS total FROM Pedidos")
    total = c.fetchone()["total"]
    conn.close()
    return f"PED-{total + 1:04d}"


# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """Renderiza el dashboard con métricas y últimos pedidos."""
    tc, tp, tped, tv = _stats()
    return render_template(
        "index.html", active="dashboard",
        total_clientes=tc, total_productos=tp,
        total_pedidos=tped, total_ventas=tv,
        ultimos_pedidos=_ultimos_pedidos(),
    )


# ─── Catálogos ────────────────────────────────────────────────────────────────

@app.route("/catalogos")
def catalogos():
    clientes = Cliente.listar_clientes()
    productos = Producto.listar_productos()
    _, _, tped, _ = _stats()
    return render_template("catalogos.html", active="catalogos",
                           clientes=clientes, productos=productos, total_pedidos=tped)


# ─── Clientes CRUD ────────────────────────────────────────────────────────────

@app.route("/clientes")
def clientes():
    lista = Cliente.listar_clientes()
    return render_template("clientes.html", active="clientes", clientes=lista)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def cliente_nuevo():
    if request.method == "POST":
        clave     = request.form.get("clave", "").strip()
        nombre    = request.form.get("nombre", "").strip()
        direccion = request.form.get("direccion", "").strip()
        correo    = request.form.get("correo_electronico", "").strip()
        telefono  = request.form.get("telefono", "").strip()
        if not clave or not nombre:
            flash("La clave y el nombre son obligatorios.", "error")
            return render_template("form_cliente.html", active="clientes",
                                   accion="Agregar", cliente=None)
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Clientes (clave,nombre,direccion,correo_electronico,telefono) VALUES(?,?,?,?,?)",
                (clave, nombre, direccion, correo, telefono),
            )
            conn.commit()
            flash(f"Cliente '{nombre}' agregado correctamente.", "success")
            return redirect(url_for("clientes"))
        except Exception:
            flash(f"La clave '{clave}' ya existe.", "error")
        finally:
            conn.close()
    return render_template("form_cliente.html", active="clientes", accion="Agregar", cliente=None)


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def cliente_editar(id_cliente):
    cliente = _get_cliente(id_cliente)
    if not cliente:
        flash("Cliente no encontrado.", "error")
        return redirect(url_for("clientes"))
    if request.method == "POST":
        nombre    = request.form.get("nombre", "").strip()
        direccion = request.form.get("direccion", "").strip()
        correo    = request.form.get("correo_electronico", "").strip()
        telefono  = request.form.get("telefono", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "error")
            return render_template("form_cliente.html", active="clientes",
                                   accion="Editar", cliente=cliente)
        conn = get_connection()
        conn.execute(
            "UPDATE Clientes SET nombre=?,direccion=?,correo_electronico=?,telefono=? WHERE id_cliente=?",
            (nombre, direccion, correo, telefono, id_cliente),
        )
        conn.commit(); conn.close()
        flash(f"Cliente '{nombre}' actualizado.", "success")
        return redirect(url_for("clientes"))
    return render_template("form_cliente.html", active="clientes", accion="Editar", cliente=cliente)


@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
def cliente_eliminar(id_cliente):
    cliente = _get_cliente(id_cliente)
    if cliente:
        conn = get_connection()
        conn.execute("DELETE FROM Clientes WHERE id_cliente=?", (id_cliente,))
        conn.commit(); conn.close()
        flash(f"Cliente '{cliente['nombre']}' eliminado.", "success")
    else:
        flash("Cliente no encontrado.", "error")
    return redirect(url_for("clientes"))


# ─── Menú / Productos CRUD ────────────────────────────────────────────────────

@app.route("/menu")
def menu_productos():
    lista = Producto.listar_productos()
    return render_template("menu.html", active="menu", productos=lista)


@app.route("/menu/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    if request.method == "POST":
        clave  = request.form.get("clave", "").strip()
        nombre = request.form.get("nombre", "").strip()
        categoria = request.form.get("categoria", "General").strip()
        descripcion = request.form.get("descripcion", "").strip()
        precio_str = request.form.get("precio", "").strip()
        if not clave or not nombre or not precio_str:
            flash("Clave, nombre y precio son obligatorios.", "error")
            return render_template("form_producto.html", active="menu", accion="Agregar", producto=None)
        try:
            precio = float(precio_str)
            if precio <= 0: raise ValueError
        except ValueError:
            flash("El precio debe ser mayor a 0.", "error")
            return render_template("form_producto.html", active="menu", accion="Agregar", producto=None)
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Productos (clave,nombre,precio) VALUES(?,?,?)",
                (clave, nombre, precio),
            )
            conn.commit()
            flash(f"Producto '{nombre}' agregado.", "success")
            return redirect(url_for("menu_productos"))
        except Exception:
            flash(f"La clave '{clave}' ya existe.", "error")
        finally:
            conn.close()
    return render_template("form_producto.html", active="menu", accion="Agregar", producto=None)


@app.route("/menu/editar/<int:id_producto>", methods=["GET", "POST"])
def producto_editar(id_producto):
    producto = _get_producto(id_producto)
    if not producto:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("menu_productos"))
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio_str = request.form.get("precio", "").strip()
        if not nombre or not precio_str:
            flash("Todos los campos son obligatorios.", "error")
            return render_template("form_producto.html", active="menu", accion="Editar", producto=producto)
        try:
            precio = float(precio_str)
            if precio <= 0: raise ValueError
        except ValueError:
            flash("El precio debe ser mayor a 0.", "error")
            return render_template("form_producto.html", active="menu", accion="Editar", producto=producto)
        conn = get_connection()
        conn.execute("UPDATE Productos SET nombre=?,precio=? WHERE id_producto=?",
                     (nombre, precio, id_producto))
        conn.commit(); conn.close()
        flash(f"Producto '{nombre}' actualizado.", "success")
        return redirect(url_for("menu_productos"))
    return render_template("form_producto.html", active="menu", accion="Editar", producto=producto)


@app.route("/menu/eliminar/<int:id_producto>", methods=["POST"])
def producto_eliminar(id_producto):
    producto = _get_producto(id_producto)
    if producto:
        conn = get_connection()
        conn.execute("DELETE FROM Productos WHERE id_producto=?", (id_producto,))
        conn.commit(); conn.close()
        flash(f"Producto '{producto['nombre']}' eliminado.", "success")
    else:
        flash("Producto no encontrado.", "error")
    return redirect(url_for("menu_productos"))


# ─── Pedidos ──────────────────────────────────────────────────────────────────

@app.route("/pedidos", methods=["GET", "POST"])
def consulta_pedido():
    """Lista pedidos separados por estado, con filtro de fecha y búsqueda."""
    pedido_detalle = None
    buscado        = False
    numero         = ""
    filtro_fecha   = request.args.get("fecha", "")

    if request.method == "POST":
        numero  = request.form.get("numero_pedido", "").strip()
        buscado = True
        if numero:
            pedido_detalle = Pedido.consultar_pedido(numero)

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) AS n FROM Pedidos WHERE estado='pendiente'")
    total_pendientes = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) AS n FROM Pedidos WHERE estado='completado'")
    total_completados = c.fetchone()["n"]

    # Productos del día (por DetallePedido)
    dia_consulta = filtro_fecha if filtro_fecha else str(date.today())
    c.execute("""
        SELECT pr.nombre AS producto,
               SUM(dp.cantidad) AS unidades,
               SUM(dp.subtotal) AS total
        FROM DetallePedido dp
        JOIN Productos pr ON dp.id_producto = pr.id_producto
        JOIN Pedidos p    ON dp.id_pedido   = p.id_pedido
        WHERE DATE(p.fecha) = ?
        GROUP BY dp.id_producto ORDER BY unidades DESC
    """, (dia_consulta,))
    productos_del_dia = c.fetchall()
    conn.close()

    pedidos_pendientes  = _todos_pedidos_con_detalle("pendiente",  filtro_fecha)
    pedidos_completados = _todos_pedidos_con_detalle("completado", filtro_fecha)

    return render_template(
        "consulta_pedido.html", active="pedidos",
        pedido_detalle=pedido_detalle, buscado=buscado, numero=numero,
        pedidos_pendientes=pedidos_pendientes,
        pedidos_completados=pedidos_completados,
        total_pendientes=total_pendientes,
        total_completados=total_completados,
        filtro_fecha=filtro_fecha,
        dia_consulta=dia_consulta,
        productos_del_dia=productos_del_dia,
    )


@app.route("/pedidos/nuevo", methods=["GET", "POST"])
def pedido_nuevo():
    """Crea un pedido con uno o varios productos."""
    clientes_lista  = Cliente.listar_clientes()
    productos_lista = Producto.listar_productos()

    if request.method == "POST":
        id_cliente   = request.form.get("id_cliente", "").strip()
        ids_producto = request.form.getlist("id_producto")
        cantidades   = request.form.getlist("cantidad")

        if not id_cliente:
            flash("Selecciona un cliente.", "error")
            return render_template("form_pedido.html", active="pedidos",
                                   clientes=clientes_lista, productos=productos_lista)

        detalles = []
        for id_p, cant_str in zip(ids_producto, cantidades):
            if not id_p: continue
            try:
                cantidad = int(cant_str)
                if cantidad <= 0: raise ValueError
            except ValueError:
                flash("Las cantidades deben ser enteros mayores a 0.", "error")
                return render_template("form_pedido.html", active="pedidos",
                                       clientes=clientes_lista, productos=productos_lista)
            prod = _get_producto(int(id_p))
            if not prod: continue
            detalles.append({"id_producto": int(id_p), "cantidad": cantidad, "precio": prod["precio"]})

        if not detalles:
            flash("Agrega al menos un producto al pedido.", "error")
            return render_template("form_pedido.html", active="pedidos",
                                   clientes=clientes_lista, productos=productos_lista)

        numero_pedido = _siguiente_numero_pedido()
        p = Pedido(numero_pedido, int(id_cliente), detalles)
        p.crear_pedido()
        flash(f"Pedido {numero_pedido} creado con {len(detalles)} producto(s). Ticket generado.", "success")
        return redirect(url_for("consulta_pedido"))

    return render_template("form_pedido.html", active="pedidos",
                           clientes=clientes_lista, productos=productos_lista)


@app.route("/pedidos/completar/<numero_pedido>", methods=["POST"])
def pedido_completar(numero_pedido):
    """Marca un pedido como completado."""
    conn = get_connection()
    conn.execute("UPDATE Pedidos SET estado='completado' WHERE numero_pedido=?", (numero_pedido,))
    conn.commit(); conn.close()
    flash(f"Pedido {numero_pedido} marcado como completado.", "success")
    return redirect(request.referrer or url_for("consulta_pedido"))


@app.route("/pedidos/reabrir/<numero_pedido>", methods=["POST"])
def pedido_reabrir(numero_pedido):
    """Regresa un pedido completado a estado pendiente."""
    conn = get_connection()
    conn.execute("UPDATE Pedidos SET estado='pendiente' WHERE numero_pedido=?", (numero_pedido,))
    conn.commit(); conn.close()
    flash(f"Pedido {numero_pedido} regresado a pendiente.", "success")
    return redirect(request.referrer or url_for("consulta_pedido"))


@app.route("/pedidos/cancelar/<numero_pedido>", methods=["POST"])
def pedido_cancelar(numero_pedido):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_pedido FROM Pedidos WHERE numero_pedido=?", (numero_pedido,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM DetallePedido WHERE id_pedido=?", (row["id_pedido"],))
        cursor.execute("DELETE FROM Pedidos WHERE id_pedido=?", (row["id_pedido"],))
        conn.commit()
        flash(f"Pedido {numero_pedido} cancelado.", "success")
    else:
        flash("Pedido no encontrado.", "error")
    conn.close()
    return redirect(url_for("consulta_pedido"))


# ─── Reportes ─────────────────────────────────────────────────────────────────

@app.route("/reportes")
def reportes():
    """Reportes con gráficas de ventas por producto y comparativa por día."""
    tc, tp, tped, tv = _stats()
    ticket_promedio = (tv / tped) if tped > 0 else 0

    conn = get_connection()
    c = conn.cursor()

    # Top productos (unidades desde DetallePedido)
    c.execute("""
        SELECT pr.nombre AS producto,
               SUM(dp.cantidad) AS total_unidades,
               SUM(dp.subtotal) AS total_ingreso
        FROM DetallePedido dp JOIN Productos pr ON dp.id_producto=pr.id_producto
        GROUP BY dp.id_producto ORDER BY total_unidades DESC LIMIT 6
    """)
    top_productos = c.fetchall()

    # Top clientes
    c.execute("""
        SELECT cl.nombre AS cliente,
               COUNT(p.id_pedido) AS total_pedidos,
               SUM(p.subtotal) AS total_gastado
        FROM Pedidos p JOIN Clientes cl ON p.id_cliente=cl.id_cliente
        GROUP BY p.id_cliente ORDER BY total_pedidos DESC LIMIT 5
    """)
    top_clientes = c.fetchall()

    # Ventas por día (últimos 7 días)
    c.execute("""
        SELECT DATE(fecha) AS dia,
               SUM(subtotal) AS total_ventas,
               COUNT(*) AS total_pedidos
        FROM Pedidos
        GROUP BY DATE(fecha)
        ORDER BY dia DESC LIMIT 7
    """)
    ventas_diarias_raw = list(reversed(c.fetchall()))

    # Todos los pedidos
    c.execute("""
        SELECT p.numero_pedido, p.fecha, p.cantidad, p.precio, p.subtotal, p.estado,
               cl.nombre AS cliente, pr.nombre AS producto
        FROM Pedidos p
        JOIN Clientes  cl ON p.id_cliente=cl.id_cliente
        JOIN Productos pr ON p.id_producto=pr.id_producto
        ORDER BY p.id_pedido DESC
    """)
    todos_pedidos = c.fetchall()
    conn.close()

    # Datos para Chart.js (JSON)
    chart_prod_labels  = json.dumps([r["producto"] for r in top_productos])
    chart_prod_units   = json.dumps([r["total_unidades"] for r in top_productos])
    chart_prod_revenue = json.dumps([round(r["total_ingreso"], 2) for r in top_productos])

    chart_dias_labels  = json.dumps([r["dia"] for r in ventas_diarias_raw])
    chart_dias_ventas  = json.dumps([round(r["total_ventas"], 2) for r in ventas_diarias_raw])
    chart_dias_pedidos = json.dumps([r["total_pedidos"] for r in ventas_diarias_raw])

    return render_template(
        "reportes.html", active="reportes",
        total_clientes=tc, total_productos=tp,
        total_pedidos=tped, total_ventas=tv,
        ticket_promedio=ticket_promedio,
        top_productos=top_productos, top_clientes=top_clientes,
        todos_pedidos=todos_pedidos,
        chart_prod_labels=chart_prod_labels,
        chart_prod_units=chart_prod_units,
        chart_prod_revenue=chart_prod_revenue,
        chart_dias_labels=chart_dias_labels,
        chart_dias_ventas=chart_dias_ventas,
        chart_dias_pedidos=chart_dias_pedidos,
    )


@app.route("/pedidos/ticket/<numero_pedido>")
def ver_ticket(numero_pedido):
    """Muestra el ticket del pedido en pantalla con opción de descarga."""
    resultado = Pedido.consultar_pedido(numero_pedido)
    if not resultado:
        flash(f"Pedido {numero_pedido} no encontrado.", "error")
        return redirect(url_for("consulta_pedido"))

    ruta = os.path.join("tickets", f"ticket_{numero_pedido}.txt")
    ticket_txt = None
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            ticket_txt = f.read()

    return render_template(
        "ticket.html", active="pedidos",
        pedido=resultado,
        ticket_txt=ticket_txt,
        numero_pedido=numero_pedido,
    )


@app.route("/pedidos/ticket/<numero_pedido>/descargar")
def descargar_ticket(numero_pedido):
    """Descarga el archivo TXT del ticket."""
    ruta = os.path.join("tickets", f"ticket_{numero_pedido}.txt")
    if not os.path.exists(ruta):
        flash(f"No se encontró el archivo del ticket {numero_pedido}.", "error")
        return redirect(url_for("consulta_pedido"))
    return send_file(
        ruta,
        mimetype="text/plain",
        as_attachment=True,
        download_name=f"ticket_{numero_pedido}.txt",
    )


if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
