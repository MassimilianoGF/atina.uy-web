# atina.uy

Sitio institucional estático de atina.uy, publicado en GitHub Pages.

## Cómo está armado
- `src/build.py`: genera todas las páginas (portada, servicios, 404, sitemap y llms.txt) en `_site/`.
  Los textos de los servicios y las preguntas frecuentes están en ese archivo.
- `public/`: archivos estáticos que se copian tal cual (estilos, logos, imágenes, robots.txt, CNAME).
- `.github/workflows/pages.yml`: en cada push a `main` corre `python3 src/build.py` y publica `_site/`.

Para ver el sitio en local: `python3 src/build.py && cd _site && python3 -m http.server`.
