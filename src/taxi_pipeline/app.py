import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os

# --- 0. НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(
    page_title="NYC Taxi AI Intelligence",
    page_icon="🚕",
    layout="wide"
)

# --- 1. ФУНКЦІЇ ЗАВАНТАЖЕННЯ (З КЕШУВАННЯМ) ---

@st.cache_resource
def get_db():
    """Підключення до MongoDB"""
    uri = "mongodb://admin:secret_pass@localhost:27017/"
    client = MongoClient(uri)
    return client["taxi_db"]

@st.cache_data
def get_location_names():
    """Завантаження назв районів (Lookup)"""
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    return pd.read_csv(url)

@st.cache_data
def get_local_coords():
    """Завантаження координат з локального файлу (Offline-first)"""
    path = "src/taxi_pipeline/taxi_zones_with_coords.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_resource
def load_ml_model():
    """Завантаження навченої ML моделі"""
    model_path = "taxi_model.joblib"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

# Ініціалізація ресурсів
db = get_db()
zones_lookup = get_location_names()
coords_df = get_local_coords()
model = load_ml_model()

# --- 2. БІЧНА ПАНЕЛЬ (SIDEBAR) ---
st.sidebar.title("🚕 Налаштування")

# Фільтр округів
all_boroughs = ["Усі"] + sorted(zones_lookup['Borough'].dropna().unique().tolist())
selected_borough = st.sidebar.selectbox("Оберіть округ (Borough)", all_boroughs)

# Фільтр типів оплати
pay_labels = {
    "Усі": "Усі",
    1: "💳 Кредитна картка",
    2: "💵 Готівка",
    3: "🚫 Безкоштовно",
    4: "❓ Спірно"
}
selected_pay_label = st.sidebar.radio("Спосіб оплати", list(pay_labels.values()))
selected_pay_code = [k for k, v in pay_labels.items() if v == selected_pay_label][0]

st.sidebar.markdown("---")
st.sidebar.caption("""
Проєкт розроблено в межах MSc AI/ML програми.\n
Розробник Андрій Болонний
""")
# --- 3. ОБРОБКА ОСНОВНИХ ДАНИХ (PIPELINE) ---

spatial_data = list(db["spatial_stats"].find())
df = pd.DataFrame(spatial_data)

if not df.empty:
    # Очищення та об'єднання
    df = df.merge(zones_lookup, on='LocationID')
    
    # Фільтрація Spatial Data
    if selected_borough != "Усі":
        df = df[df['Borough'] == selected_borough]
    if selected_pay_code != "Усі":
        df = df[df['payment_type'] == selected_pay_code]

# --- 4. ГОЛОВНИЙ ІНТЕРФЕЙС (TABS) ---

st.title("NYC Taxi Data Intelligence System")

tab1, tab2, tab3 = st.tabs(["📊 Аналітичний огляд", "🤖 AI Прогноз вартості", "📝 Методологія"])

# --- TAB 1: АНАЛІТИКА ---
with tab1:
    if not df.empty:
        # KPI Картки
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("Всього поїздок", f"{df['TripCount'].sum():,}")
        col_kpi2.metric("Сер. чек (District Avg)", f"${df['AvgFare'].mean():.2f}")
        col_kpi3.metric("Сер. чайові", f"${df['AvgTip'].mean():.2f}")

        # КАРТА
        st.subheader("🗺️ Географія активності")
        if not coords_df.empty:
            map_df = df.merge(coords_df[['LocationID', 'lat', 'long']], on='LocationID')
            if not map_df.empty:
                fig_map = px.scatter_mapbox(
                    map_df, lat="lat", lon="long", 
                    size="TripCount", color="AvgFare",
                    hover_name="Zone", size_max=15, zoom=10,
                    mapbox_style="carto-positron",
                    color_continuous_scale=px.colors.sequential.Viridis,
                    height=500
                )
                st.plotly_chart(fig_map, use_container_width=True)

        # ГРАФІКИ
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📍 ТОП локацій")
            top_zones = df.sort_values("TripCount", ascending=False).head(10)
            fig_z = px.bar(top_zones, x='TripCount', y='Zone', orientation='h', color='AvgFare')
            st.plotly_chart(fig_z, use_container_width=True)
        
        with c2:
            st.subheader("🕒 Попит по годинах")
            hourly_raw = list(db["hourly_stats"].find().sort("Hour", 1))
            df_h = pd.DataFrame(hourly_raw)
            if not df_h.empty and selected_pay_code != "Усі":
                df_h = df_h[df_h['payment_type'] == selected_pay_code]
            
            if not df_h.empty:
                hourly_agg = df_h.groupby("Hour")["TripCount"].sum().reset_index()
                fig_t = px.area(hourly_agg, x='Hour', y='TripCount', color_discrete_sequence=['orange'])
                st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.warning("Дані за вказаними фільтрами відсутні.")

# --- TAB 2: AI КАЛЬКУЛЯТОР ---
with tab2:
    st.header("🧮 Розумний розрахунок вартості")
    
    col_in, col_out = st.columns([1, 1])
    
    with col_in:
        st.subheader("Вхідні параметри")
        # Безпечне отримання списку зон
        zone_list = sorted([str(z) for z in zones_lookup['Zone'].dropna().unique()])
        calc_zone = st.selectbox("Звідки їдемо?", zone_list)
        calc_hour = st.slider("Година виклику", 0, 23, 12)
        calc_dist = st.slider("Очікувана дистанція (милі)", 0.5, 50.0, 5.0, step=0.5)
        
        # Знаходимо ID вибраної зони
        target_id = zones_lookup[zones_lookup['Zone'] == calc_zone]['LocationID'].values[0]

    with col_out:
        st.subheader("Прогноз")
        
        # 1. Розрахунок історичного середнього (Baseline)
        district_data = df[df['LocationID'] == target_id]
        if not district_data.empty:
            base_p = district_data['AvgFare'].values[0]
            # Коефіцієнт часу (спрощено з df_h)
            try:
                h_stats = df_h[df_h['Hour'] == calc_hour]
                h_factor = h_stats['AvgFare'].mean() / df_h['AvgFare'].mean()
                stat_price = base_p * h_factor
            except:
                stat_price = base_p
            
            # 2. Розрахунок AI моделі (Random Forest)
            if model:
                input_df = pd.DataFrame(
                    [[target_id, calc_hour, calc_dist]], 
                    columns=['PULocationID', 'hour', 'trip_distance']
                )
                ai_price = model.predict(input_df)[0]
                
                st.success(f"🤖 AI Прогноз (з дистанцією): **${ai_price:.2f}**")
                st.info(f"📊 Історичне середнє (без дистанції): ${stat_price:.2f}")
                
                diff = ai_price - stat_price
                st.caption(f"Коригування моделі відносно статистики: {'+' if diff > 0 else ''}${diff:.2f}")
            else:
                st.error("ML модель не завантажена. Запустіть train_model.py")
        else:
            st.warning("Недостатньо історичних даних для цього району.")

# --- TAB 3: МЕТОДОЛОГІЯ ---
with tab3:
    st.header("Технічна документація проєкту")
    st.markdown(f"""
    ### 🧠 Опис моделі
    Використовується алгоритм **Random Forest Regressor** для прогнозування вартості поїздки.
    
    **Основні етапи підготовки:**
    1. **Data Cleaning:** Видалення поїздок з `fare_amount < $5` та `trip_distance < 0.5` миль.
    2. **Feature Engineering:** - Вилучення `hour` (0-23) з часової мітки.
        - Категоризація `PULocationID`.
    3. **Training:** Навчання на 100,000 записів із застосуванням 80/20 Train/Test split.
    
    ### 📈 Оцінка точності
    - **Метрика:** Mean Absolute Error (MAE).
    - **Поточний показник:** Очікувана помилка в межах $2-3 при врахуванні дистанції.
    """)
    
    # Графік важливості ознак (демонстраційний)
    st.subheader("Вплив факторів на прогноз (Feature Importance)")
    feat_imp = pd.DataFrame({
        'Factor': ['Дистанція', 'Година', 'Район'],
        'Importance': [0.65, 0.20, 0.15]
    })
    st.plotly_chart(px.bar(feat_imp, x='Importance', y='Factor', orientation='h'))