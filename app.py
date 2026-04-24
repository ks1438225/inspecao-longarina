import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import io

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Inspeção Longarina Cadeirinha",
    page_icon="🔧",
    layout="wide",
)

st.markdown("""
<script>
setTimeout(function() {
    const inputs = window.parent.document.querySelectorAll('input');

    inputs.forEach((input, index) => {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const next = inputs[index + 1];
                if (next) next.focus();
            }
        });
    });
}, 1000);
</script>
""", unsafe_allow_html=True)

# ── CSS personalizado ───────────────────────────────────────────────────────
st.markdown("""
<style>
    .header-box {
        background-color: #cc0000;
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .header-box h1 { color: white; margin: 0; font-size: 28px; }
    .header-box p  { color: #ffdada; margin: 4px 0 0; font-size: 14px; }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 20px;
    }
    .info-card {
        background: #f5f5f5;
        border-left: 4px solid #cc0000;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 13px;
    }
    .info-card strong { display: block; font-size: 11px; color: #666; text-transform: uppercase; }

    .step-box {
        background: #fff8e1;
        border: 1px solid #ffe082;
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 8px;
        font-size: 14px;
    }
    .step-box b { color: #cc0000; }

    .ok   { color: #2e7d32; font-weight: bold; }
    .nok  { color: #c62828; font-weight: bold; }
    .warn { color: #ef6c00; font-weight: bold; }

    div[data-testid="stMetricValue"] { font-size: 22px !important; }
</style>
""", unsafe_allow_html=True)

# ── Banco de dados ──────────────────────────────────────────────────────────
DB = "inspecoes.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inspecoes (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                data      TEXT,
                op        TEXT,
                inspetor  TEXT,
                hora      TEXT,
                med_a     REAL,
                med_b     REAL,
                med_c     REAL,
                med_d     REAL,
                med_e     REAL,
                bandeja   TEXT,
                comp      REAL,
                status    TEXT,
                obs       TEXT,
                criado_em TEXT
            )
        """)
        conn.commit()

init_db()

# ── Lógica de validação ─────────────────────────────────────────────────────
SPECS = {
    "A": {"nom": 30.0,  "tol": 0.5},
    "B": {"nom": 70.0,  "tol": 0.5},
    "C": {"nom": 20.0,  "tol": 0.5},
    "D": {"nom": 20.0,  "tol": 0.5},
    "E": {"nom": 15.0,  "tol": 0.5},
}

def check(key, value):
    s = SPECS[key]
    return abs(value - s["nom"]) <= s["tol"]

def overall_status(row):
    medidas_ok = all(check(k, row[f"med_{k.lower()}"]) for k in SPECS)
    bandeja_ok = str(row["bandeja"]).strip().upper() == "OK"
    return "OK" if (medidas_ok and bandeja_ok) else "NÃO OK"

# ── Cabeçalho ───────────────────────────────────────────────────────────────
IMG_DIR = Path(__file__).parent / "imagens"
logo_path = IMG_DIR / "logo_aguia.png"

import base64

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = img_to_base64(str(logo_path)) if logo_path.exists() else ""

st.markdown(f"""
<div style="display:flex;align-items:stretch;gap:0;border-radius:8px;overflow:hidden;margin-bottom:10px;">
  <div style="background:white;border:2px solid #cc0000;border-right:none;border-radius:8px 0 0 8px;
              padding:10px 16px;display:flex;align-items:center;justify-content:center;min-width:160px;">
    <img src="data:image/png;base64,{logo_b64}" style="height:80px;object-fit:contain;">
  </div>
  <div style="background:#cc0000;padding:16px 24px;border-radius:0 8px 8px 0;flex:1;
              display:flex;flex-direction:column;justify-content:center;">
    <div style="color:white;font-size:24px;font-weight:bold;margin:0;">
      INSPEÇÃO LONGARINA CADEIRINHA
    </div>
    <div style="color:#ffdada;font-size:12px;margin-top:6px;">
      Águia Sistemas &nbsp;·&nbsp; Setor: Qualidade Industrial &nbsp;·&nbsp; Revisão: 2 &nbsp;·&nbsp;
      Data: 01/08/2025 &nbsp;·&nbsp; Autora: Evelyn Ruth da Silva &nbsp;·&nbsp;
      Verificado: Melina Favaro &nbsp;·&nbsp;
      &nbsp; Desenvolvido: Programadora Web Kauane Silva·&nbsp; 
      <p <span style="color:white;font-weight:bold;">Inspeção: a cada 60 minutos</span> </p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Registros de Qualidade - PR na mesma linha com input inline
st.markdown("""
<style>
.pr-linha {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0px;
    font-size: 20px;
    font-weight: bold;
    margin: 8px 0;
}
.pr-linha input {
    font-size: 18px;
    font-weight: bold;
    width: 90px;
    border: none;
    border-bottom: 2px solid #aaa;
    outline: none;
    background: transparent;
    text-align: center;
    padding: 0 4px;
    margin-left: 6px;
    color: inherit;
}
.pr-linha input::placeholder {
    color: transparent;
}
</style>
<div class="pr-linha">
    Registros de Qualidade - PR<input type="text" maxlength="10" id="pr_input">
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Passos de inspeção ──────────────────────────────────────────────────────
with st.expander("Instruções de Inspeção", expanded=True):
    col_p1, col_p2, col_p3 = st.columns(3)
    passos = [
        (col_p1, "1º PASSO", "Inspecionar as medidas A (30), B (70), C (20), D (20 ± 0,5) e E (15).", "passo1.png"),
        (col_p2, "2º PASSO", "Conferir a altura da longarina cadeirinha de 20 (+0,5) mm com uma bandeja, avaliando o encaixe correto.", "passo2.png"),
        (col_p3, "3º PASSO", "Inspecionar o comprimento da longarina.", "passo3.png"),
    ]
    for col, titulo, descricao, img_file in passos:
        with col:
            st.markdown(f"**{titulo}**")
            st.caption(descricao)
            img_path = IMG_DIR / img_file
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                st.warning(f"Imagem não encontrada: {img_file}")

# ── Abas ────────────────────────────────────────────────────────────────────
aba1, aba2, aba3 = st.tabs(["Registrar Inspeção", "Histórico & Análise", "Exportar"])

# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 – REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
with aba1:
    st.subheader("Nova Inspeção")

    # Identificação
    col1, col2, col3 = st.columns(3)
    with col1:
        data_insp = st.date_input("Data", value=date.today())
    with col2:
        op = st.text_input("Ordem de Produção (O.P.)", placeholder="Ex: OP-2025-001")
    with col3:
        inspetor = st.text_input("Inspetor", placeholder="Nome do inspetor")

    hora = st.time_input("Hora da inspeção", value=datetime.now().time())

    st.divider()
    st.markdown("#### Medidas (mm)")

    labels = {
        "A": ("A", 30.0),
        "B": ("B", 70.0),
        "C": ("C", 20.0),
        "D": ("D ± 0,5", 20.0),
        "E": ("E", 15.0)
    }

    inputs = {}
    cols = st.columns(5)

    for i, (key, (lbl, nom)) in enumerate(labels.items()):
        with cols[i]:
            val_str = st.text_input(
                f"Medida {lbl}",
                placeholder=f"Ex: {nom}",
                key=f"med_{key}"
            )

            try:
                inputs[key] = round(float(val_str.replace(",", ".")), 1) if val_str else 0.0
            except:
                inputs[key] = 0.0

    st.divider()

    col_band, col_comp = st.columns(2)

    with col_band:
        st.markdown("#### Bandeja (encaixe)")
        bandeja = st.radio("Resultado da bandeja:", ["OK", "NÃO"], horizontal=True)

        if bandeja == "OK":
            st.success("Bandeja OK")
        else:
            st.error("Bandeja com problema — verificar encaixe!")

    with col_comp:
        st.markdown("#### Comprimento (mm)")

        comp_str = st.text_input("Comprimento", placeholder="Ex: 20,0") 

        try:
            comp = round(float(comp_str.replace(",", ".")), 1) if comp_str else 0.0
        except:
            comp = 0.0

    obs = st.text_area("Observações", placeholder="Registre qualquer observação...")

    st.divider()

    medidas_ok = all(check(k, inputs[k]) for k in inputs)
    bandeja_ok = bandeja.strip().upper() == "OK"
    status_preview = "OK" if (medidas_ok and bandeja_ok) else "NÃO OK"

    # ✅ BOTÃO ÚNICO (CORRIGIDO)
    if st.button("Salvar Inspeção", type="primary", use_container_width=True):
        if not op.strip():
            st.error("Preencha a Ordem de Produção.")
        elif not inspetor.strip():
            st.error("Preencha o nome do inspetor.")
        else:
            with get_conn() as conn:
                conn.execute("""
                    INSERT INTO inspecoes
                    (data, op, inspetor, hora, med_a, med_b, med_c, med_d, med_e,
                     bandeja, comp, status, obs, criado_em)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    str(data_insp), op.strip(), inspetor.strip(), hora.strftime("%H:%M:%S"),
                    inputs["A"], inputs["B"], inputs["C"], inputs["D"], inputs["E"],
                    bandeja, comp, status_preview, obs.strip(),
                    datetime.now().isoformat()
                ))
                conn.commit()

            st.success("Inspeção registrada com sucesso!")
            st.balloons()
# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 – HISTÓRICO
# ══════════════════════════════════════════════════════════════════════════════
with aba2:
    st.subheader("Histórico de Inspeções")

    with get_conn() as conn:
        df = pd.read_sql("SELECT * FROM inspecoes ORDER BY criado_em DESC", conn)

    if df.empty:
        st.info("Nenhuma inspeção registrada ainda.")
    else:
        # KPIs
        total  = len(df)
        ok_ct  = (df["status"] == "OK").sum()
        nok_ct = total - ok_ct
        taxa   = round(ok_ct / total * 100, 1)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total de Inspeções", total)
        k2.metric("Conformes", ok_ct)
        k3.metric("NÃO Conformes", nok_ct)
        k4.metric("Taxa de Conformidade", f"{taxa}%")

        st.divider()

        # Filtros
        f1, f2 = st.columns(2)
        with f1:
            ops_disp = ["Todas"] + sorted(df["op"].unique().tolist())
            op_filt  = st.selectbox("Filtrar por O.P.", ops_disp)
        with f2:
            status_filt = st.selectbox("Filtrar por Status", ["Todos", "OK", "NÃO OK"])

        df_filt = df.copy()
        if op_filt != "Todas":
            df_filt = df_filt[df_filt["op"] == op_filt]
        if status_filt != "Todos":
            df_filt = df_filt[df_filt["status"] == status_filt]

        # Tabela com colunas amigáveis
        df_show = df_filt[[
            "data","hora","op","inspetor",
            "med_a","med_b","med_c","med_d","med_e",
            "bandeja","comp","status","obs"
        ]].rename(columns={
            "data":"Data","hora":"Hora","op":"O.P.","inspetor":"Inspetor",
            "med_a":"A","med_b":"B","med_c":"C","med_d":"D","med_e":"E",
            "bandeja":"Bandeja","comp":"Comp.","status":"Status","obs":"Obs."
        })

        df_show = df_show.round(1)
        st.dataframe(df_show, use_container_width=True, hide_index=True)
       
        # Gráfico de conformidade por data
        if len(df) >= 2:
            st.markdown("#### Conformidade por dia")
            df["data_dt"] = pd.to_datetime(df["data"])
            graf = df.groupby("data_dt").apply(
                lambda x: round((x["status"] == "OK").sum() / len(x) * 100, 1)
            ).reset_index()
            graf.columns = ["Data", "% Conformidade"]
            st.line_chart(graf.set_index("Data"))
# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 – EXPORTAR PDF
# ══════════════════════════════════════════════════════════════════════════════
with aba3:
    st.subheader("Exportar Histórico em PDF")

    with get_conn() as conn:
        df_exp = pd.read_sql("SELECT * FROM inspecoes ORDER BY data ASC, hora ASC", conn)

    if df_exp.empty:
        st.info("Nenhum dado para exportar.")
    else:
        # Filtro por data
        datas_disp = sorted(df_exp["data"].unique().tolist())
        st.markdown("#### Selecione a data para exportar")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_ini = st.selectbox("Data início", datas_disp, index=0)
        with col_d2:
            data_fim = st.selectbox("Data fim", datas_disp, index=len(datas_disp)-1)

        df_filtrado = df_exp[
            (df_exp["data"] >= data_ini) &
            (df_exp["data"] <= data_fim)
        ]

        st.caption(f"{len(df_filtrado)} registro(s) encontrado(s).")

        if not df_filtrado.empty and st.button(
            "Gerar PDF do período",
            type="primary",
            use_container_width=True
        ):

            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib import colors
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_CENTER

            buf_pdf = io.BytesIO()

            doc = SimpleDocTemplate(
                buf_pdf,
                pagesize=landscape(A4),
                leftMargin=10*mm,
                rightMargin=10*mm,
                topMargin=10*mm,
                bottomMargin=10*mm
            )

            story = []

            # ── ESTILOS (ANTES DE USAR) ──
            titulo_style = ParagraphStyle(
                "titulo",
                fontSize=14,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                spaceAfter=6
            )

            sub_style = ParagraphStyle(
                "sub",
                fontSize=9,
                fontName="Helvetica",
                alignment=TA_CENTER,
                spaceAfter=10
            )

            # ── CABEÇALHO COM LOGO ──
            if logo_path.exists():
                img = Image(str(logo_path), width=70, height=40)  

                titulo = Paragraph(
                    "INSPEÇÃO LONGARINA CADEIRINHA — Águia Sistemas",
                    titulo_style
                    )

                cabecalho = Table(
                    [[img, titulo]],
                    colWidths=[80, 640]  
                    )

                cabecalho.setStyle(TableStyle([
                    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                    ("LEFTPADDING", (0,0), (-1,-1), 0),   
                    ("RIGHTPADDING", (0,0), (-1,-1), 0),
                    ("TOPPADDING", (0,0), (-1,-1), 0),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                    ]))

                story.append(cabecalho)

            else:
                story.append(Paragraph(
                    "INSPEÇÃO LONGARINA CADEIRINHA — Águia Sistemas",
                    titulo_style
                    ))

            story.append(Spacer(1, 6))

            # ── SUBTÍTULO ──
            story.append(Paragraph(
                f"Período: {data_ini} a {data_fim} | Setor: Qualidade Industrial",
                sub_style
            ))

            # ── TABELA ──
            colunas = [
                "Data", "Hora", "O.P.", "Inspetor",
                "A", "B", "C", "D", "E",
                "Bandeja", "Comp.", "Status", "Obs."
            ]

            dados = [colunas]

            for _, row in df_filtrado.iterrows():
                dados.append([
                    str(row["data"]),
                    pd.to_datetime(str(row["hora"])).strftime("%H:%M:%S"),
                    str(row["op"]),
                    str(row["inspetor"]),
                    f"{row['med_a']:.1f}",
                    f"{row['med_b']:.1f}",
                    f"{row['med_c']:.1f}",
                    f"{row['med_d']:.1f}",
                    f"{row['med_e']:.1f}",
                    str(row["bandeja"]),
                    f"{row['comp']:.1f}",
                    str(row["status"]),
                    str(row["obs"])[:30]
                ])
            tabela = Table(dados, repeatRows=1)

            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#cc0000")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1),
                    [colors.white, colors.HexColor("#f5f5f5")]
                ),
                ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
            ]))

            story.append(tabela)

            doc.build(story)
            buf_pdf.seek(0)

            st.download_button(
                label="Baixar PDF",
                data=buf_pdf,
                file_name=f"inspecoes_{data_ini}_a_{data_fim}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
