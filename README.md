# Happy Burger — Sistema Administrativo

Sistema administrativo para la franquicia **Happy Burger**, desarrollado en Python. Incluye una interfaz de consola (CLI) para la operación diaria y una interfaz web (Flask) para la consulta y gestión de pedidos.

---

## Objetivo

Desarrollar una aplicación en Python que simule un software administrativo usando programación orientada a objetos, persistencia de datos con SQLite y una interfaz web con Flask.

---

## Requisitos

- Python 3.10 o superior
- Flask (ver `requirements.txt`)

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Cómo ejecutar

### Interfaz de consola (CLI)

```bash
python main.py
```

Muestra un menú con las opciones: Pedidos, Clientes, Menú y Salir.

### Interfaz web (Flask)

```bash
python app.py
```

Abre el navegador en `http://localhost:5000`

---

## Estructura del proyecto

```
burger/
├── base.py          # Clase base EntidadBase (herencia)
├── cliente.py       # Clase Cliente (hereda de EntidadBase)
├── producto.py      # Clase Producto (hereda de EntidadBase)
├── pedido.py        # Clase Pedido (hereda de EntidadBase) + ticket TXT
├── database.py      # Conexión SQLite e inicialización de tablas
├── main.py          # Punto de entrada CLI con menú principal
├── app.py           # Aplicación web Flask
├── templates/       # Plantillas HTML (Jinja2)
│   ├── layout.html
│   ├── index.html
│   ├── clientes.html
│   ├── menu.html
│   ├── consulta_pedido.html
│   ├── form_cliente.html
│   ├── form_pedido.html
│   ├── form_producto.html
│   ├── catalogos.html
│   ├── reportes.html
│   └── ticket.html
├── static/
│   └── style.css
├── tickets/         # Archivos TXT generados por cada pedido
├── requirements.txt
└── README.md
```

---

## Funcionalidades

### Clientes
- Agregar, actualizar y eliminar clientes.
- Campos: clave, nombre, dirección, correo electrónico, teléfono.

### Menú / Productos
- Agregar, actualizar y eliminar productos del menú.
- Campos: clave, nombre, precio.

### Pedidos
- Crear pedidos con uno o varios productos.
- Cancelar pedidos existentes.
- Consultar pedidos por número.
- Generar ticket en archivo `.txt` al confirmar cada pedido.
- Marcar pedidos como completados desde la interfaz web.

### Interfaz Web (Flask)
- Dashboard con métricas globales (clientes, productos, pedidos, ventas).
- Gestión completa de clientes y productos desde el navegador.
- Consulta de pedidos por número de pedido.
- Reportes con gráficas de ventas y productos más vendidos.
- Descarga del ticket TXT desde el navegador.

---

## Base de datos

El sistema usa **SQLite** (`happy_burger.db`) con las siguientes tablas:

| Tabla          | Descripción                              |
|----------------|------------------------------------------|
| `Clientes`     | Directorio de clientes registrados       |
| `Productos`    | Catálogo del menú                        |
| `Pedidos`      | Encabezado de cada pedido                |
| `DetallePedido`| Líneas de productos por pedido           |

La base de datos se crea automáticamente al iniciar la aplicación.

---

## Programación Orientada a Objetos

El proyecto aplica los principios de POO:

- **Encapsulamiento**: cada clase maneja sus propios datos y operaciones.
- **Herencia**: `Cliente`, `Producto` y `Pedido` heredan de la clase base `EntidadBase`, que centraliza la clave identificadora, el nombre y las representaciones de texto comunes.
- **Modularización**: cada entidad vive en su propio módulo (`.py`).
- **Docstrings**: todas las clases y funciones están documentadas.
