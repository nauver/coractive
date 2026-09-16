#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
orbbec_depth_bridge.py — Pont profondeur Orbbec Astra Pro -> LumoCoR (WebSocket)
================================================================================

Pourquoi ce pont ?
------------------
Un navigateur ne peut PAS lire le flux de profondeur d'une Astra Pro : via
getUserMedia il ne voit que la caméra couleur UVC de l'Astra, pas la profondeur.
La profondeur passe par OpenNI2 / le SDK Orbbec, côté natif. Ce script lit la
profondeur, en déduit une grille d'« occupation » (où se trouvent des personnes /
objets plus proches que le sol) et la diffuse en WebSocket. L'app LumoCoR se
connecte à ws://localhost:8765 (source « Orbbec 3D » dans Caméra & calibrage).

L'avantage de la profondeur sur le frame-diff webcam : la détection est robuste
à la lumière et détecte une présence IMMOBILE (quelqu'un debout sur une case),
ce que le frame-diff ne voit pas. Idéal pour une projection au sol.

Prérequis
---------
1) Le SDK OpenNI2 d'Orbbec pour l'Astra Pro (pilotes + Redist OpenNI2).
   - Windows/Linux : https://www.orbbec.com/developers/openni-sdk/
   - Repère le dossier "OpenNI2/Redist" (contient OpenNI2.dll / libOpenNI2.so).
2) pip install : numpy websockets  (+ un binding OpenNI2 : "openni" ou "primesense")
       pip install numpy websockets openni
   ("openni" = bindings primesense/OpenNI2. Selon l'install, le paquet peut
    s'appeler "primesense" — les deux imports sont tentés ci-dessous.)

Lancement
---------
    python orbbec_depth_bridge.py --openni-redist "C:/Program Files/OpenNI2/Redist"

Puis dans LumoCoR : Caméra & calibrage -> source "Orbbec 3D" -> Connecter.
IMPORTANT : héberge la page LumoCoR toi-même (Netlify, ou en local) pour que le
navigateur autorise le WebSocket local. L'aperçu claude.ai le bloque (mixed
content / bac à sable).

Astuce calibrage : au démarrage, laisse la zone VIDE ~2 s (le sol sert de fond
de référence). Puis règle --fg-threshold (mm) : plus bas = plus sensible.

--------------------------------------------------------------------------------
Note : ce pont est un point de départ testé « à blanc » — je n'ai pas ton Astra
sous la main. Si l'import OpenNI2 diffère chez toi (SDK Orbbec v2 / pyorbbec
pour les modèles récents), la seule partie à adapter est open_depth_stream().
Le reste (fond, occupation, WebSocket, protocole) est indépendant du SDK.
--------------------------------------------------------------------------------
"""

import argparse
import asyncio
import json
import sys
import time

import numpy as np

try:
    import websockets
except ImportError:
    sys.exit("Manque 'websockets' :  pip install websockets")

# ----- import OpenNI2 (deux noms de paquet possibles) -----
_openni2 = None
try:
    from openni import openni2 as _openni2          # binding "openni"
except Exception:
    try:
        from primesense import openni2 as _openni2  # binding "primesense"
    except Exception:
        _openni2 = None


# ==========================================================================
#  Acquisition profondeur
# ==========================================================================
class DepthSource:
    """Ouvre l'Astra via OpenNI2 et fournit des frames profondeur (numpy uint16, mm)."""

    def __init__(self, redist):
        if _openni2 is None:
            sys.exit("OpenNI2 introuvable. Installe le SDK Orbbec + 'pip install openni'. "
                     "Voir l'en-tête du script.")
        _openni2.initialize(redist)          # redist = dossier OpenNI2/Redist
        self.dev = _openni2.Device.open_any()
        self.stream = self.dev.create_depth_stream()
        self.stream.start()
        vm = self.stream.get_video_mode()
        self.w, self.h = vm.resolutionX, vm.resolutionY
        print(f"[orbbec] profondeur {self.w}x{self.h} @ {vm.fps}fps")

    def read(self):
        frame = self.stream.read_frame()
        buf = frame.get_buffer_as_uint16()
        d = np.frombuffer(buf, dtype=np.uint16).reshape(self.h, self.w)
        return d

    def close(self):
        try:
            self.stream.stop()
            _openni2.unload()
        except Exception:
            pass


class SimSource:
    """Source de secours (aucune caméra) : une tache mobile, pour tester le pont/protocole."""
    def __init__(self):
        self.w, self.h, self.t = 320, 240, 0.0
        print("[sim] pas de caméra — génération d'une tache de test")

    def read(self):
        self.t += 0.05
        d = np.full((self.h, self.w), 3000, np.uint16)   # « sol » à 3 m
        cx = int((0.5 + 0.35 * np.sin(self.t)) * self.w)
        cy = int((0.5 + 0.35 * np.cos(self.t * 0.7)) * self.h)
        yy, xx = np.ogrid[:self.h, :self.w]
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 < (self.w * 0.10) ** 2
        d[mask] = 1500                                    # « personne » à 1.5 m
        return d

    def close(self):
        pass


# ==========================================================================
#  Traitement : profondeur -> grille d'occupation (GW x GH, 0..255)
# ==========================================================================
class Occupancy:
    def __init__(self, gw, gh, near, far, fg_thr):
        self.gw, self.gh = gw, gh
        self.near, self.far = near, far        # plage valide (mm)
        self.fg_thr = fg_thr                   # écart mini au fond pour « présence » (mm)
        self.bg = None                         # modèle de fond (sol), par pixel

    def _update_bg(self, d, valid):
        # Le fond (sol) est la surface stable la PLUS LOINTAINE vue par pixel.
        if self.bg is None:
            self.bg = np.where(valid, d, self.far).astype(np.float32)
            return
        # remonte vite vers le plus loin (sol qui se dégage), redescend lentement
        farther = valid & (d > self.bg)
        self.bg[farther] = d[farther]
        self.bg = self.bg * 0.999 + np.where(valid, d, self.bg) * 0.001

    def process(self, d):
        valid = (d >= self.near) & (d <= self.far)
        self._update_bg(d, valid)
        # présence = nettement plus proche que le fond
        fg = valid & ((self.bg - d) > self.fg_thr)
        # downsample en moyenne d'occupation par cellule
        H, W = fg.shape
        fh, fw = H // self.gh, W // self.gw
        fg = fg[:fh * self.gh, :fw * self.gw].astype(np.float32)
        cells = fg.reshape(self.gh, fh, self.gw, fw).mean(axis=(1, 3))
        # petite courbe pour renforcer les cellules bien occupées
        cells = np.clip(cells * 2.2, 0, 1)
        return (cells * 255).astype(np.uint8).flatten().tolist()


# ==========================================================================
#  Serveur WebSocket
# ==========================================================================
class Bridge:
    def __init__(self, src, occ, fps):
        self.src, self.occ = src, occ
        self.period = 1.0 / fps
        self.clients = set()
        self.latest = None

    async def producer(self):
        gw, gh = self.occ.gw, self.occ.gh
        while True:
            t0 = time.time()
            try:
                d = self.src.read()
                grid = self.occ.process(d)
                self.latest = json.dumps({"w": gw, "h": gh, "d": grid})
            except Exception as e:
                print("[warn] frame:", e)
            if self.clients and self.latest:
                dead = set()
                for ws in self.clients:
                    try:
                        await ws.send(self.latest)
                    except Exception:
                        dead.add(ws)
                self.clients -= dead
            await asyncio.sleep(max(0, self.period - (time.time() - t0)))

    async def handler(self, ws):
        self.clients.add(ws)
        print(f"[ws] client connecté ({len(self.clients)})")
        try:
            await ws.wait_closed()
        finally:
            self.clients.discard(ws)
            print(f"[ws] client parti ({len(self.clients)})")


async def main():
    ap = argparse.ArgumentParser(description="Pont profondeur Orbbec -> LumoCoR")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--grid-w", type=int, default=48, help="largeur grille (doit matcher l'app)")
    ap.add_argument("--grid-h", type=int, default=36, help="hauteur grille (doit matcher l'app)")
    ap.add_argument("--near", type=int, default=600, help="profondeur mini valide (mm)")
    ap.add_argument("--far", type=int, default=8000, help="profondeur maxi valide (mm)")
    ap.add_argument("--fg-threshold", type=int, default=300,
                    help="écart au sol pour compter une présence (mm) — baisse = + sensible")
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--openni-redist", default=None,
                    help="dossier OpenNI2/Redist du SDK Orbbec")
    ap.add_argument("--sim", action="store_true", help="mode test sans caméra")
    args = ap.parse_args()

    if args.sim or _openni2 is None:
        if _openni2 is None and not args.sim:
            print("[info] OpenNI2 absent -> mode simulation. Installe le SDK pour la vraie profondeur.")
        src = SimSource()
    else:
        src = DepthSource(args.openni_redist)

    occ = Occupancy(args.grid_w, args.grid_h, args.near, args.far, args.fg_threshold)
    bridge = Bridge(src, occ, args.fps)

    print(f"[ws] écoute ws://{args.host}:{args.port}  (grille {args.grid_w}x{args.grid_h})")
    async with websockets.serve(bridge.handler, args.host, args.port):
        try:
            await bridge.producer()
        finally:
            src.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[bye]")
