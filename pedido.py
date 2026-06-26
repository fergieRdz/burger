"""Módulo con la clase Pedido, generación de tickets y operaciones en SQLite."""

import os
from datetime import datetime

from base import EntidadBase
from database import get_connection

TICKETS_DIR = "tickets"


class Pedido(EntidadBase):
    """Representa un pedido de Happy Burger con uno o varios productos.

    Hereda clave y nombre de EntidadBase, usando numero_pedido como
    clave identificadora y una descripción generada como nombre.

    Attributes:
        numero_pedido (str): Identificador único del pedido (mismo que clave).
        id_cliente (int): ID del cliente en la base de datos.
        detalles (list): Lista de dicts con {id_producto, cantidad, precio}.
        subtotal (float): Total calculado sumando todas las líneas.
        fecha (str): Fecha y hora de creación del pedido.
        estado (str): 'pendiente' o 'completado'.
    """

    def __init__(self, numero_pedido: str, id_cliente: int,
                 detalles: list, fecha: str = None) -> None:
        """Inicializa el pedido, hereda clave/nombre y calcula el subtotal."""
        super().__init__(numero_pedido, f"Pedido {numero_pedido}")
        self.numero_pedido = numero_pedido
        self.id_cliente = id_cliente
        self.detalles = detalles  # [{id_producto, cantidad, precio}, ...]
        self.subtotal = sum(d["precio"] * d["cantidad"] for d in detalles)
        self.fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.estado = "pendiente"

    def crear_pedido(self) -> None:
        """Guarda el pedido y sus líneas en la base de datos; genera ticket TXT."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Encabezado del pedido
            cursor.execute("""
                INSERT INTO Pedidos (numero_pedido, id_cliente, subtotal, fecha, estado)
                VALUES (?, ?, ?, ?, 'pendiente')
            """, (self.numero_pedido, self.id_cliente, self.subtotal, self.fecha))
            id_pedido = cursor.lastrowid

            # Líneas de detalle
            for d in self.detalles:
                sub = d["precio"] * d["cantidad"]
                cursor.execute("""
                    INSERT INTO DetallePedido (id_pedido, id_producto, cantidad, precio, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_pedido, d["id_producto"], d["cantidad"], d["precio"], sub))

            conn.commit()
            self._generar_ticket(cursor, id_pedido)
            print(f"\n  Pedido {self.numero_pedido} creado correctamente.")
        except Exception as e:
            print(f"\n  Error al crear pedido: {e}")
        finally:
            conn.close()

    def _generar_ticket(self, cursor, id_pedido: int) -> None:
        """Genera un archivo TXT con el resumen completo del pedido.

        Args:
            cursor: Cursor SQLite activo.
            id_pedido: ID del pedido recién creado.
        """
        cursor.execute("SELECT nombre FROM Clientes WHERE id_cliente=?", (self.id_cliente,))
        fila = cursor.fetchone()
        cliente_nombre = fila["nombre"] if fila else "Desconocido"

        cursor.execute("""
            SELECT pr.nombre, dp.cantidad, dp.precio, dp.subtotal
            FROM DetallePedido dp
            JOIN Productos pr ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = ?
        """, (id_pedido,))
        lineas = cursor.fetchall()

        os.makedirs(TICKETS_DIR, exist_ok=True)
        ruta = os.path.join(TICKETS_DIR, f"ticket_{self.numero_pedido}.txt")
        sep = "=" * 44

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"{sep}\n")
            f.write(f"             HAPPY BURGER\n")
            f.write(f"{sep}\n")
            f.write(f"Numero de pedido : {self.numero_pedido}\n")
            f.write(f"Fecha            : {self.fecha}\n")
            f.write(f"Cliente          : {cliente_nombre}\n")
            f.write(f"{sep}\n")
            f.write(f"{'Producto':<22} {'Cant':>4} {'P.Unit':>8} {'Total':>9}\n")
            f.write(f"{'-' * 44}\n")
            for l in lineas:
                f.write(f"{l['nombre'][:22]:<22} {l['cantidad']:>4} "
                        f"${l['precio']:>7.2f} ${l['subtotal']:>8.2f}\n")
            f.write(f"{sep}\n")
            f.write(f"{'TOTAL':>35} ${self.subtotal:>8.2f}\n")
            f.write(f"{sep}\n")
            f.write(f"       Gracias por tu preferencia!\n")
            f.write(f"{sep}\n")

        print(f"  Ticket guardado en: {ruta}")

    @staticmethod
    def cancelar_pedido(numero_pedido: str) -> None:
        """Elimina un pedido y sus líneas de detalle.

        Args:
            numero_pedido: Número único del pedido a cancelar.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_pedido FROM Pedidos WHERE numero_pedido=?", (numero_pedido,))
            row = cursor.fetchone()
            if row:
                cursor.execute("DELETE FROM DetallePedido WHERE id_pedido=?", (row["id_pedido"],))
                cursor.execute("DELETE FROM Pedidos WHERE id_pedido=?", (row["id_pedido"],))
                conn.commit()
                print(f"\n  Pedido {numero_pedido} cancelado.")
            else:
                print(f"\n  No se encontró el pedido {numero_pedido}.")
        except Exception as e:
            print(f"\n  Error al cancelar pedido: {e}")
        finally:
            conn.close()

    @staticmethod
    def consultar_pedido(numero_pedido: str):
        """Retorna el encabezado y las líneas de detalle de un pedido.

        Args:
            numero_pedido: Número único del pedido a buscar.

        Returns:
            Dict con 'header' (Row) y 'detalles' (list of Row), o None.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id_pedido, p.numero_pedido, p.fecha, p.subtotal, p.estado,
                   c.nombre AS cliente
            FROM Pedidos p
            JOIN Clientes c ON p.id_cliente = c.id_cliente
            WHERE p.numero_pedido = ?
        """, (numero_pedido,))
        header = cursor.fetchone()
        if not header:
            conn.close()
            return None
        cursor.execute("""
            SELECT pr.nombre AS producto, dp.cantidad, dp.precio, dp.subtotal
            FROM DetallePedido dp
            JOIN Productos pr ON dp.id_producto = pr.id_producto
            WHERE dp.id_pedido = ?
        """, (header["id_pedido"],))
        detalles = cursor.fetchall()
        conn.close()
        return {"header": header, "detalles": detalles}
