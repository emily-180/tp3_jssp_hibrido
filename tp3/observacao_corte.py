import argparse
import time

from comum import gerar_instancia
from exato import ModeloJSSP
from heuristica import ils
from hibrido import limitante_trivial

ap = argparse.ArgumentParser()
ap.add_argument("--N", type=int, default=10)
ap.add_argument("--m", type=int, default=5)
ap.add_argument("--T", type=float, default=60)
a = ap.parse_args()

rotas = gerar_instancia(a.N, a.m, 2026 + a.N)
h = ils(rotas, a.m, 0.15 * a.T, 0, parada_estagnacao=3)
print(f"N={a.N}: ILS = {h['makespan']} | limitante trivial = {limitante_trivial(rotas, a.m)}")
for corte in (False, True):
    mod = ModeloJSSP(rotas, a.m, corte_carga=corte)
    mod.definir_inicial(h["inicio"], h["makespan"])
    t0 = time.time()
    r = mod.resolver(a.T, warm=True)
    print(f"  corte={corte}: makespan={r['ub']}  limitante do CBC={r['lb']}  "
          f"status={r['status']}  tempo={time.time() - t0:.1f}s")
