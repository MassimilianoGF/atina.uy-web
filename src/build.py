#!/usr/bin/env python3
"""Genera el sitio estático de atina.uy en _site/.

Copia public/ (archivos estáticos) y escribe las páginas HTML usando
el layout común. Uso: python3 src/build.py
"""
import json
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
BASE = "https://atina.uy"
EMAIL = "info@atina.uy"
YEAR = 2026
LASTMOD = "2026-10-15"

# El formulario de contacto se envía por FormSubmit (https://formsubmit.co), que
# reenvía cada consulta por mail. La primera vez pide confirmar desde info@atina.uy.
FORM_ACTION = f"https://formsubmit.co/{EMAIL}"

CSP = ("default-src 'none'; img-src 'self' data:; style-src 'self'; base-uri 'none'; "
       "form-action https://formsubmit.co; upgrade-insecure-requests")


# Los botones de presupuesto llevan a la página de contacto, que usa un
# formulario: el enlace mailto: no hace nada sin un programa de correo configurado.
QUOTE = "/contacto/"

LOGO = (
    '<svg viewBox="0 0 470 140" aria-hidden="true"><defs><linearGradient id="lg" gradientUnits="userSpaceOnUse" '
    'x1="18" y1="0" x2="390" y2="0"><stop offset="0" stop-color="#7457E8"/><stop offset=".55" stop-color="#4E67EA"/>'
    '<stop offset="1" stop-color="#45A3EC"/></linearGradient></defs><g fill="none" stroke="url(#lg)" stroke-width="16" '
    'stroke-linejoin="round" stroke-linecap="round"><path d="M18 110 L54 30 L90 110"/><path d="M38 92 H56" '
    'stroke-width="10"/><path d="M80 30 H148 M114 30 V110"/><path d="M170 30 V110"/><path d="M194 110 V30 L246 110 V30"/>'
    '<path d="M266 110 L302 30 L338 110"/></g><path d="M284 110 L350 30 H372" fill="none" stroke="#45A3EC" '
    'stroke-width="11" stroke-linejoin="round" stroke-linecap="round"/><circle cx="382" cy="30" r="11" fill="#45A3EC"/>'
    '<text x="392" y="110" font-family="system-ui,Segoe UI,Roboto,Arial,sans-serif" font-size="46" font-weight="600" '
    'fill="currentColor">.uy</text></svg>'
)


def icon(paths, size=24):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>')


ICONS = {
    "pc": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    "db": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "m365": '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
    "cloud": '<path d="M17.5 19a4.5 4.5 0 1 0-1.4-8.8A6 6 0 0 0 4.5 12 3.5 3.5 0 0 0 6 19z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    "map": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    "doc": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
    "life": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M5.6 5.6l3.6 3.6M14.8 14.8l3.6 3.6M18.4 5.6l-3.6 3.6M9.2 14.8l-3.6 3.6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
}

# Ilustración de la portada: la oficina conectada a la nube.
HERO_ART = '''<svg viewBox="0 0 480 420" role="img" aria-label="Equipos, servidor, correo y seguridad conectados a la nube">
<defs>
  <linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7457E8"/><stop offset=".55" stop-color="#4E67EA"/><stop offset="1" stop-color="#45A3EC"/></linearGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#4E67EA" stop-opacity=".55"/><stop offset="1" stop-color="#4E67EA" stop-opacity="0"/></radialGradient>
</defs>
<circle cx="240" cy="190" r="170" fill="url(#glow)"/>
<g stroke="#8fa2ff" stroke-opacity=".55" stroke-width="2" fill="none" class="dash">
  <path d="M240 200 L92 92"/><path d="M240 200 L392 96"/><path d="M240 200 L96 330"/><path d="M240 200 L388 326"/>
</g>
<g class="float">
  <path d="M302 222a40 40 0 1 0-12-78 56 56 0 0 0-104 18 38 38 0 0 0 6 76h110z" fill="#151a3a" stroke="url(#hg)" stroke-width="5" stroke-linejoin="round"/>
  <path d="M206 194l22 22 44-44" fill="none" stroke="#45A3EC" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<g class="float d2" transform="translate(40 44)">
  <rect width="104" height="96" rx="18" fill="#151a3a" stroke="rgba(255,255,255,.14)"/>
  <rect x="24" y="24" width="56" height="36" rx="4" fill="none" stroke="#9fb0ff" stroke-width="4"/>
  <path d="M38 74h28M52 60v14" stroke="#9fb0ff" stroke-width="4" stroke-linecap="round"/>
</g>
<g class="float d3" transform="translate(340 48)">
  <rect width="104" height="96" rx="18" fill="#151a3a" stroke="rgba(255,255,255,.14)"/>
  <rect x="26" y="22" width="52" height="52" rx="4" fill="none" stroke="#7fc4f5" stroke-width="4"/>
  <path d="M26 48h52M52 22v52" stroke="#7fc4f5" stroke-width="4"/>
</g>
<g class="float d3" transform="translate(44 282)">
  <rect width="104" height="96" rx="18" fill="#151a3a" stroke="rgba(255,255,255,.14)"/>
  <rect x="26" y="20" width="52" height="16" rx="4" fill="none" stroke="#a48cff" stroke-width="4"/>
  <rect x="26" y="42" width="52" height="16" rx="4" fill="none" stroke="#a48cff" stroke-width="4"/>
  <circle cx="36" cy="28" r="2.5" fill="#a48cff" class="pulse"/><circle cx="36" cy="50" r="2.5" fill="#a48cff" class="pulse"/>
  <path d="M38 74h28" stroke="#a48cff" stroke-width="4" stroke-linecap="round"/>
</g>
<g class="float d2" transform="translate(336 278)">
  <rect width="104" height="96" rx="18" fill="#151a3a" stroke="rgba(255,255,255,.14)"/>
  <path d="M52 18l26 10v18c0 16-11 27-26 32-15-5-26-16-26-32V28z" fill="none" stroke="#45A3EC" stroke-width="4" stroke-linejoin="round"/>
  <path d="M42 48l7 7 14-14" fill="none" stroke="#45A3EC" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</g>
<g fill="#45A3EC"><circle cx="92" cy="92" r="5" class="pulse"/><circle cx="392" cy="96" r="5" class="pulse"/><circle cx="96" cy="330" r="5" class="pulse"/><circle cx="388" cy="326" r="5" class="pulse"/></g>
</svg>'''

# ---------------------------------------------------------------- servicios
SERVICES = [
    {
        "slug": "soporte-tecnico", "icon": "pc",
        "name": "Servicio técnico informático",
        "short": "Soporte para los equipos y la infraestructura de tu oficina.",
        "bullets": ["Instalación y reinstalación de Windows", "Mantenimiento de PCs y notebooks",
                    "Redes, impresoras y correo", "Diagnóstico y solución de problemas"],
        "title": "Servicio técnico informático para empresas en Montevideo",
        "h1": "Servicio técnico informático para tu empresa",
        "desc": "Servicio técnico informático para pymes en Montevideo: instalación de Windows, mantenimiento de PCs y notebooks, redes, impresoras y correo. Atención a domicilio o remota.",
        "intro": "Cuando una PC no arranca, la impresora no imprime o internet anda mal, se frena el trabajo. Nos encargamos de que los equipos de tu oficina funcionen, a domicilio o de forma remota.",
        "includes": [
            ("Instalación y reinstalación de Windows", "Equipos nuevos o que hay que dejar a nuevo, con los programas que usás."),
            ("Mantenimiento y puesta a punto", "PCs y notebooks lentas, actualizaciones, limpieza y revisión general."),
            ("Redes e internet", "Configuración de routers, wifi y red de la oficina."),
            ("Impresoras y periféricos", "Instalación y configuración para que todos puedan usarlas."),
            ("Correo", "Configuración de cuentas de correo en computadoras y celulares."),
            ("Diagnóstico y solución de problemas", "Encontramos qué falla y lo resolvemos."),
        ],
        "signs": ["La PC tarda mucho en arrancar", "Hay que reinstalar Windows", "El wifi de la oficina se corta",
                  "La impresora no aparece en la red", "Llegó un equipo nuevo y hay que configurarlo", "El correo no sincroniza en el celular"],
        "faqs": [
            ("¿La atención es a domicilio o remota?", "Las dos. Según el problema, vamos a tu oficina o casa en Montevideo, o lo resolvemos de forma remota."),
            ("¿Instalan Windows en equipos nuevos?", "Sí. Instalamos o reinstalamos Windows y dejamos el equipo listo con los programas que usás."),
            ("¿Trabajan con empresas chicas?", "Sí. El servicio está pensado para pequeñas y medianas empresas."),
        ],
    },
    {
        "slug": "respaldos", "icon": "db",
        "name": "Respaldos y continuidad",
        "short": "Que un disco roto o un virus no te frene el negocio.",
        "bullets": ["Respaldos locales y en la nube", "Recuperación de información",
                    "Pruebas de restauración", "Protección contra ransomware"],
        "title": "Respaldos de información para empresas en Montevideo",
        "h1": "Respaldos para que tu información esté siempre a salvo",
        "desc": "Respaldos de información para pymes en Montevideo: copias locales y en la nube, recuperación de archivos, pruebas de restauración y protección contra ransomware.",
        "intro": "Un disco que se rompe, un archivo borrado o un ransomware pueden dejar a tu empresa sin su información. Armamos respaldos que funcionan y los probamos para que, si pasa algo, puedas recuperarte.",
        "includes": [
            ("Política de respaldos", "Definimos qué se respalda, cada cuánto y dónde."),
            ("Respaldos locales y en la nube", "Copias en más de un lugar para no depender de un solo equipo."),
            ("Recuperación de información", "Recuperamos archivos y equipos cuando hace falta."),
            ("Pruebas periódicas de restauración", "Un respaldo que nunca se probó no es un respaldo."),
            ("Protección básica contra ransomware", "Medidas para que un ataque no se lleve también las copias."),
        ],
        "signs": ["No sabés si tenés respaldos", "Los respaldos están en un disco en la misma oficina",
                  "Nunca probaste restaurar un respaldo", "Perdiste archivos y no pudiste recuperarlos",
                  "Te preocupa un ataque de ransomware", "La información está en un solo equipo"],
        "faqs": [
            ("¿Dónde se guardan los respaldos?", "Combinamos copias locales y en la nube, para no depender de un único lugar."),
            ("¿Cómo sé que el respaldo funciona?", "Hacemos pruebas periódicas de restauración para comprobar que la información se puede recuperar."),
            ("¿Pueden recuperar archivos que ya perdí?", "Escribinos contando qué pasó y vemos qué se puede recuperar."),
        ],
    },
    {
        "slug": "microsoft-365", "icon": "m365",
        "name": "Microsoft 365 y trabajo en la nube",
        "short": "Dejá el servidor de la oficina y trabajá desde cualquier lugar.",
        "bullets": ["Migración del correo a Microsoft 365", "Archivos del servidor a SharePoint y OneDrive",
                    "Seguridad del correo", "Capacitación en Teams y SharePoint"],
        "title": "Migración a Microsoft 365 y SharePoint para empresas en Montevideo",
        "h1": "Migración a Microsoft 365 y SharePoint",
        "desc": "Migramos el correo de tu empresa a Microsoft 365 y los archivos del servidor local a SharePoint y OneDrive para trabajar online desde cualquier lugar. Pymes en Montevideo.",
        "intro": "Si tus archivos viven en un servidor de la oficina, para trabajar hay que estar ahí. Pasamos tu correo a Microsoft 365 y tus archivos a SharePoint y OneDrive para que tu equipo trabaje online, desde donde esté.",
        "includes": [
            ("Migración del correo a Microsoft 365", "Pasamos las casillas a Exchange Online."),
            ("Archivos del servidor a SharePoint y OneDrive", "Migramos los archivos para usarlos online."),
            ("Permisos y carpetas compartidas", "Cada área accede a lo que necesita."),
            ("Seguridad del correo", "SPF, DKIM, DMARC y doble factor para proteger las cuentas."),
            ("Capacitación del equipo", "Teams, OneDrive y SharePoint en el día a día."),
        ],
        "signs": ["Tus archivos están en un servidor de la oficina", "Para trabajar desde casa hay que conectarse a la oficina",
                  "El correo está en un servicio aparte", "Se mandan archivos por mail para compartirlos",
                  "El servidor de la oficina ya está viejo", "Querés trabajar con Teams y SharePoint"],
        "faqs": [
            ("¿Pueden pasar los archivos de nuestro servidor a la nube?", "Sí. Migramos los archivos del servidor local a SharePoint y OneDrive para que tu equipo trabaje online."),
            ("¿Migran el correo a Microsoft 365?", "Sí. Pasamos las casillas de correo de tu empresa a Microsoft 365."),
            ("¿Ya lo hicieron con otras empresas?", "Sí. Por ejemplo, un estudio contable que ahora trabaja 100% online con Microsoft 365 y SharePoint."),
        ],
        "case": True,
    },
    {
        "slug": "migracion-nube", "icon": "cloud",
        "name": "Migraciones cloud (AWS y Azure)",
        "short": "Llevamos tus servidores a la nube con un plan claro y costos controlados.",
        "bullets": ["Relevamiento y arquitectura", "Migración de servidores y datos",
                    "Optimización de costos", "Soporte posterior"],
        "title": "Migración a la nube con AWS y Azure para empresas en Montevideo",
        "h1": "Migración de servidores a la nube con AWS y Azure",
        "desc": "Migramos los servidores y servicios de tu empresa a AWS o Azure: relevamiento, arquitectura, migración, optimización de costos y soporte posterior. Pymes en Montevideo.",
        "intro": "Llevar los servidores a la nube evita depender de equipos propios, pero hay que hacerlo con un plan. Relevamos tu infraestructura, proponemos una arquitectura en AWS o Azure y hacemos la migración con costos controlados.",
        "includes": [
            ("Relevamiento", "Vemos qué servidores y servicios tenés y cómo se usan."),
            ("Propuesta de arquitectura", "Diseñamos cómo va a quedar en AWS o Azure."),
            ("Migración de servidores, archivos y correo", "Hacemos el pasaje con un plan para minimizar cortes."),
            ("Optimización de costos", "Ajustamos recursos para no pagar de más en la nube."),
            ("Acompañamiento y soporte posterior", "Seguimos cerca después de la migración."),
        ],
        "signs": ["El servidor de la oficina está por quedar viejo", "Necesitás acceder a tus sistemas desde cualquier lugar",
                  "La factura de la nube creció y no sabés por qué", "Un corte de luz deja a la empresa sin sistemas",
                  "Querés comparar AWS y Azure", "Te preocupa la seguridad de tus servidores"],
        "faqs": [
            ("¿Trabajan con AWS y con Azure?", "Sí. Proponemos la plataforma que mejor se ajusta a tu caso."),
            ("¿Cómo es el proceso?", "Relevamos tu infraestructura, proponemos una arquitectura, migramos servidores, archivos y correo, y optimizamos los costos."),
            ("¿Qué pasa después de la migración?", "Te acompañamos y damos soporte para que todo siga funcionando."),
        ],
    },
]

HOME_FAQS = [
    ("¿Qué servicios ofrece atina.uy?", "Servicio técnico informático (instalación de Windows, mantenimiento de PCs y notebooks, redes, impresoras y correo), respaldos y recuperación de información, migración del correo y los archivos a Microsoft 365 y SharePoint, y migraciones a la nube con AWS y Azure."),
    ("¿Trabajan con empresas chicas?", "Sí. Nuestros servicios están pensados para pequeñas y medianas empresas de Montevideo."),
    ("¿La atención es a domicilio o remota?", "Las dos. Según el problema o el proyecto, vamos a tu oficina o casa en Montevideo, o lo resolvemos de forma remota."),
    ("¿Pueden pasar los archivos de nuestro servidor a la nube?", "Sí. Migramos los archivos del servidor local a SharePoint y OneDrive, y el correo a Microsoft 365, para que tu equipo trabaje online desde cualquier lugar."),
    ("¿Pueden migrar mis servidores a AWS o Azure?", "Sí. Relevamos tu infraestructura, proponemos una arquitectura, migramos servidores, archivos y correo, y optimizamos los costos en la nube."),
    ("¿Cómo pido un presupuesto?", f"Desde la página de contacto o escribiendo a {EMAIL} con una breve descripción de lo que necesitás. Te enviamos una propuesta."),
]

CASE_HTML = '''<div class="case-card">
  <div><span class="tag">Antes</span><h3>El punto de partida</h3><p>Los archivos del estudio estaban en un servidor local dentro de la oficina, así que para acceder a ellos había que estar ahí.</p></div>
  <div><span class="tag">Lo que hicimos</span><h3>Correo y archivos a la nube</h3><p>Migramos el correo a Microsoft 365 y pasamos todos los archivos del servidor a SharePoint.</p></div>
  <div><span class="tag">Después</span><h3>El resultado</h3><p>Ahora el estudio usa el correo y sus archivos online, desde cualquier lugar, sin depender del servidor de la oficina.</p></div>
</div>'''


# ---------------------------------------------------------------- bloques
def svc_url(s):
    return f"/servicios/{s['slug']}/"


def nav_links(current):
    items = [("/#servicios", "Servicios"), ("/#casos", "Casos"), ("/#como", "Cómo trabajamos"), ("/#preguntas", "Preguntas")]
    return "".join(f'<a href="{h}">{t}</a>' for h, t in items)


def header(current=""):
    links = nav_links(current)
    return f'''<a class="skip" href="#contenido">Ir al contenido</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/" aria-label="atina.uy, inicio">{LOGO}</a>
    <nav class="nav" aria-label="Principal">{links}<a class="btn btn-primary btn-sm" href="{QUOTE}">Pedí presupuesto</a></nav>
    <details class="menu">
      <summary aria-label="Abrir menú">{icon(ICONS["menu"])}</summary>
      <nav class="menu-panel" aria-label="Menú">{links}<a href="/contacto/">Contacto</a><a class="btn btn-primary" href="{QUOTE}">Pedí presupuesto</a></nav>
    </details>
  </div>
</header>'''


def footer():
    svc = "".join(f'<li><a href="{svc_url(s)}">{escape(s["name"])}</a></li>' for s in SERVICES)
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div><a class="logo" href="/" aria-label="atina.uy, inicio">{LOGO}</a>
        <p>Soporte informático y nube para pequeñas y medianas empresas de Montevideo.</p></div>
      <div><h4>Servicios</h4><ul>{svc}</ul></div>
      <div><h4>Contacto</h4><ul><li><a href="/contacto/">Contacto</a></li><li>{EMAIL}</li><li><a href="/#preguntas">Preguntas frecuentes</a></li></ul></div>
    </div>
    <div class="bottom"><span>© {YEAR} atina.uy · Montevideo, Uruguay</span><span>Soporte IT · Respaldos · Microsoft 365 · AWS · Azure</span></div>
  </div>
</footer>'''


def cta_block(title="¿Hablamos de tu empresa?", text="Contanos qué necesitás y te enviamos una propuesta clara, sin compromiso."):
    return f'''<section class="cta">
  <div class="wrap">
    <div class="cta-box">
      <h2>{title}</h2>
      <p>{text}</p>
      <div class="hero-ctas"><a class="btn btn-primary" href="{QUOTE}">Pedí presupuesto</a><a class="btn btn-ghost" href="/contacto/">Escribinos</a></div>
      <span class="mail">o escribí directo a {EMAIL}</span>
    </div>
  </div>
</section>'''


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


ORG = {
    "@context": "https://schema.org", "@type": "ProfessionalService", "@id": BASE + "/#empresa",
    "name": "atina.uy", "url": BASE + "/", "logo": BASE + "/logo/logo-light.svg", "image": BASE + "/og-image.jpg",
    "email": EMAIL,
    "description": "Servicio técnico informático, respaldos, Microsoft 365 y SharePoint, y migraciones a la nube (AWS y Azure) para pequeñas y medianas empresas en Montevideo, Uruguay.",
    "areaServed": {"@type": "City", "name": "Montevideo", "containedInPlace": {"@type": "Country", "name": "Uruguay"}},
    "knowsAbout": ["Soporte técnico informático", "Instalación de Windows", "Respaldos", "Redes", "Microsoft 365",
                   "SharePoint", "Exchange Online", "Amazon Web Services", "Microsoft Azure", "Migración a la nube"],
    "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Servicios", "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": BASE + svc_url(s)}} for s in SERVICES]},
}


def page(path, title, desc, body, ld, current=""):
    canonical = BASE + path
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    return f'''<!doctype html>
<html lang="es-UY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{CSP}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0e1119">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_UY">
<meta property="og:site_name" content="atina.uy">
<meta property="og:image" content="{BASE}/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
{header(current)}
<main id="contenido">
{body}
</main>
{footer()}
</body>
</html>
'''


# ---------------------------------------------------------------- páginas
def home():
    cards = "\n".join(f'''<a class="card" href="{svc_url(s)}">
  <div class="ico">{icon(ICONS[s["icon"]])}</div>
  <h3>{escape(s["name"])}</h3>
  <p>{escape(s["short"])}</p>
  <ul>{"".join(f"<li>{escape(b)}</li>" for b in s["bullets"])}</ul>
  <span class="more">Ver más <span>→</span></span>
</a>''' for s in SERVICES)
    why = [
        ("user", "Atención directa", "Hablás con quien resuelve, sin intermediarios ni call centers."),
        ("map", "A domicilio o remoto", "Vamos a tu oficina en Montevideo o lo resolvemos a distancia, según convenga."),
        ("doc", "Propuestas claras", "Antes de empezar sabés qué vamos a hacer y por qué."),
        ("life", "Acompañamiento", "Seguimos cerca después del trabajo para que todo siga funcionando."),
    ]
    why_html = "".join(f'<div><div class="ico">{icon(ICONS[i])}</div><h3>{t}</h3><p>{d}</p></div>' for i, t, d in why)
    body = f'''<section class="hero">
  <div class="wrap">
    <div>
      <span class="badge rise"><i></i>Soporte IT y nube para pymes en Montevideo</span>
      <h1 class="rise d1">Soporte informático y nube para tu empresa, <span class="hl">sin vueltas.</span></h1>
      <p class="sub rise d2">Mantenemos tus equipos funcionando, tus datos respaldados y te ayudamos a trabajar en la nube con Microsoft 365, AWS o Azure.</p>
      <div class="hero-ctas rise d3"><a class="btn btn-primary" href="{QUOTE}">Pedí presupuesto</a><a class="btn btn-ghost" href="#servicios">Ver servicios</a></div>
    </div>
    <div class="hero-art">{HERO_ART}</div>
  </div>
</section>
<div class="tech" aria-label="Tecnologías con las que trabajamos">
  <div class="wrap"><span class="lbl">Trabajamos con</span><span class="chip">Microsoft 365</span><span class="chip">Windows</span><span class="chip">SharePoint</span><span class="chip">Microsoft Azure</span><span class="chip">AWS</span></div>
</div>

<section id="servicios">
  <div class="wrap">
    <p class="eyebrow">Servicios</p>
    <h2>Lo que hacemos</h2>
    <p class="lead">Servicios pensados para pymes: el día a día de la informática y el paso al trabajo en la nube.</p>
    <div class="grid">{cards}</div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <p class="eyebrow">Por qué atina</p>
    <h2>Tecnología que funciona, con alguien cerca</h2>
    <p class="lead">Somos el equipo de IT que una pyme necesita, sin tener que armar uno propio.</p>
    <div class="why">{why_html}</div>
  </div>
</section>

<section id="casos">
  <div class="wrap">
    <p class="eyebrow">Caso real</p>
    <h2>Un estudio contable que ahora trabaja 100% online</h2>
    <p class="lead">Migración del correo a Microsoft 365 y de los archivos del servidor a SharePoint.</p>
    {CASE_HTML}
  </div>
</section>

<section id="como" class="alt">
  <div class="wrap">
    <p class="eyebrow">Cómo trabajamos</p>
    <h2>Simple y transparente</h2>
    <p class="lead">Atención directa, sin intermediarios, con propuestas a la medida de cada empresa.</p>
    <div class="steps">
      <div class="step"><h3>Nos contás qué necesitás</h3><p>Por correo, con una breve descripción del problema o el proyecto.</p></div>
      <div class="step"><h3>Relevamos y proponemos</h3><p>Analizamos tu situación y te enviamos una propuesta clara.</p></div>
      <div class="step"><h3>Lo resolvemos</h3><p>A domicilio o de forma remota, según lo que convenga.</p></div>
      <div class="step"><h3>Te acompañamos</h3><p>Soporte continuo para que todo siga funcionando.</p></div>
    </div>
  </div>
</section>

<section id="preguntas">
  <div class="wrap">
    <div class="center"><p class="eyebrow">Preguntas frecuentes</p><h2>Lo que más nos preguntan</h2></div>
    <div class="faq">{"".join(f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in HOME_FAQS)}</div>
  </div>
</section>

<div id="contacto">{cta_block()}</div>'''
    ld = [ORG, {"@context": "https://schema.org", "@type": "WebSite", "name": "atina.uy", "url": BASE + "/", "inLanguage": "es-UY"}, faq_ld(HOME_FAQS)]
    return page("/", "atina.uy | Soporte informático y nube para pymes en Montevideo",
                "Servicio técnico informático para empresas en Montevideo: instalación de Windows, mantenimiento de PCs, redes, respaldos, Microsoft 365 y SharePoint, y migraciones a la nube con AWS y Azure para pymes.",
                body, ld)


def service_page(s):
    includes = "".join(f"<li><strong>{escape(t)}</strong><span>{escape(d)}</span></li>" for t, d in s["includes"])
    signs = "".join(f"<div>{escape(x)}</div>" for x in s["signs"])
    others = "".join(f'''<a class="card" href="{svc_url(o)}"><div class="ico">{icon(ICONS[o["icon"]])}</div><h3>{escape(o["name"])}</h3><p>{escape(o["short"])}</p><span class="more">Ver más <span>→</span></span></a>'''
                     for o in SERVICES if o is not s)
    case = ""
    if s.get("case"):
        case = f'''<section><div class="wrap"><p class="eyebrow">Caso real</p><h2>Un estudio contable que ahora trabaja 100% online</h2><p class="lead">Así quedó uno de nuestros clientes después de la migración.</p>{CASE_HTML}</div></section>'''
    quote = QUOTE
    body = f'''<section class="hero page-hero">
  <div class="wrap">
    <div>
      <div class="crumbs rise"><a href="/">Inicio</a> / <a href="/#servicios">Servicios</a> / {escape(s["name"])}</div>
      <h1 class="rise d1">{escape(s["h1"])}</h1>
      <p class="sub rise d2">{escape(s["intro"])}</p>
      <div class="hero-ctas rise d3"><a class="btn btn-primary" href="{quote}">Pedí presupuesto</a><a class="btn btn-ghost" href="#incluye">Qué incluye</a></div>
    </div>
  </div>
</section>

<section id="incluye">
  <div class="wrap two">
    <div>
      <p class="eyebrow">Qué incluye</p>
      <h2>{escape(s["name"])}</h2>
      <ul class="checks">{includes}</ul>
    </div>
    <aside class="aside">
      <h3>¿Lo necesitás para tu empresa?</h3>
      <p>Contanos tu caso y te enviamos una propuesta clara, sin compromiso.</p>
      <a class="btn btn-primary" href="{quote}">Pedí presupuesto</a>
    </aside>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <p class="eyebrow">¿Te pasa esto?</p>
    <h2>Señales de que podemos ayudarte</h2>
    <p class="lead">Si te identificás con alguna, escribinos.</p>
    <div class="signs">{signs}</div>
  </div>
</section>
{case}
<section>
  <div class="wrap">
    <div class="center"><p class="eyebrow">Preguntas frecuentes</p><h2>Sobre este servicio</h2></div>
    <div class="faq">{"".join(f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in s["faqs"])}</div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <p class="eyebrow">Otros servicios</p>
    <h2>También podemos ayudarte con</h2>
    <div class="related">{others}</div>
  </div>
</section>
<div class="spacer" aria-hidden="true"></div>
{cta_block("¿Lo necesitás para tu empresa?")}'''
    url = BASE + svc_url(s)
    ld = [
        {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "description": s["desc"], "url": url,
         "serviceType": s["name"], "areaServed": {"@type": "City", "name": "Montevideo", "containedInPlace": {"@type": "Country", "name": "Uruguay"}},
         "provider": {"@id": BASE + "/#empresa", "@type": "ProfessionalService", "name": "atina.uy", "url": BASE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Inicio", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": s["name"], "item": url}]},
        faq_ld(s["faqs"]),
    ]
    return page(svc_url(s), f'{s["title"]} | atina.uy', s["desc"], body, ld)


def not_found():
    body = f'''<section class="notfound"><div>
  <p class="big hl">404</p>
  <h1>Esta página no existe</h1>
  <p class="lead">Puede que el enlace esté mal o que la página se haya movido.</p>
  <div class="hero-ctas"><a class="btn btn-primary" href="/">Ir al inicio</a><a class="btn btn-outline" href="/#servicios">Ver servicios</a></div>
</div></section>'''
    html = page("/404.html", "Página no encontrada | atina.uy", "La página que buscás no existe.", body, ORG)
    return html.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')


def contact_page():
    body = f'''<section class="hero page-hero">
  <div class="wrap"><div>
    <div class="crumbs rise"><a href="/">Inicio</a> / Contacto</div>
    <h1 class="rise d1">Pedí tu presupuesto</h1>
    <p class="sub rise d2">Completá el formulario y te respondemos con una propuesta clara, sin compromiso. Atendemos en Montevideo, a domicilio o de forma remota.</p>
  </div></div>
</section>
<section>
  <div class="wrap two">
    <form class="form" action="{FORM_ACTION}" method="post">
      <input type="hidden" name="_subject" value="Nueva consulta desde atina.uy">
      <input type="hidden" name="_next" value="{BASE}/gracias/">
      <input type="hidden" name="_captcha" value="false">
      <input type="hidden" name="_template" value="table">
      <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="row"><label>Nombre<input name="nombre" required autocomplete="name"></label><label>Empresa<input name="empresa" autocomplete="organization"></label></div>
      <div class="row"><label>Correo<input type="email" name="email" required autocomplete="email"></label><label>Teléfono<input type="tel" name="telefono" autocomplete="tel"></label></div>
      <label>¿Qué necesitás?<textarea name="mensaje" rows="6" required placeholder="Contanos brevemente el problema o el proyecto, y cuántas personas o equipos son."></textarea></label>
      <button class="btn btn-primary" type="submit">Enviar consulta</button>
      <p class="form-alt">¿Preferís escribirnos directo? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </form>
    <aside class="aside">
      <h3>¿Qué pasa después?</h3>
      <ul class="checks">
        <li><strong>Leemos tu consulta</strong><span>Y te respondemos al correo que nos dejaste.</span></li>
        <li><strong>Si hace falta, te preguntamos algo más</strong><span>Por correo o por teléfono.</span></li>
        <li><strong>Te enviamos una propuesta</strong><span>Clara y sin compromiso.</span></li>
      </ul>
    </aside>
  </div>
</section>'''
    ld = [ORG, {"@context": "https://schema.org", "@type": "ContactPage", "url": BASE + "/contacto/", "name": "Contacto atina.uy"}]
    return page("/contacto/", "Contacto y presupuesto | atina.uy",
                "Pedí un presupuesto de soporte informático, respaldos, Microsoft 365 o migración a la nube para tu empresa en Montevideo.", body, ld)


def thanks_page():
    body = '''<section class="notfound"><div>
  <p class="big hl">¡Gracias!</p>
  <h1>Recibimos tu consulta</h1>
  <p class="lead">Te respondemos a la brevedad al correo que nos dejaste.</p>
  <div class="hero-ctas"><a class="btn btn-primary" href="/">Volver al inicio</a><a class="btn btn-outline" href="/#servicios">Ver servicios</a></div>
</div></section>'''
    html = page("/gracias/", "Gracias | atina.uy", "Recibimos tu consulta.", body, ORG)
    return html.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')


def sitemap():
    urls = ["/"] + [svc_url(s) for s in SERVICES] + ["/contacto/"]
    items = "\n".join(f"  <url>\n    <loc>{BASE}{u}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n  </url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}\n</urlset>\n'


def llms():
    lines = ["# atina.uy", "",
             f"> Empresa de servicios informáticos de Montevideo, Uruguay, para pequeñas y medianas empresas: servicio técnico, respaldos, Microsoft 365 y SharePoint, y migraciones a la nube con AWS y Azure. Contacto: {EMAIL}", "",
             "## Servicios", ""]
    for s in SERVICES:
        lines.append(f"- [{s['name']}]({BASE}{svc_url(s)}): " + "; ".join(t.lower() if i else t for i, (t, _) in enumerate(s["includes"])) + ".")
    lines += ["", "## Caso real", "",
              "Un estudio contable tenía sus archivos en un servidor local. Migramos su correo a Microsoft 365 y sus archivos a SharePoint, y ahora trabaja 100% online desde cualquier lugar.", "",
              "## Cómo trabajamos", "",
              "Atención directa en Montevideo, a domicilio o remota. El cliente describe lo que necesita por correo, relevamos la situación, enviamos una propuesta, lo resolvemos y damos soporte continuo.", "",
              "## Preguntas frecuentes", ""]
    lines += [f"- {q} {a}" for q, a in HOME_FAQS]
    lines += ["", "## Enlaces", "", f"- [Sitio web]({BASE}/)", f"- [Contacto]({BASE}/contacto/)", ""]
    return "\n".join(lines)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "public", OUT)
    (OUT / "index.html").write_text(home(), encoding="utf-8")
    for s in SERVICES:
        d = OUT / "servicios" / s["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(service_page(s), encoding="utf-8")
    (OUT / "404.html").write_text(not_found(), encoding="utf-8")
    for slug, fn in (("contacto", contact_page), ("gracias", thanks_page)):
        (OUT / slug).mkdir(exist_ok=True)
        (OUT / slug / "index.html").write_text(fn(), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (OUT / "llms.txt").write_text(llms(), encoding="utf-8")
    print(f"Sitio generado en {OUT}")


if __name__ == "__main__":
    main()
