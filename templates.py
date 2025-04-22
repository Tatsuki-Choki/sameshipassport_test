import base64
import os

def get_image_base64(image_path):
    """画像ファイルを読み込んでbase64エンコードした文字列を返す"""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def get_mobile_select_fix_js():
    """モバイル端末でセレクトボックスのキーボードを表示させないためのJavaScript"""
    return """
    <script>
    // モバイル端末かどうかを検出
    function isMobileDevice() {
        return (typeof window.orientation !== "undefined") || (navigator.userAgent.indexOf('IEMobile') !== -1);
    }
    
    // ドキュメントの読み込みが完了した後に実行
    document.addEventListener("DOMContentLoaded", function() {
        // 一定間隔で実行してDOMの変更を監視
        const interval = setInterval(function() {
            // セレクトボックスのテキスト入力要素を見つける
            const selectInputs = document.querySelectorAll('.stSelectbox input, div[role="combobox"] input');
            
            if (selectInputs.length > 0) {
                selectInputs.forEach(function(input) {
                    // readonlyとaria-readonlyを設定してテキスト入力を禁止
                    input.setAttribute('readonly', 'readonly');
                    input.setAttribute('aria-readonly', 'true');
                    
                    // モバイル端末の場合、追加の属性を設定
                    if (isMobileDevice()) {
                        // キーボードを表示させない
                        input.setAttribute('inputmode', 'none');
                        
                        // フォーカス時のイベント
                        input.addEventListener('focus', function(e) {
                            // フォーカスを外して再度当てる（キーボード表示を防止）
                            input.blur();
                            setTimeout(function() {
                                input.focus();
                            }, 10);
                        });
                    }
                });
                
                // セレクトボックスが見つかったらintervalを解除
                // clearInterval(interval);
            }
        }, 500); // 500msごとに実行
    });
    </script>
    """

def get_header_html(logo_html):
    """ヘッダー部分のHTMLを返す"""
    # applogo.pngをbase64エンコード
    app_logo_base64 = get_image_base64("images/applogo.png")
    app_logo_html = f'<img src="data:image/png;base64,{app_logo_base64}" alt="サ飯パスポート" style="max-width:50%; height:auto;" />'
    
    return f"""
    <div class="passport-header">
        <div class="passport-title" style="margin-bottom:0px;">{app_logo_html}</div>
        <div class="centered-icon" style="margin-bottom:0px;">
            {logo_html}
        </div>
        <div class="passport-en-title">SAMESHI PASSPORT</div>
    </div>
    """

def get_stamp_watermark_html(stamp_base64):
    """透かし用のHTML"""
    return f"""
    <div class="stamp-watermark">
        <img src="data:image/png;base64,{stamp_base64}" width="400" height="400" alt="スタンプ" />
    </div>
    """

def get_menu_card_html(menu, tags_html, image_html=""):
    """メニューカードのHTML"""
    return f"""
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
    """

def get_price_summary_html(sauna_fee, total_food_price, total_price, menu_count):
    """価格サマリーのHTML"""
    return f"""
    <div class="price-summary">
        <div style="flex: 1; margin-right: 20px;">
            <h3 style="color: #006dee; margin: 0 0 10px 0; font-weight: 700;">合計金額</h3>
            <p style="color: #006dee; font-size: 16px; font-weight: 700; margin: 0 0 5px 0;">サウナ入浴料: ￥{sauna_fee}</p>
            <p style="color: #006dee; font-size: 16px; font-weight: 700; margin: 0;">サウナ飯（{menu_count}品合計）: ￥{total_food_price}</p>
        </div>
        <div style="display: flex; flex-direction: column; align-items: flex-start;">
            <p style="color: #006dee; font-size: 16px; font-weight: 700; margin: 0; line-height: 1;"></p>
            <p style="color: #006dee; font-size: 40px; font-weight: 700; margin: 0; line-height: 1;">￥{total_price}</p>
        </div>
    </div>
    """

def get_maps_html(lat, lng, markers_js, api_key):
    """Google Maps埋め込みHTML"""
    return f'''
    <div id="map" style="height:450px; width:100%;"></div>
    <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&language=ja"></script>
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

def get_store_card_html(store, image_html, stars, distance_text):
    """店舗カードのHTML"""
    return f"""
    <div class="result-card">
        <div style="display: flex; align-items: flex-start;"> 
            {image_html} 
            <div style="flex: 1;">
                <p class="menu-name">{store['name']}（{store['keyword']}）</p>
                <p class="price">評価: {store['rating']} {stars}</p>
                <p class="description">{distance_text}</p>
                <a href="{store['maps_url']}" target="_blank" style="color:#006dee;">Googleマップで見る</a>
            </div>
        </div>
    </div>
    """

def get_markers_js(lat, lng, sauna_name, nearby_foods, icon_map):
    """GoogleマップマーカーのJavaScript"""
    markers_js = f"""
    var saunaMarker = new google.maps.Marker({{
        position: {{lat: {lat}, lng: {lng}}},
        map: map,
        icon: {{ url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png" }},
        title: "{sauna_name}"
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
    
    return markers_js

def get_footer_html():
    """フッターのHTML"""
    return """
    <div class="footer">
        <p>このサイトは、有志により開発された非公式ファンサイトです。<br>メニューは実際の取扱と異なることがあります。</p>
    </div>
    """ 