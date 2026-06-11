import numpy as np, pyvista as pv, os, subprocess, time
from PIL import Image

if not os.path.exists('/tmp/.X99-lock'):
    subprocess.Popen(["Xvfb", ":99", "-screen", "0", "2400x1400x24"]); time.sleep(2)
os.environ["DISPLAY"] = ":99"

# ---------- Protsedurali teksturalar ----------
def fbm(shape, octaves=6, seed=1):
    rng = np.random.default_rng(seed)
    out = np.zeros(shape)
    for o in range(octaves):
        f = 2 ** o
        small = rng.random((shape[0] // f + 2, shape[1] // f + 2))
        img = np.array(Image.fromarray((small * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)) / 255.0
        out += img / f
    return (out - out.min()) / (out.max() - out.min())

def marble_texture(path, size=2048, seed=3):
    rng = np.random.default_rng(seed)
    # katta masshtabli silliq shovqin (domain warp uchun)
    def smooth_noise(sz, cells, sd):
        r = np.random.default_rng(sd)
        small = r.random((cells, cells))
        return np.array(Image.fromarray((small*255).astype(np.uint8)).resize((sz,sz), Image.BICUBIC))/255.0
    n1 = smooth_noise(size, 6, seed)
    n2 = smooth_noise(size, 12, seed+1)
    n3 = smooth_noise(size, 24, seed+2)
    warp = n1*0.6 + n2*0.3 + n3*0.1
    x = np.linspace(0, 9*np.pi, size)
    xx = np.tile(x, (size,1))
    # asosiy tomirlar
    v1 = np.abs(np.sin(xx*0.9 + warp*11.0))
    veins1 = np.clip(1.0 - v1, 0, 1)**22
    # ikkilamchi nozik tomirlar
    v2 = np.abs(np.sin(xx*2.3 + warp*18.0 + 1.7))
    veins2 = np.clip(1.0 - v2, 0, 1)**30
    # qoramtir baza, juda yengil o'zgaruvchan
    base = np.zeros((size,size,3))
    tone = 0.85 + n1*0.3
    base[...,0] = 0.105*tone; base[...,1] = 0.075*tone; base[...,2] = 0.058*tone
    img = base.copy()
    img += veins1[...,None]*np.array([0.50,0.40,0.30])*0.55
    img += veins2[...,None]*np.array([0.65,0.61,0.55])*0.30
    img = np.clip(img,0,1)
    im = Image.fromarray((img*255).astype(np.uint8)).filter(__import__('PIL.ImageFilter',fromlist=['x']).GaussianBlur(1.2))
    im.save(path)

def wood_texture(path, size=1024, seed=7):
    n = fbm((size, size), 6, seed)
    y = np.linspace(0, 40 * np.pi, size)
    yy = np.tile(y[:, None], (1, size))
    grain = 0.5 + 0.5 * np.sin(yy * 0.35 + n * 9)
    img = np.zeros((size, size, 3))
    img[..., 0] = 0.58 + grain * 0.10
    img[..., 1] = 0.52 + grain * 0.09
    img[..., 2] = 0.42 + grain * 0.07
    planks = ((yy / (np.pi * 5)).astype(int) % 2) * 0.03
    img -= planks[..., None]
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path)

marble_texture("/home/claude/marble.png")
wood_texture("/home/claude/wood.png")

# ---------- OBJ parse (vt bilan) ----------
OBJ = "/mnt/user-data/uploads/1.obj"
verts, uvs = [], []
groups = {}   # mat -> list of [(vi,ti)x3]
cur = "default"
for line in open(OBJ, errors="ignore"):
    if line.startswith("v "):
        p = line.split(); verts.append((float(p[1]), float(p[2]), float(p[3])))
    elif line.startswith("vt "):
        p = line.split(); uvs.append((float(p[1]), float(p[2])))
    elif line.startswith("usemtl"):
        cur = line.strip().split(None, 1)[1]; groups.setdefault(cur, [])
    elif line.startswith("f "):
        corner = []
        for t in line.split()[1:]:
            parts = t.split("/")
            vi = int(parts[0]) - 1
            ti = int(parts[1]) - 1 if len(parts) > 1 and parts[1] else 0
            corner.append((vi, ti))
        g = groups.setdefault(cur, [])
        for i in range(1, len(corner) - 1):
            g.append((corner[0], corner[i], corner[i + 1]))

verts = np.array(verts, dtype=np.float32)
verts = verts[:, [0, 2, 1]]; verts[:, 1] *= -1
uvs = np.array(uvs, dtype=np.float32) if uvs else np.zeros((1, 2), np.float32)

TEX_MARBLE = {"stoleshnitsa", "fasrtuk"}
TEX_WOOD = {"pol"}

def style(name):
    n = name.lower()
    if "stena" in n:                          return (0.89,0.85,0.79), 0.0, 0.95, 1.0
    if "steklo" in n:                         return (0.78,0.87,0.90), 0.3, 0.05, 0.30
    if "dukhovka" in n or "duxovka" in n or "mikrovolnovka" in n:
                                              return (0.09,0.09,0.10), 0.55, 0.35, 1.0
    if "chernyy" in n or "grafit" in n or "anthracite" in n:
                                              return (0.08,0.08,0.09), 0.2, 0.4, 1.0
    if any(k in n for k in ("khrom","nikel","stal","anodirovanie","tsink","zink","galvanized","nerzhav")):
                                              return (0.78,0.79,0.81), 0.9, 0.22, 1.0
    if "krasnaya" in n or "oranzh" in n or "orange" in n:
                                              return (0.88,0.88,0.87), 0.1, 0.6, 1.0
    if "seryy" in n or n == "10" or "zamena" in n:
                                              return (0.66,0.66,0.66), 0.2, 0.6, 1.0
    return (0.965,0.962,0.955), 0.0, 0.45, 1.0

pl = pv.Plotter(off_screen=True, window_size=(2200, 1300), lighting="none")
pl.set_background("#e9ecf0", top="#f9fafc")

tex_marble = pv.read_texture("/home/claude/marble.png")
tex_marble.repeat = True
tex_marble.interpolate = True
tex_marble.mipmap = True
tex_wood = pv.read_texture("/home/claude/wood.png")
tex_wood.repeat = True
tex_wood.interpolate = True
tex_wood.mipmap = True

for mat, faces in groups.items():
    if not faces: continue
    n = mat.lower()
    textured = any(k in n for k in TEX_MARBLE) or any(k in n for k in TEX_WOOD)
    fa_pairs = faces
    if textured:
        # har bir burchak (vi,ti) alohida nuqta
        pair_map = {}
        pts, tcs, f2 = [], [], []
        for tri in fa_pairs:
            idxs = []
            for (vi, ti) in tri:
                key = (vi, ti)
                if key not in pair_map:
                    pair_map[key] = len(pts)
                    pts.append(verts[vi])
                    u, vv = uvs[min(ti, len(uvs)-1)]
                    tcs.append((u * 0.16, vv * 0.16) if any(k in n for k in TEX_MARBLE) else (u * 0.12, vv * 0.12))
                idxs.append(pair_map[key])
            f2.append(idxs)
        pts = np.array(pts, np.float32); f2 = np.array(f2, np.int64)
        cells = np.hstack([np.full((len(f2),1), 3, np.int64), f2]).ravel()
        mesh = pv.PolyData(pts, cells)
        mesh.active_texture_coordinates = np.array(tcs, np.float32)
        tex = tex_marble if any(k in n for k in TEX_MARBLE) else tex_wood
        pl.add_mesh(mesh, texture=tex, pbr=False,
                    specular=0.25 if "pol" not in n else 0.05,
                    specular_power=70 if "pol" not in n else 8,
                    diffuse=(0.95 if "pol" not in n else 0.75), ambient=0.18,
                    smooth_shading=False)
    else:
        fa = np.array([[c[0] for c in tri] for tri in fa_pairs], np.int64)
        used = np.unique(fa)
        remap = np.zeros(used.max() + 1, np.int64); remap[used] = np.arange(len(used))
        pts = verts[used]; f2 = remap[fa]
        cells = np.hstack([np.full((len(f2),1), 3, np.int64), f2]).ravel()
        mesh = pv.PolyData(pts, cells)
        color, metal, rough, opac = style(mat)
        if metal > 0.3:
            pl.add_mesh(mesh, color=color, pbr=True, metallic=metal, roughness=rough,
                        opacity=opac, smooth_shading=False)
        else:
            pl.add_mesh(mesh, color=color, pbr=False, opacity=opac,
                        diffuse=0.58, ambient=0.20, specular=0.10, specular_power=25,
                        smooth_shading=False)

c = [2230.0, -1000.0, 1300.0]
key  = pv.Light(position=(-4000, -7500, 5200), focal_point=c, intensity=2.2, light_type="scene light")
fill = pv.Light(position=(5500, -6500, 3000), focal_point=c, intensity=1.0, light_type="scene light")
top  = pv.Light(position=(2200, -2000, 9000), focal_point=c, intensity=0.8, light_type="scene light")
amb  = pv.Light(light_type="headlight", intensity=0.5)
for L in (key, fill, top, amb): pl.add_light(L)

views = {
    "render_umumiy_1":  dict(pos=(-3600, -8200, 4500), focal=(2500, -900, 1300), angle=33),
    "render_umumiy_2":  dict(pos=(-1500, -9200, 4200), focal=(2300, -800, 1300), angle=33),
    "render_orqa_qator": dict(pos=(-2200, -5200, 1750), focal=(2600, -300, 1400), angle=33),
    "render_yaqindan_plita": dict(pos=(-900, -3600, 1700), focal=(1700, 0, 1050), angle=33),
}
pl.enable_anti_aliasing("fxaa")
try: pl.enable_ssao(radius=18, kernel_size=64)
except Exception as e: print("ssao skip:", e)

for name, vw in views.items():
    pl.camera_position = [vw["pos"], vw["focal"], (0, 0, 1)]
    pl.camera.view_angle = vw["angle"]
    pl.render()
    pl.screenshot(f"/home/claude/{name}.png")
    print("saved", name, flush=True)
pl.close()
print("DONE")
