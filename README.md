# accounting_pdf_reports_view

Extensión para Odoo 17 que agrega vista en pantalla para asistentes de reportes PDF contables.

## Objetivo

Permitir previsualizar reportes contables desde el wizard antes de descargar el PDF.

## Dependencias

- `accounting_pdf_reports`

## Instalación / actualización

```bash
docker-compose run --rm web-dev odoo -d openlab-dev -u accounting_pdf_reports_view --stop-after-init
docker-compose restart web-dev
```

## Licencia

LGPL-3 (ver archivo `LICENSE`).
