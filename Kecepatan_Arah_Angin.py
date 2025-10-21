import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# ==============================
# 🔧 Konfigurasi Halaman
# ==============================
st.set_page_config(
    page_title="Perhitungan Arah & Kecepatan Angin",
    layout="centered",
)

st.title("🌬️ Perhitungan Arah dan Kecepatan Angin")

st.markdown("""
Aplikasi ini menghitung **arah datang, arah bertiup, dan kecepatan angin**  
berdasarkan data **U10** dan **V10** dari file Excel (.xlsx).  

📘 **Format wajib file input:**
- Kolom **U10**
- Kolom **V10**
""")

# ==============================
# 📂 Upload File Excel
# ==============================
uploaded_file = st.file_uploader("Upload file Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"❌ Gagal membaca file: {e}")
        st.stop()

    if not {"U10", "V10"}.issubset(df.columns):
        st.error("❌ File tidak memiliki kolom 'U10' dan 'V10'. Pastikan nama kolom sesuai.")
        st.stop()

    st.success(f"✅ File berhasil dibaca ({len(df)} baris data)")

    if st.button("▶️ Mulai Perhitungan"):
        with st.spinner("Sedang menghitung arah dan kecepatan angin..."):

            # ==============================
            # 🔢 Perhitungan utama
            # ==============================
            df["U_neg"] = -df["U10"]
            df["V_neg"] = -df["V10"]

            # Gunakan arctan2 agar tidak error saat U=0
            df["phi"] = np.degrees(np.arctan2(df["V_neg"], df["U_neg"]))

            # Konversi ke arah datang (0–360°)
            df["Arah_Datang_deg"] = (270 - df["phi"]) % 360

            # Kecepatan angin
            df["Kecepatan"] = np.sqrt(df["U10"]**2 + df["V10"]**2)

            # Label arah
            def arah_label(deg):
                if deg > 337.5 or deg <= 22.5:
                    return "Utara"
                elif deg <= 67.5:
                    return "Timur Laut"
                elif deg <= 112.5:
                    return "Timur"
                elif deg <= 157.5:
                    return "Tenggara"
                elif deg <= 202.5:
                    return "Selatan"
                elif deg <= 247.5:
                    return "Barat Daya"
                elif deg <= 292.5:
                    return "Barat"
                else:
                    return "Barat Laut"

            df["Arah_Datang_Label"] = df["Arah_Datang_deg"].apply(arah_label)

            # Arah bertiup (kebalikan arah datang)
            df["Arah_Bertiup_deg"] = (df["Arah_Datang_deg"] + 180) % 360
            df["Arah_Bertiup_Label"] = df["Arah_Bertiup_deg"].apply(arah_label)

            # ==============================
            # 💾 Ekspor ke Excel
            # ==============================
            def to_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    dataframe.to_excel(writer, index=False, sheet_name="Hasil_Perhitungan")
                return output.getvalue()

            excel_bytes = to_excel(df)

            st.success("✅ Perhitungan selesai!")
            st.download_button(
                label="💾 Unduh Hasil Perhitungan (Excel)",
                data=excel_bytes,
                file_name="hasil_perhitungan_angin.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:
    st.info("⬆️ Silakan unggah file Excel untuk memulai.")

