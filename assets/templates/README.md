Coloca aqui la plantilla Word usada para generar el PDF del ATS.

- Nombre esperado por la app: `ats_template.docx`
- Ruta completa esperada: `assets/templates/ats_template.docx`

Notas:
- Si el archivo no existe, la app detiene la generacion y muestra error.
- Para conversion DOCX -> PDF con plantilla, instala `python-docx` y `docx2pdf`.
- En Windows, `docx2pdf` usa Microsoft Word para la conversion.
- No hay fallback a otros motores de conversion en esta fase.
