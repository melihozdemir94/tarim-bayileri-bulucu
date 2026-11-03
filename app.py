import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Tarım ve Damla Sulama Bayileri Arama Portalı", page_icon="🌱", layout="wide")

st.title("🌱 Türkiye Tarım, Gübre ve Damla Sulama Bayileri Arama Portalı")
st.write("İl seçimi yaparak bölgedeki tescilli tarım, gübre ve damla sulama bayilerini anlık olarak listeleyebilirsiniz.")

# Türkiye'nin illeri listesi
cities_turkey = [
    "Ankara", "Konya", "İzmir", "İstanbul", "Bursa", "Antalya", "Adana", "Mersin", 
    "Kayseri", "Eskişehir", "Sivas", "Manisa", "Aydın", "Denizli", "Balıkesir", 
    "Samsun", "Trabzon", "Gaziantep", "Diyarbakır", "Şanlıurfa", "Aksaray", "Karaman"
]

selected_city = st.sidebar.selectbox("Bir İl Seçin:", sorted(cities_turkey))

@st.cache_data(ttl=3600)
def get_live_osm_data(city):
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:20];
    area[name="{city}"]->.searchArea;
    (
      node["shop"~"agrarian|farm"](area.searchArea);
      node["name"~"tarım|gübre|sulama|ziraat", i](area.searchArea);
    );
    out body;
    """
    try:
        response = requests.post(url, data={'data': query}, timeout=25)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            results = []
            for el in elements:
                tags = el.get("tags", {})
                if "name" in tags:
                    results.append({
                        "Firma İsmi": tags.get("name"),
                        "İlçe/Konum": tags.get("addr:suburb", "Merkez"),
                        "Açık Adres": tags.get("addr:street", "-"),
                        "Telefon": tags.get("phone", tags.get("contact:phone", "-")),
                        "Web Sitesi": tags.get("website", tags.get("contact:website", "-")),
                        "E-posta": tags.get("email", "-")
                    })
            return pd.DataFrame(results)
    except Exception as e:
        st.error(f"Veri çekilirken bir hata oluştu: {e}")
    return pd.DataFrame()

if st.sidebar.button("🔍 Bayileri Listele"):
    with st.spinner(f"{selected_city} için gerçek bayi verileri taranıyor, lütfen bekleyin..."):
        df = get_live_osm_data(selected_city)
        
        if not df.empty:
            st.success(f"{selected_city} için {len(df)} adet işletme bulundu!")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Excel olarak indirme
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 {selected_city} Listesini CSV/Excel İndir",
                data=csv_data,
                file_name=f"{selected_city}_tarim_bayileri.csv",
                mime="text/csv"
            )
        else:
            st.info(f"{selected_city} için harita kayıtlarında eşleşen sonuç bulunamadı.")
else:
    st.info("Sol menüden il seçip **'Bayileri Listele'** butonuna basarak anında güncel listeye ulaşabilirsiniz.")
