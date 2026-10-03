import itertools
import random
import time

from comum import caminho_critico, decodificar, sequencia_de_agenda
from exato import ModeloJSSP
from heuristica import ils


def limitante_trivial(rotas, m):
    carga = [0] * m
    for rota in rotas:
        for k, d in rota:
            carga[k] += d
    return max(max(carga), max(sum(d for _, d in r) for r in rotas))

def compactar(rotas, m, inicio):
    return decodificar(rotas, m, sequencia_de_agenda(rotas, inicio))

def vizinhancas_janela(rotas, inicio, ms, frac, chaves):
    dur = {(j, k): d for j, r in enumerate(rotas) for k, d in r}
    w = max(1, frac * ms)
    a = 0.0
    lista = []
    while a < ms:
        b = a + w
        dentro = {op for op in inicio if inicio[op] < b and inicio[op] + dur[op] > a}
        livres = {(i, j, k) for (i, j, k) in chaves if (i, k) in dentro and (j, k) in dentro}
        if livres:
            lista.append(livres)
        a += w / 2
    return lista

def vizinhancas_maquinas(rotas, m, inicio, ms, qtd, chaves, rng, limite=8):
    criticas = [k for _, k in caminho_critico(rotas, m, inicio, ms)]
    freq = {k: criticas.count(k) for k in range(m)}
    combos = list(itertools.combinations(range(m), qtd))
    rng.shuffle(combos)
    combos.sort(key=lambda c: -sum(freq[k] for k in c))
    lista = []
    for c in combos[:limite]:
        lista.append({key for key in chaves if key[2] in c})
    return lista

def fix_and_optimize(modelo, rotas, m, inicio, ms, tempo, estrategia="janela",
                     sub_t=5, semente=0, t_base=0.0):
    rng = random.Random(semente)
    t0 = time.time()
    prazo = t0 + tempo
    chaves = list(modelo.y.keys())
    historico = []
    tam = 0.3 if estrategia == "janela" else 2   
    subproblemas = 0
    while time.time() < prazo - 1:
        if estrategia == "janela":
            viz = vizinhancas_janela(rotas, inicio, ms, tam, chaves)
        else:
            viz = vizinhancas_maquinas(rotas, m, inicio, ms, tam, chaves, rng)
        melhorou = False
        for livres in viz:
            restante = prazo - time.time()
            if restante < 1:
                break
            modelo.fixar(livres, inicio)
            modelo.definir_inicial(inicio, ms)
            res = modelo.resolver(min(sub_t, restante), warm=True)
            subproblemas += 1
            if res["ub"] is not None and res["ub"] < ms:
                ms_c, ini_c = compactar(rotas, m, res["inicio"])
                if ms_c <= res["ub"]:
                    ms, inicio = ms_c, ini_c
                else:
                    ms, inicio = res["ub"], res["inicio"]
                historico.append((t_base + time.time() - t0, ms))
                melhorou = True
                break  
        if not melhorou:  
            if estrategia == "janela":
                tam = tam * 1.5
                if tam > 0.7:
                    break 
            else:
                tam = tam + 1
                if tam > m - 1:
                    break
    modelo.fixar(None)
    return inicio, ms, historico, subproblemas

def heuristica_pura(rotas, m, T, semente=0):
    h = ils(rotas, m, T, semente)
    return {"ub": h["makespan"], "lb": None, "status": "heuristica",
            "historico": h["historico"], "t_prova": None}

def exato_puro(rotas, m, T, semente=0, corte_carga=False):
    t0 = time.time()
    mod = ModeloJSSP(rotas, m, corte_carga)
    res = mod.resolver(T - (time.time() - t0))
    hist = [(time.time() - t0, res["ub"])] if res["ub"] is not None else []
    return {"ub": res["ub"], "lb": res["lb"], "status": res["status"], "historico": hist,
            "t_prova": time.time() - t0 if res["status"] == "otimo" else None}

def hibrido(rotas, m, T, semente=0, estrategia="janela", frac_heur=0.15, frac_fo=0.5, sub_t=5):
    t0 = time.time()
    h = ils(rotas, m, frac_heur * T, semente, parada_estagnacao=3)
    hist = list(h["historico"])
    mod = ModeloJSSP(rotas, m)
    inicio, ms, hist_fo, nsub = fix_and_optimize(
        mod, rotas, m, h["inicio"], h["makespan"], frac_fo * T, estrategia,
        sub_t, semente, t_base=time.time() - t0)
    hist += hist_fo
    mod.definir_inicial(inicio, ms)
    t_solver = time.time()
    res = mod.resolver(T - (time.time() - t0), warm=True)
    t_solver = time.time() - t_solver
    ub = min(ms, res["ub"] or ms)
    hist.append((time.time() - t0, ub))
    return {"ub": ub, "lb": res["lb"], "status": res["status"], "historico": hist,
            "t_prova": time.time() - t0 if res["status"] == "otimo" else None,
            "subproblemas": nsub, "ub_apos_fo": ms, "t_solver_final": t_solver}
