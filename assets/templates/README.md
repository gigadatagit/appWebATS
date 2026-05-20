Coloca aqui la plantilla Word usada para generar el PDF del ATS.

- Nombre esperado por la app: `ats_template.docx`
- Ruta completa esperada: `assets/templates/ats_template.docx`

Notas:
- Si el archivo no existe, la app detiene la generacion y muestra error.
- El llenado del template se hace con `python-docx`.
- En Windows, la conversion DOCX -> PDF puede usar `docx2pdf` (requiere Microsoft Word).
- En Linux, usa `libreoffice` (`soffice --headless`) para la conversion a PDF.
