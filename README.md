# atina.uy

Sitio institucional estático de atina.uy (HTML y CSS, sin backend). Se publica en Cloudflare Pages: cada push a `main` se publica solo.


Recomendado: **Cloudflare Pages** (gratis, HTTPS automático, CDN).

## 1. Subir el sitio
1. Crear cuenta gratis en https://dash.cloudflare.com
2. Workers & Pages → Create → Pages → "Connect to Git" → elegir `MassimilianoGF/atina.uy-web`.
   Build: sin framework, sin comando de build, carpeta de salida `public`.
3. Guardar y publicar. Queda en `algo.pages.dev` y cada cambio en `main` se publica solo.

## 2. Llevar el DNS del dominio a Cloudflare
1. En Cloudflare: "Add a site" → `atina.uy` → plan Free. Cloudflare te da 2 nameservers
   (ej. `xxx.ns.cloudflare.com`, `yyy.ns.cloudflare.com`).
2. En https://nic.com.uy → Mis dominios → `atina.uy` → Delegación / Servidores DNS:
   reemplazar los servidores por los 2 de Cloudflare y guardar.
3. Esperar la propagación (de minutos a unas horas). Cloudflare avisa cuando el dominio queda activo.

## 3. Conectar el dominio al sitio
En el proyecto de Pages → Custom domains → agregar `atina.uy` y `www.atina.uy`.
Cloudflare crea los registros y el certificado HTTPS solo.

## Ojo con el correo
Si `info@atina.uy` ya funciona (Google Workspace, Zoho, etc.), antes de cambiar los
nameservers verificar que Cloudflare importó los registros **MX, SPF (TXT) y DKIM**.
Si faltan, copiarlos a mano desde el proveedor de correo; si no, el correo deja de llegar.
Opción gratis para alias: Cloudflare Email Routing (reenvía `contacto@atina.uy` a otra casilla).
