import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sample_data import generate_equipment_specs
from condition_monitoring import (
    generate_checklist_diario,
    generate_termografia,
    generate_vibracao,
)


class ReliabilityAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df          = df.copy()
        self.specs       = generate_equipment_specs()
        self.H_ANO       = 8760
        self.checklists  = generate_checklist_diario()
        self.termografia = generate_termografia()
        self.vibracao    = generate_vibracao()

    def calcular_mtbf(self) -> pd.DataFrame:
        rows = []
        for eq in self.df["equipamento"].unique():
            d    = self.df[self.df["equipamento"] == eq]
            n    = len(d)
            tr   = d["tempo_reparo_horas"].sum()
            mtbf = round((self.H_ANO - tr) / n, 1) if n else self.H_ANO
            mttr = round(d["tempo_reparo_horas"].mean(), 2)
            disp = round(mtbf / (mtbf + mttr) * 100, 2)
            s    = self.specs.get(eq, {})
            rows.append({
                "equipamento":          eq,
                "area":                 s.get("area", "—"),
                "criticidade":          s.get("criticidade", "—"),
                "n_falhas":             n,
                "mtbf_horas":           mtbf,
                "mtbf_alvo":            s.get("mtbf_alvo_horas"),
                "mtbf_status":          "✅" if s.get("mtbf_alvo_horas") and mtbf >= s.get("mtbf_alvo_horas") else "❌",
                "mttr_horas":           mttr,
                "mttr_alvo":            s.get("mttr_alvo_horas"),
                "mttr_status":          "✅" if s.get("mttr_alvo_horas") and mttr <= s.get("mttr_alvo_horas") else "❌",
                "disponibilidade_pct":  disp,
                "disponibilidade_alvo": round(s.get("disponibilidade_alvo", 0.95) * 100, 1),
                "disp_status":          "✅" if disp >= s.get("disponibilidade_alvo", 0.95) * 100 else "❌",
            })
        return pd.DataFrame(rows).sort_values("disponibilidade_pct")

    def analise_pareto(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        pf = (self.df.groupby("tipo_falha")
              .agg(ocorrencias=("tipo_falha","count"),
                   custo_total=("custo_reparo","sum"),
                   tempo_total=("tempo_reparo_horas","sum"))
              .sort_values("ocorrencias", ascending=False).reset_index())
        pf["pct"]      = (pf["ocorrencias"]/pf["ocorrencias"].sum()*100).round(2)
        pf["pct_acum"] = pf["pct"].cumsum().round(2)
        pf["classe"]   = pf["pct_acum"].apply(
            lambda x: "A" if x<=80 else "B" if x<=95 else "C")
        pe = (self.df.groupby("equipamento")
              .agg(ocorrencias=("equipamento","count"),
                   custo_total=("custo_reparo","sum"),
                   tempo_parado=("tempo_reparo_horas","sum"),
                   producao_perdida=("producao_perdida_caixas","sum"))
              .sort_values("custo_total", ascending=False).reset_index())
        pe["pct_custo"] = (pe["custo_total"]/pe["custo_total"].sum()*100).round(2)
        pe["pct_acum"]  = pe["pct_custo"].cumsum().round(2)
        return pf, pe

    def analise_fmea(self) -> pd.DataFrame:
        sev_map = {"Crítica":10,"Alta":7,"Média":4,"Baixa":2}
        rows = []
        for eq in self.df["equipamento"].unique():
            de = self.df[self.df["equipamento"]==eq]
            cr = de["criticidade"].iloc[0]
            for f in de["tipo_falha"].unique():
                df_f = de[de["tipo_falha"]==f]
                occ  = len(df_f)
                osc  = min(10, max(1, occ//3))
                pp   = (df_f["tipo_manutencao"]=="Preditiva").mean()
                pv   = (df_f["tipo_manutencao"]=="Preventiva").mean()
                dsc  = 3 if pp>0.3 else 5 if pv>0.4 else 8
                sv   = sev_map.get(cr, 5)
                rpn  = sv*osc*dsc
                rows.append({
                    "equipamento":   eq, "modo_falha": f,
                    "criticidade":   cr, "severidade": sv,
                    "ocorrencia":    osc, "deteccao": dsc, "rpn": rpn,
                    "n_ocorrencias": occ,
                    "custo_medio":   round(df_f["custo_reparo"].mean(), 2),
                    "ttf_medio":     round(df_f["tempo_reparo_horas"].mean(), 2),
                    "prioridade":    ("CRÍTICA" if rpn>=400 else "ALTA" if rpn>=200
                                     else "MÉDIA" if rpn>=100 else "BAIXA"),
                })
        return pd.DataFrame(rows).sort_values("rpn", ascending=False).reset_index(drop=True)

    def analise_checklists(self) -> pd.DataFrame:
        df = self.checklists.copy()
        df["is_nok"] = df["status"].isin(["ALERTA","NOK"])
        res = (df.groupby(["equipamento","item_checklist"])
               .agg(total=("status","count"), qtd_nok=("is_nok","sum"))
               .reset_index())
        res["taxa_pct"]   = (res["qtd_nok"]/res["total"]*100).round(1)
        res["prioridade"] = res["taxa_pct"].apply(
            lambda x: "ALTA" if x>=20 else "MÉDIA" if x>=10 else "BAIXA")
        return res.sort_values("taxa_pct", ascending=False)

    def analise_termografia(self) -> pd.DataFrame:
        df = self.termografia.copy()
        df["is_crit"] = df["severidade"].isin(["Crítico","Emergencial"])
        res = (df.groupby(["equipamento","ponto_medicao"])
               .agg(n=("data","count"),
                    temp_max=("temperatura_medida_c","max"),
                    temp_media=("temperatura_medida_c","mean"),
                    n_crit=("is_crit","sum"),
                    limite=("limite_critico_c","first"))
               .reset_index())
        res["taxa_crit_pct"] = (res["n_crit"]/res["n"]*100).round(1)
        res["prioridade"]    = res["taxa_crit_pct"].apply(
            lambda x: "ALTA" if x>=30 else "MÉDIA" if x>=10 else "BAIXA")
        return res.sort_values("taxa_crit_pct", ascending=False)

    def analise_vibracao(self) -> pd.DataFrame:
        df = self.vibracao.copy()
        df["is_ruim"] = df["classe_iso"].isin(
            ["C — Insatisfatório","D — Inaceitável"])
        res = (df.groupby(["equipamento","ponto_medicao"])
               .agg(n=("data","count"),
                    vib_max=("vib_mm_s_rms","max"),
                    vib_media=("vib_mm_s_rms","mean"),
                    n_ruim=("is_ruim","sum"))
               .reset_index())
        res["taxa_ruim_pct"] = (res["n_ruim"]/res["n"]*100).round(1)
        res["prioridade"]    = res["taxa_ruim_pct"].apply(
            lambda x: "ALTA" if x>=30 else "MÉDIA" if x>=10 else "BAIXA")
        return res.sort_values("taxa_ruim_pct", ascending=False)

    def calcular_oee(self) -> pd.DataFrame:
        kpis = self.calcular_mtbf()
        np.random.seed(7)
        rows = []
        for _, r in kpis.iterrows():
            disp = r["disponibilidade_pct"]/100
            perf = np.random.uniform(0.78, 0.96)
            qual = np.random.uniform(0.95, 0.999)
            oee  = disp*perf*qual
            rows.append({
                "equipamento":   r["equipamento"],
                "disponibilidade": round(disp*100, 2),
                "desempenho":    round(perf*100, 2),
                "qualidade":     round(qual*100, 2),
                "oee_pct":       round(oee*100,  2),
                "status": ("🏆 Excelente" if oee>=0.85 else "✅ Aceitável"
                           if oee>=0.65 else "⚠️ Atenção" if oee>=0.50 else "🚨 Crítico"),
            })
        return pd.DataFrame(rows).sort_values("oee_pct", ascending=False)

    def gerar_recomendacoes(self) -> List[Dict]:
        recs  = []
        kpis  = self.calcular_mtbf()
        fmea  = self.analise_fmea()
        termo = self.analise_termografia()
        vib   = self.analise_vibracao()
        _, pe = self.analise_pareto()
        for _, r in kpis[kpis["disp_status"]=="❌"].iterrows():
            recs.append({"prioridade":"🚨 URGENTE","equipamento":r["equipamento"],
                "fonte":"KPI","problema":f"Disponibilidade {r['disponibilidade_pct']}% < meta {r['disponibilidade_alvo']}%",
                "acao":"Revisar plano preventivo. Análise de causa raiz."})
        for _, r in fmea[fmea["prioridade"].isin(["CRÍTICA","ALTA"])].head(6).iterrows():
            recs.append({"prioridade":"🔴 ALTA","equipamento":r["equipamento"],
                "fonte":"FMEA","problema":f"Modo '{r['modo_falha']}' — RPN {r['rpn']}",
                "acao":f"Preditiva. Custo médio: R$ {r['custo_medio']:,.2f}"})
        for _, r in termo[termo["prioridade"]=="ALTA"].head(4).iterrows():
            recs.append({"prioridade":"🌡️ TERMOGRAFIA","equipamento":r["equipamento"],
                "fonte":"Termografia","problema":f"'{r['ponto_medicao']}' T.máx {r['temp_max']:.1f}°C",
                "acao":"Reaperto / limpeza / ventilação."})
        for _, r in vib[vib["prioridade"]=="ALTA"].head(4).iterrows():
            recs.append({"prioridade":"📳 VIBRAÇÃO","equipamento":r["equipamento"],
                "fonte":"Vibração","problema":f"'{r['ponto_medicao']}' {r['vib_max']:.2f} mm/s",
                "acao":"Alinhamento/balanceamento. Classe D: parar."})
        for _, r in pe.head(3).iterrows():
            recs.append({"prioridade":"💰 CUSTO","equipamento":r["equipamento"],
                "fonte":"Pareto","problema":f"R$ {r['custo_total']:,.2f} ({r['pct_custo']:.1f}%)",
                "acao":"Substituição componentes. Preditiva."})
        return recs

    def analise_turnos(self) -> pd.DataFrame:
        return (self.df.groupby("turno")
                .agg(ocorrencias=("turno","count"),
                     custo_total=("custo_reparo","sum"),
                     ttf_medio=("tempo_reparo_horas","mean"))
                .round(2).reset_index())

    def analise_tecnicos(self) -> pd.DataFrame:
        return (self.df.groupby("tecnico_responsavel")
                .agg(atendimentos=("tecnico_responsavel","count"),
                     ttf_medio=("tempo_reparo_horas","mean"),
                     custo_total=("custo_reparo","sum"),
                     taxa_resolucao=("resolvido","mean"))
                .round(3).reset_index().sort_values("ttf_medio"))
