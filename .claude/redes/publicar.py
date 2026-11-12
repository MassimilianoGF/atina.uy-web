#!/usr/bin/env python3
"""Publica en las redes de atina.uy (Facebook, Instagram y, por Buffer, LinkedIn).

Lo usa la rutina automática (/mnt/project-files/redes/RUTINA.md). Massi pidió que
las redes se publiquen solas, sin aprobación por publicación, y este script está
habilitado en .claude/settings.json para que las corridas programadas no se frenen.

Lee META_TOKEN y BUFFER_TOKEN del entorno y nunca los imprime. Cada comando
imprime un JSON con los ids y links que hay que anotar en cola.md y registro.md.

Comandos:
  fb-foto IMAGEN [--texto ARCHIVO] [--oculta]   foto en la página (oculta: solo para tener URL pública)
  fb-carrusel --texto ARCHIVO IMAGEN...         post de Facebook con varias fotos
  ig-imagen --texto ARCHIVO URL                 post de Instagram con una imagen
  ig-carrusel --texto ARCHIVO URL...            carrusel de Instagram
  historia IMAGEN                               historia en Facebook e Instagram
  reel VIDEO --texto ARCHIVO [--solo fb|ig]     reel en Instagram y en Facebook
  fb-video-oculto VIDEO                         sube un video sin publicar y da su URL pública
  buffer --texto ARCHIVO (--imagen URL | --video URL) [--canal ID]
  buffer-canales                                lista los canales conectados a Buffer
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import time

G = "https://graph.facebook.com/v21.0"
PAGE = "1420915107761834"
IG = "17841475605614144"
BUFFER = "https://api.buffer.com"
BUFFER_ORG = "6ad15a56eb2d5b90ec416429"
LINKEDIN = "6ad15abc778b240e2f207806"


def token(name):
    t = os.environ.get(name)
    if not t:
        sys.exit(f"Falta la variable de entorno {name}")
    return t


def curl(args, data=None):
    cmd = ["curl", "-sS", "--max-time", "600"] + args
    out = subprocess.run(cmd, input=data, capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"curl falló ({out.returncode}): {out.stderr.decode(errors='replace')[:300]}")
    body = out.stdout.decode(errors="replace")
    try:
        res = json.loads(body)
    except json.JSONDecodeError:
        raise SystemExit(f"Respuesta inesperada: {body[:300]}")
    if isinstance(res, dict) and "error" in res:
        raise SystemExit(f"Error de la API: {json.dumps(res['error'], ensure_ascii=False)[:500]}")
    return res


def graph(method, path, tok, fields=None, files=None, get=None):
    args = ["-H", f"Authorization: Bearer {tok}"]
    if method == "GET":
        url = f"{G}/{path}"
        if get:
            args += ["-G"] + sum([["--data-urlencode", f"{k}={v}"] for k, v in get.items()], [])
        return curl(args + [url])
    args += ["-X", "POST"]
    for k, v in (fields or {}).items():
        args += ["--form-string", f"{k}={v}"]
    for k, v in (files or {}).items():
        args += ["-F", f"{k}=@{v}"]
    return curl(args + [f"{G}/{path}"])


def page_token():
    res = graph("GET", "me/accounts", token("META_TOKEN"), get={"fields": "id,access_token"})
    for a in res.get("data", []):
        if a["id"] == PAGE:
            return a["access_token"]
    return token("META_TOKEN")


def leer(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip()


def url_foto(photo_id):
    return graph("GET", photo_id, token("META_TOKEN"), get={"fields": "images"})["images"][0]["source"]


def esperar(container, intentos=30, pausa=10):
    for _ in range(intentos):
        st = graph("GET", container, token("META_TOKEN"), get={"fields": "status_code"}).get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise SystemExit(f"El contenedor {container} quedó en {st}")
        time.sleep(pausa)
    raise SystemExit(f"El contenedor {container} no terminó de procesarse")


def ig_publicar(container):
    t = token("META_TOKEN")
    esperar(container)
    mid = graph("POST", f"{IG}/media_publish", t, {"creation_id": container})["id"]
    link = graph("GET", mid, t, get={"fields": "permalink"}).get("permalink")
    return {"ig_id": mid, "ig_link": link}


def fb_foto(imagen, texto=None, oculta=False):
    fields = {"published": "false" if oculta else "true"}
    if texto:
        fields["caption"] = texto
    res = graph("POST", f"{PAGE}/photos", page_token(), fields, {"source": imagen})
    out = {"photo_id": res["id"]}
    if res.get("post_id"):
        out["fb_post_id"] = res["post_id"]
        out["fb_link"] = f"https://www.facebook.com/{res['post_id']}"
    out["url"] = url_foto(res["id"])
    return out


def cmd_fb_foto(a):
    return fb_foto(a.imagen, leer(a.texto) if a.texto else None, a.oculta)


def cmd_fb_carrusel(a):
    pt = page_token()
    ids, urls = [], []
    for img in a.imagenes:
        pid = graph("POST", f"{PAGE}/photos", pt, {"published": "false"}, {"source": img})["id"]
        ids.append(pid)
        urls.append(url_foto(pid))
    fields = {"message": leer(a.texto)}
    for i, pid in enumerate(ids):
        fields[f"attached_media[{i}]"] = json.dumps({"media_fbid": pid})
    post = graph("POST", f"{PAGE}/feed", pt, fields)["id"]
    return {"fb_post_id": post, "fb_link": f"https://www.facebook.com/{post}", "photo_ids": ids, "urls": urls}


def cmd_ig_imagen(a):
    c = graph("POST", f"{IG}/media", token("META_TOKEN"), {"image_url": a.url, "caption": leer(a.texto)})["id"]
    return ig_publicar(c)


def cmd_ig_carrusel(a):
    t = token("META_TOKEN")
    hijos = []
    for u in a.urls:
        h = graph("POST", f"{IG}/media", t, {"image_url": u, "is_carousel_item": "true"})["id"]
        esperar(h)
        hijos.append(h)
    c = graph("POST", f"{IG}/media", t,
              {"media_type": "CAROUSEL", "children": ",".join(hijos), "caption": leer(a.texto)})["id"]
    return ig_publicar(c)


def cmd_historia(a):
    out = {}
    pt = page_token()
    foto = fb_foto(a.imagen, oculta=True)
    try:
        out["fb_historia"] = graph("POST", f"{PAGE}/photo_stories", pt, {"photo_id": foto["photo_id"]}).get("post_id")
    except SystemExit as e:
        out["fb_error"] = str(e)
    try:
        c = graph("POST", f"{IG}/media", token("META_TOKEN"), {"media_type": "STORIES", "image_url": foto["url"]})["id"]
        out["ig_historia"] = ig_publicar(c)["ig_id"]
    except SystemExit as e:
        out["ig_error"] = str(e)
    return out


def subir_rupload(url, tok, video):
    size = os.path.getsize(video)
    return curl(["-X", "POST", "-H", f"Authorization: OAuth {tok}", "-H", "offset: 0",
                 "-H", f"file_size: {size}", "--data-binary", f"@{video}", url])


def fb_video_oculto(video):
    pt = page_token()
    vid = graph("POST", f"{PAGE}/videos", pt, {"published": "false"}, {"source": video})["id"]
    for _ in range(30):
        src = graph("GET", vid, token("META_TOKEN"), get={"fields": "source"}).get("source")
        if src:
            return {"video_id": vid, "url": src}
        time.sleep(10)
    raise SystemExit(f"El video {vid} no tiene URL pública todavía")


def reel_ig(video, texto):
    t = token("META_TOKEN")
    res = graph("POST", f"{IG}/media", t, {"media_type": "REELS", "upload_type": "resumable",
                                           "caption": texto, "share_to_feed": "true"})
    try:
        subir_rupload(res["uri"], t, video)
        c = res["id"]
    except SystemExit:
        url = fb_video_oculto(video)["url"]
        c = graph("POST", f"{IG}/media", t, {"media_type": "REELS", "video_url": url,
                                             "caption": texto, "share_to_feed": "true"})["id"]
    return ig_publicar(c)


def reel_fb(video, texto):
    pt = page_token()
    try:
        start = graph("POST", f"{PAGE}/video_reels", pt, {"upload_phase": "start"})
        vid = start["video_id"]
        subir_rupload(start.get("upload_url") or f"https://rupload.facebook.com/video-upload/v21.0/{vid}", pt, video)
        graph("POST", f"{PAGE}/video_reels", pt, {"upload_phase": "finish", "video_id": vid,
                                                  "video_state": "PUBLISHED", "description": texto})
        return {"fb_video_id": vid, "fb_link": f"https://www.facebook.com/reel/{vid}"}
    except SystemExit:
        vid = graph("POST", f"{PAGE}/videos", pt, {"description": texto}, {"source": video})["id"]
        return {"fb_video_id": vid, "fb_link": f"https://www.facebook.com/{PAGE}/videos/{vid}", "fb_nota": "subido como video"}


def cmd_reel(a):
    texto = leer(a.texto)
    out = {}
    for red, fn in (("ig", reel_ig), ("fb", reel_fb)):
        if a.solo and a.solo != red:
            continue
        try:
            out.update(fn(a.video, texto))
        except SystemExit as e:
            out[f"{red}_error"] = str(e)
    return out


def cmd_fb_video_oculto(a):
    return fb_video_oculto(a.video)


def buffer(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    res = curl(["-X", "POST", "-H", f"Authorization: Bearer {token('BUFFER_TOKEN')}",
                "-H", "Content-Type: application/json", "--data-binary", "@-", BUFFER], data=body)
    if res.get("errors"):
        raise SystemExit(f"Error de Buffer: {json.dumps(res['errors'], ensure_ascii=False)[:500]}")
    return res["data"]


def cmd_buffer(a):
    due = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    asset = {"image": {"url": a.imagen}} if a.imagen else {"video": {"url": a.video}}
    q = ("mutation($input: CreatePostInput!){createPost(input:$input){__typename "
         "... on PostActionSuccess { post { id status dueAt } } ... on MutationError { message }}}")
    res = buffer(q, {"input": {"channelId": a.canal, "text": leer(a.texto), "schedulingType": "automatic",
                               "mode": "customScheduled", "dueAt": due, "needsApproval": False, "assets": [asset]}})
    r = res["createPost"]
    if "post" not in r:
        raise SystemExit(f"Buffer no programó el post: {json.dumps(r, ensure_ascii=False)}")
    return r["post"]


def cmd_buffer_canales(a):
    q = 'query($o: OrganizationId!){channels(input:{organizationId:$o}){id name service}}'
    try:
        return buffer(q, {"o": BUFFER_ORG})
    except SystemExit:
        return buffer('{channels(input:{organizationId:"%s"}){id name service}}' % BUFFER_ORG)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("fb-foto"); x.add_argument("imagen"); x.add_argument("--texto"); x.add_argument("--oculta", action="store_true")
    x = s.add_parser("fb-carrusel"); x.add_argument("--texto", required=True); x.add_argument("imagenes", nargs="+")
    x = s.add_parser("ig-imagen"); x.add_argument("--texto", required=True); x.add_argument("url")
    x = s.add_parser("ig-carrusel"); x.add_argument("--texto", required=True); x.add_argument("urls", nargs="+")
    x = s.add_parser("historia"); x.add_argument("imagen")
    x = s.add_parser("reel"); x.add_argument("video"); x.add_argument("--texto", required=True); x.add_argument("--solo", choices=["fb", "ig"])
    x = s.add_parser("fb-video-oculto"); x.add_argument("video")
    x = s.add_parser("buffer"); x.add_argument("--texto", required=True); x.add_argument("--canal", default=LINKEDIN)
    g = x.add_mutually_exclusive_group(required=True); g.add_argument("--imagen"); g.add_argument("--video")
    s.add_parser("buffer-canales")
    a = p.parse_args()
    print(json.dumps(globals()["cmd_" + a.cmd.replace("-", "_")](a), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
