import requests
import time

cultivos = {
    # CAFÉ
    "kwvf-nwea": "Café — Nacional",
    "qaa2-6p2j": "Café — Quindío",
    "ggaa-6f3s": "Café — Nariño",
    "879x-8fjs": "Café — Meta",
    "h4ms-ukui": "Café sostenible — Cesar",
    # CACAO
    "jdjx-qer4": "Cacao — Nacional",
    "mqnw-3mh7": "Cacao — Nariño",
    "rudm-65w2": "Cacao — Huila",
    "mb3q-3sz7": "Cacao — Quindío",
    "y9yk-egv6": "Cacao tradicional — Cesar",
    # AGUACATE
    "tx7u-frn2": "Aguacate Hass — Nacional",
    "sa3-4smd":  "Aguacate Hass — Nariño",
    "7iny-qc7t": "Aguacate Hass — Quindío",
    "4ia2-7v6d": "Aguacate Hass — Cesar",
    "eyi3-xt36": "Aguacate Hass — Caldas",
    "636v-m2ev": "Aguacate Hass — Huila",
    "jypt-2gk9": "Aguacate Lorena — Guaviare",
    "25qu-8req": "Aguacate Lorena — Huila",
    "fy4v-wdq8": "Aguacate Lorena — Cundinamarca",
    "69q9-rai5": "Aguacate — Providencia",
    # MANGO
    "xt32-m7dh": "Mango — Nacional",
    "3et4-t2c5": "Mango Keitt — Cesar",
    "y4cn-bxu2": "Mango — Providencia",
    # BANANO / PLÁTANO
    "rcfj-3e57": "Banano exportación — Nacional",
    "u2p6-8yb3": "Plátano Dominico Hartón — Cundinamarca",
    "dem5-6d9s": "Plátano Hartón — Atlántico",
    "ivuy-xix4": "Plátano Dominico-Hartón — Quindío",
    "b54w-9ds5": "Plátano Hartón — La Guajira",
    "s677-e5cz": "Plátano Hartón — Meta",
    "6wzx-ggdn": "Plátano Dominico Hartón — Huila",
    "3yy6-rhsa": "Plátano Dominico Hartón — Guaviare",
    "anfi-qbc9": "Plátano Hartón — Nariño",
    "ajqd-rrw4": "Plátano Hartón — Providencia",
    "5rh6-a2iu": "Banano — Quindío",
    # PIÑA
    "8fa5-z4v3": "Piña — Nacional",
    "64hn-54ty": "Piña — Guaviare",
    # PAPAYA
    "urxm-qzje": "Papaya Tainung — Nacional",
    "qas8-ccb3": "Papaya — Providencia",
    # MARACUYÁ
    "hxs5-w7gt": "Maracuyá — Nacional",
    "y9hs-jfab": "Maracuyá — Providencia",
    # GULUPA
    "q6xp-whkm": "Gulupa — Nacional",
    # GRANADILLA
    "aikj-ub3k": "Granadilla — Nacional",
    "mhhn-vmqz": "Granadilla — Nariño",
    "9med-ri2n": "Granadilla — Huila",
    # FRESA
    "emsg-94di": "Fresa — Nacional",
    # CAÑA PANELERA
    "p9xp-sm4v": "Caña panelera — Nacional",
    "6x5b-q3gn": "Caña panelera — Cundinamarca",
    "3mhn-7v7g": "Caña panelera — Nariño",
    "pkzc-fdc6": "Caña panelera — Providencia",
    # MAÍZ
    "frjn-92um": "Maíz tradicional — Nacional",
    "a5yc-uszt": "Maíz tecnificado S1 — Nacional",
    "tzga-4zse": "Maíz tecnificado S2 — Nacional",
    "2jg2-cz3h": "Maíz — Nariño",
    "5xf8-ad6s": "Maíz amarillo tradicional — Atlántico",
    "v7fj-zkda": "Maíz amarillo — Huila",
    "7w2f-3igv": "Maíz — Guaviare",
    "nrux-cqtm": "Maíz S1 — Cesar",
    "rbyp-j3mc": "Maíz S2 — Cesar",
    "difg-83ug": "Maíz comercial — La Guajira",
    "debn-kdjs": "Maíz tradicional — Providencia",
    "g39x-8d2s": "Maíz Lago de Tota — Boyacá",
    # ARROZ
    "ibc9-9f7c": "Arroz secano — Nacional",
    "53g3-xmry": "Arroz riego S2 — Cesar",
    "29cv-av7d": "Arroz riego — Cundinamarca",
    "xk39-mtxv": "Arroz riego S1/S2 — Huila",
    # SOYA
    "2qt2-dhv7": "Soya S1 — Nacional",
    "hixf-wnis": "Soya S2 — Nacional",
    "4vcv-s5e4": "Soya S1 — Meta",
    "sndv-njkv": "Soya S2 — Meta",
    # PAPA
    "jwn7-76wn": "Papa S1 — Nacional",
    "s455-c4e6": "Papa S2 — Nacional",
    "krw4-fwxq": "Papa Diacol Capiro S1 — Nacional",
    "xcau-7myt": "Papa Diacol Capiro S2 — Nacional",
    "pxyg-5a3u": "Papa — Nariño",
    "eu27-em7n": "Papa Lago de Tota — Boyacá",
    # CEBOLLA
    "btsg-jtqh": "Cebolla bulbo S1 — Nacional",
    "nxvg-ufyf": "Cebolla bulbo S2 — Nacional",
    "s8ha-htq3": "Cebolla bulbo S1 — Quindío",
    "3v25-65vb": "Cebolla bulbo S2 — Quindío",
    "gmhx-jpnm": "Cebolla junca Lago de Tota — Boyacá",
    "j3wf-8pc3": "Cebolla — Providencia",
    # PIMENTÓN
    "ejwn-f7s3": "Pimentón — Nacional",
    "jk8t-3tkp": "Pimentón — Providencia",
    # AJÍ
    "yhkr-7mkb": "Ají tabasco — Nacional",
    "kdv9-gkv3": "Ají dulce — Atlántico",
    "6qqs-nvat": "Ají tabasco — Providencia",
    # FRIJOL Y LEGUMINOSAS
    "3km6-irsn": "Frijol voluble S1 — Cundinamarca",
    "kkgy-qrxf": "Frijol voluble S2 — Cundinamarca",
    "a43r-dc7n": "Frijol — Nariño",
    "x759-i2ry": "Frijol comercial — La Guajira",
    "feta-2znm": "Frijol voluble S1 — Huila",
    "pfbw-b9ii": "Frijol voluble S2 — Huila",
    "xav2-8ydm": "Frijol Caupí — Providencia",
    "4r7r-xeii": "Arveja — Nariño",
    "qxjk-6yi9": "Arveja — Cundinamarca",
    "kt5r-xnym": "Leguminosas clima frío — Boyacá",
    "ybku-2354": "Guandul — Providencia",
    # YUCA
    "uumx-3w28": "Yuca tecnificada — La Guajira",
    "4nrr-z5es": "Yuca tecnificada — Atlántico",
    "y54p-nmuh": "Yuca tecnificada — Guaviare",
    "s285-a6ur": "Yuca tradicional — Meta",
    "siim-cru8": "Yuca — Providencia",
    # MORA
    "ktcq-6bpt": "Mora — Nariño",
    "h47g-czi9": "Mora Castilla — Quindío",
    "icwf-97sk": "Mora Castilla — Cundinamarca",
    # TOMATE
    "xsme-6vyj": "Tomate — Huila",
    # ZANAHORIA
    "ijus-ubej": "Zanahoria — Cundinamarca",
    # HORTALIZAS
    "jggq-mvpu": "Brócoli — Nariño",
    "72wu-5rhp": "Lechuga — Nariño",
    "gcsg-vnpm": "Hortalizas clima frío — Cundinamarca",
    # CÍTRICOS
    "vmtc-ncna": "Naranja — Cesar",
    "ucuk-raek": "Limón Tahití — Quindío",
    "28p6-pmgg": "Limón criollo — Atlántico",
    "stbn-yd46": "Limón tahití — Nariño",
    "shk3-wean": "Limón — Providencia",
    "v534-yr4y": "Cítricos — Guaviare",
    # CUCURBITÁCEAS
    "2ish-f4p6": "Patilla S1 — Meta",
    "gd2m-mne6": "Patilla S2 — Meta",
    "ya3i-feur": "Patilla — La Guajira",
    "uw8p-y6se": "Patilla — Providencia",
    "pi86-3vyw": "Melón — La Guajira",
    "rtjr-qdfb": "Melón Cantaloupe — Atlántico",
    "ezuf-ch6k": "Melón — Providencia",
    "u27e-3x6i": "Ahuyama tradicional — Atlántico",
    "mvw3-dyd9": "Ahuyama comercial — La Guajira",
    "x7ng-52ik": "Ahuyama — Providencia",
    # QUINUA
    "r55b-dpkh": "Quinua — Nariño",
    # ACUICULTURA
    "c7qw-4mck": "Pirarucú — Nacional",
    "ettd-cd85": "Cachama — Nacional",
    "sf4k-mkw2": "Tilapia — Nacional",
    "9cr3-4384": "Trucha arcoíris — Huila",
    "76gh-h4ct": "Bocachico/Bagre/Yamu — Huila",
    # OTROS
    "2cfr-3988": "Guanábana — Providencia",
    "dy4b-zarf": "Coco — Providencia",
    "7xfm-jym2": "Chontaduro — Guaviare",
    "n5rr-wiea": "Árbol del pan — Providencia",
    "yqqe-3s5c": "Batata — Providencia",
    "2m9w-xveu": "Ñame — Providencia",
}

print(f"Total datasets a verificar: {len(cultivos)}")
print("=" * 60)

ok, error = [], []
for dataset_id, nombre in cultivos.items():
    url = f"https://www.datos.gov.co/resource/{dataset_id}.json?$select=count(*)"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and r.json():
            total = r.json()[0].get("count", "?")
            print(f"✅ {nombre} ({dataset_id}) — {total} registros")
            ok.append(nombre)
        else:
            print(f"❌ {nombre} ({dataset_id}) — HTTP {r.status_code}")
            error.append(nombre)
    except Exception as e:
        print(f"❌ {nombre} ({dataset_id}) — ERROR: {e}")
        error.append(nombre)
    time.sleep(0.2)  # evitar rate limiting

print(f"\n{'='*60}")
print(f"✅ Accesibles:  {len(ok)}")
print(f"❌ Con error:   {len(error)}")
if error:
    print(f"\nFallidos:")
    for e in error:
        print(f"  {e}")