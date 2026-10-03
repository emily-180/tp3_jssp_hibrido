# TP-III – Hibridização Heurística + Exato para o Job Shop (JSSP)

**Grupo:** Arielce Pereira, Emily Ferreira e Linicker Ostroski · **Disciplina:** Tópicos Especiais I · **Prof.:** Matheus Guedes

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `comum.py` | Gerador de instâncias (parametrizado por N), leitura/escrita, decodificador e caminho crítico |
| `heuristica.py` | ILS adaptado do TP-I (sequência de operações, inserção + perturbação por trocas) |
| `exato.py` | Modelo de Manne do TP-II (CBC), com warm start e fixação de variáveis |
| `hibrido.py` | Híbrido (warm start + Fix-and-Optimize) e as abordagens comparadas |
| `experimentos.py` | Bateria completa; salva `resultados/resultados.csv` e `historicos.json` (retoma se interrompida) |
| `graficos.py` | Gera os 3 gráficos em `resultados/` |
| `observacao_corte.py` | Observação extra da pergunta 4: limitante do CBC com e sem o corte de carga |
| `instancias/` | As 6 instâncias geradas |

## Como executar

```
pip install pulp matplotlib
python experimentos.py --tamanhos 6 8 10 12 15 20 --m 5 --T 60
python graficos.py
```

`--T` é o orçamento de tempo (s) igual para todas as abordagens; `--reps 3` repete as abordagens com aleatoriedade.
A bateria completa leva cerca de 20 minutos com T = 60 s.

## Família de instâncias

Gerador estilo Taillard: m = 5 máquinas, rota sorteada, durações uniformes em [1, 99]. **Semente = 2026 + N.**

| N | m | Semente | Binárias | Arquivo |
| --- | --- | --- | --- | --- |
| 6 | 5 | 2032 | 75 | `instancias/jssp_N6_m5.txt` |
| 8 | 5 | 2034 | 140 | `instancias/jssp_N8_m5.txt` |
| 10 | 5 | 2036 | 225 | `instancias/jssp_N10_m5.txt` |
| 12 | 5 | 2038 | 330 | `instancias/jssp_N12_m5.txt` |
| 15 | 5 | 2041 | 525 | `instancias/jssp_N15_m5.txt` |
| 20 | 5 | 2046 | 950 | `instancias/jssp_N20_m5.txt` |

## Abordagens (mesmo tempo T)

1. **Heurística (ILS)** pura.
2. **Exato (CBC)** puro.
3. **Híbrido (janela)**: ILS (warm start) → Fix-and-Optimize liberando a ordem das operações dentro de uma janela de tempo → CBC com warm start no tempo restante. É o híbrido principal.
4. **Híbrido (máquinas)**: igual, mas liberando a ordem inteira nas máquinas do caminho crítico. É a segunda lógica testada para escolher as variáveis livres.
