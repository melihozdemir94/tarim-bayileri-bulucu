import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Türkiye Geneli Canlı Tarım Bayileri Portalı", page_icon="🌱", layout="wide")

st.title("🌱 Türkiye Geneli Canlı Tarım, Gübre ve Damla Sulama Bayileri Portalı")
st.write("Bu portal, seçtiğiniz ildeki tescilli tarım, gübre ve damla sulama bayilerini harita veritabanından **anlık ve otomatik olarak** tarayıp listeler.")

# Türkiye'nin 81 ilinin listesi
all_81_cities = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara", "Antalya", 
    "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt", "Bilecik", 
    "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", 
    "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", 
    "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", 
    "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri", "Kilis", 
    "Kırıkkale", "Kırklareli", "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", 
    "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", 
    "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", 
    "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
]

selected_city = st.sidebar.selectbox("Türkiye 81 İl Seçimi:", sorted(all_81_cities))

# Canlı harita sorgulama fonksiyonu
@st.cache_data(ttl=1800)
def fetch_live_data_from_map(city):
    url = "https://overpass-api.de/api/interpreter"
    # Harita üzerinde tarım, gübre, sulama ve ziraat bayilerini arayan esnek sorgu
    query = f"""
    [out:json][timeout:30];
    area[name="{city}"]->.searchArea;
    (
      node["shop"~"agrarian|farm|hardware|garden"](area.searchArea);
      way["shop"~"agrarian|farm|hardware|garden"](area.searchArea);
      node["name"~"tarım|gübre|sulama|ziraat|tohum|agro", i](area.searchArea);
      way["name"~"tarım|gübre|sulama|ziraat|tohum|agro", i](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(url, data={'data': query}, timeout=35)
        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])
            results = []
            for el in elements:
                tags = el.get("tags", {})
                name = tags.get("name")
                if name:
                    results.append({
                        "Firma İsmi": name,
                        "İlçe/Konum": tags.get("addr:suburb", tags.get("addr:district", "Merkez")),
                        "Açık Adres": tags.get("addr:street", tags.get("addr:full", "-")),
                        "Telefon": tags.get("phone", tags.get("contact:phone", "-")),
                        "Web Sitesi": tags.get("website", tags.get("contact:website", "-")),
                        "E-posta": tags.get("email", "-")
                    })
            return pd.DataFrame(results).drop_duplicates(subset=["Firma İsmi"])
    except Exception as e:
        print(f"Hata: {e}")
    return pd.DataFrame()

st.sidebar.markdown("---")
if st.sidebar.button("🔍 Canlı Verileri Tara ve Listele"):
    with st.spinner(f"{selected_city} için harita veritabanından canlı bayiler taranıyor, lütfen bekleyin..."):
        df = fetch_live_data_from_map(selected_city)
        
        if not df.empty:
            st.success(f"{selected_city} için canlı tarama tamamlandı: {len(df)} adet işletme bulundu!")
            
            search_query = st.text_input("Firma İsmi İçinde Filtrele:", "")
            if search_query:
                df = df[df["Firma İsmi"].str.contains(search_query, case=False, na=False)]
                
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 {selected_city} Canlı Listeyi İndir (CSV/Excel)",
                data=csv_data,
                file_name=f"{selected_city}_canli_tarim_bayileri.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"{selected_city} için harita veritabanında bu kriterlere uygun anlık kayıt dönmedi. Alternatif olarak il merkezli ziraat odaları ve tarım kooperatifleri sorgulanabilir.")
else:
    st.info("Sol menüden dilediğiniz ili seçip **'Canlı Verileri Tara ve Listele'** butonuna basarak harita üzerinden otomatik ve anlık sonuç alabilirsiniz.")
