import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import matplotlib as mpl
import matplotlib.font_manager as fm

# =========================================
# SunRockers Shibuyaテーマカラー（黒、黄色、紫）に基づいたデザイン
# 背景を白に戻す
# =========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&family=Noto+Sans+JP:wght@300;400;500;600;700;800;900&display=swap');

/* SunRockers Shibuyaカラーパレット - ライトテーマ版 */
:root {
    --main-bg: #FFFFFF;  /* 白背景 */
    --secondary-bg: #F8F8F8;
    --text-color: #333333;
    --text-muted: #666666;
    --border: #E0E0E0;
    
    /* チームカラー */
    --sr-black: #000000;
    --sr-yellow: #FFD700;
    --sr-purple: #8A56AC;
    
    /* アクセントカラー */
    --sr-dark-purple: #4B0082;
    --sr-light-yellow: #FFF8E1;
    --sr-gray: #DDDDDD;
    --sr-light-gray: #F0F0F0;
    --section-text: #FFFFFF;  /* セクションヘッダーのテキスト色 */
}

/* 全体のベーススタイル - 背景を白に */
body {
    background-color: var(--main-bg) !important;
    color: var(--text-color) !important;
    font-family: "Montserrat", "Noto Sans JP", sans-serif !important;
    font-weight: 400 !important;
}

/* メインコンテナスタイリング */
.reportview-container, .main, .block-container {
    background-color: var(--main-bg) !important;
    padding: 0 !important;
    max-width: 1200px !important;
}

/* サイドバースタイリング */
.sidebar .sidebar-content {
    background-color: var(--sr-purple) !important;
    color: white !important;
    border-right: none !important;
}

.sidebar .sidebar-content .stTextInput label {
    color: white !important;
}

/* スタイリッシュなヘッダー */
h1 {
    color: var(--text-color) !important;
    font-weight: 700 !important;
    text-align: center !important;
    font-size: 2.2rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-bottom: 1.5rem !important;
    padding: 1rem !important;
}

h2, h3, h4, h5, h6 {
    color: var(--text-color) !important;
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
    letter-spacing: 1px !important;
}

/* テキスト入力フィールド */
.stTextInput > div > div > input {
    background-color: var(--main-bg) !important;
    color: var(--text-color) !important;
    border: 2px solid var(--sr-purple) !important;
    border-radius: 4px !important;
    padding: 10px !important;
    font-family: "Montserrat", "Noto Sans JP", sans-serif !important;
    font-weight: 500 !important;
}

.stTextInput > div > div > input:focus {
    border: 2px solid var(--sr-yellow) !important;
    box-shadow: 0 0 5px rgba(255, 215, 0, 0.3) !important;
}

/* Streamlitデフォルトラベルの色を変更 */
.stTextInput > div > label {
    color: var(--text-color) !important;
}

/* ボタンスタイリング */
.stButton > button {
    background-color: var(--sr-purple) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

.stButton > button:hover {
    background-color: var(--sr-dark-purple) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(138, 86, 172, 0.3) !important;
}

/* テーブルスタイリング */
.dataframe {
    background-color: var(--main-bg) !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    margin: 1rem 0 !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
    width: 100% !important;
}

.dataframe th {
    background-color: var(--sr-purple) !important;
    color: white !important;
    padding: 14px 15px !important;
    text-align: center !important;
    font-weight: 600 !important;
    border: none !important;
    letter-spacing: 1px !important;
    font-size: 0.9rem !important;
}

.dataframe td {
    background-color: var(--main-bg) !important;
    color: var(--text-color) !important;
    padding: 12px 15px !important;
    border-top: 1px solid var(--border) !important;
    text-align: center !important;
    font-size: 0.9rem !important;
}

/* 偶数行に薄い背景色を適用 */
.dataframe tr:nth-child(even) td {
    background-color: var(--secondary-bg) !important;
}

/* アラートとインフォメッセージ */
.stAlert {
    background-color: #FFF8E1 !important;
    border-left: 3px solid var(--sr-yellow) !important;
    padding: 1rem !important;
    border-radius: 4px !important;
}

/* グラフコンテナ */
.stPlotly, .stPlot {
    background-color: var(--main-bg) !important;
    border-radius: 6px !important;
    padding: 0 !important;
    margin: 0.5rem 0 1.5rem 0 !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
    width: 100% !important;
}

/* アプリタイトルエリア */
.title-container {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 35px;
  background: linear-gradient(135deg, #8A56AC 0%, #000000 100%);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  position: relative;
}

/* タイトルテキスト - 白色で強い影を追加 */
.title-text {
  margin: 0;
  font-size: 4.5rem;
  color: #FFFFFF;
  letter-spacing: 5px;
  font-weight: 900;
  text-transform: uppercase;
  text-shadow: 2px 2px 0px #FFD700, 
               4px 4px 0px rgba(0, 0, 0, 0.7),
               0px 0px 15px rgba(0, 0, 0, 0.9);
  position: relative;
  z-index: 2;
  display: inline-block;
  padding: 0 10px;
}

.title-line {
  width: 150px;
  height: 5px;
  background: linear-gradient(90deg, #FFD700, #FFFFFF);
  margin: 24px auto;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
}

.subtitle-text {
  color: white;
  font-size: 1.5rem;
  margin-top: 15px;
  margin-bottom: 0;
  letter-spacing: 4px;
  font-weight: 600;
  text-transform: uppercase;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.9);
}

/* 装飾要素を強化 */
.circle-decoration-1 {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 100px;
  height: 100px;
  background: rgba(255, 215, 0, 0.15);
  border-radius: 50%;
  filter: blur(2px);
}

.circle-decoration-2 {
  position: absolute;
  bottom: -30px;
  left: -30px;
  width: 150px;
  height: 150px;
  background: rgba(255, 215, 0, 0.1);
  border-radius: 50%;
  filter: blur(2px);
}

/* 背景の輝き効果 */
.title-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 60%;
  background: radial-gradient(circle, rgba(255,215,0,0.15) 0%, rgba(255,215,0,0) 70%);
  z-index: 1;
}

/* データセクション */
.data-section {
    background-color: var(--main-bg) !important;
    border-radius: 6px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
}

/* スクロールバーのカスタマイズ */
::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
}

::-webkit-scrollbar-track {
    background: var(--sr-light-gray) !important;
}

::-webkit-scrollbar-thumb {
    background: var(--sr-purple) !important;
    border-radius: 3px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--sr-dark-purple) !important;
}

/* コンテナの幅を最大化 */
.css-1d391kg, .css-12oz5g7 {
    max-width: 1200px !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* グラフセクション間のマージンを減らす */
.stplot > div > div {
    margin-bottom: 0 !important;
}

/* メトリクス表示のカスタマイズ */
.metric-card {
    padding: 12px 15px !important;
    background-color: var(--secondary-bg) !important;
    margin-bottom: 10px !important;
    border-radius: 6px !important;
    border-left: 3px solid var(--sr-purple) !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
}

.metric-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
}

/* セクションヘッダー */
.section-header {
    background: linear-gradient(90deg, var(--sr-purple) 0%, var(--sr-black) 100%) !important;
    padding: 15px !important;
    border-radius: 6px 6px 0 0 !important;
    margin-top: 30px !important;
}

.section-header h3 {
    color: white !important;
    margin: 0 !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 1.1rem !important;
}

/* コンテンツカードのスタイル改善 */
.content-card {
    background-color: var(--main-bg) !important;
    border-radius: 6px !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
    margin: 15px 0 !important;
    overflow: hidden !important;
}

/* テーブルコンテナの背景を暗めに */
.stTable {
    background-color: var(--main-bg) !important;
    border-radius: 6px !important;
    padding: 0 !important;
    overflow: hidden !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
}

/* 紫背景の文字はすべて白に */
.purple-gradient-bg {
    background: linear-gradient(90deg, #8A56AC 0%, #000000 100%);
    padding: 15px;
    border-radius: 6px;
    color: white !important;
}

.purple-gradient-bg h1, 
.purple-gradient-bg h2, 
.purple-gradient-bg h3, 
.purple-gradient-bg h4, 
.purple-gradient-bg h5, 
.purple-gradient-bg h6, 
.purple-gradient-bg p, 
.purple-gradient-bg span, 
.purple-gradient-bg a {
    color: white !important;
}

/* ライトモード用のグラフコンテナ背景 */
.chart-container {
    background-color: var(--main-bg) !important;
    border-radius: 0 0 6px 6px !important;
    padding: 15px !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1) !important;
}

/* メトリクスカードのライトモード対応 */
.light-metric-card {
    padding: 12px 15px; 
    background-color: #FFFFFF; 
    margin-bottom: 10px; 
    border-radius: 6px; 
    border-left: 3px solid #8A56AC; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

/* 特に重要なメトリクスをハイライト */
.highlight-metric {
    border-left: 3px solid #FFD700 !important;
    background-color: rgba(255, 215, 0, 0.1) !important;
}

/* カテゴリーセクションスタイル */
.category-section {
    margin-top: 20px;
    margin-bottom: 30px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.category-header {
    background: linear-gradient(90deg, #8A56AC 20%, #333333 100%);
    color: white;
    padding: 12px 18px;
    font-weight: 600;
    letter-spacing: 1px;
    font-size: 1.1rem;
    text-transform: uppercase;
    display: flex;
    align-items: center;
}

.category-header i {
    margin-right: 10px;
    font-size: 1.2rem;
}

.category-content {
    padding: 15px;
    background-color: white;
}

/* アコーディオンスタイル */
.accordion {
    margin-bottom: 15px;
}

.accordion-header {
    background-color: #F3F3F3;
    padding: 10px 15px;
    cursor: pointer;
    border-radius: 4px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background-color 0.3s;
}

.accordion-header:hover {
    background-color: #EAEAEA;
}

.accordion-content {
    padding: 15px;
    border: 1px solid #EAEAEA;
    border-top: none;
    border-radius: 0 0 4px 4px;
}
</style>
""", unsafe_allow_html=True)

# タイトルコンテナをレンダリング - 強化されたタイトルスタイル
st.markdown("""
<div class="title-container">
  <div class="circle-decoration-1"></div>
  <div class="circle-decoration-2"></div>
  <div class="title-glow"></div>
  <h1 class="title-text">SUNROCKERS SHIBUYA</h1>
  <div class="title-line"></div>
  <p class="subtitle-text">PHYSICAL DATA TRACKER</p>
</div>
""", unsafe_allow_html=True)

# 日本語フォント設定を改善
def setup_japanese_fonts():
    """日本語フォント設定"""
    # 利用可能なフォントを確認
    fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 日本語フォント優先順位
    jp_fonts = ['Noto Sans JP', 'Hiragino Sans', 'Meiryo', 'Yu Gothic', 'MS Gothic']
    
    # 利用可能な日本語フォントを探す
    available_jp_fonts = [f for f in jp_fonts if f in fonts]
    
    if available_jp_fonts:
        # 利用可能な最初の日本語フォントを使用
        jp_font = available_jp_fonts[0]
    else:
        # 日本語フォントが見つからない場合はデフォルト
        jp_font = 'sans-serif'
    
    # フォント設定
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = [jp_font, 'sans-serif']
    
    # 文字化け防止の設定
    mpl.rcParams['axes.unicode_minus'] = False
    
    return jp_font

# カスタムデザイン関数 - SunRockersテーマカラーを反映 (ライトモード対応)
def set_matplotlib_style(jp_font):
    """Matplotlibのグラフスタイルを設定 - SunRockersテーマカラー対応 (ライトモード)"""
    # ライトモードのデフォルトスタイルに設定
    plt.style.use('default')
    
    # SunRockersカラーパレット
    sr_black = '#000000'
    sr_yellow = '#FFD700'
    sr_purple = '#8A56AC'
    sr_bg = '#FFFFFF'
    
    mpl.rcParams['axes.facecolor'] = sr_bg
    mpl.rcParams['figure.facecolor'] = sr_bg
    mpl.rcParams['grid.color'] = '#E0E0E0'
    mpl.rcParams['grid.linestyle'] = '-'
    mpl.rcParams['grid.alpha'] = 0.5
    
    # 軸とラベルのスタイル
    mpl.rcParams['xtick.color'] = '#333333'
    mpl.rcParams['ytick.color'] = '#333333'
    mpl.rcParams['axes.labelcolor'] = '#333333'
    mpl.rcParams['axes.edgecolor'] = '#CCCCCC'
    mpl.rcParams['axes.grid'] = True
    
    # タイトルスタイル
    mpl.rcParams['axes.titlesize'] = 14
    mpl.rcParams['axes.titleweight'] = 'bold'
    mpl.rcParams['axes.titlecolor'] = '#333333'
    
    # フォント設定
    mpl.rcParams['font.family'] = ['sans-serif']
    mpl.rcParams['font.sans-serif'] = [jp_font, 'sans-serif']
    mpl.rcParams['font.weight'] = 'medium'
    
    # 凡例スタイル
    mpl.rcParams['legend.frameon'] = True
    mpl.rcParams['legend.facecolor'] = '#FFFFFF'
    mpl.rcParams['legend.edgecolor'] = '#CCCCCC'
    mpl.rcParams['legend.framealpha'] = 0.9
    mpl.rcParams['legend.fontsize'] = 10

# 日本語フォント設定を適用
jp_font = setup_japanese_fonts()

# Matplotlibスタイル設定
set_matplotlib_style(jp_font)

# CSVファイルを読み込む
try:
    df = pd.read_csv("data.csv", encoding="utf-8")
    df.columns = df.columns.str.strip()
    
    # 体脂肪量(kg)をFat mass(kg)に列名変更
    if "体脂肪量(kg)" in df.columns:
        df = df.rename(columns={"体脂肪量(kg)": "Fat mass(kg)"})
    
    # 目標値を含む行を抽出（1行目 = インデックス0）
    if len(df) > 0:
        target_values = df.iloc[0].copy()
    
    # 数値カラムを明示的に数値型に変換
    numeric_columns = [
        "5m Sprint(s)", "10m Sprint(s)", "20m Sprint(s)", "20m Multh", "20m Multi",
        "Sprint Momentum", "BW*スコア", "BW*20m Multi", "BSQ", "BP", "CMJ", "Pro Agility",
        "Weight", "Fat mass(kg)", "BMI", "LBM/m", "CODD"
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # 無効な値はNaNに変換
            
except Exception as e:
    st.error(f"データの読み込みエラー: {e}")
    st.stop()

# サイドバーを紫背景に設定
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        width: 18rem !important;
        background-color: #8A56AC !important;
        color: white !important;
        border-right: none !important;
    }
    
    section[data-testid="stSidebar"] .stTextInput label {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] p {
        color: white !important;
    }
    
    @media (max-width: 1000px) {
        section[data-testid="stSidebar"] {
            width: 12rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 名前入力セクション - 紫背景に白文字のクラスを適用
st.markdown("""
<div class="purple-gradient-bg" style="margin-bottom: 25px; border-radius: 6px; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);">
    <h3 style="margin: 0 0 15px 0; letter-spacing: 1px; font-weight: 600; text-transform: uppercase;">Player Data Search</h3>
</div>
""", unsafe_allow_html=True)

name = st.text_input("Enter player name:")

if name:
    user_data = df[df["名前"] == name]
    if not user_data.empty:
        # 測定日を日付型に変換
        user_data["測定日"] = pd.to_datetime(
            user_data["測定日"].astype(str).str.strip(), errors="coerce"
        )
        user_data = user_data.sort_values("測定日")
        
        # 選手情報表示セクション - 紫背景に白文字のクラスを適用
        st.markdown(f"""
        <div class="purple-gradient-bg" style="padding: 25px; border-radius: 6px; margin: 25px 0; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);">
            <h2 style="margin: 0; letter-spacing: 2px; font-weight: 700; text-transform: uppercase;">{name}</h2>
            <p style="margin: 10px 0 0 0; font-weight: 500; letter-spacing: 1px;">Data Period: {user_data['測定日'].min().strftime('%Y/%m/%d')} - {user_data['測定日'].max().strftime('%Y/%m/%d')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 2カラムレイアウトを使用してスペースを効率よく使う
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # ==========
            # データサマリーテーブル（最新・平均・最大値）
            # 新しい変数（Weight, Fat mass(kg), LBM/m, BMI, CODD, 20m Multh, BW*20m Multh）も追加
            # ==========
            columns_of_interest = [
                "Sprint Momentum", "BW*スコア", "LBM/m", "BW*20m Multi",
                "5m Sprint(s)", "10m Sprint(s)", "20m Sprint(s)",
                "BSQ", "BP", "CMJ", "Pro Agility", "CODD", "20m Multh", "20m Multi",
                "Weight", "Fat mass(kg)", "BMI"
            ]
            summary = {"Metric": [], "Latest": [], "Average": [], "Max": []}
            for col in columns_of_interest:
                if col in user_data.columns:
                    series = user_data[col]
                    summary["Metric"].append(col)
                    
                    # 最新値を安全に取得
                    latest = series.dropna().iloc[-1] if not series.dropna().empty else None
                    if latest is not None and not pd.isna(latest):
                        try:
                            summary["Latest"].append(round(float(latest), 2))
                        except (ValueError, TypeError):
                            summary["Latest"].append(latest)  # 変換できない場合はそのまま使用
                    else:
                        summary["Latest"].append(None)
                    
                    # 平均値を安全に取得
                    mean_val = series.mean()
                    if not pd.isna(mean_val):
                        try:
                            summary["Average"].append(round(float(mean_val), 2))
                        except (ValueError, TypeError):
                            summary["Average"].append(mean_val)
                    else:
                        summary["Average"].append(None)
                    
                    # 最大値を安全に取得
                    max_val = series.max() 
                    if not pd.isna(max_val):
                        try:
                            summary["Max"].append(round(float(max_val), 2))
                        except (ValueError, TypeError):
                            summary["Max"].append(max_val)
                    else:
                        summary["Max"].append(None)
            
            # サマリーテーブル表示前のヘッダー - 紫背景に白文字のクラスを適用
            st.markdown("""
            <div class="purple-gradient-bg" style="border-radius: 6px 6px 0 0; margin-top: 15px; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);">
                <h3 style="margin: 0; letter-spacing: 1px; font-weight: 600; text-transform: uppercase;">Physical Data Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # サマリーテーブル表示 - ライトモード対応
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.table(pd.DataFrame(summary))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # グラフセクションヘッダー - 紫背景に白文字のクラスを適用
            st.markdown("""
            <div class="purple-gradient-bg" style="border-radius: 6px 6px 0 0; margin-top: 15px; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);">
                <h3 style="margin: 0; letter-spacing: 1px; font-weight: 600; text-transform: uppercase;">Latest Metrics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # メトリクス表示のコンテナ - ライトモード対応
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # 最新のデータを取得
            latest_data = user_data.iloc[-1]
            
            # 最新のデータがある項目のみ表示
            metrics_to_show = {}
            for col in columns_of_interest:
                if col in latest_data and not pd.isna(latest_data[col]):
                    # 数値型かどうかをチェックして安全に変換
                    try:
                        metrics_to_show[col] = round(float(latest_data[col]), 2)
                    except (ValueError, TypeError):
                        metrics_to_show[col] = latest_data[col]  # 数値変換できない場合はそのまま
            
            # 重要なメトリクスを先に表示
            important_metrics = ["Sprint Momentum", "BW*スコア", "LBM/m"]
            
            # メトリクス表示 - 重要なメトリクスを先に表示してハイライト
            for label in important_metrics:
                if label in metrics_to_show:
                    value = metrics_to_show[label]
                    # スプリント系は下向き矢印（低いほど良い）、その他は上向き（高いほど良い）
                    icon = "↓" if "Sprint(s)" in label or label == "Pro Agility" else "↑"
                    
                    # メトリクスカードのアイコン色を設定
                    icon_color = "#FFD700"  # 黄色（向上を示す）
                    
                    st.markdown(f"""
                    <div class="light-metric-card highlight-metric">
                        <span style="font-weight: 500; color: #333333; letter-spacing: 0.5px;">{label}</span>
                        <span style="font-weight: 600; color: #333333; display: flex; align-items: center;">
                            <span>{value}</span>
                            <span style="color: {icon_color}; margin-left: 5px; font-size: 18px;">{icon}</span>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # その他のメトリクスを表示
            for label, value in metrics_to_show.items():
                if label not in important_metrics:
                    # スプリント系は下向き矢印（低いほど良い）、その他は上向き（高いほど良い）
                    icon = "↓" if "Sprint(s)" in label or label == "Pro Agility" else "↑"
                    
                    # メトリクスカードのアイコン色を設定
                    icon_color = "#8A56AC"  # 紫（通常指標）
                    
                    st.markdown(f"""
                    <div class="light-metric-card">
                        <span style="font-weight: 500; color: #333333; letter-spacing: 0.5px;">{label}</span>
                        <span style="font-weight: 600; color: #333333; display: flex; align-items: center;">
                            <span>{value}</span>
                            <span style="color: {icon_color}; margin-left: 5px; font-size: 18px;">{icon}</span>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ==========
        # 個別グラフ描画関数 - SunRockersカラーバージョン (ライトモード対応)
        # 目標値の表示機能を追加
        # ==========
        def plot_improved_graph(label, color="#8A56AC", marker="o", highlight=False):
            data = user_data[["測定日", label]].dropna()
            if data.empty:
                st.warning(f"No data available for {label}.")
                return
            
            # データが1つ以上あることを確認
            if len(data) > 0:
                # 重要なメトリクスは少し大きめのグラフサイズに
                figsize = (10, 4.5) if highlight else (10, 4)
                fig, ax = plt.subplots(figsize=figsize)
                
                # データプロット - すべてのグラフのライン色を紫色に統一
                ax.plot(
                    data["測定日"], data[label],
                    marker=marker, linestyle="-" if len(data) > 1 else "None",
                    color="#8A56AC", linewidth=2.5, markersize=8  # 色を#8A56ACに統一
                )
                
                # 改善点/悪化点をハイライト
                if len(data) > 1:
                    # データの変化率を計算
                    changes = data[label].pct_change()
                    for i in range(1, len(data)):
                        if not np.isnan(changes.iloc[i]):
                            # スプリントやPro Agilityは減少が改善、その他は増加が改善
                            is_time_based = "Sprint(s)" in label or label == "Pro Agility"
                            is_decreasing_good = is_time_based or label == "Fat mass(kg)"  # Fat mass(kg)も減少が改善
                            # 20m Multhは回数なので増加が改善
                            
                            if (is_decreasing_good and changes.iloc[i] < -0.05) or (not is_decreasing_good and changes.iloc[i] > 0.05):
                                ax.scatter(
                                    data["測定日"].iloc[i], data[label].iloc[i],
                                    color='#FFD700', s=120, alpha=0.8, zorder=10  # 改善は黄色
                                )
                            elif (is_decreasing_good and changes.iloc[i] > 0.05) or (not is_decreasing_good and changes.iloc[i] < -0.05):
                                ax.scatter(
                                    data["測定日"].iloc[i], data[label].iloc[i],
                                    color='#FF4500', s=120, alpha=0.8, zorder=10  # 悪化は赤
                                )
                
                # グリッド追加
                ax.grid(True, linestyle='-', alpha=0.3, color='#CCCCCC')
                
                # グラフスタイル設定
                ax.set_xlabel("Date", fontsize=12, fontweight='bold')
                
                # Y軸ラベルの単位を項目に応じて設定
                unit = ""
                if "Sprint" in label and "(s)" in label:
                    unit = " (sec)"
                elif label == "Pro Agility":
                    unit = " (sec)"
                elif "BW*スコア" in label:
                    unit = " (kg*score)"
                elif "BSQ" in label or "BP" in label:
                    unit = " (kg)"
                elif "CMJ" in label:
                    unit = " (cm)"
                elif "Weight" in label:
                    unit = " (kg)"
                elif "Fat mass(kg)" in label:
                    unit = " (kg)"
                elif "BMI" in label:
                    unit = ""  # BMIは単位なし
                elif "LBM/m" in label:
                    unit = " (kg/m)"
                elif "CODD" in label:
                    unit = " (m/s)"
                elif "20m Multh" in label or "20m Multi" in label:
                    unit = " (reps)"
                    
                ax.set_ylabel(label + unit, fontsize=12, fontweight='bold')
                
                # グラフタイトル - "の推移"を英語に変更（文字化け対策）
                if highlight:
                    ax.set_title(f"{label} Trend", fontsize=16, fontweight='bold', color='#8A56AC')
                else:
                    ax.set_title(f"{label} Trend", fontsize=16, fontweight='bold', color='#333333')
                
                # X軸の日付フォーマット調整
                plt.gcf().autofmt_xdate()
                
                # Y軸の範囲を安全に設定
                vals = data[label].values
                if len(vals) > 0 and not np.any(np.isnan(vals)):
                    if len(vals) > 1:
                        margin = (vals.max() - vals.min()) * 0.1
                        if margin == 0:  # すべての値が同じ場合
                            margin = vals.mean() * 0.1 if vals.mean() > 0 else 1
                    else:
                        # データが1点しかない場合
                        margin = vals[0] * 0.1 if vals[0] > 0 else 1
                    
                    # スプリント、Pro Agility、体脂肪量は下がるほど良いので、Y軸を調整
                    is_decreasing_good = "Sprint(s)" in label or label == "Pro Agility" or label == "Fat mass(kg)"
                    if is_decreasing_good:
                        ax.set_ylim(vals.max() + margin, max(0, vals.min() - margin))
                    else:
                        # その他は標準的な上向きの良さ
                        ax.set_ylim(max(0, vals.min() - margin), vals.max() + margin)
                
                # 平均線を追加
                avg = data[label].mean()
                ax.axhline(y=avg, color='#8A56AC', linestyle='--', alpha=0.7, label=f'Average: {avg:.2f}')
                
                # 目標値を点線で表示（存在する場合）
                if label in target_values and not pd.isna(target_values[label]):
                    try:
                        target_val = float(target_values[label])
                        ax.axhline(y=target_val, color='#FF4500', linestyle='-.', alpha=0.7, 
                                  label=f'Target: {target_val:.2f}')
                    except (ValueError, TypeError):
                        pass  # 数値に変換できない場合はスキップ
                
                # Y軸の目盛り数を整数に制限
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                
                # 最後のデータポイントに値を表示
                if not data.empty:
                    # 最後のデータポイントの値を安全に取得して表示
                    try:
                        last_value = float(data[label].iloc[-1])
                        value_text = f'{last_value:.2f}'
                    except (ValueError, TypeError):
                        value_text = str(data[label].iloc[-1])
                        
                    ax.annotate(
                        value_text,
                        xy=(data["測定日"].iloc[-1], data[label].iloc[-1]),
                        xytext=(10, 0), textcoords='offset points',
                        fontsize=12, color='#333333', fontweight='bold'
                    )
                
                # 凡例の追加 - SunRockersカラーに合わせてスタイル調整（ライトモード対応）
                legend = ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#CCCCCC')
                
                plt.tight_layout()
                st.pyplot(fig)
        
        # 個別メトリクス用のカラー設定 - SunRockersテーマカラーを使用（ライトモード対応）
        # 全て紫色に統一するため、実際には使用しませんが、既存の関数との互換性のために残しておく
        metrics_colors = {
            "Sprint Momentum": "#8A56AC",    # 紫に統一
            "BW*スコア": "#8A56AC",          # 紫に統一
            "LBM/m": "#8A56AC",              # 紫に統一
            "BW*20m Multi": "#8A56AC",       # 紫に統一 - 新たに追加
            "5m Sprint(s)": "#8A56AC",       # 紫
            "10m Sprint(s)": "#8A56AC",      # 紫
            "20m Sprint(s)": "#8A56AC",      # 紫
            "BSQ": "#8A56AC",                # 紫に統一
            "BP": "#8A56AC",                 # 紫
            "CMJ": "#8A56AC",                # 紫に統一
            "Pro Agility": "#8A56AC",        # 紫
            "CODD": "#8A56AC",               # 紫
            "20m Multh": "#8A56AC",          # 紫
            "20m Multi": "#8A56AC",          # 紫 - 新たに追加
            "Weight": "#8A56AC",             # 紫に統一
            "Fat mass(kg)": "#8A56AC",       # 紫
            "BMI": "#8A56AC",                # 紫に統一
        }
        
        # メトリックスタイプに応じたマーカー
        metrics_markers = {
            "Sprint Momentum": "D",        # ダイヤモンド
            "BW*スコア": "D",             # ダイヤモンド
            "LBM/m": "D",                 # ダイヤモンド
            "BW*20m Multi": "D",          # ダイヤモンド - 新たに追加
            "5m Sprint(s)": "o",          # 円
            "10m Sprint(s)": "o",         # 円
            "20m Sprint(s)": "o",         # 円
            "BSQ": "^",                   # 三角形
            "BP": "^",                    # 三角形
            "CMJ": "s",                   # 四角形
            "Pro Agility": "o",           # 円
            "CODD": "o",                  # 円
            "20m Multh": "o",             # 円
            "20m Multi": "o",             # 円 - 新たに追加
            "Weight": "s",                # 四角形
            "Fat mass(kg)": "s",          # 四角形
            "BMI": "s",                   # 四角形
        }
        
        # ==========
        # 重要メトリクスセクション - メインとなる3つの指標を表示
        # ==========
        st.markdown("""
        <div class="purple-gradient-bg" style="border-radius: 6px 6px 0 0; margin-top: 30px; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);">
            <h3 style="margin: 0; letter-spacing: 1px; font-weight: 600; text-transform: uppercase;">Key Performance Metrics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # メイン指標用コンテナ
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 重要なメトリクスを先頭に表示（全幅で表示）
        important_metrics = ["Sprint Momentum", "BW*スコア", "LBM/m", "BW*20m Multi"]
        
        for metric in important_metrics:
            if metric in user_data.columns:
                color = metrics_colors.get(metric, "#8A56AC")
                marker = metrics_markers.get(metric, "D")
                plot_improved_graph(metric, color, marker, highlight=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ==========
        # 各カテゴリ別のセクション - カテゴリごとに指標をグループ化
        # ==========
        
        # 1. スピード指標セクション
        st.markdown("""
        <div class="category-section">
            <div class="category-header">
                <i>⚡</i> Speed Metrics
            </div>
            <div class="category-content">
        """, unsafe_allow_html=True)
        
        # 2列レイアウトでスピード指標を表示
        speed_metrics = ["5m Sprint(s)", "10m Sprint(s)", "20m Sprint(s)", "Pro Agility", "CODD"]
        
        # スピード指標を2列で表示
        col1, col2 = st.columns(2)
        
        for i, metric in enumerate(speed_metrics):
            if metric in user_data.columns:
                with col1 if i % 2 == 0 else col2:
                    color = metrics_colors.get(metric, "#8A56AC")
                    marker = metrics_markers.get(metric, "o")
                    plot_improved_graph(metric, color, marker)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # 2. 持久力指標セクション
        st.markdown("""
        <div class="category-section">
            <div class="category-header">
                <i>🏃</i> Endurance Metrics
            </div>
            <div class="category-content">
        """, unsafe_allow_html=True)
        
        # 持久力指標を表示
        endurance_metrics = ["20m Multh", "20m Multi"]
        
        for metric in endurance_metrics:
            if metric in user_data.columns:
                color = metrics_colors.get(metric, "#8A56AC")
                marker = metrics_markers.get(metric, "o")
                plot_improved_graph(metric, color, marker)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # 3. 筋力・パワー指標セクション
        st.markdown("""
        <div class="category-section">
            <div class="category-header">
                <i>💪</i> Strength & Power Metrics
            </div>
            <div class="category-content">
        """, unsafe_allow_html=True)
        
        # 筋力・パワー指標を2列で表示
        strength_power_metrics = ["BSQ", "BP", "CMJ"]
        
        col1, col2 = st.columns(2)
        
        for i, metric in enumerate(strength_power_metrics):
            if metric in user_data.columns:
                with col1 if i % 2 == 0 else col2:
                    color = metrics_colors.get(metric, "#8A56AC")
                    marker = metrics_markers.get(metric, "^" if "SQ" in metric or "BP" in metric else "s")
                    plot_improved_graph(metric, color, marker)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # 4. 体組成指標セクション
        st.markdown("""
        <div class="category-section">
            <div class="category-header">
                <i>📊</i> Body Composition Metrics
            </div>
            <div class="category-content">
        """, unsafe_allow_html=True)
        
        # 体組成指標を2列で表示
        body_comp_metrics = ["Weight", "Fat mass(kg)", "BMI"]
        
        col1, col2 = st.columns(2)
        
        for i, metric in enumerate(body_comp_metrics):
            if metric in user_data.columns:
                with col1 if i % 2 == 0 else col2:
                    color = metrics_colors.get(metric, "#8A56AC")
                    marker = metrics_markers.get(metric, "s")
                    plot_improved_graph(metric, color, marker)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        st.error(f"No data found for player '{name}'.")

# フッターを追加 - SunRockersテーマ（ライトモード対応）
st.markdown("""
<div style="text-align: center; padding: 20px; margin-top: 40px; border-top: 1px solid #E0E0E0;">
    <p style="color: #666666; font-size: 0.9rem;">© 2025 SunRockers Shibuya Physical Performance Lab</p>
</div>
""", unsafe_allow_html=True)