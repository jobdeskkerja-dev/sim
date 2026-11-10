# ================================================================
# SIPRES — DASHBOARD PREMIUM KEHADIRAN SISWA (ULTRA MODERN + NAVIGASI)
# Modul Khusus BK dan Wali Kelas — SMKN 4 OKU
# Google Colab + Gradio + Plotly + Ngrok (Fixed Port 7870)
# ================================================================


import pandas as pd
import gradio as gr
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import html
import base64
import os
import glob

# ----------------------- PENCARIAN LOGO DI FOLDER --------------------
def get_logo_base64():
    for pattern in ["*logo*.*", "*.png", "*.jpg", "*.jpeg"]:
        files_found = glob.glob(pattern)
        for file_path in files_found:
            if os.path.isfile(file_path) and not file_path.endswith('.py'):
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    ext = file_path.split('.')[-1].lower()
                    mime = "image/png" if ext == "png" else "image/jpeg"
                    print(f"✅ Logo berhasil dimuat: {file_path}")
                    return f"data:{mime};base64,{encoded_string}"
    print("⚠️ Peringatan: Belum ada file logo yang diunggah. Menggunakan teks.")
    return ""

LOGO_BASE64 = get_logo_base64()

# ----------------------- KONFIGURASI WARNA MODERN -----------------

PRIMARY = "#4F46E5"
DARK_BG = "#0F172A"
CARD_BG = "#FFFFFF"
YELLOW = "#F59E0B"
ORANGE = "#F97316"
GREEN = "#10B981"
RED = "#EF4444"

REQUIRED_COLS = [
    "NIS", "Nama", "Kelas",
    "Alpa", "Menit_Terlambat", "Jumlah_Sanksi"
]

# ----------------------- LOGIKA BK & GRAFIK -----------------------

def evaluasi_status_sp(alpa, menit, sanksi):
    if alpa >= 5 or sanksi >= 3 or menit >= 120:
        return "🔴 Perlu SP 2"
    elif alpa >= 3 or sanksi >= 2 or menit >= 40:
        return "🟡 Perlu SP 1"
    return "🟢 Aman"

def kartu(nilai, judul, ikon, warna, keterangan):
    return f"""
    <div class="kpi-card" style="--accent:{warna}">
        <div class="kpi-top">
            <span class="kpi-label">{judul}</span>
            <span class="kpi-icon">{ikon}</span>
        </div>
        <div class="kpi-value">{nilai:,}</div>
        <div class="kpi-note">{keterangan}</div>
        <div class="kpi-line"></div>
    </div>
    """

def grafik_kosong(judul, pesan="Unggah file Excel untuk melihat statistik analitik"):
    fig = go.Figure()
    fig.add_annotation(
        text=pesan,
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=14, color="#94A3B8", family="Inter")
    )
    fig.update_layout(
        title=dict(text=judul, font=dict(size=16, color="#1E293B", family="Inter", weight=700)),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=25, r=25, t=55, b=25),
        autosize=True
    )
    return fig

def grafik_status(df):
    if df is None or df.empty or "Status_SP" not in df.columns:
        return grafik_kosong("Distribusi Status Kedisiplinan Siswa")

    urutan = ["🟢 Aman", "🟡 Perlu SP 1", "🔴 Perlu SP 2"]
    jumlah = df["Status_SP"].value_counts().reindex(urutan, fill_value=0)

    fig = go.Figure(go.Pie(
        labels=["Aman", "Perlu SP 1", "Perlu SP 2"],
        values=jumlah.values,
        hole=0.7,
        sort=False,
        marker=dict(colors=[GREEN, YELLOW, RED], line=dict(color="#FFFFFF", width=3)),
        textinfo="percent",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value} siswa<extra></extra>"
    ))

    fig.add_annotation(
        text=f"<b>{len(df)}</b><br><span style='font-size:11px; color:#64748B'>Total Siswa</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=22, color="#1E293B", family="Inter")
    )

    fig.update_layout(
        title=dict(text="Distribusi Status Kedisiplinan Siswa", font=dict(size=16, color="#1E293B", family="Inter", weight=700)),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=55, b=35),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center", font=dict(family="Inter", size=12)),
        font=dict(family="Inter", color="#64748B"),
        autosize=True
    )
    return fig

def grafik_pelanggaran(df):
    if df is None or df.empty or not all(col in df.columns for col in ["Alpa", "Menit_Terlambat", "Jumlah_Sanksi"]):
        return grafik_kosong("Statistik Jenis Pelanggaran")

    kategori = ["Alpa", "Terlambat", "Pelanggaran"]
    jumlah = [
        int((df["Alpa"] > 0).sum()),
        int((df["Menit_Terlambat"] > 0).sum()),
        int((df["Jumlah_Sanksi"] > 0).sum())
    ]

    fig = go.Figure(go.Bar(
        x=kategori,
        y=jumlah,
        marker=dict(
            color=[RED, YELLOW, PRIMARY],
            cornerradius=10
        ),
        text=jumlah,
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Siswa terdampak: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="Statistik Jenis Pelanggaran", font=dict(size=16, color="#1E293B", family="Inter", weight=700)),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=35, r=25, t=55, b=45),
        yaxis=dict(
            title="Jumlah Siswa",
            rangemode="tozero",
            gridcolor="#E2E8F0",
            dtick=1 if len(df) < 20 else None,
            title_font=dict(family="Inter", size=12)
        ),
        xaxis=dict(title="", tickfont=dict(size=12, family="Inter")),
        showlegend=False,
        font=dict(family="Inter", color="#64748B"),
        autosize=True
    )
    return fig

# ----------------------- FUNGSI INTERAKTIF KLIK SISWA --------------------

def detail_siswa_terpilih(df_semua, evt: gr.SelectData):
    """Menangkap baris/sel yang diklik pada tabel database siswa."""
    if df_semua is None or df_semua.empty:
        return "⚠️ Belum ada data atau tabel masih kosong."
    try:
        row_idx = evt.index[0]
        row_data = df_semua.iloc[row_idx]

        pesan_detail = (
            f"🔍 DETAIL DATA SISWA TERPILIH:\n"
            f"----------------------------------------\n"
            f"📌 Nama Lengkap  : {row_data['Nama']}\n"
            f"🆔 NIS           : {row_data['NIS']}\n"
            f"🏫 Kelas         : {row_data['Kelas']}\n"
            f"📋 Total Alpa    : {row_data['Alpa']} hari\n"
            f"⏱️ Keterlambatan : {row_data['Menit_Terlambat']} menit\n"
            f"⚠️ Jumlah Sanksi : {row_data['Jumlah_Sanksi']} kali\n"
            f"📊 Status Kedisiplinan: {row_data['Status_SP']}\n"
        )
        return pesan_detail
    except Exception as e:
        return f"⚠️ Gagal membaca data siswa: {str(e)}"

# ----------------------- PROSES EXCEL ----------------------------

def proses_excel_bk(file_obj):
    fig_awal_1 = grafik_kosong("Distribusi Status Kedisiplinan Siswa")
    fig_awal_2 = grafik_kosong("Statistik Jenis Pelanggaran")

    kosong = [
        "Pilih dan unggah file Excel terlebih dahulu.",
        pd.DataFrame(columns=["NIS", "Nama", "Kelas", "Status_SP"]),
        pd.DataFrame(),
        kartu(0, "Total Siswa", "👥", PRIMARY, "Siswa terdata di sistem"),
        kartu(0, "Total Alpa", "📋", RED, "Akumulasi tanpa keterangan"),
        kartu(0, "Menit Terlambat", "⏱️", ORANGE, "Akumulasi waktu terlambat"),
        kartu(0, "Total Pelanggaran", "⚠️", GREEN, "Akumulasi sanksi disiplin"),
        fig_awal_1,
        fig_awal_2,
        "Klik baris/nama siswa di tabel database untuk melihat rincian..."
    ]

    if file_obj is None:
        return kosong

    try:
        file_path = getattr(file_obj, "name", file_obj)
        df = pd.read_excel(file_path)
        df.columns = df.columns.astype(str).str.strip()

        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            kosong[0] = f"❌ Kolom Excel belum sesuai. Belum ditemukan: {', '.join(missing)}. Gunakan format kolom baku."
            return kosong

        if df.empty:
            kosong[0] = "⚠️ File Excel tidak berisi data siswa."
            return kosong

        df["NIS"] = df["NIS"].fillna("").astype(str).str.strip()

        kolom_angka = ["Alpa", "Menit_Terlambat", "Jumlah_Sanksi"]
        for kolom in kolom_angka:
            df[kolom] = pd.to_numeric(df[kolom], errors="coerce")
            if df[kolom].isna().any():
                kosong[0] = f"❌ Kolom {kolom} memiliki data kosong atau bukan angka valid."
                return kosong
            if (df[kolom] < 0).any():
                kosong[0] = f"❌ Nilai pada kolom {kolom} tidak boleh bernilai negatif."
                return kosong
            df[kolom] = df[kolom].astype(int)

        df["Status_SP"] = df.apply(
            lambda r: evaluasi_status_sp(r["Alpa"], r["Menit_Terlambat"], r["Jumlah_Sanksi"]),
            axis=1
        )

        total_siswa = len(df)
        total_alpa = int(df["Alpa"].sum())
        total_menit = int(df["Menit_Terlambat"].sum())
        total_sanksi = int(df["Jumlah_Sanksi"].sum())

        aman = int((df["Status_SP"] == "🟢 Aman").sum())
        sp1 = int((df["Status_SP"] == "🟡 Perlu SP 1").sum())
        sp2 = int((df["Status_SP"] == "🔴 Perlu SP 2").sum())

        ringkasan = (
            "📊 RINGKASAN EVALUASI KEDISIPLINAN SEKOLAH\n\n"
            f"👥 Total Siswa Terdata : {total_siswa}\n"
            f"🟢 Status Aman        : {aman} siswa\n"
            f"🟡 Rekomendasi SP 1    : {sp1} siswa\n"
            f"🔴 Rekomendasi SP 2    : {sp2} siswa\n\n"
            "💡 Status SP dihitung secara otomatis berdasarkan parameter ambang batas pelanggaran."
        )

        df_bahaya = df[
            df["Status_SP"].isin(["🟡 Perlu SP 1", "🔴 Perlu SP 2"])
        ][["NIS", "Nama", "Kelas", "Alpa", "Menit_Terlambat", "Jumlah_Sanksi", "Status_SP"]].copy()

        if df_bahaya.empty:
            df_bahaya = pd.DataFrame([{
                "NIS": "-", "Nama": "Luar biasa! Tidak ada siswa melewati ambang batas SP",
                "Kelas": "-", "Alpa": 0, "Menit_Terlambat": 0, "Jumlah_Sanksi": 0, "Status_SP": "🟢 Aman"
            }])

        cards = [
            kartu(total_siswa, "Total Siswa", "👥", PRIMARY, "Siswa terdata di sistem"),
            kartu(total_alpa, "Total Alpa", "📋", RED, "Akumulasi tanpa keterangan"),
            kartu(total_menit, "Menit Terlambat", "⏱️", ORANGE, "Akumulasi waktu terlambat"),
            kartu(total_sanksi, "Total Pelanggaran", "⚠️", GREEN, "Akumulasi sanksi disiplin")
        ]

        return (
            ringkasan,
            df_bahaya,
            df,
            *cards,
            grafik_status(df),
            grafik_pelanggaran(df),
            "✅ Data berhasil dimuat. Silakan klik baris siswa pada tab 'Database Seluruh Siswa' untuk melihat detail."
        )

    except Exception as e:
        kosong[0] = f"❌ Gagal memproses file Excel: {str(e)}"
        return kosong

# ----------------------- DESAIN CSS ULTRA MODERN + FIX HEADER -----

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.gradio-container {
    max-width: 1550px !important;
    margin: auto !important;
    background: #F8FAFC !important;
    font-family: 'Inter', sans-serif !important;
}

body { background: #F8FAFC !important; }

/* PAKSA HEADER DAN SELURUH TEKS DI DALAMNYA TERANG */
.main-header, .main-header *, .main-header h1, .main-header p, .main-header span {
    color: #FFFFFF !important;
}

.main-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #312E81 100%) !important;
    padding: 35px 40px !important;
    border-radius: 24px !important;
    margin: 12px 0 24px !important;
    box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.3) !important;
    position: relative !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.header-content {
    display: flex !important;
    align-items: center !important;
    gap: 28px !important;
}

.header-logo {
    width: 90px !important;
    height: 90px !important;
    object-fit: contain !important;
    background: transparent !important;
    padding: 2px !important;
    border-radius: 12px !important;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3)) !important;
    flex-shrink: 0 !important;
}

.main-header h1 {
    font-size: clamp(26px, 3.2vw, 38px) !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin: 0 0 10px !important;
    letter-spacing: -0.5px !important;
}

.main-header p {
    margin: 0 !important;
    color: #CBD5E1 !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    max-width: 800px !important;
}

.brand-tag {
    display: inline-block !important;
    background: rgba(99, 102, 241, 0.4) !important;
    color: #C7D2FE !important;
    border: 1px solid rgba(165, 180, 252, 0.5) !important;
    padding: 6px 14px !important;
    border-radius: 30px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1.2px !important;
    margin-bottom: 14px !important;
    text-transform: uppercase !important;
}

.kpi-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important;
    padding: 22px !important;
    min-height: 145px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
    margin-bottom: 8px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.kpi-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 30px rgba(79, 70, 229, 0.08) !important;
    border-color: #C7D2FE !important;
}

.kpi-top {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 8px !important;
}

.kpi-label {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.kpi-icon {
    background: #F1F5F9 !important;
    border-radius: 14px !important;
    padding: 8px 10px !important;
    font-size: 18px !important;
}

.kpi-value {
    font-size: 32px !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    margin: 12px 0 4px !important;
    letter-spacing: -1px !important;
}

.kpi-note {
    font-size: 11px !important;
    color: #94A3B8 !important;
}

.kpi-line {
    height: 4px !important;
    width: 40px !important;
    border-radius: 4px !important;
    background: var(--accent) !important;
    margin-top: 14px !important;
}

.section-heading {
    color: #0F172A !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    margin: 18px 0 4px !important;
    letter-spacing: -0.3px !important;
}

.section-subtitle {
    color: #64748B !important;
    font-size: 13px !important;
    margin: 0 0 16px !important;
}

.primary-btn {
    background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
    transition: all 0.2s ease !important;
}

.primary-btn:hover {
    opacity: 0.95 !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4) !important;
    transform: translateY(-1px) !important;
}

button {
    border-radius: 12px !important;
    font-weight: 600 !important;
}

input, textarea, .gr-box {
    border-radius: 14px !important;
    border-color: #E2E8F0 !important;
}
"""

# ----------------------- BANGUN APLIKASI GRADIO ------------------

with gr.Blocks(
    title="SIPRES | Dashboard Kehadiran Siswa SMKN 4 OKU",
    css=CSS
) as app:

    if LOGO_BASE64:
        logo_html = f'<img src="{LOGO_BASE64}" class="header-logo" alt="Logo SMKN 4 OKU">'
    else:
        logo_html = '<div class="header-logo" style="display:flex;align-items:center;justify-content:center;font-size:10px;color:#64748B;text-align:center;">Logo Kosong</div>'

    gr.HTML(f"""
    <div class="main-header" style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #312E81 100%); padding: 35px 40px; border-radius: 24px; color: #FFFFFF !important;">
        <div class="header-content" style="display: flex; align-items: center; gap: 28px;">
            {logo_html}
            <div>
                <span class="brand-tag" style="background: rgba(99, 102, 241, 0.4); color: #C7D2FE !important; padding: 6px 14px; border-radius: 30px; font-size: 11px; font-weight: 700;">SIPRES • SMART SCHOOL</span>
                <h1 style="color: #FFFFFF !important; font-size: 34px; font-weight: 800; margin: 10px 0 8px 0;">Dashboard Kehadiran Siswa</h1>
                <p style="color: #CBD5E1 !important; font-size: 14px; margin: 0; max-width: 800px; line-height: 1.6;">
                    Sistem Informasi Kehadiran & Kedisiplinan Siswa khusus Guru BK dan Wali Kelas.
                    Pantau analitik kehadiran, deteksi dini siswa bermasalah, dan ambil tindakan preventif secara cepat dan akurat.
                </p>
            </div>
        </div>
    </div>
    """)

    # ------------------ SISTEM NAVIGASI TAB UTAMA ------------------
    with gr.Tabs():

        # --- TAB 1: DASHBOARD & ANALITIK UTAMA ---
        with gr.TabItem("📊 Dashboard & Analitik Utama"):
            gr.HTML("""
            <div class="section-heading">Ringkasan Kinerja Sekolah</div>
            <div class="section-subtitle">Indikator utama kedisiplinan yang terakumulasi secara real-time dari database absensi.</div>
            """)

            with gr.Row():
                html_siswa = gr.HTML(kartu(0, "Total Siswa", "👥", PRIMARY, "Siswa terdata di sistem"))
                html_alpa = gr.HTML(kartu(0, "Total Alpa", "📋", RED, "Akumulasi tanpa keterangan"))
                html_terlambat = gr.HTML(kartu(0, "Menit Terlambat", "⏱️", ORANGE, "Akumulasi waktu terlambat"))
                html_sanksi = gr.HTML(kartu(0, "Total Pelanggaran", "⚠️", GREEN, "Akumulasi sanksi disiplin"))

            with gr.Row():
                with gr.Column(scale=1, min_width=300):
                    with gr.Group():
                        gr.HTML("""
                        <div class="section-heading">📂 Import Data Absensi</div>
                        <div class="section-subtitle">Unggah laporan absensi format .xlsx</div>
                        """)
                        input_file = gr.File(
                            label="Pilih File Excel (.xlsx)",
                            file_types=[".xlsx"],
                            type="filepath"
                        )
                        btn_proses = gr.Button(
                            "🚀 Proses & Perbarui Dashboard",
                            variant="primary",
                            elem_classes=["primary-btn"]
                        )
                        btn_reset = gr.Button("↺ Reset Tampilan")

                        gr.Markdown("""
                        ---
                        **Format Kolom Wajib di Excel:**
                        `NIS` | `Nama` | `Kelas` | `Alpa` | `Menit_Terlambat` | `Jumlah_Sanksi`
                        """)

                with gr.Column(scale=2, min_width=380):
                    with gr.Group():
                        gr.HTML("""
                        <div class="section-heading">📌 Hasil Evaluasi BK</div>
                        <div class="section-subtitle">Ringkasan rekomendasi penanganan siswa</div>
                        """)
                        output_ringkasan = gr.Textbox(
                            label="Laporan Status Evaluasi",
                            lines=7,
                            interactive=False,
                            placeholder="Menunggu file Excel diunggah..."
                        )

            gr.HTML("""
            <div class="section-heading">📈 Analitik & Statistik Visual</div>
            <div class="section-subtitle">Grafik interaktif untuk membaca pola kehadiran dan kedisiplinan siswa secara menyeluruh.</div>
            """)

            with gr.Row():
                with gr.Column():
                    chart_status = gr.Plot(value=grafik_kosong("Distribusi Status Kedisiplinan Siswa"), label="Distribusi Status")
                with gr.Column():
                    chart_pelanggaran = gr.Plot(value=grafik_kosong("Statistik Jenis Pelanggaran"), label="Statistik Pelanggaran")

        # --- TAB 2: PUSAT PERINGATAN DINI (EARLY WARNING SYSTEM) ---
        with gr.TabItem("⚠️ Pusat Peringatan BK"):
            gr.HTML("""
            <div class="section-heading">Pusat Peringatan Dini (Early Warning System)</div>
            <div class="section-subtitle">Daftar siswa yang memerlukan perhatian khusus atau rekomendasi Surat Peringatan (SP 1 / SP 2) berdasarkan akumulasi pelanggaran.</div>
            """)
            output_peringatan = gr.Dataframe(
                label="Siswa yang Memerlukan Pendampingan",
                interactive=False,
                wrap=True
            )

        # --- TAB 3: DATABASE SELURUH SISWA (DENGAN FITUR KLIK) ---
        with gr.TabItem("🗂️ Database Seluruh Siswa"):
            gr.HTML("""
            <div class="section-heading">Database Seluruh Siswa</div>
            <div class="section-subtitle">Klik baris atau nama siswa pada tabel untuk melihat rincian kedisiplinan secara mendetail di sebelah kanan.</div>
            """)

            with gr.Row():
                with gr.Column(scale=2):
                    output_tabel_semua = gr.Dataframe(
                        label="Riwayat Data Kehadiran Keseluruhan (Klik baris siswa)",
                        interactive=False,
                        wrap=True
                    )
                with gr.Column(scale=1):
                    output_detail_klik = gr.Textbox(
                        label="Rincian Siswa Terpilih",
                        lines=10,
                        interactive=False,
                        placeholder="Klik baris/nama siswa di tabel sebelah kiri..."
                    )

        # --- TAB 4: PANDUAN & ATURAN SP ---
        with gr.TabItem("📖 Panduan & Aturan SP"):
            gr.Markdown("""
            ### 📘 Panduan Sistem Rekomendasi Surat Peringatan (SP)
            Sistem secara otomatis menghitung dan memberikan rekomendasi status kedisiplinan siswa berdasarkan kriteria ambang batas berikut:

            * 🟢 **Aman**: Siswa belum melewati ambang batas kedisiplinan.
            * 🟡 **Perlu SP 1**: Diberikan jika siswa memenuhi salah satu kriteria berikut:
              * Jumlah **Alpa** ≥ 3 hari
              * Akumulasi **Menit Terlambat** ≥ 40 menit
              * Jumlah **Sanksi / Pelanggaran** ≥ 2 kali
            * 🔴 **Perlu SP 2**: Diberikan jika siswa memenuhi salah satu kriteria berikut:
              * Jumlah **Alpa** ≥ 5 hari
              * Akumulasi **Menit Terlambat** ≥ 120 menit
              * Jumlah **Sanksi / Pelanggaran** ≥ 3 kali
            """)

    gr.HTML("""
    <div style="text-align:center; padding:25px; margin-top:20px; color:#94A3B8; font-size:12px; border-top:1px solid #E2E8F0;">
        <b>SIPRES • Smart School</b> — Dashboard Analitik Kehadiran Siswa & Kedisiplinan Sekolah<br>
        Dibuat khusus untuk Guru Bimbingan Konseling dan Wali Kelas
    </div>
    """)

    outputs = [
        output_ringkasan,
        output_peringatan,
        output_tabel_semua,
        html_siswa,
        html_alpa,
        html_terlambat,
        html_sanksi,
        chart_status,
        chart_pelanggaran,
        output_detail_klik
    ]

    btn_proses.click(fn=proses_excel_bk, inputs=[input_file], outputs=outputs)

    def reset_dashboard():
        data = proses_excel_bk(None)
        return [None] + list(data)

    btn_reset.click(fn=reset_dashboard, inputs=[], outputs=[input_file] + outputs)

    # Event saat baris tabel di Tab Database diklik
    output_tabel_semua.select(
        fn=detail_siswa_terpilih,
        inputs=[output_tabel_semua],
        outputs=[output_detail_klik]
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    print(f"Menjalankan SIPRES pada port {port}...")
    app.launch(server_name="0.0.0.0", server_port=port, share=False, show_error=True)
