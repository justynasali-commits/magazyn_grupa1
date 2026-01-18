import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Zarządzanie Produktami", layout="wide")
st.title("📦 System Zarządzania Produktami")

# --- FUNKCJE POMOCNICZE ---
def get_categories():
    response = supabase.table("Kategorie").select("*").execute()
    return response.data

def get_products():
    # Pobieramy produkty wraz z nazwą kategorii (join)
    response = supabase.table("Produkty").select("*, Kategorie(nazwa)").execute()
    return response.data

# --- SIDEBAR: DODAWANIE KATEGORII ---
with st.sidebar:
    st.header("➕ Dodaj Kategorię")
    kat_nazwa = st.text_input("Nazwa Kategorii")
    kat_opis = st.text_area("Opis Kategorii")
    
    if st.button("Dodaj Kategorię"):
        if kat_nazwa:
            data = {"nazwa": kat_nazwa, "opis": kat_opis}
            supabase.table("Kategorie").insert(data).execute()
            st.success(f"Dodano kategorię: {kat_nazwa}")
            st.rerun()
        else:
            st.error("Nazwa jest wymagana!")

# --- GŁÓWNY PANEL: PRODUKTY ---
tab1, tab2 = st.tabs(["🛒 Produkty", "📂 Kategorie"])

with tab1:
    st.header("Lista Produktów")
    products = get_products()
    categories = get_categories()
    
    if products:
        for p in products:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 2, 1])
            col1.write(f"**{p['nazwa']}**")
            col2.write(f"{p['cena']} zł")
            col3.write(f"Sztuk: {p['liczba']}")
            # Bezpieczne pobieranie nazwy kategorii z relacji
            kat_name = p.get('Kategorie', {}).get('nazwa', 'Brak')
            col4.write(f"Kat: {kat_name}")
            
            if col5.button("Usuń", key=f"del_prod_{p['id']}"):
                supabase.table("Produkty").delete().eq("id", p["id"]).execute()
                st.rerun()
    else:
        st.info("Brak produktów w bazie.")

    st.divider()
    st.header("➕ Dodaj nowy produkt")
    
    with st.form("add_product"):
        p_nazwa = st.text_input("Nazwa produktu")
        p_liczba = st.number_input("Liczba", min_value=0, step=1)
        p_cena = st.number_input("Cena", min_value=0.0, format="%.2f")
        
        # Wybór kategorii z listy
        cat_options = {c['nazwa']: c['id'] for c in categories}
        p_kat_nazwa = st.selectbox("Kategoria", options=list(cat_options.keys()))
        
        submit = st.form_submit_button("Dodaj Produkt")
        
        if submit:
            if p_nazwa and p_kat_nazwa:
                new_prod = {
                    "nazwa": p_nazwa,
                    "liczba": p_liczba,
                    "cena": p_cena,
                    "kategoria": cat_options[p_kat_nazwa]
                }
                supabase.table("Produkty").insert(new_prod).execute()
                st.success("Dodano produkt!")
                st.rerun()

with tab2:
    st.header("Lista Kategorii")
    for c in categories:
        col1, col2, col3 = st.columns([2, 4, 1])
        col1.write(f"**{c['nazwa']}**")
        col2.write(c['opis'])
        if col3.button("Usuń", key=f"del_cat_{c['id']}"):
            try:
                supabase.table("Kategorie").delete().eq("id", c["id"]).execute()
                st.rerun()
            except Exception:
                st.error("Nie można usunąć kategorii, która zawiera produkty!")
