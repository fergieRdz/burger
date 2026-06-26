"""Clase base compartida por las entidades principales del sistema."""


class EntidadBase:
    """Clase base para Cliente, Producto y Pedido.

    Centraliza los atributos comunes (clave identificadora y nombre
    descriptivo) y provee representaciones de texto reutilizables
    para todas las entidades del sistema.

    Attributes:
        clave (str): Identificador único legible de la entidad.
        nombre (str): Nombre o descripción de la entidad.
    """

    def __init__(self, clave: str, nombre: str) -> None:
        """Inicializa la entidad con su clave y nombre."""
        self.clave = clave
        self.nombre = nombre

    def __str__(self) -> str:
        """Retorna representación legible: [clave] nombre."""
        return f"[{self.clave}] {self.nombre}"

    def __repr__(self) -> str:
        """Retorna representación técnica de la entidad."""
        return f"{self.__class__.__name__}(clave={self.clave!r}, nombre={self.nombre!r})"
