import itertools
import os
import re
import tempfile
import time

import pulp

class ModeloJSSP:
    def __init__(self, rotas, m, corte_carga=False):
        self.rotas, self.m = rotas, m
        n = len(rotas)
        J, M = range(n), range(m)
        self.p = {(j, k): d for j in J for (k, d) in rotas[j]}
        V = sum(self.p.values())  # big-M
        mod = pulp.LpProblem("JSSP", pulp.LpMinimize)
        self.s = pulp.LpVariable.dicts("s", self.p.keys(), lowBound=0)
        self.cmax = pulp.LpVariable("Cmax", lowBound=0)
        self.y = {(i, j, k): pulp.LpVariable(f"y_{i}_{j}_{k}", cat="Binary")
                  for k in M for i, j in itertools.combinations(J, 2)}
        mod += self.cmax
        s, p = self.s, self.p
        for j in J:  
            for a in range(m - 1):
                (k1, d1), (k2, _) = rotas[j][a], rotas[j][a + 1]
                mod += s[j, k2] >= s[j, k1] + d1
        for (i, j, k), yv in self.y.items(): 
            mod += s[i, k] >= s[j, k] + p[j, k] - V * yv
            mod += s[j, k] >= s[i, k] + p[i, k] - V * (1 - yv)
        for j in J:  
            k, d = rotas[j][-1]
            mod += self.cmax >= s[j, k] + d
        if corte_carga:
           
            for k in M:
                mod += self.cmax >= sum(p[j, k] for j in J)
        self.modelo = mod

    @staticmethod
    def y_de_agenda(inicio, chaves):
        return {(i, j, k): 1 if inicio[(i, k)] < inicio[(j, k)] else 0
                for (i, j, k) in chaves}

    def definir_inicial(self, inicio, makespan):
        for op, var in self.s.items():
            var.setInitialValue(inicio[op])
        for key, val in self.y_de_agenda(inicio, self.y.keys()).items():
            self.y[key].setInitialValue(val)
        self.cmax.setInitialValue(makespan)

    def fixar(self, livres=None, inicio=None):
        if livres is None:
            for var in self.y.values():
                var.lowBound, var.upBound = 0, 1
            return
        valores = self.y_de_agenda(inicio, self.y.keys())
        for key, var in self.y.items():
            if key in livres:
                var.lowBound, var.upBound = 0, 1
            else:
                var.lowBound = var.upBound = valores[key]

    def resolver(self, tempo, warm=False):
        fd, log = tempfile.mkstemp(suffix=".log")
        os.close(fd)
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=max(1, tempo),
                                   warmStart=warm, logPath=log)
        t0 = time.time()
        self.modelo.solve(solver)
        gasto = time.time() - t0
        texto = open(log).read()
        os.remove(log)
        ub = self.cmax.value()
        ok_solucao = ub is not None and self.modelo.sol_status in (1, 2)
        provado = "Optimal solution found" in texto
        lb = None
        mlb = re.search(r"Lower bound:\s*([-\d.eE+]+)", texto)
        if provado and ok_solucao:
            lb = ub
        elif mlb:
            lb = float(mlb.group(1))
        inicio = {op: round(v.value()) for op, v in self.s.items()} if ok_solucao else None
        return {"status": "otimo" if provado else ("viavel" if ok_solucao else "sem solucao"),
                "ub": round(ub) if ok_solucao else None, "lb": lb,
                "inicio": inicio, "tempo": gasto}
