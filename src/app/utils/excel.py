"""
Utilidades para generar archivos Excel en memoria.
Se usa para exportar listados administrativos sin depender de archivos temporales.
"""

from __future__ import annotations

from io import BytesIO
from typing import Iterable

import xlsxwriter


def build_applications_excel(applications: Iterable[object]) -> bytes:
    """
    Genera un XLSX con el listado de solicitudes de inscripción.

    El archivo se construye completamente en memoria para poder enviarlo como descarga.
    """
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("Solicitudes")

    header_format = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#F3E8FF",
            "font_color": "#2D0C57",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )
    text_format = workbook.add_format({"text_wrap": True, "valign": "top"})
    date_format = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm"})

    headers = [
        "ID",
        "Usuario",
        "Email",
        "Curso",
        "Estado",
        "DARDE",
        "Formación previa",
        "Creada",
        "Actualizada",
    ]

    for column, header in enumerate(headers):
        worksheet.write(0, column, header, header_format)

    worksheet.set_column(0, 0, 8)
    worksheet.set_column(1, 2, 24)
    worksheet.set_column(3, 3, 28)
    worksheet.set_column(4, 5, 14)
    worksheet.set_column(6, 6, 40)
    worksheet.set_column(7, 8, 20)

    for row_index, application in enumerate(applications, start=1):
        user = getattr(application, "user", None)
        course = getattr(application, "course", None)
        status = getattr(application, "status", None)

        if hasattr(status, "value"):
            status_value = status.value
        else:
            status_value = str(status) if status is not None else ""

        has_darde = getattr(application, "has_darde", None)
        if has_darde is None:
            darde_value = "Sin informar"
        else:
            darde_value = "Sí" if has_darde else "No"

        created_at = getattr(application, "created_at", None)
        updated_at = getattr(application, "updated_at", None)

        worksheet.write(row_index, 0, getattr(application, "id", ""))
        worksheet.write(row_index, 1, getattr(user, "name", ""))
        worksheet.write(row_index, 2, getattr(user, "email", ""))
        worksheet.write(row_index, 3, getattr(course, "name", f"Curso #{getattr(application, 'course_id', '')}"))
        worksheet.write(row_index, 4, status_value)
        worksheet.write(row_index, 5, darde_value)
        worksheet.write(row_index, 6, getattr(application, "previous_education", "") or "", text_format)

        if created_at:
            worksheet.write_datetime(row_index, 7, created_at, date_format)
        else:
            worksheet.write(row_index, 7, "")

        if updated_at:
            worksheet.write_datetime(row_index, 8, updated_at, date_format)
        else:
            worksheet.write(row_index, 8, "")

    workbook.close()
    output.seek(0)
    return output.read()