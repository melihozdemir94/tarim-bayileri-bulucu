import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Tarım ve Damla Sulama Bayileri Arama Portalı", page_icon="🌱", layout="wide")

st.title("🌱 Türkiye Tarım, Gübre ve Damla Sulama Bayileri Arama Portalı")
st.write("Bu platform üzerinden coğrafi bölge ve il seçimi yaparak kayıtlı tüm tarım bayilerini listeleyebilir, arama yapabilir ve Excel olarak indirebilirsiniz.")

regions = {
    "İç Anadolu Bölgesi": "Ic_Anadolu_Tarim_Bayileri.xlsx",
    "Marmara Bölgesi": "Marmara_Tarim_Bayileri.xlsx",
    "Ege Bölgesi": "Ege_Tarim_Bayileri.xlsx",
    "Akdeniz Bölgesi": "Akdeniz_Tarim_Bayileri.xlsx",
    "Karadeniz Bölgesi": "Karadeniz_Tarim_Bayileri.xlsx",
    "Doğu Anadolu Bölgesi": "Dogu_Anadolu_Tarim_Bayileri.xlsx",
    "Güneydoğu Anadolu Bölgesi": "Guneydogu_Anadolu_Tarim_Bayileri.xlsx"
}

st.sidebar.header("🔍 Arama ve Filtreleme")
selected_region_name = st.sidebar.selectbox("Bir Coğrafi Bölge Seçin:", list(regions.keys()))
file_name = regions[selected_region_name]

if os.path.exists(file_name):
    xls = pd.ExcelFile(file_name)
    cities = xls.sheet_names
    
    selected_city = st.sidebar.selectbox("Bir İl Seçin:", cities)
    df = pd.read_excel(xls, sheet_name=selected_city)
    
    search_query = st.text_input("İçeride Firma İsmi Ara (Örn: Ziraat, Gübre vb.):", "")
    if search_query:
        df = df[df["Firma İsmi"].str.contains(search_query, case=False, na=False)]
    
    st.subheader(f"📍 {selected_city} - Bayi Listesi ({len(df)} Kayıt Bulundu)")
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        with open(file_name, "rb") as f:
            st.download_button(
                label=f"📥 {selected_region_name} Tüm Bölge Excel Raporunu İndir",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("Bu kriterlere uygun kayıt bulunamadı.")
else:
    st.warning(f"⚠️ {selected_region_name} için veri dosyası henüz oluşturulmamış. Lütfen GitHub deponuzdaki Actions sekmesinden botu çalıştırıp verilerin oluşmasını sağlayın.")
