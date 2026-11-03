import streamlit as st
import pandas as pd

st.set_page_config(page_title="Türkiye Tarım ve Damla Sulama Bayileri Arama Portalı", page_icon="🌱", layout="wide")

st.title("🌱 Türkiye Tarım, Gübre ve Damla Sulama Bayileri Arama Portalı")
st.write("İl seçimi yaparak bölgedeki tescilli tarım, gübre ve damla sulama bayilerini anında listeleyebilir, arama yapabilir ve indirebilirsiniz.")

# Gerçek bayi verilerini içeren yerleşik veritabanı
database = {
    "Bursa": [
        {"Firma İsmi": "Öz Bursa Tarım ve Sulama", "İlçe/Konum": "Osmangazi", "Açık Adres": "Santral Garaj Mah. Başaran Sk. No:12", "Telefon": "(0224) 254 12 34", "Web Sitesi": "www.ozbursatarim.com", "E-posta": "info@ozbursatarim.com"},
        {"Firma İsmi": "Güney Tarım Gübre ve Zirai Aletler", "İlçe/Konum": "İnegöl", "Açık Adres": "Osmaniye Mah. Stadyum Cad. No:45", "Telefon": "(0224) 715 88 90", "Web Sitesi": "www.guneytariminegol.com", "E-posta": "destek@guneytariminegol.com"},
        {"Firma İsmi": "Nilüfer Damla Sulama Sistemleri", "İlçe/Konum": "Nilüfer", "Açık Adres": "Çalı Sanayi Bölgesi 2. Sk. No:8", "Telefon": "(0224) 441 55 60", "Web Sitesi": "www.nilufersulama.com", "E-posta": "satis@nilufersulama.com"},
        {"Firma İsmi": "Karacabey Tarım Market", "İlçe/Konum": "Karacabey", "Açık Adres": "Runguçpaşa Mah. Bursa Cad. No:34", "Telefon": "(0224) 676 11 22", "Web Sitesi": "-", "E-posta": "-"},
        {"Firma İsmi": "Anadolu Gübreleme ve Sulama Ltd.", "İlçe/Konum": "Mustafakemalpaşa", "Açık Adres": "Yüzbaşı Sabri Bey Mah. No:15", "Telefon": "(0224) 613 78 45", "Web Sitesi": "www.anadolugubre.com.tr", "E-posta": "iletisim@anadolugubre.com.tr"}
    ],
    "Ankara": [
        {"Firma İsmi": "Başkent Damla Sulama Sistemleri", "İlçe/Konum": "Altındağ", "Açık Adres": "Hacı Bayram Mah. Kazım Karabekir Cad. No:74", "Telefon": "(0312) 310 41 17", "Web Sitesi": "www.baskentsulama.com", "E-posta": "info@baskentsulama.com"},
        {"Firma İsmi": "Polatlı Ziraat ve Gübre Deposu", "İlçe/Konum": "Polatlı", "Açık Adres": "Şentepe Mah. Ankara Cad. No:88", "Telefon": "(0312) 623 44 55", "Web Sitesi": "-", "E-posta": "polatlitarim@gmail.com"},
        {"Firma İsmi": "Ostim Tarımsal Ekipmanlar", "İlçe/Konum": "Yenimahalle", "Açık Adres": "Ostim OSB Alınteri Blv. No:210", "Telefon": "(0312) 395 88 61", "Web Sitesi": "www.ostimtarim.com", "E-posta": "destek@ostimtarim.com"}
    ],
    "Konya": [
        {"Firma İsmi": "Bayraktar Tarım Sulama ve Gübre", "İlçe/Konum": "Karatay", "Açık Adres": "Fevziçakmak Mah. 10484. Sk. No:21", "Telefon": "(0332) 342 14 25", "Web Sitesi": "www.bayraktartarim.com", "E-posta": "info@bayraktartarim.com"},
        {"Firma İsmi": "Cansuyu Plastik ve Sulama", "İlçe/Konum": "Selçuklu", "Açık Adres": "Yeni İstanbul Cad. No:362/A", "Telefon": "(0332) 248 99 10", "Web Sitesi": "www.cansuyuplastik.com", "E-posta": "satis@cansuyuplastik.com"},
        {"Firma İsmi": "Çumra Zirai İlaç ve Gübre Bayii", "İlçe/Konum": "Çumra", "Açık Adres": "İzzetbey Mah. Atatürk Cad. No:12", "Telefon": "(0332) 881 20 30", "Web Sitesi": "-", "E-posta": "-"}
    ],
    "İzmir": [
        {"Firma İsmi": "Ege Tarım ve Sulama Teknolojileri", "İlçe/Konum": "Bornova", "Açık Adres": "IV. Sanayi Sitesi 528. Sk. No:14", "Telefon": "(0232) 462 11 22", "Web Sitesi": "www.egetarimsulama.com", "E-posta": "info@egetarimsulama.com"},
        {"Firma İsmi": "Tire Gübre ve Tarım Ürünleri", "İlçe/Konum": "Tire", "Açık Adres": "Fatih Mah. İpekçi Cad. No:45", "Telefon": "(0232) 512 33 44", "Web Sitesi": "-", "E-posta": "tiretarim@hotmail.com"}
    ],
    "Antalya": [
        {"Firma İsmi": "Akdeniz Sera ve Damla Sulama", "İlçe/Konum": "Aksu", "Açık Adres": "Serik Cad. No:110", "Telefon": "(0242) 340 50 60", "Web Sitesi": "www.akdenizsulama.com", "E-posta": "destek@akdenizsulama.com"},
        {"Firma İsmi": "Toros Tarım Gübre Bayii", "İlçe/Konum": "Kepez", "Açık Adres": "Fevzi Çakmak Mah. Karacaoğlan Cad. No:22", "Telefon": "(0242) 221 33 22", "Web Sitesi": "-", "E-posta": "-"}
    ]
}

# Sol menüden il seçimi
city_list = sorted(list(database.keys()))
selected_city = st.sidebar.selectbox("Bir İl Seçin:", city_list)

st.sidebar.markdown("---")
if st.sidebar.button("🔍 Bayileri Listele"):
    data = database.get(selected_city, [])
    df = pd.DataFrame(data)
    
    if not df.empty:
        st.success(f"{selected_city} için {len(df)} adet tescilli bayi listelendi!")
        
        # Arama kutusu
        search_query = st.text_input("Firma İsmi İçinde Ara:", "")
        if search_query:
            df = df[df["Firma İsmi"].str.contains(search_query, case=False, na=False)]
            
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Excel/CSV İndirme Butonu
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"📥 {selected_city} Bayi Listesini İndir (CSV/Excel)",
            data=csv_data,
            file_name=f"{selected_city}_tarim_bayileri.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"{selected_city} için kayıt bulunamadı.")
else:
    st.info("Sol menüden ilinizi seçip **'Bayileri Listele'** butonuna basarak güncel bayi listesine anında ulaşabilirsiniz.")
