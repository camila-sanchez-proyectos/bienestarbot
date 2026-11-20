"""Ejecuta un archivo .sql en la base bienestarbot.  Uso:  python ejecutar_sql.py sql\\danzas.sql"""
import sys
from db import get_connection


def sentencias(texto):
    lineas = [l for l in texto.splitlines() if not l.strip().startswith("--")]
    for s in "\n".join(lineas).split(";"):
        if s.strip():
            yield s.strip()


def main():
    if len(sys.argv) != 2:
        print("Uso: python ejecutar_sql.py ruta\\archivo.sql")
        return 1
    with open(sys.argv[1], encoding="utf-8") as f:
        texto = f.read()
    con = get_connection()
    cur = con.cursor()
    n = 0
    try:
        for s in sentencias(texto):
            cur.execute(s)
            n += 1
            if cur.with_rows:
                filas = cur.fetchall()
                print([c[0] for c in cur.description])
                for fila in filas:
                    print(fila)
        con.commit()
    except Exception as e:
        con.rollback()
        print("ERROR:", e)
        print("Sentencia:", s[:200])
        return 1
    finally:
        con.close()
    print(f"Listo: {n} sentencias ejecutadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
