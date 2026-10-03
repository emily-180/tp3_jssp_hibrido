import bisect
import random

def gerar_instancia(n, m, semente, pmin=1, pmax=99):
    rng = random.Random(semente)
    rotas = []
    for _ in range(n):
        maqs = list(range(m))
        rng.shuffle(maqs)
        rotas.append([(k, rng.randint(pmin, pmax)) for k in maqs])
    return rotas


def salvar_instancia(rotas, m, caminho, comentario=""):
    with open(caminho, "w") as f:
        if comentario:
            f.write(f"# {comentario}\n")
        f.write(f"{len(rotas)} {m}\n")
        for rota in rotas:
            f.write(" ".join(f"{k} {d}" for k, d in rota) + "\n")


def ler_instancia(caminho):
    with open(caminho) as f:
        linhas = [l.split() for l in f if l.strip() and not l.startswith("#")]
    n, m = int(linhas[0][0]), int(linhas[0][1])
    rotas = []
    for j in range(n):
        v = list(map(int, linhas[1 + j]))
        rotas.append([(v[2 * k], v[2 * k + 1]) for k in range(m)])
    return rotas, m

def decodificar(rotas, m, seq):
    n = len(rotas)
    prox = [0] * n           
    pronto = [0] * n        
    ocup_ini = [[] for _ in range(m)]   
    ocup_fim = [[] for _ in range(m)]   
    inicio = {}
    makespan = 0
    for j in seq:
        k, d = rotas[j][prox[j]]
        prox[j] += 1
        ini_k, fim_k = ocup_ini[k], ocup_fim[k]
        t = pronto[j]
        
        pos = len(ini_k)
        for idx in range(len(ini_k)):
            if t + d <= ini_k[idx]:
                pos = idx
                break
            if fim_k[idx] > t:
                t = fim_k[idx]
        ini_k.insert(pos, t)
        fim_k.insert(pos, t + d)
        inicio[(j, k)] = t
        pronto[j] = t + d
        if t + d > makespan:
            makespan = t + d
    return makespan, inicio


def sequencia_de_agenda(rotas, inicio):
    ops = []
    for j, rota in enumerate(rotas):
        for pos, (k, _) in enumerate(rota):
            ops.append((inicio[(j, k)], pos, j))
    ops.sort()
    return [j for _, _, j in ops]


def caminho_critico(rotas, m, inicio, makespan):
    dur = {(j, k): d for j, rota in enumerate(rotas) for k, d in rota}
    pos_na_rota = {(j, k): p for j, rota in enumerate(rotas) for p, (k, _) in enumerate(rota)}
    fim = {op: inicio[op] + dur[op] for op in inicio}
    atual = max(fim, key=lambda op: fim[op])
    caminho = [atual]
    while inicio[atual] > 0:
        j, k = atual
        t = inicio[atual]
        anterior = None
        p = pos_na_rota[atual]
        if p > 0:  
            kp = rotas[j][p - 1][0]
            if fim[(j, kp)] == t:
                anterior = (j, kp)
        if anterior is None: 
            for (j2, k2), f in fim.items():
                if k2 == k and j2 != j and f == t:
                    anterior = (j2, k2)
                    break
        if anterior is None:
            break
        caminho.append(anterior)
        atual = anterior
    return caminho[::-1]
