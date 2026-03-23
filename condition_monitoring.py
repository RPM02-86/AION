import pandas as pd
import numpy as np
from datetime import datetime, timedelta

ITENS_CHECKLIST = {
    "Sopradora_Multipet_VBlow_18K": [
        "Alinhamento molde PET", "Resistências pré-forma OK",
        "Pressão câmara sopro OK", "Lubrificação guias OK",
    ],
    "Envasadora_Mesal_21K": [
        "Bicos dosadores sem vazamento", "Estrela transfer alinhada",
        "CIP realizado", "Pressão enchimento OK",
    ],
    "Envasadora_Zegla_15K": [
        "Dosagem OK (garrafa teste)", "Cilindros sem vazamento",
        "Manifold sem vazamento",
    ],
    "Compressor_AF_HP_40bar": [
        "Pressão 40 bar estável", "Temperatura descarga < 90°C",
        "Nível óleo OK", "Filtros sem saturação",
    ],
    "Compressor_GardnerDenver_LP": [
        "Pressão 7 bar estável", "Temperatura descarga < 80°C",
        "Filtro separador OK",
    ],
    "Chiller_Qualiterme": [
        "Temperatura água glicolada OK", "Pressão gás refrigerante OK",
        "Bomba circulação sem ruído",
    ],
    "Jetflow_Tampadora": [
        "Torque tampa OK", "Canal tampa livre", "Mandris sem desgaste",
    ],
    "Rotuladora_PELatina_Simplecut": [
        "Tensão bobina OK", "Faca sem lascado", "Rolos cola limpos",
    ],
    "Empacotadora_Taymak": [
        "Resistência solda OK", "Guia entrada alinhada", "Filme sem rasgo",
    ],
    "Lavadora_Tunel_Assepsia": [
        "Bicos desobstruídos", "Temperatura banho OK", "Bomba sem ruído",
    ],
    "Bombas_Processo": [
        "Sem cavitação", "Vedação sem vazamento", "Pressão estável",
    ],
}

PONTOS_TERMOGRAFIA = {
    "Sopradora_Multipet_VBlow_18K": [
        ("Resistor Pré-forma", 180, 285),
        ("Motor Carro Móvel", 45, 80),
        ("Painel Elétrico", 35, 65),
    ],
    "Envasadora_Mesal_21K": [
        ("Motor Redutor", 40, 75),
        ("Painel Inversor", 35, 65),
        ("Rolamento Estrela", 40, 70),
    ],
    "Compressor_AF_HP_40bar": [
        ("Tubulação Descarga HP", 80, 130),
        ("Rotor Parafuso", 70, 115),
        ("Separador Óleo/Ar", 60, 95),
    ],
    "Compressor_GardnerDenver_LP": [
        ("Cabeça Compressão", 55, 90),
        ("Motor Principal", 40, 75),
    ],
    "Chiller_Qualiterme": [
        ("Trocador Calor", 10, 28),
        ("Motor Compressor", 45, 80),
        ("Bomba Glicolada", 35, 65),
    ],
    "Bombas_Processo": [
        ("Motor Bomba", 40, 75),
        ("Rolamento Acoplado", 40, 70),
    ],
}

PONTOS_VIBRACAO = {
    "Sopradora_Multipet_VBlow_18K": ["Horizontal", "Vertical", "Axial"],
    "Envasadora_Mesal_21K":  ["Motor — H", "Estrela — Axial", "Redutor — V"],
    "Envasadora_Zegla_15K":  ["Motor — H", "Bomba Vácuo — V"],
    "Compressor_AF_HP_40bar": ["Motor — H", "Rotor — Axial", "Mancal — V"],
    "Compressor_GardnerDenver_LP": ["Motor — H", "Cabeça — V", "Acoplamento — Axial"],
    "Chiller_Qualiterme":    ["Compressor — H", "Bomba — V"],
    "Bombas_Processo":       ["Motor — H", "Impulsor — V", "Vedação — Axial"],
}


def generate_checklist_diario(dias: int = 90):
    np.random.seed(10)
    registros = []
    data_inicio = datetime(2024, 1, 1)
    for equip, itens in ITENS_CHECKLIST.items():
        for dia in range(dias):
            data = data_inicio + timedelta(days=dia)
            for turno in ["Manhã", "Tarde", "Noite"]:
                for item in itens:
                    p = (0.12 if any(k in item.lower()
                             for k in ["vazamento", "temperatura", "pressão"])
                         else 0.05)
                    status = np.random.choice(
                        ["OK", "ALERTA", "NOK"],
                        p=[1-p, p*0.65, p*0.35])
                    registros.append({
                        "data": data, "equipamento": equip,
                        "turno": turno, "item_checklist": item,
                        "status": status,
                        "observacao": "" if status == "OK" else "Anomalia.",
                    })
    return pd.DataFrame(registros)


def generate_termografia(dias: int = 90, intervalo: int = 7):
    np.random.seed(20)
    registros = []
    data_inicio = datetime(2024, 1, 1)
    for equip, pontos in PONTOS_TERMOGRAFIA.items():
        for dia in range(0, dias, intervalo):
            data = data_inicio + timedelta(days=dia)
            for (ponto, tmin, tmax) in pontos:
                base   = np.random.uniform(tmin, tmin + (tmax-tmin)*0.4)
                drift  = (dia/dias) * (tmax-tmin) * 0.5
                medida = base + drift + np.random.normal(0, 2)
                delta  = medida - base
                sev = ("Normal"   if delta < 5  else
                       "Alerta"   if delta < 10 else
                       "Crítico"  if delta < 20 else "Emergencial")
                registros.append({
                    "data": data, "equipamento": equip,
                    "ponto_medicao": ponto,
                    "temperatura_base_c":   round(base,   1),
                    "temperatura_medida_c": round(medida, 1),
                    "delta_t_c":            round(delta,  1),
                    "severidade": sev, "limite_critico_c": tmax,
                })
    return pd.DataFrame(registros)


def generate_vibracao(dias: int = 90, intervalo: int = 7):
    np.random.seed(30)
    registros = []
    data_inicio = datetime(2024, 1, 1)
    for equip, pontos in PONTOS_VIBRACAO.items():
        for dia in range(0, dias, intervalo):
            data = data_inicio + timedelta(days=dia)
            for ponto in pontos:
                base  = np.random.uniform(0.8, 2.2)
                drift = (dia/dias) * np.random.uniform(1.5, 5.5)
                vib   = max(0.1, round(base+drift+np.random.normal(0, 0.15), 2))
                classe = ("A — Bom"           if vib < 2.8 else
                          "B — Aceitável"      if vib < 4.5 else
                          "C — Insatisfatório" if vib < 7.1 else
                          "D — Inaceitável")
                registros.append({
                    "data": data, "equipamento": equip,
                    "ponto_medicao": ponto,
                    "vib_mm_s_rms": vib, "classe_iso": classe,
                })
    return pd.DataFrame(registros)
