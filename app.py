import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Türkiye Canlı Tarım Bayileri Portalı", page_icon="🌱", layout="wide")

st.title("🌱 Türkiye Geneli Canlı Tarım, Gübre ve Damla Sulama Bayileri Portalı")
st.write("Bu sistem, seçtiğiniz ilin coğrafi sınırlarını anlık olarak tarayarak harita veritabanındaki gerçek işletmeleri listeler.")

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

@st.cache_data(ttl=3600)
def fetch_live_map_data(city):
    try:
        # 1. Adım: İlin koordinatlarını açık kaynaklı harita servisinden güvenle al
        nominatim_url = f"https://nominatim.openstreetmap.org/search?city={city}&country=Turkey&format=json"
        headers = {'User-Agent': 'TarimBayiApp/2.0'}
        res = requests.get(nominatim_url, headers=headers, timeout=10)
        
        if res.status_code == 200 and res.json():
            place = res.json()[0]
            bbox = place.get("boundingbox") # [güney, kuzey, batı, doğu]
            
            if bbox:
                south, north, west, east = bbox[0], bbox[1], bbox[2], bbox[3]
                
                # 2. Adım: Bu koordinat içindeki tescilli tarım/gübre dükkanlarını canlı çek
                overpass_url = "https://overpass-api.de/api/interpreter"
                query = f"""
                [out:json][timeout:25];
                (
                  node["shop"~"agrarian|farm|hardware|garden"]({south},{west},{north},{east});
                  way["shop"~"agrarian|farm|hardware|garden"]({south},{west},{north},{east});
                  node["name"~"tarım|gübre|sulama|ziraat|tohum|agro|fide", i]({south},{west},{north},{east});
                );
                out body;
                """
                
                response = requests.post(overpass_url, data={'data': query}, timeout=30)
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
                                "Açık Adres": tags.get("addr:street", "-"),
                                "Telefon": tags.get("phone", tags.get("contact:phone", "-")),
                                "Web Sitesi": tags.get("website", "-")
                            })
                    if results:
                        return pd.DataFrame(results).drop_duplicates(subset=["Firma İsmi"])
    except Exception as e:
        print(f"Hata: {e}")
        
    return pd.DataFrame()

st.sidebar.markdown("---")
if st.sidebar.button("🔍 Canlı Verileri Tara ve Getir"):
    with st.spinner(f"{selected_city} için harita veritabanından canlı tarama yapılıyor..."):
        df = fetch_live_map_data(selected_city)
        
        if not df.empty:
            st.success(f"{selected_city} taraması başarılı: {len(df)} adet gerçek işletme bulundu!")
            
            search_query = st.text_input("Listede Ara:", "")
            if search_query:
                df = df[df["Firma İsmi"].str.contains(search_query, case=False, na=False)]
                
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 {selected_city} Listesini Excel/CSV İndir",
                data=csv_data,
                file_name=f"{selected_city}_canli_bayiler.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"{selected_city} için bu harita katmanında doğrudan eşleşen tescilli dükkan etiketi dönmedi.")
else:
    st.info("Sol menüden ili seçip **'Canlı Verileri Tara ve Getir'** butonuna basarak internet üzerinden anlık tarama yapabilirsiniz.")
