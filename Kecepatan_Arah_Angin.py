import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

# ==============================
# Konfigurasi Halaman
# ==============================
st.set_page_config(page_title="Perhitungan Arah & Kecepatan Angin", layout="centered")

st.title("🌬️ Perhitungan Arah dan Kecepatan Angin dari File Excel")

st.markdown("""
Aplikasi ini membaca data **U10** dan **V10** dari file Excel (.xlsx),
kemudian menghitung arah datang, arah bertiup, dan kecepatan angin.  

📘 **Format wajib file input Excel:**
- Kolom **U10**
- Kolom **V10**
""")

# ==============================
# Upload File
# ==============================
uploaded_file = st.file_uploader("📂 Upload file Excel (format .xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if "U10" not in df.columns or "V10" not in df.columns:
        st.error("❌ File tidak memiliki kolom 'U10' dan 'V10'. Pastikan nama kolom sesuai.")
    else:
        st.success(f"✅ File berhasil dibaca ({len(df)} baris data). Siap dihitung.")

        # ==============================
        # Tombol untuk memulai perhitungan
        # ==============================
        if st.button("▶️ Mulai Perhitungan"):
            with st.spinner("Sedang menghitung arah dan kecepatan angin..."):
                # ==============================
                # 🔢 PROSES PERHITUNGAN
                # ==============================
                df["U_neg"] = df["U10"] * -1
                df["V_neg"] = df["V10"] * -1

                # Alpha (radian)
                df["alpha"] = np.abs(np.arctan(df["V_neg"] / df["U_neg"]))

                # Kuadran
                def get_kuadran(U, V):
                    if U >= 0 and V >= 0:
                        return "K1"
                    elif U >= 0 and V < 0:
                        return "K2"
                    elif U < 0 and V < 0:
                        return "K3"
                    else:
                        return "K4"

                df["Kuadran"] = df.apply(lambda row: get_kuadran(row["U_neg"], row["V_neg"]), axis=1)

                # Phi (radian)
                def get_phi(k, alpha):
                    if k == "K1":
                        return (np.pi/2) - alpha
                    elif k == "K2":
                        return (np.pi/2) + alpha
                    elif k == "K3":
                        return (3*np.pi/2) - alpha
                    elif k == "K4":
                        return (3*np.pi/2) + alpha

                df["phi"] = df.apply(lambda row: get_phi(row["Kuadran"], row["alpha"]), axis=1)

                # Arah datang (derajat)
                df["Arah_Datang_deg"] = df["phi"] * 360 / (2*np.pi)

                # Kecepatan angin
                df["Kecepatan"] = np.sqrt(df["U_neg"]**2 + df["V_neg"]**2)

                # Keterangan arah datang
                def arah_label(deg):
                    if deg > 335 or deg <= 20:
                        return "Utara"
                    elif deg > 290:
                        return "Barat Laut"
                    elif deg > 245:
                        return "Barat"
                    elif deg > 200:
                        return "Barat Daya"
                    elif deg > 155:
                        return "Selatan"
                    elif deg > 110:
                        return "Tenggara"
                    elif deg > 65:
                        return "Timur"
                    else:
                        return "Timur Laut"

                df["Arah_Datang_Label"] = df["Arah_Datang_deg"].apply(arah_label)

                # Arah bertiup
                df["Arah_Bertiup_deg"] = np.where(
                    df["Arah_Datang_deg"] > 180,
                    df["Arah_Datang_deg"] - 180,
                    df["Arah_Datang_deg"] + 180
                )

                df["Arah_Bertiup_Label"] = df["Arah_Bertiup_deg"].apply(arah_label)

                # ==============================
                # 💾 EKSPOR KE EXCEL
                # ==============================
                def convert_df_to_excel(dataframe):
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Wind_Calculation"
                    for r in dataframe_to_rows(dataframe, index=False, header=True):
                        ws.append(r)
                    buffer = BytesIO()
                    wb.save(buffer)
                    buffer.seek(0)
                    return buffer

                excel_data = convert_df_to_excel(df)

                st.success("✅ Perhitungan selesai!")
                st.download_button(
                    label="💾 Unduh Hasil Perhitungan (Excel)",
                    data=excel_data,
                    file_name="hasil_perhitungan_angin.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
else:
    st.info("⬆️ Silakan unggah file Excel untuk memulai.")
