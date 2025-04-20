CUSTOM_CSS = """
<style>
    /* 全体のベースカラーとフォントをbodyおよびコンテナに適用 */
    body, .reportview-container, .stApp, .main {
        background-color: #f7e93f; /* ベースカラー黄色 */
        /* background-image: url("https://s.mj.run/qmlyfG-PEwY"); */ /* 背景画像削除 */
        /* background-repeat: repeat; */
        color: #006dee; /* アクセントカラー青をデフォルトテキスト色に */
        font-family: 'Noto Sans JP', sans-serif; /* 日本語フォント指定 */
        font-weight: 700; /* 全体のフォントウェイトを太めに */
        overflow-x: hidden; /* 横スクロールを禁止 */
    }

    /* .mainからは色とフォント指定を削除 */
    .main {
        /* background-color: #1e1e2d; */
        /* color: #e8d0a9; */
        /* font-family: 'Noto Sans JP', sans-serif; */
        padding: 0;
        max-width: 100%;
        /* overflow-x: hidden; */ /* bodyに移動 */
        box-sizing: border-box; /* padding/borderを幅に含める */
    }
    
    /* ヘッダー部分: アクセントカラー */
    .passport-header {
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
    }
    
    /* タイトル(日本語) */
    .passport-title {
        /* font-family: "Hiragino Mincho ProN", "Times New Roman", serif; */
        font-family: 'Noto Sans JP', serif; /* 日本語フォント指定 */
        font-size: 42px;
        font-weight: 700; /* 太字 */
        margin-bottom: 20px;
        letter-spacing: 2px;
        color: #f7e93f; /* ベースカラー黄色に変更 */
    }
    
    /* SAMESHI PASSPORT: 英語タイトル */
    .passport-en-title {
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
    }
    
    /* ロゴセンタリング */
    .centered-icon {
        display: block;
        margin: 0 auto 20px auto;
        text-align: center;
    }
    
    /* セレクトボックスのラベル */
    .selection-label {
        font-size: 20px;
        margin-bottom: 10px;
        color: #006dee; /* アクセントカラー青 */
        font-weight: 700; /* 太字 */
    }

    /* セレクトボックス */
    .stSelectbox > div > div {
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
    }

    /* ボタン */
    .stButton > button {
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
    }
    .stButton > button:hover {
        background-color: #0056b3 !important; /* 少し暗い青 */
        box-shadow: 0 0 8px rgba(0, 109, 238, 0.3); /* 影の色調整 */
    }
    
    /* カード全体のスタイル */
    .result-card {
        background-color: #fff; /* サブアクセント白 */
        /* border: 1px solid #006dee; */ /* ボーダー削除 */
        border-radius: 16px; /* 角丸を大きく */
        padding: 18px; /* 20pxから15pxに変更 */
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* ドロップシャドウ追加 */
    }
    
    /* メニュー名スタイル */
    .menu-name {
        font-size: 22px;
        font-weight: 700; /* 太字 */
        color: #006dee; /* アクセントカラー青 */
        margin-top: 0; /* 上マージン削除 */
        margin-bottom: 4px; /* 下マージン少し追加 */
    }
    
    /* 料金スタイル */
    .price {
        font-size: 18px;
        font-weight: 700; /* 太字 */
        color: #006dee; /* アクセントカラー青 */
        margin-top: 2px; /* 上マージン詰める */
        margin-bottom: 2px; /* 下マージン詰める */
    }
    
    /* 説明文スタイル */
    .description {
        font-size: 16px;
        font-weight: 700; /* 太字 */
        color: #006dee; /* アクセントカラー青 */
        margin-top: 4px; /* 上マージン詰める */
        margin-bottom: 2px; /* 下マージン詰める */
    }
    
    /* タグスタイル */
    .tags {
        margin-top: 8px; /* 上マージン詰める */
        /* color: #7d2a14; */ /* 親要素の色指定は不要 */
    }
    
    /* カード内区切り線 */
    hr.card-separator {
        border: none;
        height: 1px;
        background-color: #eee; /* 薄いグレー */
        margin-top: 4px;
        margin-bottom: 4px;
    }

    .tag {
        background-color: #006dee; /* アクセントカラー青 */
        color: #fff; /* サブアクセント白 */
        padding: 5px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-right: 5px;
        font-size: 14px;
        font-weight: 700; /* 太字 */
    }
    
    /* セパレーター */
    .separator {
        border-top: 1px solid #006dee; /* アクセントカラー青 */
        margin: 30px 0;
    }
    
    /* フッタースタイル */
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #006dee; /* アクセントカラー青 */
        font-size: 14px;
        font-weight: 700; /* 太字 */
    }
    
    /* 金額表示スタイル */
    .price-summary {
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
    }
    
    /* スタンプ風透かし: */
    .stamp-watermark {
        position: fixed;
        bottom: -100px;
        right: -100px;
        transform: rotate(-10deg);
        width: 400px;
        height: 400px;
        opacity: 0.05;
        z-index: 0;
        pointer-events: none;
    }
    
    /* Made with Streamlitのフッター非表示 */
    footer {
        visibility: hidden;
    }

    .centered-icon img { /* ロゴサイズ調整 */
        width: 225px; /* 1.5倍 */
        height: 225px; /* 1.5倍 */
    }
    h2 { /* h2見出しの調整 */
        font-size: 24px; /* 少し小さくする */
        word-break: keep-all; /* 単語の途中での改行を防ぐ */
        line-height: 1.4; /* 行間も少し調整 */
        font-weight: 700; /* 太字 */
    }

    /* --- レスポンシブ対応 --- */
    @media (max-width: 600px) {
        .passport-title {
            font-size: 32px; /* 小さい画面用のフォントサイズ */
            letter-spacing: 1px; /* 文字間隔も少し詰める */
        }
        .passport-en-title {
            font-size: 16px; /* 英語タイトルも調整 */
        }
        .passport-header {
            padding: 20px 15px; /* ヘッダーのパディングも調整 */
            margin-top: -60px; /* 上マージン調整 */
        }
         .centered-icon img { /* ロゴサイズ調整 (モバイル) */
            width: 225px; /* 1.5倍 */
            height: 225px; /* 1.5倍 */
        }
        /* モバイル用のh2見出し調整 */
        h2 {
            font-size: 20px !important;
            line-height: 1.2 !important;
            word-wrap: break-word !important;
        }
    }
      /* タイトルロゴセンタリング */
      .centered-title-logo {
          text-align: center;
          margin-bottom: 0px;
      }
</style>
""" 