# Ver primeras 10 líneas crudas de cada SIPSA
for nombre, ruta in [("SIPSA-A", "comprobacion/csv/2026 (I cuatrimestre).csv"), ("SIPSA-P", "comprobacion/csv/mensual 24.csv")]:
    print("=" * 60)
    print(nombre)
    print("=" * 60)
    try:
        with open(ruta, encoding="latin-1") as f:
            for i, linea in enumerate(f):
                if i >= 10:
                    break
                print(f"  Línea {i}: {linea.rstrip()}")
    except Exception as e:
        # Intentar con utf-8
        try:
            with open(ruta, encoding="utf-8") as f:
                for i, linea in enumerate(f):
                    if i >= 10:
                        break
                    print(f"  Línea {i}: {linea.rstrip()}")
        except Exception as e2:
            print(f"  ERROR: {e2}")