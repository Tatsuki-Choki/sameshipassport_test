import streamlit as st
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict  # これを追加
import time
import base64
import googlemaps
## from dotenv import load_dotenv  # Removed .env loading
import pydeck as pdk
import streamlit.components.v1 as components
## load_dotenv()
## gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"],
    scope
)
gmaps = googlemaps.Client(key=st.secrets["env"]["GOOGLE_API_KEY"])

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

# ------------------ ユーティリティ関数 ------------------
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def find_nearby_good_food(lat, lng, radius=200):
    keywords = ["ラーメン", "牛丼", "カレー", "ハンバーガー"]
    found_places = []

    for keyword in keywords:
        results = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            keyword=keyword,
            language="ja"
        ).get("results", [])

        for place in results:
            rating = place.get("rating", 0)
            name = place.get("name")
            place_lat = place["geometry"]["location"]["lat"]
            place_lng = place["geometry"]["location"]["lng"]
            distance = haversine(lat, lng, place_lat, place_lng)
            if rating >= 3.5 and distance <= radius:
                photo_ref = None
                if "photos" in place and place["photos"]:
                    photo_ref = place["photos"][0]["photo_reference"]
                # photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={os.getenv('GOOGLE_API_KEY')}" if photo_ref else None
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={st.secrets['env']['GOOGLE_API_KEY']}" if photo_ref else None

                found_places.append({
                    "name": name,
                    "rating": rating,
                    "keyword": keyword,
                    "latitude": place_lat,
                    "longitude": place_lng,
                    "distance": int(distance),
                "maps_url": f"https://www.google.com/maps/search/?api=1&query={place_lat},{place_lng}",
                    "photo_url": photo_url
                })
    return found_places

def get_restaurants_by_sauna(sauna_id: int) -> List[Dict]:
    return [r for r in restaurants if r["sauna_id"] == sauna_id]

def get_menu_items_by_restaurant(restaurant_id: int) -> List[Dict]:
    return [m for m in menu_items if m["restaurant_id"] == restaurant_id]

def get_tags_for_menu_item(menu_item_id: int) -> List[str]:
    tag_ids = [t["tag_id"] for t in menu_item_tags if t.get("menuitemid") == menu_item_id]
    return [t["name"] for t in tags if t["id"] in tag_ids]

def get_all_menu_items_for_sauna(sauna_id: int) -> List[Dict]:
    all_menus = []
    for rest in get_restaurants_by_sauna(sauna_id):
        all_menus.extend(get_menu_items_by_restaurant(rest["id"]))
    return all_menus

def get_random_menus_by_category(menu_items: List[Dict]) -> List[Dict]:
    selected = []

    # main から1品
    mains = [item for item in menu_items if item.get('category', '').strip().lower() == 'main']
    if mains:
        selected.append(random.choice(mains))

    # drink から2品（重複しないように）
    drinks = [item for item in menu_items if item.get('category', '').strip().lower() == 'drink']
    if len(drinks) >= 2:
        selected.extend(random.sample(drinks, 2))
    elif drinks:
        selected.extend(drinks)  # 1品しかない場合はその1品だけ

    return selected

# ------------------ ユーティリティ関数: get_photo_base64 ------------------
import requests

def get_photo_base64(photo_url):
    try:
        response = requests.get(photo_url)
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except Exception:
        return None
    return None

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
# ↑従来のサイズ(width=150, height=150) → 1.5倍 (225×225)
logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="225" height="225" alt="サ飯パスポートロゴ" />'

# スタンプ風の透かし用画像
# stamp_base64 = logo_base64 # 同じロゴを使用しない

st.markdown(f"""
<style>
    /* 全体のベースカラーとフォントをbodyおよびコンテナに適用 */
    body, .reportview-container, .stApp, .main {{
        background-color: #f7e93f; /* ベースカラー黄色 */
        /* background-image: url("https://s.mj.run/qmlyfG-PEwY"); */ /* 背景画像削除 */
        /* background-repeat: repeat; */
        color: #006dee; /* アクセントカラー青をデフォルトテキスト色に */
        font-family: 'Noto Sans JP', sans-serif; /* 日本語フォント指定 */
        font-weight: 700; /* 全体のフォントウェイトを太めに */
        overflow-x: hidden; /* 横スクロールを禁止 */
    }}

    /* .mainからは色とフォント指定を削除 */
    .main {{
        /* background-color: #1e1e2d; */
        /* color: #e8d0a9; */
        /* font-family: 'Noto Sans JP', sans-serif; */
        padding: 0;
        max-width: 100%;
        /* overflow-x: hidden; */ /* bodyに移動 */
        box-sizing: border-box; /* padding/borderを幅に含める */
    }}
    
    /* ヘッダー部分: アクセントカラー */
    .passport-header {{
        background-color: #006dee; /* アクセントカラー青 */
        color: #fff; /* サブアクセント白 */
        padding: 30px 20px;
        text-align: center;
        border-radius: 0;
        margin-top: -80px; /* 上方向のマージンは維持 */
        /* margin-left: -80px; */ /* 削除 */
        /* margin-right: -80px; */ /* 削除 */
        width: 100%; /* 幅を100%に */
        box-sizing: border-box; /* paddingを含めて幅計算 */
        position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    
    /* タイトル(日本語) */
    .passport-title {{
        /* font-family: "Hiragino Mincho ProN", "Times New Roman", serif; */
        font-family: 'Noto Sans JP', serif; /* 日本語フォント指定 */
        font-size: 42px;
        font-weight: 700; /* 太字 */
        margin-bottom: 20px;
        letter-spacing: 2px;
        color: #f7e93f; /* ベースカラー黄色に変更 */
    }}
    
    /* SAMESHI PASSPORT: 英語タイトル */
    .passport-en-title {{
        /* font-family: "Times New Roman", serif; */
        font-family: 'Montserrat', sans-serif; /* 英語フォント指定 */
        font-size: 20px;
        letter-spacing: 2px;
        display: inline-block;
        padding: 5px 10px;
        border: 1px solid #006dee; /* アクセントカラー青に変更 */
        margin-top: 10px;
        color: #f7e93f; /* ベースカラー黄色に変更 */
        font-weight: 700; /* 太字 */
    }}
    
    /* ロゴセンタリング */
    .centered-icon {{
        display: block;
        margin: 0 auto 20px auto;
        text-align: center;
    }}
    
    /* セレクトボックスのラベル */
    .selection-label {{
        font-size: 20px;
        margin-bottom: 10px;
        color: #006dee; /* アクセントカラー青 */
        font-weight: 700; /* 太字 */
    }}

    /* セレクトボックス */
    .stSelectbox > div > div {{
        background-color: #fff; /* サブアクセント白 */
        color: #006dee; /* アクセントカラー青 */
        border: 1px solid #006dee; /* アクセントカラー青 */
        border-radius: 0;
        padding: 12px 14px;
        font-size: 17px;
        font-weight: 700; /* 太字 */
        line-height: 1.8;
        height: auto !important;
        overflow: visible !important;
        display: flex;
        align-items: center;
    }}

    /* ボタン */
    .stButton > button {{
        background-color: #006dee !important; /* アクセントカラー青 */
        color: #fff !important; /* サブアクセント白 */
        font-weight: 700 !important; /* 太字 */
        padding: 12px 40px;
        border-radius: 0 !important;
        border: none !important;
        font-size: 18px !important;
        margin-top: 15px;
        transition: all 0.3s;
        font-family: 'Noto Sans JP', sans-serif; /* フォント指定 */
    }}
    .stButton > button:hover {{
        background-color: #0056b3 !important; /* 少し暗い青 */
        box-shadow: 0 0 8px rgba(0, 109, 238, 0.3); /* 影の色調整 */
    }}
    
    /* カード全体のスタイル */
    .result-card {{
        background-color: #fff; /* サブアクセント白 */
        /* border: 1px solid #006dee; */ /* ボーダー削除 */
        border-radius: 16px; /* 角丸を大きく */
        padding: 18px; /* 20pxから15pxに変更 */
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* ドロップシャドウ追加 */
    }}
    
    /* メニュー名スタイル */
    .menu-name {{
        font-size: 22px;
        font-weight: 700; /* 太字 */
        color: #006dee; /* アクセントカラー青 */
        margin-top: 0; /* 上マージン削除 */
        margin-bottom: 4px; /* 下マージン少し追加 */
    }}
    
    /* 料金スタイル */
    .price {{
        font-size: 18px;
        font-weight: 700; /* 太字 */
        color: #006dee; /* アクセントカラー青 */
        margin-top: 2px; /* 上マージン詰める */
        margin-bottom: 2px; /* 下マージン詰める */
    }}
    
    /* 説明文スタイル */
    .description {{
        font-size: 16px;
        font-weight: 700; /* 太字 */
        color: #006dee; /* アクセントカラー青 */
        margin-top: 4px; /* 上マージン詰める */
        margin-bottom: 2px; /* 下マージン詰める */
    }}
    
    /* タグスタイル */
    .tags {{
        margin-top: 8px; /* 上マージン詰める */
        /* color: #7d2a14; */ /* 親要素の色指定は不要 */
    }}
    
    /* カード内区切り線 */
    hr.card-separator {{
        border: none;
        height: 1px;
        background-color: #eee; /* 薄いグレー */
        margin-top: 4px;
        margin-bottom: 4px;
    }}

    .tag {{
        background-color: #006dee; /* アクセントカラー青 */
        color: #fff; /* サブアクセント白 */
        padding: 5px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-right: 5px;
        font-size: 14px;
        font-weight: 700; /* 太字 */
    }}
    
    /* セパレーター */
    .separator {{
        border-top: 1px solid #006dee; /* アクセントカラー青 */
        margin: 30px 0;
    }}
    
    /* フッタースタイル */
    .footer {{
        text-align: center;
        margin-top: 50px;
        color: #006dee; /* アクセントカラー青 */
        font-size: 14px;
        font-weight: 700; /* 太字 */
    }}
    
    /* 金額表示スタイル */
    .price-summary {{
        max-width: 700px;
        margin: 10px auto !important;
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        background-color: #fff; /* サブアクセント白 */
        /* border: 1px solid #006dee; */ /* ボーダー削除 */
        border-radius: 16px; /* 角丸を大きく */
        padding: 18px; /* パディング調整 */
        margin: 10px 0; /* マージン調整 */
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* ドロップシャドウ追加 */
    }}
    
    /* スタンプ風透かし: */
    .stamp-watermark {{
        position: fixed;
        bottom: -100px;
        right: -100px;
        transform: rotate(-10deg);
        width: 400px;
        height: 400px;
        opacity: 0.05;
        z-index: 0;
        pointer-events: none;
    }}
    
    /* Made with Streamlitのフッター非表示 */
    footer {{
        visibility: hidden;
    }}

    .centered-icon img {{ /* ロゴサイズ調整 */
        width: 225px; /* 1.5倍 */
        height: 225px; /* 1.5倍 */
    }}
    h2 {{ /* h2見出しの調整 */
        font-size: 24px; /* 少し小さくする */
        word-break: keep-all; /* 単語の途中での改行を防ぐ */
        line-height: 1.4; /* 行間も少し調整 */
        font-weight: 700; /* 太字 */
    }}

    /* --- レスポンシブ対応 --- */
    @media (max-width: 600px) {{
        .passport-title {{
            font-size: 32px; /* 小さい画面用のフォントサイズ */
            letter-spacing: 1px; /* 文字間隔も少し詰める */
        }}
        .passport-en-title {{
            font-size: 16px; /* 英語タイトルも調整 */
        }}
        .passport-header {{
            padding: 20px 15px; /* ヘッダーのパディングも調整 */
            margin-top: -60px; /* 上マージン調整 */
        }}
         .centered-icon img {{ /* ロゴサイズ調整 (モバイル) */
            width: 225px; /* 1.5倍 */
            height: 225px; /* 1.5倍 */
        }}
        /* モバイル用のh2見出し調整 */
        h2 {{
            font-size: 20px !important;
            line-height: 1.2 !important;
            word-wrap: break-word !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# 透かし用のHTML
stamp_html = f"""
<div class="stamp-watermark">
    <img src="data:image/png;base64,{stamp_base64}" width="400" height="400" alt="スタンプ" />
</div>
"""

# ヘッダー部分
st.markdown(f"""
<div class="passport-header">
    <h1 class="passport-title">サ飯パスポート</h1>
    <div class="centered-icon">
        {logo_html}
    </div>
    <div class="passport-en-title">SAMESHI PASSPORT</div>
</div>
""", unsafe_allow_html=True)

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
        candidate_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
        st.session_state.selected_menus = get_random_menus_by_category(candidate_menus)
st.markdown('</div>', unsafe_allow_html=True)

# 結果表示
if st.session_state.selected_menus:
    lat = selected_sauna.get("latitude")
    lng = selected_sauna.get("longitude")

    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #006dee; text-align: center; margin-bottom: 20px;">サ飯ガチャ 結果</h2>', unsafe_allow_html=True)

    for menu in st.session_state.selected_menus:
        icon = category_icon.get(menu.get("category", "").lower(), "🍽️")
        tags_html = ''.join([f'<span class="tag">#{t}</span>' for t in get_tags_for_menu_item(menu['id'])])
        image_path = f"images/{menu.get('image_file', '')}"
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()
            # 画像スタイル変更: サイズ縮小、左寄せ、右マージン
            image_html = f'<img src="data:image/jpeg;base64,{encoded}" style="width:80px; height:80px; object-fit: cover; border-radius:12px; margin-right:15px; flex-shrink: 0;" />'
        else:
            image_html = ""
        
        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; align-items: flex-start;"> 
                {image_html} 
                <div style="flex: 1;">
                    <p class="menu-name">{menu['name']}</p>
                    <hr class="card-separator"> 
                    <p class="price">￥{menu['price']}</p>
                    <p class="description">{menu['description']}</p>
                    <div class="tags">{tags_html}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    raw_price = selected_sauna.get("entry_fee") or selected_sauna.get("entryfee") or selected_sauna.get("price", 0)
    try:
        sauna_fee = int(str(raw_price).replace(',', ''))
    except ValueError:
        sauna_fee = 0
    total_food_price = sum(menu['price'] for menu in st.session_state.selected_menus)
    total_price = sauna_fee + total_food_price

    st.markdown(f"""
    <div class="price-summary">
        <div style="flex: 1; margin-right: 20px;">
            <h3 style="color: #006dee; margin: 0 0 10px 0; font-weight: 700;">合計金額</h3>
            <p style="color: #006dee; font-size: 16px; font-weight: 700; margin: 0 0 5px 0;">サウナ入浴料: ￥{sauna_fee}</p>
            <p style="color: #006dee; font-size: 16px; font-weight: 700; margin: 0;">サウナ飯（{len(st.session_state.selected_menus)}品合計）: ￥{total_food_price}</p>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <p style="color: #006dee; font-size: 16px; font-weight: 700; margin: 0; line-height: 1;"></p>
            <p style="color: #006dee; font-size: 40px; font-weight: 700; margin: 0; line-height: 1;">￥{total_price}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # もう一度ボタンも中央配置
    st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
    if st.button("もう一度ガチャを回す"):
        all_menus = get_all_menu_items_for_sauna(st.session_state.selected_sauna_id)
        st.session_state.selected_menus = get_random_menus_by_category(all_menus)
    st.markdown('</div>', unsafe_allow_html=True)
    if lat and lng:
        nearby_foods = find_nearby_good_food(lat, lng)
        if nearby_foods:
            # 見出しのテキストを短くしてスタイルを調整
            st.markdown('<h2 style="color: #006dee; text-align: center; margin-bottom: 20px; font-size: 22px; word-wrap: break-word; word-break: keep-all; line-height: 1.3;">徒歩圏内の高評価なサ飯処</h2>', unsafe_allow_html=True)
            # Google Maps 埋め込み
            # キーワードごとの絵文字アイコンマップ
            icon_map = {
                "ラーメン": "🍜",
                "牛丼": "🍚",
                "カレー": "🍛",
                "ハンバーガー": "🍔"
            }
            
            # 各マーカー用の JS コード生成
            markers_js = f"""
              var saunaMarker = new google.maps.Marker({{
                  position: {{lat: {lat}, lng: {lng}}},
                  map: map,
                  icon: {{ url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" }},
                  title: "{selected_sauna_name}"
              }});
              saunaMarker.addListener('click', function() {{
                  window.open("https://www.google.com/maps/search/?api=1&query={lat},{lng}", "_blank");
              }});
            """
            for p in nearby_foods:
                icon = icon_map.get(p["keyword"], "")
                markers_js += f"""
              var marker = new google.maps.Marker({{
                  position: {{lat: {p['latitude']}, lng: {p['longitude']}}},
                  map: map,
                  label: {{ text: "{icon}", fontSize: "24px" }},
                  title: "{p['name']}"
              }});
              marker.addListener('click', function() {{
                  window.open("{p['maps_url']}", "_blank");
              }});
            """
              
            map_html = f'''
              <div id="map" style="height:450px; width:100%;"></div>
              <script src="https://maps.googleapis.com/maps/api/js?key={st.secrets['env']['GOOGLE_API_KEY']}&language=ja"></script>
              <script>
                function initMap() {{
                  var center = {{lat: {lat}, lng: {lng}}};
                  var map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 16,
                    center: center,
                    mapTypeControl: false,
                    styles: [
                        {{ stylers: [ {{ saturation: -100 }}, {{ lightness: 50 }} ] }}
                    ]
                  }});
                  {markers_js}
                }}
                google.maps.event.addDomListener(window, 'load', initMap);
              </script>
              '''
            components.html(map_html, height=480)
            
            # 距離が短い順にソート
            nearby_foods = sorted(nearby_foods, key=lambda x: x['distance'])
            for store in nearby_foods:
                stars = "⭐" * int(round(store['rating']))
                photo_base64 = get_photo_base64(store["photo_url"]) if store.get("photo_url") else None
                if photo_base64:
                    # 画像スタイル変更: サイズ縮小、左寄せ、右マージン
                    image_html = f'<img src="data:image/jpeg;base64,{photo_base64}" style="width:80px; height:80px; object-fit: cover; border-radius:12px; margin-right:15px; flex-shrink: 0;" />'
                else:
                    # プレースホルダーのスタイルも変更
                    image_html = '<div style="width:80px; height:80px; background:#eee; border-radius:12px; margin-right:15px; flex-shrink: 0;"></div>'
                st.markdown(f"""
<div class="result-card">
    <div style="display: flex; align-items: flex-start;"> 
        {image_html} 
        <div style="flex: 1;">
            <p class="menu-name">{store['name']}（{store['keyword']}）</p>
            <p class="price">評価: {store['rating']} {stars}</p>
            <p class="description">距離: 約{store['distance']}m</p>
            <a href="{store['maps_url']}" target="_blank" style="color:#006dee;">Googleマップで見る</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("😢 該当エリアに評価3.5以上のお店が見つかりませんでした。", unsafe_allow_html=True)

# フッター
st.markdown("""
<div class="footer">
    <p>このサイトは、有志により開発された非公式ファンサイトです。<br>メニューは実際の取扱と異なることがあります。</p>
</div>
""", unsafe_allow_html=True)

# スタンプ風の透かし配置
st.markdown(stamp_html, unsafe_allow_html=True)