import random
import time

from comum import decodificar

def construir_mwkr(rotas, rng):
    n = len(rotas)
    restante = [sum(d for _, d in r) for r in rotas]
    falta = [len(r) for r in rotas]
    prox = [0] * n
    seq = []
    while len(seq) < sum(len(r) for r in rotas):
        candidatos = [j for j in range(n) if falta[j] > 0]
        maior = max(restante[j] for j in candidatos)
        j = rng.choice([c for c in candidatos if restante[c] == maior])
        seq.append(j)
        restante[j] -= rotas[j][prox[j]][1]
        prox[j] += 1
        falta[j] -= 1
    return seq


def busca_local(rotas, m, seq, ms, rng, prazo, max_falhas=None):
    L = len(seq)
    max_falhas = max_falhas or 2 * L
    falhas = 0
    while falhas < max_falhas and time.time() < prazo:
        a, b = rng.randrange(L), rng.randrange(L)
        if a == b or seq[a] == seq[b]:
            falhas += 1
            continue
        nova = seq[:]
        x = nova.pop(a)
        nova.insert(b, x)
        ms_nova, _ = decodificar(rotas, m, nova)
        if ms_nova < ms:
            seq, ms, falhas = nova, ms_nova, 0
        else:
            if ms_nova == ms:
                seq = nova  
            falhas += 1
    return seq, ms

def perturbar(seq, trocas, rng):
    nova = seq[:]
    L = len(nova)
    for _ in range(trocas):
        a, b = rng.randrange(L), rng.randrange(L)
        nova[a], nova[b] = nova[b], nova[a]
    return nova

def ils(rotas, m, tempo, semente=0, seq_inicial=None, trocas=2, parada_estagnacao=None):
    rng = random.Random(semente)
    t0 = time.time()
    prazo = t0 + tempo
    seq = seq_inicial[:] if seq_inicial else construir_mwkr(rotas, rng)
    ms, _ = decodificar(rotas, m, seq)
    historico = [(time.time() - t0, ms)]
    seq, ms = busca_local(rotas, m, seq, ms, rng, prazo)
    melhor_seq, melhor_ms = seq, ms
    historico.append((time.time() - t0, ms))
    atual_seq, atual_ms = seq, ms
    iteracoes = 0
    ultima_melhora = time.time()
    while time.time() < prazo:
        if parada_estagnacao and time.time() - ultima_melhora > parada_estagnacao:
            break
        iteracoes += 1
        nova = perturbar(atual_seq, trocas, rng)
        ms_nova, _ = decodificar(rotas, m, nova)
        nova, ms_nova = busca_local(rotas, m, nova, ms_nova, rng, prazo)
        if ms_nova <= atual_ms:  # criterio de aceitacao: nao piorar
            atual_seq, atual_ms = nova, ms_nova
        if ms_nova < melhor_ms:
            melhor_seq, melhor_ms = nova, ms_nova
            ultima_melhora = time.time()
            historico.append((time.time() - t0, melhor_ms))
    _, inicio = decodificar(rotas, m, melhor_seq)
    historico.append((time.time() - t0, melhor_ms))
    return {"makespan": melhor_ms, "seq": melhor_seq, "inicio": inicio,
            "historico": historico, "iteracoes": iteracoes}
