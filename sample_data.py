import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_equipment_specs():
    return {
        "Sopradora_Multipet_VBlow_18K": {
            "mtbf_alvo_horas": 650, "mttr_alvo_horas": 1.8,
            "disponibilidade_alvo": 0.94, "area": "Sopro",
            "criticidade": "Crítica", "capacidade": "18.000 un/h (500ml)",
            "marca": "Multipet", "modelo": "VBlow",
        },
        "Envasadora_Mesal_21K": {
            "mtbf_alvo_horas": 720, "mttr_alvo_horas": 1.5,
            "disponibilidade_alvo": 0.95, "area": "Envase",
            "criticidade": "Crítica", "capacidade": "21.000 un/h",
            "marca": "Mesal", "modelo": "Rotativa",
        },
        "Envasadora_Zegla_15K": {
            "mtbf_alvo_horas": 680, "mttr_alvo_horas": 2.0,
            "disponibilidade_alvo": 0.93, "area": "Envase",
            "criticidade": "Alta", "capacidade": "15.000 un/h",
            "marca": "Zegla", "modelo": "Volumétrica",
        },
        "Jetflow_Tampadora": {
            "mtbf_alvo_horas": 850, "mttr_alvo_horas": 1.2,
            "disponibilidade_alvo": 0.96, "area": "Envase",
            "criticidade": "Alta", "capacidade": "21.000 un/h",
            "marca": "Jetflow", "modelo": "Rotativo",
        },
        "Compressor_AF_HP_40bar": {
            "mtbf_alvo_horas": 8000, "mttr_alvo_horas": 8.0,
            "disponibilidade_alvo": 0.97, "area": "Utilidades",
            "criticidade": "Crítica", "capacidade": "40 bar",
            "marca": "AF", "modelo": "Alta Pressão",
        },
        "Compressor_GardnerDenver_LP": {
            "mtbf_alvo_horas": 9500, "mttr_alvo_horas": 6.0,
            "disponibilidade_alvo": 0.98, "area": "Utilidades",
            "criticidade": "Crítica", "capacidade": "7 bar",
            "marca": "Gardner Denver", "modelo": "Parafuso Seco",
        },
        "Chiller_Qualiterme": {
            "mtbf_alvo_horas": 8600, "mttr_alvo_horas": 4.0,
            "disponibilidade_alvo": 0.98, "area": "Utilidades",
            "criticidade": "Crítica", "capacidade": "Ciclo Fechado",
            "marca": "Qualiterme", "modelo": "Chiller Industrial",
        },
        "Rotuladora_PELatina_Simplecut": {
            "mtbf_alvo_horas": 450, "mttr_alvo_horas": 1.0,
            "disponibilidade_alvo": 0.92, "area": "Rotulagem",
            "criticidade": "Média", "capacidade": "21.000 un/h",
            "marca": "P.E. Latina", "modelo": "Simplecut",
        },
        "Empacotadora_Taymak": {
            "mtbf_alvo_horas": 600, "mttr_alvo_horas": 1.5,
            "disponibilidade_alvo": 0.93, "area": "Embalagem",
            "criticidade": "Alta", "capacidade": "—",
            "marca": "Taymak", "modelo": "Automática",
        },
        "Strechadora": {
            "mtbf_alvo_horas": 1200, "mttr_alvo_horas": 0.8,
            "disponibilidade_alvo": 0.97, "area": "Embalagem",
            "criticidade": "Baixa", "capacidade": "—",
            "marca": "—", "modelo": "Automática",
        },
        "Esteiras_Transportadoras": {
            "mtbf_alvo_horas": 2000, "mttr_alvo_horas": 0.5,
            "disponibilidade_alvo": 0.99, "area": "Transporte",
            "criticidade": "Média", "capacidade": "Linha completa",
            "marca": "—", "modelo": "—",
        },
        "Lavadora_Tunel_Assepsia": {
            "mtbf_alvo_horas": 1500, "mttr_alvo_horas": 2.0,
            "disponibilidade_alvo": 0.96, "area": "Higienização",
            "criticidade": "Alta", "capacidade": "Linha completa",
            "marca": "—", "modelo": "Túnel",
        },
        "Lacradora": {
            "mtbf_alvo_horas": 1000, "mttr_alvo_horas": 1.0,
            "disponibilidade_alvo": 0.97, "area": "Embalagem",
            "criticidade": "Média", "capacidade": "—",
            "marca": "—", "modelo": "Automática",
        },
        "Placas_Solares_Inversores": {
            "mtbf_alvo_horas": 43800, "mttr_alvo_horas": 4.0,
            "disponibilidade_alvo": 0.995, "area": "Energia",
            "criticidade": "Média", "capacidade": "—",
            "marca": "—", "modelo": "—",
        },
        "Bombas_Processo": {
            "mtbf_alvo_horas": 5000, "mttr_alvo_horas": 2.0,
            "disponibilidade_alvo": 0.98, "area": "Utilidades",
            "criticidade": "Alta", "capacidade": "—",
            "marca": "—", "modelo": "—",
        },
    }


def generate_maintenance_data():
    np.random.seed(42)
    specs = generate_equipment_specs()
    tipos_falha = {
        "Sopradora_Multipet_VBlow_18K": [
            "Desalinhamento molde PET",
            "Falha resistor aquecimento pré-forma",
            "Vazamento câmara de sopro",
            "Falha sensor posição carro móvel",
            "Desgaste guias lineares",
        ],
        "Envasadora_Mesal_21K": [
            "Regulagem válvula de enchimento",
            "Contaminação cabeça dosadora",
            "Falha sensor nível garrafa",
            "Desalinhamento estrela transfer",
            "Vazamento bico dosador",
        ],
        "Envasadora_Zegla_15K": [
            "Erro dosagem volumétrica",
            "Falha cilindro pneumático bico",
            "Desgaste gaxeta êmbolo",
            "Vazamento manifold",
        ],
        "Jetflow_Tampadora": [
            "Falha torque aplicação tampa",
            "Desgaste mandril cabeça",
            "Jammed tampa no canal",
        ],
        "Compressor_AF_HP_40bar": [
            "Carbonização óleo 40 bar",
            "Desgaste rotor parafuso",
            "Falha separador óleo/ar",
            "Obstrução filtro entrada ar",
            "Superaquecimento interstágio",
        ],
        "Compressor_GardnerDenver_LP": [
            "Falha filtro separador condensado",
            "Desgaste rolamento lado acoplado",
            "Alarme temperatura descarga",
            "Falha pressostato controle",
        ],
        "Chiller_Qualiterme": [
            "Incrustação trocador de calor",
            "Falha bomba água glicolada",
            "Baixa pressão gás refrigerante",
            "Obstrução filtro Y circuito",
        ],
        "Rotuladora_PELatina_Simplecut": [
            "Ajuste tensão bobina rótulo",
            "Falha faca rotativa Simplecut",
            "Acúmulo cola rolos pressão",
            "Rótulo rasgado na aplicação",
        ],
        "Empacotadora_Taymak": [
            "Falha filme PE embalagem",
            "Falha resistência solda",
            "Erro contagem fardos",
        ],
        "Strechadora": [
            "Desgaste filme stretch",
            "Falha motor giro plataforma",
        ],
        "Esteiras_Transportadoras": [
            "Desgaste correia transportadora",
            "Falha motor redutor esteira",
        ],
        "Lavadora_Tunel_Assepsia": [
            "Obstrução bicos aspersão",
            "Falha bomba recirculação solução",
            "Desregulagem temperatura banho",
        ],
        "Lacradora": [
            "Falha resistência lacre",
            "Desalinhamento posição lacre",
        ],
        "Placas_Solares_Inversores": [
            "Falha inversor string",
            "Queda geração por sujidade",
        ],
        "Bombas_Processo": [
            "Cavitação bomba centrífuga",
            "Falha vedação mecânica",
            "Superaquecimento motor bomba",
        ],
    }
    registros = []
    data_inicio = datetime(2024, 1, 1)
    for equip, spec in specs.items():
        crit = spec["criticidade"]
        n = {
            "Crítica": np.random.randint(25, 60),
            "Alta":    np.random.randint(15, 40),
            "Média":   np.random.randint(8,  25),
            "Baixa":   np.random.randint(3,  12),
        }.get(crit, 15)
        for _ in range(n):
            data_falha = data_inicio + timedelta(
                days=np.random.randint(0, 365),
                hours=np.random.randint(0, 24))
            tipo_falha = np.random.choice(
                tipos_falha.get(equip, ["Falha genérica"]))
            ttf_media = {
                "Crítica": 3.0, "Alta": 2.0,
                "Média": 1.2, "Baixa": 0.6}.get(crit, 1.5)
            ttf = max(0.25, round(np.random.exponential(ttf_media), 2))
            lo, hi = {
                "Crítica": (1200, 8000), "Alta": (400, 3000),
                "Média": (150, 900), "Baixa": (50, 300)}.get(crit, (200, 1500))
            custo = round(np.random.uniform(lo, hi), 2)
            tipo_man = np.random.choice(
                ["Corretiva", "Preventiva", "Preditiva"],
                p=[0.55, 0.30, 0.15])
            registros.append({
                "data_ocorrencia":         data_falha,
                "equipamento":             equip,
                "area":                    spec["area"],
                "criticidade":             crit,
                "tipo_falha":              tipo_falha,
                "tipo_manutencao":         tipo_man,
                "tempo_reparo_horas":      ttf,
                "custo_reparo":            custo,
                "producao_perdida_caixas": round(ttf * np.random.uniform(60, 180)),
                "tecnico_responsavel":     np.random.choice(
                    ["Carlos", "João", "Marcos", "Fernanda", "Roberto"]),
                "turno":    np.random.choice(["Manhã", "Tarde", "Noite"]),
                "resolvido": np.random.choice([True, False], p=[0.92, 0.08]),
            })
    df = pd.DataFrame(registros).sort_values(
        "data_ocorrencia").reset_index(drop=True)
    df["mes"]        = df["data_ocorrencia"].dt.month
    df["semana"]     = df["data_ocorrencia"].dt.isocalendar().week.astype(int)
    df["dia_semana"] = df["data_ocorrencia"].dt.day_name()
    return df
