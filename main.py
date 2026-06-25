"""Punto de entrada principal del sistema administrativo Happy Burger (CLI)."""

import os
import sys

from database import initialize_db
from cliente import Cliente
from producto import Producto
from pedido import Pedido


# ─── Utilidades de consola ────────────────────────────────────────────────────

def limpiar_pantalla() -> None:
    """Limpia la pantalla del terminal según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def pausa() -> None:
    """Detiene la ejecución hasta que el usuario presione Enter."""
    input("\n  Presiona Enter para continuar...")


def encabezado(titulo: str) -> None:
    """Imprime un encabezado con el nombre de la sección activa."""
    print("=" * 47)
    print(f"    HAPPY BURGER  |  {titulo}")
    print("=" * 47)


# ─── Módulo Clientes ──────────────────────────────────────────────────────────

def menu_clientes() -> None:
    """Muestra y gestiona el submenú de Clientes."""
    while True:
        limpiar_pantalla()
        encabezado("CLIENTES")
        print("  1. Agregar cliente")
        print("  2. Actualizar cliente")
        print("  3. Eliminar cliente")
        print("  4. Listar clientes")
        print("  0. Volver al menú principal")
        opcion = input("\n  Selecciona: ").strip()
        if opcion == "1":   _agregar_cliente()
        elif opcion == "2": _actualizar_cliente()
        elif opcion == "3": _eliminar_cliente()
        elif opcion == "4": _listar_clientes()
        elif opcion == "0": break
        else:
            print("\n  Opción inválida.")
            pausa()


def _agregar_cliente() -> None:
    limpiar_pantalla(); encabezado("AGREGAR CLIENTE")
    clave    = input("  Clave        : ").strip()
    nombre   = input("  Nombre       : ").strip()
    direccion= input("  Dirección    : ").strip()
    correo   = input("  Correo       : ").strip()
    telefono = input("  Teléfono     : ").strip()
    Cliente(clave, nombre, direccion, correo, telefono).agregar_cliente()
    pausa()


def _actualizar_cliente() -> None:
    limpiar_pantalla(); encabezado("ACTUALIZAR CLIENTE")
    clave = input("  Clave del cliente              : ").strip()
    print("  Campos: nombre, direccion, correo_electronico, telefono")
    campo = input("  Campo a modificar              : ").strip()
    nuevo = input("  Nuevo valor                    : ").strip()
    Cliente.actualizar_cliente(clave, campo, nuevo)
    pausa()


def _eliminar_cliente() -> None:
    limpiar_pantalla(); encabezado("ELIMINAR CLIENTE")
    clave = input("  Clave del cliente a eliminar   : ").strip()
    if input(f"  ¿Eliminar cliente '{clave}'? (s/n): ").strip().lower() == "s":
        Cliente.eliminar_cliente(clave)
    else:
        print("\n  Operación cancelada.")
    pausa()


def _listar_clientes() -> None:
    limpiar_pantalla(); encabezado("LISTA DE CLIENTES")
    clientes = Cliente.listar_clientes()
    if not clientes:
        print("  No hay clientes registrados.")
    else:
        print(f"  {'Clave':<12} {'Nombre':<25} {'Teléfono':<15}")
        print("  " + "-" * 52)
        for c in clientes:
            print(f"  {c['clave']:<12} {c['nombre']:<25} {c['telefono']:<15}")
    pausa()


# ─── Módulo Productos ─────────────────────────────────────────────────────────

def menu_productos() -> None:
    """Muestra y gestiona el submenú de Productos (Menú)."""
    while True:
        limpiar_pantalla()
        encabezado("MENÚ / PRODUCTOS")
        print("  1. Agregar producto")
        print("  2. Actualizar producto")
        print("  3. Eliminar producto")
        print("  4. Listar productos")
        print("  0. Volver al menú principal")
        opcion = input("\n  Selecciona: ").strip()
        if opcion == "1":   _agregar_producto()
        elif opcion == "2": _actualizar_producto()
        elif opcion == "3": _eliminar_producto()
        elif opcion == "4": _listar_productos()
        elif opcion == "0": break
        else:
            print("\n  Opción inválida.")
            pausa()


def _agregar_producto() -> None:
    limpiar_pantalla(); encabezado("AGREGAR PRODUCTO")
    clave  = input("  Clave   : ").strip()
    nombre = input("  Nombre  : ").strip()
    try:
        precio = float(input("  Precio  $: ").strip())
    except ValueError:
        print("\n  Precio inválido."); pausa(); return
    Producto(clave, nombre, precio).agregar_producto()
    pausa()


def _actualizar_producto() -> None:
    limpiar_pantalla(); encabezado("ACTUALIZAR PRODUCTO")
    clave = input("  Clave del producto             : ").strip()
    print("  Campos: nombre, precio")
    campo = input("  Campo a modificar              : ").strip()
    nuevo: str | float = input("  Nuevo valor                    : ").strip()
    if campo == "precio":
        try:
            nuevo = float(nuevo)
        except ValueError:
            print("\n  Precio inválido."); pausa(); return
    Producto.actualizar_producto(clave, campo, nuevo)
    pausa()


def _eliminar_producto() -> None:
    limpiar_pantalla(); encabezado("ELIMINAR PRODUCTO")
    clave = input("  Clave del producto a eliminar  : ").strip()
    if input(f"  ¿Eliminar producto '{clave}'? (s/n): ").strip().lower() == "s":
        Producto.eliminar_producto(clave)
    else:
        print("\n  Operación cancelada.")
    pausa()


def _listar_productos() -> None:
    limpiar_pantalla(); encabezado("LISTA DE PRODUCTOS")
    productos = Producto.listar_productos()
    if not productos:
        print("  No hay productos registrados.")
    else:
        print(f"  {'Clave':<12} {'Nombre':<28} {'Precio':>10}")
        print("  " + "-" * 52)
        for p in productos:
            print(f"  {p['clave']:<12} {p['nombre']:<28} ${p['precio']:>9.2f}")
    pausa()


# ─── Módulo Pedidos ───────────────────────────────────────────────────────────

def menu_pedidos() -> None:
    """Muestra y gestiona el submenú de Pedidos."""
    while True:
        limpiar_pantalla()
        encabezado("PEDIDOS")
        print("  1. Crear pedido")
        print("  2. Cancelar pedido")
        print("  3. Consultar pedido")
        print("  0. Volver al menú principal")
        opcion = input("\n  Selecciona: ").strip()
        if opcion == "1":   _crear_pedido()
        elif opcion == "2": _cancelar_pedido()
        elif opcion == "3": _consultar_pedido()
        elif opcion == "0": break
        else:
            print("\n  Opción inválida.")
            pausa()


def _seleccionar_cliente():
    clientes = Cliente.listar_clientes()
    if not clientes:
        print("\n  No hay clientes. Agrega uno primero.")
        return None, None
    print(f"\n  {'#':<4} {'Clave':<12} {'Nombre':<25}")
    print("  " + "-" * 42)
    for i, c in enumerate(clientes, 1):
        print(f"  {i:<4} {c['clave']:<12} {c['nombre']:<25}")
    try:
        idx = int(input("\n  Número del cliente: ")) - 1
        if 0 <= idx < len(clientes):
            return clientes[idx]["id_cliente"], clientes[idx]["nombre"]
    except ValueError:
        pass
    print("\n  Selección inválida.")
    return None, None


def _seleccionar_producto():
    productos = Producto.listar_productos()
    if not productos:
        print("\n  No hay productos. Agrega uno primero.")
        return None, None, None
    print(f"\n  {'#':<4} {'Clave':<12} {'Nombre':<25} {'Precio':>10}")
    print("  " + "-" * 52)
    for i, p in enumerate(productos, 1):
        print(f"  {i:<4} {p['clave']:<12} {p['nombre']:<25} ${p['precio']:>9.2f}")
    try:
        idx = int(input("\n  Número del producto: ")) - 1
        if 0 <= idx < len(productos):
            return productos[idx]["id_producto"], productos[idx]["nombre"], productos[idx]["precio"]
    except ValueError:
        pass
    print("\n  Selección inválida.")
    return None, None, None


def _siguiente_numero_pedido() -> str:
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM Pedidos")
    total = cursor.fetchone()["total"]
    conn.close()
    return f"PED-{total + 1:04d}"


def _crear_pedido() -> None:
    """Permite agregar varios productos al mismo pedido."""
    limpiar_pantalla(); encabezado("CREAR PEDIDO")

    id_cliente, nombre_cliente = _seleccionar_cliente()
    if id_cliente is None:
        pausa(); return

    detalles = []
    while True:
        print(f"\n  ── Línea {len(detalles) + 1} ──────────────────────────")
        id_p, nombre_p, precio = _seleccionar_producto()
        if id_p is None:
            break
        try:
            cantidad = int(input("  Cantidad: "))
            if cantidad <= 0: raise ValueError
        except ValueError:
            print("  Cantidad inválida."); break

        detalles.append({"id_producto": id_p, "cantidad": cantidad, "precio": precio})
        print(f"  Agregado: {nombre_p} x{cantidad} = ${precio * cantidad:.2f}")

        if input("\n  ¿Agregar otro producto? (s/n): ").strip().lower() != "s":
            break

    if not detalles:
        print("\n  No se agregaron productos. Pedido cancelado.")
        pausa(); return

    total = sum(d["precio"] * d["cantidad"] for d in detalles)
    print(f"\n  ── Resumen ──────────────────────────────")
    print(f"  Cliente : {nombre_cliente}")
    for d in detalles:
        from database import get_connection
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT nombre FROM Productos WHERE id_producto=?", (d["id_producto"],))
        pnombre = c.fetchone()["nombre"]; conn.close()
        print(f"  {pnombre[:30]:<30} x{d['cantidad']} ${d['precio'] * d['cantidad']:.2f}")
    print(f"  {'TOTAL':<35} ${total:.2f}")
    print("  ─────────────────────────────────────────")

    if input("\n  Confirmar pedido (s/n): ").strip().lower() == "s":
        numero = _siguiente_numero_pedido()
        Pedido(numero, id_cliente, detalles).crear_pedido()
    else:
        print("\n  Pedido no creado.")
    pausa()


def _cancelar_pedido() -> None:
    limpiar_pantalla(); encabezado("CANCELAR PEDIDO")
    numero = input("  Número de pedido a cancelar: ").strip()
    if input(f"  ¿Cancelar '{numero}'? (s/n): ").strip().lower() == "s":
        Pedido.cancelar_pedido(numero)
    else:
        print("\n  Operación cancelada.")
    pausa()


def _consultar_pedido() -> None:
    limpiar_pantalla(); encabezado("CONSULTAR PEDIDO")
    numero = input("  Número de pedido: ").strip()
    resultado = Pedido.consultar_pedido(numero)
    if resultado:
        h = resultado["header"]
        print(f"\n  Número  : {h['numero_pedido']}")
        print(f"  Fecha   : {h['fecha']}")
        print(f"  Cliente : {h['cliente']}")
        print(f"  Estado  : {h['estado']}")
        print(f"\n  {'Producto':<28} {'Cant':>4} {'Precio':>9} {'Total':>10}")
        print("  " + "-" * 54)
        for d in resultado["detalles"]:
            print(f"  {d['producto'][:28]:<28} {d['cantidad']:>4} "
                  f"${d['precio']:>8.2f} ${d['subtotal']:>9.2f}")
        print(f"\n  {'TOTAL':<45} ${h['subtotal']:>9.2f}")
    else:
        print(f"\n  Pedido '{numero}' no encontrado.")
    pausa()


# ─── Menú Principal ───────────────────────────────────────────────────────────

def menu_principal() -> None:
    """Inicializa la base de datos y ejecuta el bucle del menú principal."""
    initialize_db()
    while True:
        limpiar_pantalla()
        print("=" * 47)
        print("       HAPPY BURGER — SISTEMA ADMIN")
        print("=" * 47)
        print("  1. Pedidos")
        print("  2. Clientes")
        print("  3. Menú")
        print("  4. Salir")
        print("=" * 47)
        opcion = input("\n  Selecciona una opción: ").strip()
        if opcion == "1":   menu_pedidos()
        elif opcion == "2": menu_clientes()
        elif opcion == "3": menu_productos()
        elif opcion == "4":
            print("\n  Hasta luego! Gracias por usar Happy Burger.\n")
            sys.exit(0)
        else:
            print("\n  Opción inválida.")
            pausa()


if __name__ == "__main__":
    menu_principal()
