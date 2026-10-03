import argparse
import csv
import json
import os
import time

from comum import gerar_instancia, salvar_instancia
from hibrido import exato_puro, heuristica_pura, hibrido, limitante_trivial

ABORDAGENS = {
    "Heuristica (ILS)": lambda r, m, T, s: heuristica_pura(r, m, T, s),
    "Exato (CBC)": lambda r, m, T, s: exato_puro(r, m, T, s),
    "Hibrido (janela)": lambda r, m, T, s: hibrido(r, m, T, s, "janela"),
    "Hibrido (maquinas)": lambda r, m, T, s: hibrido(r, m, T, s, "maquinas"),
}

def semente_do_tamanho(n):
    return 2026 + n  

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tamanhos", type=int, nargs="+", default=[6, 8, 10, 12, 15, 20])
    ap.add_argument("--m", type=int, default=5)
    ap.add_argument("--T", type=float, default=60)
    ap.add_argument("--reps", type=int, default=1, help="repeticoes das abordagens com aleatoriedade")
    ap.add_argument("--saida", default="resultados")
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    os.makedirs("instancias", exist_ok=True)

    linhas, historicos = [], {}
    if os.path.exists(f"{a.saida}/resultados.csv"):
        linhas = list(csv.DictReader(open(f"{a.saida}/resultados.csv")))
        historicos = json.load(open(f"{a.saida}/historicos.json"))
    feitos = {(int(l["N"]), l["abordagem"], int(l["rep"])) for l in linhas}
    for n in a.tamanhos:
        sem = semente_do_tamanho(n)
        rotas = gerar_instancia(n, a.m, sem)
        salvar_instancia(rotas, a.m, f"instancias/jssp_N{n}_m{a.m}.txt",
                         f"N={n} jobs, m={a.m} maquinas, duracoes 1-99, semente {sem}")
        lb_triv = limitante_trivial(rotas, a.m)
        for nome, func in ABORDAGENS.items():
            reps = 1 if nome == "Exato (CBC)" else a.reps
            for rep in range(reps):
                if (n, nome, rep) in feitos:
                    continue
                t0 = time.time()
                r = func(rotas, a.m, a.T, rep)
                linha = {"N": n, "m": a.m, "semente": sem, "abordagem": nome, "rep": rep,
                         "makespan": r["ub"], "lb_solver": r["lb"], "lb_trivial": lb_triv,
                         "status": r["status"], "t_prova": r["t_prova"],
                         "t_solver_final": r.get("t_solver_final"),
                         "subproblemas_fo": r.get("subproblemas"),
                         "makespan_apos_fo": r.get("ub_apos_fo"),
                         "tempo_total": round(time.time() - t0, 2)}
                linhas.append(linha)
                historicos[f"{n}|{nome}|{rep}"] = r["historico"]
                print(linha, flush=True)
            
                with open(f"{a.saida}/resultados.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=list(linha.keys()), extrasaction="ignore")
                    w.writeheader()
                    w.writerows(linhas)
                with open(f"{a.saida}/historicos.json", "w") as f:
                    json.dump(historicos, f)
