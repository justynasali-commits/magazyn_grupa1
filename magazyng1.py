import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Zarządzanie Magazynem", layout="wide", page_icon="📊")
st.title("📦 System Zarządzania Produktami")

# --- FUNKCJE POMOCNICZE ---
def get_categories():
    response = supabase.table("Kategorie").select("*").execute()
    return response.data

def get_products():
    response = supabase.table("Produkty").select("*, Kategorie(nazwa)").execute()
    return response.data

# --- SIDEBAR: DODAWANIE KATEGORII ---
with st.sidebar:
    st.header("➕ Nowa Kategoria")
    kat_nazwa = st.text_input("Nazwa Kategorii")
    kat_opis = st.text_area("Opis Kategorii")
    
    if st.button("Dodaj Kategorię", use_container_width=True):
        if kat_nazwa:
            data = {"nazwa": kat_nazwa, "opis": kat_opis}
            supabase.table("Kategorie").insert(data).execute()
            st.success(f"Dodano: {kat_nazwa}")
            st.rerun()
        else:
            st.error("Nazwa jest wymagana!")

# --- GŁÓWNY PANEL Z ZAKŁADKAMI ---
tab1, tab2, tab3 = st.tabs(["🛒 Produkty", "📂 Kategorie", "📊 Analityka Stanu"])

with tab1:
    st.header("Lista Produktów")
    products = get_products()
    categories = get_categories()
    
    if products:
        # Nagłówki tabeli
        h1, h2, h3, h4, h5 = st.columns([2, 1, 1, 2, 1])
        h1.write("**Nazwa**")
        h2.write("**Cena**")
        h3.write("**Stan**")
        h4.write("**Kategoria**")
        h5.write("**Akcja**")
        st.divider()

        for p in products:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
            col1.write(p['nazwa'])
            col2.write(f"{p['cena']} zł")
            col3.write(f"{p['liczba']} szt.")
            kat_name = p.get('Kategorie', {}).get('nazwa', 'Brak')
            col4.write(kat_name)
            
            if col5.button("Usuń", key=f"del_prod_{p['id']}", type="secondary"):
                supabase.table("Produkty").delete().eq("id", p["id"]).execute()
                st.rerun()
    else:
        st.info("Brak produktów w bazie.")

    st.divider()
    st.subheader("➕ Dodaj nowy produkt")
    with st.form("add_product"):
        p_nazwa = st.text_input("Nazwa produktu")
        col_a, col_b = st.columns(2)
        p_liczba = col_a.number_input("Liczba", min_value=0, step=1)
        p_cena = col_b.number_input("Cena (zł)", min_value=0.0, format="%.2f")
        
        cat_options = {c['nazwa']: c['id'] for c in categories}
        p_kat_nazwa = st.selectbox("Kategoria", options=list(cat_options.keys()))
        
        submit = st.form_submit_button("Zapisz Produkt")
        if submit and p_nazwa:
            new_prod = {
                "nazwa": p_nazwa,
                "liczba": p_liczba,
                "cena": p_cena,
                "kategoria": cat_options[p_kat_nazwa]
            }
            supabase.table("Produkty").insert(new_prod).execute()
            st.success("Produkt dodany!")
            st.rerun()

with tab2:
    st.header("Zarządzanie Kategoriami")
    for c in categories:
        c1, c2, c3 = st.columns([2, 4, 1])
        c1.write(f"**{c['nazwa']}**")
        c2.write(c['opis'] if c['opis'] else "Brak opisu")
        if c3.button("Usuń", key=f"del_cat_{c['id']}"):
            try:
                supabase.table("Kategorie").delete().eq("id", c["id"]).execute()
                st.rerun()
            except:
                st.error("Nie można usunąć kategorii przypisanej do produktów!")

with tab3:
    st.header("Wizualizacja Stanów Magazynowych")
    if products:
        # Przygotowanie danych do wykresu
        df = pd.DataFrame(products)
        
        # Wykres słupkowy: Liczba sztuk per Produkt
        st.subheader("Ilość sztuk na magazynie")
        st.bar_chart(data=df, x="nazwa", y="liczba", color="#FF4B4B")
        
        # Opcjonalnie: Podsumowanie wartości
        total_value = sum(p['cena'] * p['liczba'] for p in products)
        st.metric("Całkowita wartość magazynu", f"{total_value:,.2f} zł")
    else:
        st.warning("Dodaj produkty, aby zobaczyć statystyki.")
