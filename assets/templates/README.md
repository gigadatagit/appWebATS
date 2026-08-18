# Plantillas DOCX historicas

Este directorio conserva plantillas Word heredadas solo como referencia historica.
La generacion documental vigente no usa DOCX ni conversion a PDF.

El flujo actual renderiza plantillas HTML ubicadas en `templates/<formato>/template.html`,
embebe logos, firmas e imagenes como Data URI cuando aplica, y sube el HTML final
autocontenido a Supabase Storage.
