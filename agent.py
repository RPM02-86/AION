import os
import json
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

try:
    from openai import OpenAI
    OPENAI_OK = True
except ImportError:
    OPENAI_OK = False

from analyzer import ReliabilityAnalyzer
from sample_data import generate_equipment_specs

AION_SYSTEM = """Você é AION — Artificial Intelligence for Operations & iNtegrity.
Engenheiro Sênior de Confiabilidade Industrial com 20 anos de experiência
em fábricas de sopro e envase de água mineral.
Responda SEMPRE em português. Seja técnico e direto.
Use os dados reais. Estruture: Diagnóstico → Causa → Ação → Prazo.
Sinalize CRÍTICO quando houver risco imediato."""


class AIONAgent:
    VERSION = "2.0.0"

    def __init__(self, df: pd.DataFrame, api_key: str = ""):
        self.df      = df.copy()
        self.az      = ReliabilityAnalyzer(df)
        self.specs   = generate_equipment_specs()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.history: List[Dict] = []
        self._ctx    = self._build_context()

    def _build_context(self) -> Dict:
        kpis     = self.az.calcular_mtbf()
        pf, pe   = self.az.analise_pareto()
        fmea     = self.az.analise_fmea()
        oee      = self.az.calcular_oee()
        turnos   = self.az.analise_turnos()
        tecnicos = self.az.analise_tecnicos()
        chk      = self.az.analise_checklists()
        termo    = self.az.analise_termografia()
        vib      = self.az.analise_vibracao()
        recs     = self.az.gerar_recomendacoes()
        return {
            "snapshot": {
                "total_ocorrencias":   len(self.df),
                "periodo":             f"{self.df['data_ocorrencia'].min().date()} → {self.df['data_ocorrencia'].max().date()}",
                "custo_total_rs":      round(self.df["custo_reparo"].sum(), 2),
                "horas_paradas_total": round(self.df["tempo_reparo_horas"].sum(), 2),
                "producao_perdida_cx": int(self.df["producao_perdida_caixas"].sum()),
                "pct_corretiva":       round((self.df["tipo_manutencao"]=="Corretiva").mean()*100, 1),
                "pct_preventiva":      round((self.df["tipo_manutencao"]=="Preventiva").mean()*100, 1),
                "pct_preditiva":       round((self.df["tipo_manutencao"]=="Preditiva").mean()*100, 1),
            },
            "kpis":              kpis.to_dict("records"),
            "pareto_falhas":     pf.head(10).to_dict("records"),
            "pareto_equip":      pe.head(10).to_dict("records"),
            "fmea_top15":        fmea.head(15).to_dict("records"),
            "oee":               oee.to_dict("records"),
            "turnos":            turnos.to_dict("records"),
            "tecnicos":          tecnicos.to_dict("records"),
            "checklists_top15":  chk.head(15).to_dict("records"),
            "termografia_top15": termo.head(15).to_dict("records"),
            "vibracao_top15":    vib.head(15).to_dict("records"),
            "recomendacoes":     recs,
        }

    def _ctx_text(self) -> str:
        return "DADOS DA PLANTA:\n" + json.dumps(
            self._ctx, ensure_ascii=False, default=str)[:7000]

    def chat(self, msg: str) -> Tuple[str, str]:
        self.history.append({"role": "user", "content": msg})
        if self.api_key and OPENAI_OK:
            resp, modo = self._openai(msg), "GPT-4o"
        else:
            resp, modo = self._local(msg), "Local"
        self.history.append({"role": "assistant", "content": resp})
        return resp, modo

    def _openai(self, msg: str) -> str:
        try:
            client   = OpenAI(api_key=self.api_key)
            system   = AION_SYSTEM + "\n\n" + self._ctx_text()
            messages = [{"role":"system","content":system}] + self.history[-16:]
            r = client.chat.completions.create(
                model="gpt-4o", messages=messages,
                temperature=0.2, max_tokens=2500)
            return r.choices[0].message.content
        except Exception as e:
            return f"⚠️ Erro OpenAI: {e}\n\n" + self._local(msg)

    def _local(self, msg: str) -> str:
        m = msg.lower()
        def hit(*kw): return any(k in m for k in kw)
        if hit("quem é você","aion","apresente"):       return self._id()
        if hit("resumo","visão geral","situação"):       return self._resumo()
        if hit("compressor af","40 bar"):               return self._equip("Compressor_AF_HP_40bar")
        if hit("gardner","7 bar"):                      return self._equip("Compressor_GardnerDenver_LP")
        if hit("sopradora","vblow","multipet"):         return self._equip("Sopradora_Multipet_VBlow_18K")
        if hit("mesal","21k"):                          return self._equip("Envasadora_Mesal_21K")
        if hit("zegla","15k"):                          return self._equip("Envasadora_Zegla_15K")
        if hit("chiller","qualiterme"):                 return self._equip("Chiller_Qualiterme")
        if hit("rotuladora","simplecut"):               return self._equip("Rotuladora_PELatina_Simplecut")
        if hit("taymak","empacotadora"):                return self._equip("Empacotadora_Taymak")
        if hit("jetflow","tampadora"):                  return self._equip("Jetflow_Tampadora")
        if hit("bomba","bombas"):                       return self._equip("Bombas_Processo")
        if hit("lavadora","túnel","assepsia"):          return self._equip("Lavadora_Tunel_Assepsia")
        if hit("pareto","falhas"):                      return self._pareto()
        if hit("fmea","rpn","risco"):                   return self._fmea()
        if hit("mtbf","mttr","disponibilidade","kpi"):  return self._kpis()
        if hit("oee","eficiência"):                     return self._oee()
        if hit("vibração","vibracao"):                  return self._vibracao()
        if hit("termografia","hotspot"):                return self._termografia()
        if hit("checklist"):                            return self._checklist()
        if hit("recomend","plano","melhoria"):          return self._recomendacoes()
        if hit("urgente","crítico","emergência"):       return self._urgentes()
        return (
            f'Não encontrei análise para: *"{msg}"*\n\n'
            "Pergunte sobre: equipamento, MTBF, OEE, Pareto, FMEA, "
            "vibração, termografia, checklist ou situação geral."
        )

    def _id(self):
        s = self._ctx["snapshot"]
        return (
            f"**AION** — Artificial Intelligence for Operations & iNtegrity | v{self.VERSION}\n\n"
            f"Agente de Confiabilidade desta fábrica de água mineral.\n\n"
            f"Monitorando **{s['total_ocorrencias']:,} ocorrências** | {s['periodo']}\n\n"
            "Analiso: MTBF, MTTR, OEE, Pareto, FMEA, Checklists, Termografia e Vibração.\n\n"
            "Como posso ajudar?"
        )

    def _resumo(self):
        s    = self._ctx["snapshot"]
        kpis = pd.DataFrame(self._ctx["kpis"])
        recs = self._ctx["recomendacoes"]
        fmea = pd.DataFrame(self._ctx["fmea_top15"])
        pior = kpis.sort_values("disponibilidade_pct").iloc[0]
        n_urg = sum(1 for r in recs if "URGENTE" in r["prioridade"])
        return f"""## 📊 Diagnóstico Geral — AION

| Indicador | Valor |
|---|---|
| Ocorrências | **{s['total_ocorrencias']:,}** |
| Custo total | **R$ {s['custo_total_rs']:,.2f}** |
| Horas paradas | **{s['horas_paradas_total']:.0f} h** |
| Produção perdida | **{s['producao_perdida_cx']:,} caixas** |
| % Corretiva | **{s['pct_corretiva']}%** ⚠️ |
| % Preventiva | **{s['pct_preventiva']}%** |
| % Preditiva | **{s['pct_preditiva']}%** |

### 🚨 Alertas
- **{n_urg}** equipamento(s) abaixo da meta de disponibilidade
- Pior disponibilidade: **{pior['equipamento'].replace('_',' ')}** → {pior['disponibilidade_pct']}%
- RPN máximo: **{fmea['rpn'].max()}**

### Mix de Manutenção
Com **{s['pct_corretiva']}%** corretiva a operação está em modo reativo.
Meta ideal: Corretiva ≤25% | Preventiva ≥45% | Preditiva ≥20%"""

    def _equip(self, eid: str):
        nome  = eid.replace("_"," ")
        spec  = self.specs.get(eid, {})
        kpis  = pd.DataFrame(self._ctx["kpis"])
        fmea  = pd.DataFrame(self._ctx["fmea_top15"])
        termo = pd.DataFrame(self._ctx["termografia_top15"])
        vib   = pd.DataFrame(self._ctx["vibracao_top15"])
        chk   = pd.DataFrame(self._ctx["checklists_top15"])
        krow  = kpis[kpis["equipamento"]==eid]
        frow  = fmea[fmea["equipamento"]==eid]
        trow  = termo[termo["equipamento"]==eid]
        vrow  = vib[vib["equipamento"]==eid]
        crow  = chk[chk["equipamento"]==eid]
        kpi_txt = "Sem dados."
        if len(krow):
            k = krow.iloc[0]
            kpi_txt = (
                f"| MTBF | {k['mtbf_horas']}h | {k['mtbf_alvo']}h | {k['mtbf_status']} |\n"
                f"| MTTR | {k['mttr_horas']}h | {k['mttr_alvo']}h | {k['mttr_status']} |\n"
                f"| Disponibilidade | {k['disponibilidade_pct']}% | {k['disponibilidade_alvo']}% | {k['disp_status']} |"
            )
        alertas = []
        if len(krow) and krow.iloc[0]["disp_status"]=="❌":
            alertas.append("⚠️ Disponibilidade abaixo da meta")
        if len(vrow) and vrow["vib_max"].max()>=7.1:
            alertas.append("🚨 Vibração Classe D — parada recomendada")
        if len(trow) and trow["taxa_crit_pct"].max()>=30:
            alertas.append("🌡️ Ponto termográfico crítico recorrente")
        return f"""## 🔧 AION — {nome}
**Área:** {spec.get('area','—')} | **Criticidade:** {spec.get('criticidade','—')} | **Cap.:** {spec.get('capacidade','—')}

### KPIs
| Indicador | Real | Meta | Status |
|---|---|---|---|
{kpi_txt}

### FMEA
{chr(10).join([f"- **{r['modo_falha']}** → RPN {r['rpn']} ({r['prioridade']})" for _,r in frow.head(4).iterrows()]) or "Sem dados."}

### 🌡️ Termografia
{chr(10).join([f"- **{r['ponto_medicao']}**: T.máx {r['temp_max']:.1f}°C | {r['taxa_crit_pct']}% críticas" for _,r in trow.head(3).iterrows()]) or "Sem dados."}

### 📳 Vibração
{chr(10).join([f"- **{r['ponto_medicao']}**: {r['vib_max']:.2f} mm/s | {r['taxa_ruim_pct']}% C/D" for _,r in vrow.head(3).iterrows()]) or "Sem dados."}

### ✅ Checklist
{chr(10).join([f"- **{r['item_checklist']}**: {r['taxa_pct']}% ALERTA/NOK" for _,r in crow.head(3).iterrows()]) or "Sem anomalias."}

### 🧠 Diagnóstico
{chr(10).join(alertas) if alertas else "✅ Sem alertas críticos imediatos."}"""

    def _pareto(self):
        pf = pd.DataFrame(self._ctx["pareto_falhas"])
        pe = pd.DataFrame(self._ctx["pareto_equip"])
        fa = pf[pf["classe"]=="A"]
        lf = "\n".join([f"| {r['tipo_falha']} | {r['ocorrencias']} | R$ {r['custo_total']:,.0f} |" for _,r in fa.iterrows()])
        le = "\n".join([f"| {r['equipamento'].replace('_',' ')} | R$ {r['custo_total']:,.0f} | {r['pct_custo']:.1f}% |" for _,r in pe.head(5).iterrows()])
        return f"""## 📊 Pareto — AION
### Classe A (80% dos problemas)
| Modo de Falha | Ocorrências | Custo |
|---|---|---|
{lf}
### Top 5 por Custo
| Equipamento | Custo | % Total |
|---|---|---|
{le}"""

    def _fmea(self):
        fmea = pd.DataFrame(self._ctx["fmea_top15"])
        crit = fmea[fmea["prioridade"].isin(["CRÍTICA","ALTA"])]
        linhas = "\n".join([
            f"| {r['equipamento'].replace('_',' ')} | {r['modo_falha']} | {r['rpn']} | {r['prioridade']} |"
            for _,r in crit.head(10).iterrows()])
        return f"""## 🎯 FMEA — AION
| Equipamento | Modo de Falha | RPN | Prioridade |
|---|---|---|---|
{linhas}"""

    def _kpis(self):
        kpis = pd.DataFrame(self._ctx["kpis"])
        linhas = "\n".join([
            f"| {r['equipamento'].replace('_',' ')} | {r['mtbf_horas']}h {r['mtbf_status']} | {r['mttr_horas']}h {r['mttr_status']} | {r['disponibilidade_pct']}% {r['disp_status']} |"
            for _,r in kpis.iterrows()])
        return f"""## 📈 KPIs — AION
| Equipamento | MTBF | MTTR | Disponibilidade |
|---|---|---|---|
{linhas}"""

    def _oee(self):
        oee = pd.DataFrame(self._ctx["oee"])
        linhas = "\n".join([
            f"| {r['equipamento'].replace('_',' ')} | {r['disponibilidade']}% | {r['desempenho']}% | {r['oee_pct']}% | {r['status']} |"
            for _,r in oee.iterrows()])
        return f"""## ⚙️ OEE — AION
| Equipamento | Disp. | Desempenho | OEE | Status |
|---|---|---|---|---|
{linhas}"""

    def _vibracao(self):
        vib  = pd.DataFrame(self._ctx["vibracao_top15"])
        crit = vib[vib["prioridade"]=="ALTA"]
        d    = vib[vib["vib_max"]>=7.1]
        alerta = ""
        if len(d):
            alerta = "\n🚨 **CLASSE D — Parada imediata:**\n" + "\n".join([
                f"- {r['equipamento'].replace('_',' ')} — {r['ponto_medicao']}: {r['vib_max']:.2f} mm/s"
                for _,r in d.iterrows()])
        linhas = "\n".join([
            f"| {r['equipamento'].replace('_',' ')} | {r['ponto_medicao']} | {r['vib_max']:.2f} | {r['taxa_ruim_pct']}% |"
            for _,r in crit.head(8).iterrows()])
        return f"""## 📳 Vibração — AION
A<2.8 Bom | B<4.5 Aceitável | C<7.1 Insatisfatório | D≥7.1 Inaceitável
{alerta}

| Equipamento | Ponto | Máx mm/s | Taxa C/D |
|---|---|---|---|
{linhas}"""

    def _termografia(self):
        termo = pd.DataFrame(self._ctx["termografia_top15"])
        crit  = termo[termo["prioridade"]=="ALTA"]
        linhas = "\n".join([
            f"| {r['equipamento'].replace('_',' ')} | {r['ponto_medicao']} | {r['temp_max']:.1f}°C | {r['taxa_crit_pct']}% |"
            for _,r in crit.head(8).iterrows()])
        return f"""## 🌡️ Termografia — AION
| Equipamento | Ponto | T.Máxima | Taxa Crítica |
|---|---|---|---|
{linhas}"""

    def _checklist(self):
        chk  = pd.DataFrame(self._ctx["checklists_top15"])
        crit = chk[chk["prioridade"]=="ALTA"]
        linhas = "\n".join([
            f"| {r['equipamento'].replace('_',' ')} | {r['item_checklist']} | {r['taxa_pct']}% |"
            for _,r in crit.head(8).iterrows()])
        return f"""## ✅ Checklists — AION
| Equipamento | Item | Taxa ALERTA/NOK |
|---|---|---|
{linhas}"""

    def _recomendacoes(self):
        recs = self._ctx["recomendacoes"]
        urg  = [r for r in recs if "URGENTE"    in r["prioridade"]]
        alt  = [r for r in recs if "ALTA"       in r["prioridade"]]
        def fmt(lst):
            return "\n".join([
                f"**{r['equipamento'].replace('_',' ')}** — {r['problema']}\n→ {r['acao']}"
                for r in lst[:4]]) or "_Nenhum._"
        return f"""## 💡 Recomendações — AION
### 🚨 Urgentes
{fmt(urg)}
### 🔴 Alta Prioridade
{fmt(alt)}"""

    def _urgentes(self):
        recs = self._ctx["recomendacoes"]
        urg  = [r for r in recs if "URGENTE" in r["prioridade"]]
        vib  = pd.DataFrame(self._ctx["vibracao_top15"])
        d    = vib[vib["vib_max"]>=7.1]
        alerta_d = ""
        if len(d):
            alerta_d = "\n🚨 **VIBRAÇÃO CLASSE D:**\n" + "\n".join([
                f"- {r['equipamento'].replace('_',' ')} — {r['ponto_medicao']}"
                for _,r in d.iterrows()])
        lista = "\n".join([
            f"🚨 **{r['equipamento'].replace('_',' ')}** — {r['problema']}\n→ {r['acao']}"
            for r in urg]) or "Nenhum item urgente no momento."
        return f"""## 🚨 Urgentes — AION
{alerta_d}

{lista}"""
