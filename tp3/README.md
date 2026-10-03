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

## Abordagens (mesmo tempo T)

1. **Heurística (ILS)** pura.
2. **Exato (CBC)** puro.
3. **Híbrido (janela)**: ILS (warm start) → Fix-and-Optimize liberando a ordem das operações dentro de uma janela de tempo → CBC com warm start no tempo restante. É o híbrido principal.
4. **Híbrido (máquinas)**: igual, mas liberando a ordem inteira nas máquinas do caminho crítico. É a segunda lógica testada para escolher as variáveis livres.
