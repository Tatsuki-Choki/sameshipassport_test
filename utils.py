import math
import random
import requests
import base64
from typing import List, Dict
import googlemaps
import streamlit as st
import os

# gmaps クライアントの初期化 (sameshipassport.py から移動)
gmaps = googlemaps.Client(key=st.secrets["env"]["GOOGLE_API_KEY"])

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
        # gmaps はこのファイル内で初期化されたものを使用
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
                # st.secrets を使用
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={st.secrets['env']['GOOGLE_API_KEY']}" if photo_ref else None

                found_places.append({
                    "name": name,
                    "rating": rating,
                    "keyword": keyword,
                    "latitude": place_lat,
                    "longitude": place_lng,
                    "maps_url": f"https://www.google.com/maps/search/?api=1&query={place_lat},{place_lng}",
                    "photo_url": photo_url
                })
    return found_places

def get_restaurants_by_sauna(restaurants: List[Dict], sauna_id: int) -> List[Dict]:
    return [r for r in restaurants if r["sauna_id"] == sauna_id]

def get_menu_items_by_restaurant(menu_items: List[Dict], restaurant_id: int) -> List[Dict]:
    return [m for m in menu_items if m["restaurant_id"] == restaurant_id]

def get_tags_for_menu_item(menu_item_tags: List[Dict], tags: List[Dict], menu_item_id: int) -> List[str]:
    tag_ids = [t["tag_id"] for t in menu_item_tags if t.get("menuitemid") == menu_item_id]
    return [t["name"] for t in tags if t["id"] in tag_ids]

def get_all_menu_items_for_sauna(restaurants: List[Dict], menu_items: List[Dict], sauna_id: int) -> List[Dict]:
    all_menus = []
    # get_restaurants_by_sauna と get_menu_items_by_restaurant を呼び出す
    for rest in get_restaurants_by_sauna(restaurants, sauna_id):
        all_menus.extend(get_menu_items_by_restaurant(menu_items, rest["id"]))
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

def get_photo_base64(photo_url):
    if not photo_url:
        return None
    try:
        response = requests.get(photo_url, timeout=10) # タイムアウトを追加
        response.raise_for_status() # ステータスコードチェック
        if response.status_code == 200:
            return base64.b64encode(response.content).decode()
    except requests.exceptions.RequestException as e:
        st.error(f"写真の取得に失敗しました: {e}") # エラーログ
        return None
    return None

# アイコン画像をbase64エンコードする関数 (sameshipassport.pyの地図部分で使用)
def get_icon_data(entry, icon_map: Dict[str, str], default_icon_url: str) -> Dict:
    icon_path_or_url = icon_map.get(entry['type'], default_icon_url)
    # ローカルファイルパスかどうかを判定 (簡易的な判定)
    if icon_path_or_url.startswith("images/") and os.path.exists(icon_path_or_url):
        try:
            with open(icon_path_or_url, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            return {
                "url": f"data:image/png;base64,{image_data}",
                "width": 40,
                "height": 40,
                "anchorY": 40
            }
        except Exception as e:
            st.warning(f"アイコンファイル読み込みエラー ({icon_path_or_url}): {e}")
            # エラー時はデフォルトURLを使用
            return {
                "url": default_icon_url,
                "width": 40,
                "height": 40,
                "anchorY": 40
            }
    else: # URLの場合 or ファイルが存在しない場合
        return {
            "url": icon_path_or_url, # そのままURLを使用 (デフォルトURLの場合も含む)
            "width": 40,
            "height": 40,
            "anchorY": 40
        } 