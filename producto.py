"""Módulo con la clase Producto y sus operaciones CRUD sobre SQLite."""

from base import EntidadBase
from database import get_connection


class Producto(EntidadBase):
    """Representa un producto del menú de Happy Burger.

    Hereda clave y nombre de EntidadBase y agrega el precio
    unitario propio de un artículo del menú.

    Attributes:
        clave (str): Identificador único legible del producto.
        nombre (str): Nombre del producto.
        precio (float): Precio unitario del producto.
    """

    def __init__(self, clave: str, nombre: str, precio: float) -> None:
        """Inicializa una instancia de Producto con sus datos básicos."""
        super().__init__(clave, nombre)
        self.precio = precio

    def agregar_producto(self) -> None:
        """Inserta este producto en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Productos (clave, nombre, precio) VALUES (?, ?, ?)",
                (self.clave, self.nombre, self.precio),
            )
            conn.commit()
            print(f"\n  Producto '{self.nombre}' agregado correctamente.")
        except Exception as e:
            print(f"\n  Error al agregar producto: {e}")
        finally:
            conn.close()

    @staticmethod
    def actualizar_producto(clave: str, campo: str, nuevo_valor) -> None:
        """Actualiza un campo específico del producto identificado por su clave.

        Args:
            clave: Clave única del producto a modificar.
            campo: Nombre del campo a actualizar ('nombre' o 'precio').
            nuevo_valor: Nuevo valor para ese campo.
        """
        campos_validos = {"nombre", "precio"}
        if campo not in campos_validos:
            print(f"\n  Campo inválido. Opciones: {', '.join(sorted(campos_validos))}")
            return
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"UPDATE Productos SET {campo} = ? WHERE clave = ?",
                (nuevo_valor, clave),
            )
            if cursor.rowcount == 0:
                print(f"\n  No se encontró producto con clave '{clave}'.")
            else:
                conn.commit()
                print("\n  Producto actualizado correctamente.")
        except Exception as e:
            print(f"\n  Error al actualizar producto: {e}")
        finally:
            conn.close()

    @staticmethod
    def eliminar_producto(clave: str) -> None:
        """Elimina de la base de datos el producto con la clave indicada.

        Args:
            clave: Clave única del producto a eliminar.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Productos WHERE clave = ?", (clave,))
            if cursor.rowcount == 0:
                print(f"\n  No se encontró producto con clave '{clave}'.")
            else:
                conn.commit()
                print(f"\n  Producto '{clave}' eliminado.")
        except Exception as e:
            print(f"\n  Error al eliminar producto: {e}")
        finally:
            conn.close()

    @staticmethod
    def listar_productos() -> list:
        """Retorna todos los productos registrados ordenados por nombre."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Productos ORDER BY nombre")
        productos = cursor.fetchall()
        conn.close()
        return productos
