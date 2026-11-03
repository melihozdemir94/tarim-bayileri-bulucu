import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Tarım ve Damla Sulama Bayileri Arama Portalı", page_icon="🌱", layout="wide")

st.title("🌱 Türkiye Tarım, Gübre ve Damla Sulama Bayileri Arama Portalı")
st.write("İl seçimi yaparak bölgedeki tescilli tarım, gübre ve damla sulama bayilerini anlık olarak listeleyebilirsiniz.")

cities_turkey = [
    "Ankara", "Konya", "İzmir", "İstanbul", "Bursa", "Antalya", "Adana", "Mersin", 
    "Kayseri", "Eskişehir", "Sivas", "Manisa", "Aydın", "Denizli", "Balıkesir", 
    "Samsun", "Trabzon", "Gaziantep", "Diyarbakır", "Şanlıurfa", "Aksaray", "Karaman"
]

selected_city = st.sidebar.selectbox("Bir İl Seçin:", sorted(cities_turkey))

@st.cache_data(ttl=3600)
def get_live_osm_data(city):
    url = "https://overpass-api.de/api/interpreter"
    # Overpass API için uluslararası standart tarım/ziraat dükkan etiketleri
    query = f"""
    [out:json][timeout:25];
    area[name="{city}"]->.searchArea;
    (
      node["shop"~"agrarian|farm|hardware|garden"](area.searchArea);
      way["shop"~"agrarian|farm|hardware|garden"](area.searchArea);
      node["amenity"~"marketplace"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(url, data={'data': query}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            results = []
            for el in elements:
                tags = el.get("tags", {})
                # İsmi olan veya tarım/gübre/sulama geçen yerleri al
                name = tags.get("name", "")
                shop_type = tags.get("shop", tags.get("amenity", ""))
                
                if name:
                    results.append({
                        "Firma İsmi": name,
                        "Faaliyet Alanı": shop_type.title() if shop_type else "Tarım / Ziraat",
                        "İlçe/Konum": tags.get("addr:suburb", tags.get("addr:district", "Merkez")),
                        "Açık Adres": tags.get("addr:street", "-"),
                        "Telefon": tags.get("phone", tags.get("contact:phone", "-")),
                        "Web Sitesi": tags.get("website", tags.get("contact:website", "-")),
                        "E-posta": tags.get("email", "-")
                    })
            return pd.DataFrame(results).drop_duplicates(subset=["Firma İsmi"])
    except Exception as e:
        st.error(f"Veri çekilirken bağlantı hatası oluştu: {e}")
    return pd.DataFrame()

if st.sidebar.button("🔍 Bayileri Listele"):
    with st.spinner(f"{selected_city} için gerçek bayiler taranıyor, lütfen bekleyin..."):
        df = get_live_osm_data(selected_city)
        
        if not df.empty:
            st.success(f"{selected_city} için {len(df)} adet işletme bulundu!")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 {selected_city} Listesini Excel/CSV Olarak İndir",
                data=csv_data,
                file_name=f"{selected_city}_tarim_bayileri.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"{selected_city} için harita veritabanında doğrudan eşleşen kayıt bulunamadı. Alternatif olarak ilçe merkezli tarım kooperatifleri veya ziraat odaları çevresinde arama yapabilirsiniz.")
else:
    st.info("Sol menüden il seçip **'Bayileri Listele'** butonuna basarak anında güncel listeye ulaşabilirsiniz.")
