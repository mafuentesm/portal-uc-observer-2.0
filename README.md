# portal-uc-observer-2.0

Código que permite observar cambios en el portal UC para ver si horarios banner fueron habilitados (Version 2.0: considera el uso de portlets y AJAX por parte de la página)

## Requisitos

- Python 3.8 o superior
- pip (administrador de paquetes)

Instala las dependencias con:
`pip install -r requirements.txt`

## Configuración

1. Abre el archivo `main.py.`

Modifica las siguientes variables según la página que quieras vigilar:

2. Modifica las siguientes variables según la página a observar:

```
LOGIN_URL=https://sso.uc.cl/cas/login?service=https%3A%2F%2Fportal.uc.cl%2Fc%2Fportal%2Flogin
TARGET_URL=https://portal.uc.cl/
PORTLET_URL=<depende_del_fetch_de_la_pagina>
USERNAME=usuario_portal_uc
PASSWORD=contrasena_portal
```

## Notas

- En macOS, las notificaciones se muestran con AppleScript (osascript), garantizando persistencia.
- En Windows/Linux, se usa `plyer` (si está instalado).
- Si la página no está disponible, el programa seguirá intentando cada CHECK_INTERVAL segundos.

## Autor

Prototipo desarrollado por Matias Fuentes.
