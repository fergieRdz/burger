"""Módulo con la clase Cliente y sus operaciones CRUD sobre SQLite."""

from base import EntidadBase
from database import get_connection


class Cliente(EntidadBase):
    """Representa a un cliente registrado en Happy Burger.

    Hereda clave y nombre de EntidadBase y agrega los datos
    de contacto propios de un cliente.

    Attributes:
        clave (str): Identificador único legible del cliente.
        nombre (str): Nombre completo del cliente.
        direccion (str): Dirección de entrega.
        correo_electronico (str): Correo de contacto.
        telefono (str): Número de teléfono.
    """

    def __init__(self, clave: str, nombre: str, direccion: str,
                 correo_electronico: str, telefono: str) -> None:
        """Inicializa una instancia de Cliente con sus datos básicos."""
        super().__init__(clave, nombre)
        self.direccion = direccion
        self.correo_electronico = correo_electronico
        self.telefono = telefono

    def agregar_cliente(self) -> None:
        """Inserta este cliente en la base de datos."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO Clientes (clave, nombre, direccion, correo_electronico, telefono)
                   VALUES (?, ?, ?, ?, ?)""",
                (self.clave, self.nombre, self.direccion,
                 self.correo_electronico, self.telefono),
            )
            conn.commit()
            print(f"\n  Cliente '{self.nombre}' agregado correctamente.")
        except Exception as e:
            print(f"\n  Error al agregar cliente: {e}")
        finally:
            conn.close()

    @staticmethod
    def actualizar_cliente(clave: str, campo: str, nuevo_valor: str) -> None:
        """Actualiza un campo específico del cliente identificado por su clave.

        Args:
            clave: Clave única del cliente a modificar.
            campo: Nombre del campo a actualizar.
            nuevo_valor: Nuevo valor para ese campo.
        """
        campos_validos = {"nombre", "direccion", "correo_electronico", "telefono"}
        if campo not in campos_validos:
            print(f"\n  Campo inválido. Opciones: {', '.join(sorted(campos_validos))}")
            return
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"UPDATE Clientes SET {campo} = ? WHERE clave = ?",
                (nuevo_valor, clave),
            )
            if cursor.rowcount == 0:
                print(f"\n  No se encontró cliente con clave '{clave}'.")
            else:
                conn.commit()
                print("\n  Cliente actualizado correctamente.")
        except Exception as e:
            print(f"\n  Error al actualizar cliente: {e}")
        finally:
            conn.close()

    @staticmethod
    def eliminar_cliente(clave: str) -> None:
        """Elimina de la base de datos al cliente con la clave indicada.

        Args:
            clave: Clave única del cliente a eliminar.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Clientes WHERE clave = ?", (clave,))
            if cursor.rowcount == 0:
                print(f"\n  No se encontró cliente con clave '{clave}'.")
            else:
                conn.commit()
                print(f"\n  Cliente '{clave}' eliminado.")
        except Exception as e:
            print(f"\n  Error al eliminar cliente: {e}")
        finally:
            conn.close()

    @staticmethod
    def listar_clientes() -> list:
        """Retorna todos los clientes registrados ordenados por nombre."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Clientes ORDER BY nombre")
        clientes = cursor.fetchall()
        conn.close()
        return clientes
