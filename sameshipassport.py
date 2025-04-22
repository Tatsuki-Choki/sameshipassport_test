import streamlit as st
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict
import time
import base64
import pydeck as pdk
import streamlit.components.v1 as components
# utils, styles, templates をインポート
import utils
import styles
import templates

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scope
)

st.set_page_config(
    page_title="サ飯パスポート", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 認証 ---
# Using st.secrets for credentials (already set above)

# --- シートID ---
SHEET_ID = "1c1WDtrWXvDyTVis_1wzyVzkWf2Hq7SxRKuGkrdN3K4M"
 
category_icon = {
    "main": "🍽️",
    "drink": "🍺"
}


@st.cache_data
def load_sheet_as_df(sheet_id: str, sheet_name: str, _creds) -> pd.DataFrame:
    client = gspread.authorize(_creds)
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
    return df

saunas_df = load_sheet_as_df(SHEET_ID, "Saunas", creds)
saunas_df = saunas_df.dropna(subset=["name"])
saunas_df = saunas_df[saunas_df["name"].str.strip() != ""]
restaurants_df = load_sheet_as_df(SHEET_ID, "Restaurants", creds)
menu_items_df = load_sheet_as_df(SHEET_ID, "Menu", creds)
tags_df = load_sheet_as_df(SHEET_ID, "MenuTags", creds)
menu_item_tags_df = load_sheet_as_df(SHEET_ID, "MenuTagRelation", creds)

saunas = saunas_df.to_dict(orient="records")
restaurants = restaurants_df.to_dict(orient="records")
menu_items = menu_items_df.to_dict(orient="records")
tags = tags_df.to_dict(orient="records")
menu_item_tags = menu_item_tags_df.to_dict(orient="records")

# ------------------ Streamlit UI ------------------
# ロゴ（同フォルダ内の画像をbase64化）
with open("sameshi_logo02.png", "rb") as f:
    logo_data = f.read()
logo_base64 = base64.b64encode(logo_data).decode()

# 透かし用のロゴ
with open("sameshi_logo_sukashi.png", "rb") as f:
    stamp_data = f.read()
stamp_base64 = base64.b64encode(stamp_data).decode()

# メインロゴHTML
logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="225" height="225" alt="サ飯パスポートロゴ" />'

# スタイル定義を styles.py から取得
st.markdown(styles.CUSTOM_CSS, unsafe_allow_html=True)

# モバイル端末向けのセレクトボックス修正JavaScriptを適用
st.markdown(templates.get_mobile_select_fix_js(), unsafe_allow_html=True)

# 透かし用のHTML
stamp_html = templates.get_stamp_watermark_html(stamp_base64)

# ヘッダー部分
st.markdown(templates.get_header_html(logo_html), unsafe_allow_html=True)

# セッションステート初期化
if "selected_sauna_id" not in st.session_state:
    st.session_state.selected_sauna_id = None
if "selected_menus" not in st.session_state:
    st.session_state.selected_menus = []

st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
st.markdown('<p class="selection-label">サウナ施設を選ぶ</p>', unsafe_allow_html=True)

# サウナ選択
sauna_names = [s["name"] for s in saunas]
selected_sauna_name = st.selectbox("", sauna_names, label_visibility="collapsed")
selected_sauna = next(s for s in saunas if s["name"] == selected_sauna_name)
st.session_state.selected_sauna_id = selected_sauna["id"]

# ガチャを回すボタンを中央に配置
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
if st.button("ガチャを回す"):
    with st.spinner("サ飯を選定中..."):
        time.sleep(1.5)
        # utils.py の関数を使用
        candidate_menus = utils.get_all_menu_items_for_sauna(restaurants, menu_items, st.session_state.selected_sauna_id)
        st.session_state.selected_menus = utils.get_random_menus_by_category(candidate_menus)
st.markdown('</div>', unsafe_allow_html=True)

# 結果表示
if st.session_state.selected_menus:
    lat = selected_sauna.get("latitude")
    lng = selected_sauna.get("longitude")

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #006dee; text-align: center; margin-bottom: 20px;">サ飯ガチャ 結果</h2>', unsafe_allow_html=True)

    for menu in st.session_state.selected_menus:
        icon = category_icon.get(menu.get("category", "").lower(), "🍽️")
        # utils.py の関数を使用
        tags_html = ''.join([f'<span class="tag">#{t}</span>' for t in utils.get_tags_for_menu_item(menu_item_tags, tags, menu['id'])])
        image_path = f"images/{menu.get('image_file', '')}"
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
            # 画像スタイル変更: サイズ縮小、左寄せ、右マージン
            image_html = f'<img src="data:image/jpeg;base64,{encoded}" style="width:80px; height:80px; object-fit: cover; border-radius:12px; margin-right:15px; flex-shrink: 0;" />'
        else:
            image_html = ""
        
        # templates.pyの関数を使用
        st.markdown(templates.get_menu_card_html(menu, tags_html, image_html), unsafe_allow_html=True)

    raw_price = selected_sauna.get("entry_fee") or selected_sauna.get("entryfee") or selected_sauna.get("price", 0)
    try:
        sauna_fee = int(str(raw_price).replace(',', ''))
    except ValueError:
        sauna_fee = 0
    total_food_price = sum(menu['price'] for menu in st.session_state.selected_menus)
    total_price = sauna_fee + total_food_price

    # templates.pyの関数を使用
    st.markdown(templates.get_price_summary_html(sauna_fee, total_food_price, total_price, len(st.session_state.selected_menus)), unsafe_allow_html=True)

    # もう一度ボタンも中央配置
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("もう一度ガチャを回す"):
        # utils.py の関数を使用
        all_menus = utils.get_all_menu_items_for_sauna(restaurants, menu_items, st.session_state.selected_sauna_id)
        st.session_state.selected_menus = utils.get_random_menus_by_category(all_menus)
    st.markdown('</div>', unsafe_allow_html=True)
    if lat and lng:
        # utils.py の関数を使用
        nearby_foods = utils.find_nearby_good_food(lat, lng)
        if nearby_foods:
            # 見出しのテキストを短くしてスタイルを調整
            st.markdown('<h2 style="color: #006dee; text-align: center; margin-bottom: 20px; font-size: 22px; word-wrap: break-word; word-break: keep-all; line-height: 1.3;">徒歩圏内の高評価なサ飯処</h2>', unsafe_allow_html=True)
            
            # キーワードごとの絵文字アイコンマップ
            icon_map = {
                "ラーメン": "🍜",
                "牛丼": "🍚",
                "カレー": "🍛",
                "ハンバーガー": "🍔"
            }
            
            # templates.pyの関数を使用してマーカーJSを生成
            markers_js = templates.get_markers_js(lat, lng, selected_sauna_name, nearby_foods, icon_map)
            
            # templates.pyの関数を使用してマップHTMLを生成
            map_html = templates.get_maps_html(lat, lng, markers_js, st.secrets['env']['GOOGLE_API_KEY'])
            components.html(map_html, height=480)
            
            # 距離が短い順にソート
            if "distance" in nearby_foods[0]:
                nearby_foods = sorted(nearby_foods, key=lambda x: x['distance'])
            
            for store in nearby_foods:
                stars = "⭐" * int(round(store['rating']))
                # utils.py の関数を使用
                photo_base64 = utils.get_photo_base64(store["photo_url"]) if store.get("photo_url") else None
                if photo_base64:
                    # 画像スタイル変更: サイズ縮小、左寄せ、右マージン
                    image_html = f'<img src="data:image/jpeg;base64,{photo_base64}" style="width:80px; height:80px; object-fit: cover; border-radius:12px; margin-right:15px; flex-shrink: 0;" />'
                else:
                    # プレースホルダーのスタイルも変更
                    image_html = '<div style="width:80px; height:80px; background:#eee; border-radius:12px; margin-right:15px; flex-shrink: 0;"></div>'
                
                distance_text = f"距離: 約{store.get('distance', 0)}m" if store.get('distance') else ""
                
                # templates.pyの関数を使用して店舗カードを表示
                st.markdown(templates.get_store_card_html(store, image_html, stars, distance_text), unsafe_allow_html=True)
        else:
            st.markdown("😢 該当エリアに評価3.5以上のお店が見つかりませんでした。", unsafe_allow_html=True)

# フッター
st.markdown(templates.get_footer_html(), unsafe_allow_html=True)

# スタンプ風の透かし配置
st.markdown(stamp_html, unsafe_allow_html=True)