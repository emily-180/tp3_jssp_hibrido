import csv
from collections import defaultdict

import matplotlib.pyplot as plt

PASTA = "resultados"
CORES = {"Heuristica (ILS)": "#1f77b4", "Exato (CBC)": "#c62828",
         "Hibrido (janela)": "#2e7d32", "Hibrido (maquinas)": "#f9a825"}
MARC = {"Heuristica (ILS)": "o", "Exato (CBC)": "s", "Hibrido (janela)": "D", "Hibrido (maquinas)": "v"}

def num(x):
    return float(x) if x not in ("", "None", None) else None

linhas = list(csv.DictReader(open(f"{PASTA}/resultados.csv")))
Ns = sorted({int(l["N"]) for l in linhas})
nomes = list(dict.fromkeys(l["abordagem"] for l in linhas))
res = defaultdict(list)
for l in linhas:
    res[(int(l["N"]), l["abordagem"])].append(l)

def media(lst, campo):
    v = [num(x[campo]) for x in lst if num(x[campo]) is not None]
    return sum(v) / len(v) if v else None

LB = {}
for n in Ns:
    da_vez = [l for l in linhas if int(l["N"]) == n]
    LB[n] = max([num(da_vez[0]["lb_trivial"])] +
                [num(l["lb_solver"]) for l in da_vez if num(l["lb_solver"]) is not None])

fig, ax = plt.subplots(figsize=(10, 5.5))
for i, nome in enumerate(nomes):
    ys = [100 * (media(res[(n, nome)], "makespan") - LB[n]) / LB[n] for n in Ns]
    ax.plot(Ns, ys, marker=MARC[nome], color=CORES[nome], label=nome, linewidth=2,
            markersize=9 - 1.5 * i)
ax.set_xlabel("N (numero de jobs)")
ax.set_ylabel("Gap para o melhor limitante inferior (%)")
ax.set_title("Qualidade da solucao em 60 s (0% = otimo)", fontweight="bold")
ax.set_xticks(Ns)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(f"{PASTA}/gap_por_tamanho.png", dpi=200)
plt.close(fig)

exatas = [n for n in nomes if n != "Heuristica (ILS)"]
T = max(num(l["tempo_total"]) for l in linhas)
fig, ax = plt.subplots(figsize=(10, 5.5))
larg = 0.8 / len(exatas)
for i, nome in enumerate(exatas):
    for k, n in enumerate(Ns):
        lst = res[(n, nome)]
        x = k + (i - (len(exatas) - 1) / 2) * larg
        if lst and all(num(l["t_prova"]) for l in lst):
            ax.bar(x, media(lst, "t_prova"), larg, color=CORES[nome], label=nome if k == 0 else None)
        else:
            ax.bar(x, T, larg, color=CORES[nome], alpha=0.18, hatch="//", label=nome if k == 0 else None)
            ax.text(x, T, "x", ha="center", va="bottom", fontweight="bold", color=CORES[nome])
ax.set_xticks(range(len(Ns)))
ax.set_xticklabels([f"N={n}" for n in Ns])
ax.set_ylabel("Tempo ate provar o otimo (s)")
ax.set_title("Quem fecha o gap? (hachurado com x = nao provou em 60 s)", fontweight="bold")
ax.legend()
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{PASTA}/tempo_para_provar.png", dpi=200)
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.5))
melhor = [min(media(res[(n, a)], "makespan") for a in nomes) for n in Ns]
triv = [num([l for l in linhas if int(l["N"]) == n][0]["lb_trivial"]) for n in Ns]
lb_cbc = [media(res[(n, "Exato (CBC)")], "lb_solver") for n in Ns]
ax.plot(Ns, melhor, "o-", color="#2e7d32", linewidth=2, label="Melhor solucao encontrada")
ax.plot(Ns, triv, "s--", color="#555555", linewidth=2, label="Limitante trivial (maquina mais carregada)")
ax.plot(Ns, lb_cbc, "^-", color="#c62828", linewidth=2, label="Limitante inferior do CBC")
ax.set_xlabel("N (numero de jobs)")
ax.set_ylabel("Makespan")
ax.set_title("O limitante do CBC nao acompanha o crescimento do otimo", fontweight="bold")
ax.set_xticks(Ns)
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(f"{PASTA}/limitantes.png", dpi=200)
plt.close(fig)
print("Graficos salvos em", PASTA)
