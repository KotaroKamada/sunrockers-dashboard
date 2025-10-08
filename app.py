import streamlit as st
import pandas as pd
import numpy as np
import warnings
import base64
import io
from datetime import datetime
warnings.filterwarnings('ignore')

# Google Sheets連携用ライブラリ
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    st.warning("Google Sheets連携ライブラリがインストールされていません。Excelファイルから読み込みます。")

# Plotlyが利用可能かチェック
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotlyライブラリが見つかりません。グラフ機能は無効になります。requirements.txtにplotlyを追加してください。")

# PDFライブラリの確認
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ページ設定
st.set_page_config(
    page_title="SR SHIBUYA 測定データ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（レスポンシブ対応とモダンなデザイン）
st.markdown("""
<style>
    /* レスポンシブ対応の基本設定 */
    @media screen and (max-width: 768px) {
        .stApp > div {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .main-header {
            font-size: 2rem !important;
            padding: 1.5rem !important;
        }
        
        .section-header {
            font-size: 1.2rem !important;
            padding: 0.8rem 1.5rem !important;
        }
        
        .metric-card {
            margin: 0.5rem 0 !important;
            padding: 1.5rem !important;
        }
        
        .highlight-metric {
            font-size: 2rem !important;
        }
        
        .stDataFrame {
            font-size: 0.9rem !important;
        }
    }
    
    .main-header {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        padding: 2.5rem;
        border-radius: 0px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 2.8rem;
        box-shadow: 0 8px 32px rgba(30, 41, 59, 0.25);
        border-left: 6px solid #0F172A;
    }
    
    .welcome-container {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        border: 1px solid #CBD5E1;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    .welcome-title {
        color: #1E293B;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .welcome-subtitle {
        color: #64748B;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .section-header {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        padding: 1.2rem 2rem;
        border-radius: 0px;
        color: white;
        font-weight: 600;
        margin: 2rem 0 1.5rem 0;
        font-size: 1.4rem;
        box-shadow: 0 4px 16px rgba(51, 65, 85, 0.2);
        border-left: 4px solid #1E293B;
    }
    
    .key-indicator-title {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 1.5rem 2rem;
        border-radius: 0px;
        color: white;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        font-size: 1.6rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.3);
        border-left: 4px solid #64748B;
        text-align: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #334155 0%, #475569 100%);
        padding: 2rem;
        border-radius: 0px;
        margin: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(51, 65, 85, 0.15);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
        height: 240px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(51, 65, 85, 0.25);
    }
    
    .highlight-metric {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.6rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    .metric-label {
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .comparison-text {
        font-size: 0.8rem;
        opacity: 0.85;
        margin-top: 0.4rem;
        font-weight: 400;
    }
    
    /* データフレームのスタイル改善 */
    .stDataFrame {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        overflow: hidden;
    }
    
    .stDataFrame table {
        font-size: 1rem !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%) !important;
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.8rem !important;
        border: none !important;
    }
    
    .stDataFrame td {
        padding: 0.7rem !important;
        font-size: 1rem !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    
    .stDataFrame tr:hover {
        background-color: #F8FAFC !important;
    }
    
    /* サイドバーのスタイル改善 */
    .css-1d391kg {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }
    
    /* タイトルエリアの改善 */
    .player-title {
        color: #1E293B;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding: 1rem 0;
        border-bottom: 3px solid #334155;
    }
    
    .date-info {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        padding: 1rem;
        border-radius: 8px;
        color: #1E293B;
        font-weight: 500;
        text-align: center;
        border: 1px solid #C7D2FE;
    }
    
    /* グラフセクションの改善 */
    .graph-section {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .graph-title {
        color: #374151;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* レスポンシブグラフ対応 */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    @media screen and (max-width: 768px) {
        .js-plotly-plot {
            height: 400px !important;
        }
    }
    
    /* 概要テーブルのスタイル */
    .summary-table {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* レーダーチャート用スタイル */
    .radar-chart-container {
        background: transparent;
        border-radius: 0px;
        padding: 0rem;
        margin: 1rem 0;
        box-shadow: none;
        border: none;
        height: 400px;
        display: flex;
        flex-direction: column;
    }
    
    .radar-chart-title {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# 統一されたカラーパレット
CHART_COLOR = '#4B5563'  # Gray 600
CHART_COLORS = [CHART_COLOR] * 6

# チーム分析用のカラーパレット
TEAM_COLORS = [
    '#4B5563',  # Gray 600
    '#EF4444',  # Red 500
    '#3B82F6',  # Blue 500
    '#10B981',  # Emerald 500
    '#F59E0B',  # Amber 500
    '#8B5CF6',  # Violet 500
    '#EC4899',  # Pink 500
    '#14B8A6',  # Teal 500
    '#F97316',  # Orange 500
    '#6366F1'   # Indigo 500
]

# 名前入力による簡単なアクセス制御
def validate_player_name(df, input_name):
    """入力された名前が存在するかチェック"""
    if not input_name or input_name.strip() == "":
        return False, "名前を入力してください"
    
    available_names = df[df['名前'] != '目標値']['名前'].dropna().unique()
    
    if input_name in available_names:
        return True, "認証成功"
    
    for name in available_names:
        if input_name in str(name) or str(name) in input_name:
            return True, f"'{name}' として認識しました"
    
    return False, f"選手名 '{input_name}' が見つかりません"

@st.cache_data(ttl=300)  # 5分間キャッシュ（データ更新を反映）
def load_data():
    """Googleスプレッドシートまたはエクセルファイルを読み込む関数"""
    
    # まずGoogleスプレッドシートから読み込みを試行
    if GSPREAD_AVAILABLE:
        try:
            # 認証情報の取得
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Streamlit Secretsが利用可能かチェック（Streamlit Cloud環境）
            try:
                if 'gcp_service_account' in st.secrets:
                    # Streamlit Cloud環境：secretsから読み込み
                    credentials_dict = dict(st.secrets["gcp_service_account"])
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                        credentials_dict, 
                        scope
                    )
                    SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "1haqC1GhKMj5KJvIUyAvTwpr9CKQtMa7hr6qGcGagSrc")
                else:
                    raise KeyError("Secrets not configured")
            except (KeyError, FileNotFoundError):
                # ローカル環境：credentials.jsonから読み込み
                import os
                
                # credentials.jsonのパスを指定
                credentials_path = 'credentials.json'
                
                # 見つからない場合は絶対パスを試す
                if not os.path.exists(credentials_path):
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    credentials_path = os.path.join(current_dir, 'credentials.json')
                
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    credentials_path, 
                    scope
                )
                
                # スプレッドシートIDを設定
                SPREADSHEET_ID = "1haqC1GhKMj5KJvIUyAvTwpr9CKQtMa7hr6qGcGagSrc"
            
            if not SPREADSHEET_ID or SPREADSHEET_ID == "あなたのスプレッドシートID":
                raise ValueError("スプレッドシートIDが設定されていません")
            
            # スプレッドシートに接続
            gc = gspread.authorize(credentials)
            worksheet = gc.open_by_key(SPREADSHEET_ID).sheet1
            
            # データを取得してDataFrameに変換
            data = worksheet.get_all_values()
            
            if not data or len(data) < 2:
                raise ValueError("スプレッドシートにデータがありません")
            
            # ヘッダーとデータを分離
            headers = data[0]
            rows = data[1:]
            
            # DataFrameを作成
            df = pd.DataFrame(rows, columns=headers)
            
        except Exception as e:
            st.warning(f"⚠️ Googleスプレッドシート読み込みエラー: {str(e)}")
            st.info("Excelファイルからの読み込みにフォールバックします...")
            df = load_from_excel()
            
    else:
        # gspreadが利用できない場合はExcelから読み込み
        df = load_from_excel()
    
    if df.empty:
        return df
    
    # データ型の変換
    df.columns = df.columns.astype(str)
    
    for col in df.columns:
        if col not in ['名前', 'カテゴリー', '測定日']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # BMI計算
    if all(col in df.columns for col in ['Height', 'Weight']):
        if 'BMI' not in df.columns:
            df['BMI'] = np.nan
        
        mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
               (df['Height'] > 0) & (df['Weight'] > 0))
        
        recalc_mask = mask & (pd.isna(df['BMI']) | (df['BMI'] == 0))
        
        if recalc_mask.any():
            df.loc[recalc_mask, 'BMI'] = (df.loc[recalc_mask, 'Weight'] / 
                                         ((df.loc[recalc_mask, 'Height'] / 100) ** 2))
    
    # BW*20m Mulch計算
    if all(col in df.columns for col in ['Weight', '20m Mulch']):
        mask = pd.isna(df['BW*20m Mulch']) & pd.notna(df['Weight']) & pd.notna(df['20m Mulch'])
        df.loc[mask, 'BW*20m Mulch'] = df.loc[mask, 'Weight'] * df.loc[mask, '20m Mulch']
    
    # 測定日の処理
    if '測定日' in df.columns:
        df['測定日'] = pd.to_datetime(df['測定日'], errors='coerce')
        df['測定日'] = df['測定日'].dt.strftime('%Y-%m-%d')
    
    return df

def load_from_excel():
    """Excelファイルから読み込むフォールバック関数"""
    try:
        df = pd.read_excel('SR_physicaldata.xlsx', sheet_name=0)
        return df
    except Exception as e:
        st.error(f"❌ Excelファイル読み込みエラー: {str(e)}")
        st.error("SR_physicaldata.xlsxファイルが存在することを確認してください。")
        return pd.DataFrame()

def get_category_config(category):
    """カテゴリー別の設定を取得"""
    config = {
        'U18': {
            'highlight': {
                'Sprint Momentum': '',
                'LBM/m': '',
                'BW*20m Mulch': ''
            },
            'sections': {
                'Body Composition': {
                    'metrics': ['Height', 'Weight', 'BMI', 'Fat%', 'LBM/m'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Fat%': '%', 'LBM/m': ''}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD', 'Sprint Momentum'],
                    'units': {'20m Sprint(s)': '秒', 'Pro Agility': '秒', 'CODD': '秒', 'Sprint Momentum': ''}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch', 'BW*20m Mulch'],
                    'units': {'20m Mulch': '回', 'BW*20m Mulch': ''}
                },
                'Strength': {
                    'metrics': ['BSQ', 'BP', 'BSQ/BW', 'BP/BW'],
                    'units': {'BSQ': 'kg', 'BP': 'kg', 'BSQ/BW': '', 'BP/BW': ''}
                }
            }
        },
        'U15': {
            'highlight': {
                'BW*20m Mulch': '',
                'Height': 'cm',
                'Weight': 'kg',
                'Maturity': 'year'
            },
            'sections': {
                'Body Composition': {
                    'metrics': ['Height', 'Weight', 'BMI', 'Maturity', 'LBM/m'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Maturity': 'year', 'LBM/m': ''}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD', 'Sprint Momentum'],
                    'units': {'20m Sprint(s)': '秒', 'Pro Agility': '秒', 'CODD': '秒', 'Sprint Momentum': ''}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch', 'BW*20m Mulch'],
                    'units': {'20m Mulch': '回', 'BW*20m Mulch': ''}
                }
            }
        },
        'U12': {
            'highlight': {
                'Weight': 'kg',
                '20m Sprint(s)': '秒',
                'CMJ': 'cm'
            },
            'sections': {
                'Body Composition': {
                    'metrics': ['Height', 'Weight', 'BMI', 'Maturity', 'LBM/m'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Maturity': 'year', 'LBM/m': ''}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD', 'Side Hop(右)', 'Side Hop(左)', 'Sprint Momentum'],
                    'units': {'20m Sprint(s)': '秒', 'Pro Agility': '秒', 'CODD': '秒', 'Side Hop(右)': '回', 'Side Hop(左)': '回', 'Sprint Momentum': ''}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch', 'BW*20m Mulch'],
                    'units': {'20m Mulch': '回', 'BW*20m Mulch': ''}
                }
            }
        }
    }
    return config.get(category, config['U18'])

def safe_get_value(data, column, default=None):
    """安全に値を取得する関数（項目ごとの最新のデータを遡って取得）- Sprint MomentumとBW*20m Mulchの計算を含む"""
    try:
        if column not in data.columns or data.empty:
            # Sprint MomentumやBW*20m Mulchの計算を試行
            if column == 'Sprint Momentum' and all(col in data.columns for col in ['Weight', '20m Sprint(s)']):
                weight_val = safe_get_value(data, 'Weight', default)
                sprint_val = safe_get_value(data, '20m Sprint(s)', default)
                if weight_val is not None and sprint_val is not None:
                    return float(weight_val) * float(sprint_val)
            elif column == 'BW*20m Mulch' and all(col in data.columns for col in ['Weight', '20m Mulch']):
                weight_val = safe_get_value(data, 'Weight', default)
                mulch_val = safe_get_value(data, '20m Mulch', default)
                if weight_val is not None and mulch_val is not None:
                    return float(weight_val) * float(mulch_val)
            return default
        
        # その項目で有効な値があるデータのみフィルター
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if valid_data.empty:
            # Sprint MomentumやBW*20m Mulchの計算を試行
            if column == 'Sprint Momentum' and all(col in data.columns for col in ['Weight', '20m Sprint(s)']):
                weight_val = safe_get_value(data, 'Weight', default)
                sprint_val = safe_get_value(data, '20m Sprint(s)', default)
                if weight_val is not None and sprint_val is not None:
                    return float(weight_val) * float(sprint_val)
            elif column == 'BW*20m Mulch' and all(col in data.columns for col in ['Weight', '20m Mulch']):
                weight_val = safe_get_value(data, 'Weight', default)
                mulch_val = safe_get_value(data, '20m Mulch', default)
                if weight_val is not None and mulch_val is not None:
                    return float(weight_val) * float(mulch_val)
            return default
        
        # 測定日がある場合は、その項目の最新のデータを取得
        if '測定日' in valid_data.columns:
            # 測定日でソートして最新のデータを取得
            latest_valid = valid_data.sort_values('測定日', ascending=False).iloc[0]
            value = latest_valid[column]
        else:
            value = valid_data.iloc[0][column]
        
        if pd.isna(value):
            return default
        
        # 数値型の場合
        if isinstance(value, (int, float, np.number)):
            if np.isfinite(value):
                return float(value)
        
        # 文字列の場合の処理
        if isinstance(value, str):
            try:
                if column == 'Fat%':
                    # Fat%の場合は%記号を取り除いて数値変換
                    clean_value = value.strip().replace('%', '')
                    num_val = float(clean_value)
                    if np.isfinite(num_val):
                        return num_val
                else:
                    # その他の場合は直接数値変換
                    num_val = float(value.strip())
                    if np.isfinite(num_val):
                        return num_val
            except (ValueError, TypeError):
                # 数値変換できない場合はそのまま返す（文字列データの場合）
                return str(value)
        
        # 上記のいずれにも該当しない場合はそのまま返す
        return value
        
    except Exception as e:
        return default

def safe_get_previous_value(data, column, default=None):
    """前回の測定値を安全に取得する関数（項目ごとの前回データを取得）"""
    try:
        if column not in data.columns or data.empty:
            return default
        
        # その項目で有効な値があるデータのみフィルター
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if len(valid_data) < 2:
            return default
        
        if '測定日' in valid_data.columns:
            sorted_data = valid_data.sort_values('測定日', ascending=False)
            # 2番目に新しいデータを取得（その項目での前回値）
            previous_value = sorted_data.iloc[1][column]
        else:
            previous_value = valid_data.iloc[1][column]
        
        if pd.isna(previous_value):
            return default
        
        # 数値型の場合
        if isinstance(previous_value, (int, float, np.number)):
            if np.isfinite(previous_value):
                return float(previous_value)
        
        # 文字列の場合の処理
        if isinstance(previous_value, str):
            try:
                if column == 'Fat%':
                    clean_value = previous_value.strip().replace('%', '')
                    num_val = float(clean_value)
                    if np.isfinite(num_val):
                        return num_val
                else:
                    num_val = float(previous_value.strip())
                    if np.isfinite(num_val):
                        return num_val
            except (ValueError, TypeError):
                return str(previous_value)
        
        return previous_value
        
    except Exception as e:
        return default

def safe_get_latest_and_previous_for_player(df, player_name, id_group, metric):
    """特定の選手の特定の項目の最新値と前回値を取得（ID別グルーピング対応版）"""
    try:
        # 該当選手の全データを取得（IDグループでフィルタ）
        player_all_data = df[(df['名前'] == player_name) & (df['ID'] == id_group)]
        
        if player_all_data.empty or metric not in player_all_data.columns:
            return None, None, "-", "-"
        
        # その項目で有効な値があるデータのみフィルター
        valid_data = player_all_data[
            player_all_data[metric].notna() & 
            (player_all_data[metric] != '') & 
            (player_all_data[metric] != 'null')
        ].copy()
        
        if valid_data.empty:
            return None, None, "-", "-"
        
        # 測定日でソート
        if '測定日' in valid_data.columns:
            valid_data['測定日'] = pd.to_datetime(valid_data['測定日'], errors='coerce')
            valid_data = valid_data.dropna(subset=['測定日']).sort_values('測定日', ascending=False)
        
        # 最新値と測定日を取得
        latest_val = None
        latest_date = "-"
        if len(valid_data) > 0:
            latest_row = valid_data.iloc[0]
            latest_val = latest_row[metric]
            if '測定日' in latest_row and pd.notna(latest_row['測定日']):
                latest_date = latest_row['測定日'].strftime('%Y-%m-%d')
        
        # 前回値と測定日を取得
        previous_val = None
        previous_date = "-"
        if len(valid_data) > 1:
            previous_row = valid_data.iloc[1]
            previous_val = previous_row[metric]
            if '測定日' in previous_row and pd.notna(previous_row['測定日']):
                previous_date = previous_row['測定日'].strftime('%Y-%m-%d')
        
        return latest_val, previous_val, latest_date, previous_date
        
    except Exception as e:
        return None, None, "-", "-"

def safe_mean(series):
    """安全に平均値を計算"""
    if series.empty:
        return None
    
    numeric_values = []
    for value in series:
        if pd.notna(value) and value != '' and value != 'null':
            try:
                if isinstance(value, str):
                    clean_value = str(value).strip().replace('%', '')
                    numeric_val = float(clean_value)
                else:
                    numeric_val = float(value)
                
                if np.isfinite(numeric_val):
                    numeric_values.append(numeric_val)
            except (ValueError, TypeError):
                continue
    
    return np.mean(numeric_values) if len(numeric_values) > 0 else None

def calculate_z_score(player_val, comparison_data, column):
    """選手の値を比較データ平均を基準としたZスコアで評価（5段階評価）
    
    Args:
        player_val: 選手の値
        comparison_data: 比較対象データ（個人分析ではカテゴリーデータ、比較分析ではIDグループデータ）
        column: 評価する項目名
    """
    try:
        if player_val is None or comparison_data.empty or column not in comparison_data.columns:
            return 3  # デフォルト値
        
        # 比較データの有効値を取得
        valid_values = []
        for _, row in comparison_data.iterrows():
            val = safe_get_value(pd.DataFrame([row]), column)
            if val is not None:
                valid_values.append(val)
        
        if len(valid_values) < 2:
            return 3  # データ不足の場合は中央値
        
        group_mean = np.mean(valid_values)
        group_std = np.std(valid_values, ddof=1)
        
        if group_std == 0:
            return 3
        
        z_score = (player_val - group_mean) / group_std
        
        # Sprint、Agility、CODDは低い方が良いので評価を逆転
        reverse_score_metrics = ['20m Sprint(s)', 'Pro Agility', 'CODD']
        
        if column in reverse_score_metrics:
            # 低い方が良い項目：+1.5SD以上で1、+1.5~0.5SDで2、+0.5SD~-0.5SDで3、-0.5~-1.5SDで4、-1.5SD以下で5
            if z_score >= 1.5:
                return 1
            elif z_score >= 0.5:
                return 2
            elif z_score >= -0.5:
                return 3
            elif z_score >= -1.5:
                return 4
            else:
                return 5
        else:
            # 高い方が良い項目：従来通り
            if z_score <= -1.5:
                return 1
            elif z_score <= -0.5:
                return 2
            elif z_score <= 0.5:
                return 3
            elif z_score <= 1.5:
                return 4
            else:
                return 5
        
    except Exception:
        return 3

def create_radar_chart(player_data, comparison_data, config):
    """Key Indicators用のレーダーチャートを作成（Sprint Momentum、BW*20m Mulch、LBM/mの3つを使用）"""
    if not PLOTLY_AVAILABLE:
        return None
    
    try:
        # 3つの指標を固定で使用
        radar_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        
        # 各メトリクスの値とZスコアを計算
        radar_data = {
            'metrics': [],
            'values': [],
            'z_scores': []
        }
        
        for metric in radar_metrics:
            player_val = safe_get_value(player_data, metric)
            
            if player_val is not None:
                z_score = calculate_z_score(player_val, comparison_data, metric)
                radar_data['metrics'].append(metric)
                radar_data['values'].append(player_val)
                radar_data['z_scores'].append(z_score)
        
        # データが不足している場合
        if len(radar_data['metrics']) < 2:
            return None
        
        # レーダーチャートの作成
        fig = go.Figure()
        
        # プレイヤーのデータ
        fig.add_trace(go.Scatterpolar(
            r=radar_data['z_scores'],
            theta=radar_data['metrics'],
            fill='toself',
            name='現在のレベル',
            line=dict(color='#4B5563', width=3),
            fillcolor='rgba(75, 85, 99, 0.3)',
            marker=dict(size=8, color='#4B5563')
        ))
        
        # レイアウト設定
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=['1 (要改善)', '2 (やや劣る)', '3 (平均的)', '4 (良好)', '5 (優秀)'],
                    tickfont=dict(size=10),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color='#374151')
                ),
                bgcolor='rgba(248, 250, 252, 0.5)',
                domain=dict(x=[0.0, 0.8], y=[0.0, 1.0])
            ),
            showlegend=False,
            height=360,
            margin=dict(l=10, r=50, t=30, b=70),
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=10, color="#374151")
        )
        
        return fig
        
    except Exception as e:
        return None

def format_value(value, unit="", column_name=""):
    """値を安全にフォーマット（Fat%は×100して%表記、N/Aは空欄）"""
    if value is None or pd.isna(value):
        return ""
    try:
        float_val = float(value)
        if column_name == 'Fat%':
            return f"{float_val * 100:.1f}%"
        elif unit == '%' and column_name != 'Fat%':
            return f"{float_val:.1f}%"
        else:
            return f"{float_val:.1f}{unit}"
    except:
        return ""

def get_measurement_date(data, column):
    """特定の項目の測定日を取得"""
    try:
        if column not in data.columns or data.empty:
            return "-"
        
        # まず基本的なフィルタリング
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if valid_data.empty:
            return "-"
        
        if '測定日' in valid_data.columns:
            latest_valid = valid_data.sort_values('測定日', ascending=False).iloc[0]
            return latest_valid['測定日']
        
        return "-"
        
    except Exception as e:
        return "-"

def create_comprehensive_summary_table(player_data, category_avg, goal_data, config):
    """全項目を含む包括的な概要テーブルを作成"""
    table_data = []
    
    all_metrics = []
    for section_data in config['sections'].values():
        all_metrics.extend(section_data['metrics'])
    
    # 重複を除去しつつ順序を保持
    seen = set()
    unique_metrics = []
    for metric in all_metrics:
        if metric not in seen and metric in player_data.columns:
            seen.add(metric)
            unique_metrics.append(metric)
    
    for metric in unique_metrics:
        # 最新値と前回値を取得
        current_val = safe_get_value(player_data, metric)
        previous_val = safe_get_previous_value(player_data, metric)
        avg_val = safe_mean(category_avg[metric]) if metric in category_avg.columns else None
        goal_val = safe_get_value(goal_data, metric) if not goal_data.empty else None
        
        # 変化を計算（色付き、Fat%は×100して表示）
        change = ""
        if current_val is not None and previous_val is not None:
            diff = current_val - previous_val
            if metric == 'Fat%':
                # Fat%の場合は×100して表示
                if diff > 0:
                    change = f'<span style="color: #DC2626;">↑ +{diff * 100:.1f}%</span>'  # 赤色
                elif diff < 0:
                    change = f'<span style="color: #2563EB;">↓ {diff * 100:.1f}%</span>'   # 青色
                else:
                    change = "→ 0.0%"
            else:
                # その他の項目は通常の差分表示
                if diff > 0:
                    change = f'<span style="color: #DC2626;">↑ +{diff:.1f}</span>'  # 赤色
                elif diff < 0:
                    change = f'<span style="color: #2563EB;">↓ {diff:.1f}</span>'   # 青色
                else:
                    change = "→ 0.0"
        
        # 測定日を取得
        measurement_date = get_measurement_date(player_data, metric)
        
        # 目標値との比較で色付け
        latest_val_display = format_value(current_val, "", metric)
        
        table_data.append({
            '項目': metric,
            '最新測定値': latest_val_display,
            '前回測定値': format_value(previous_val, "", metric),
            '変化': change,
            'カテゴリー平均': format_value(avg_val, "", metric),
            '目標値': format_value(goal_val, "", metric) if goal_val is not None else "",
            '最新測定日': measurement_date
        })
    
    return pd.DataFrame(table_data)

def show_team_analysis(df):
    """比較分析画面を表示（ID別グルーピング版）"""
    st.markdown('<div class="main-header">SR SHIBUYA 比較分析</div>', unsafe_allow_html=True)
    
    # データの前処理：BMIの再計算
    if all(col in df.columns for col in ['Height', 'Weight', 'BMI']):
        mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
               (df['Height'] > 0) & (df['Weight'] > 0) & 
               (pd.isna(df['BMI']) | (df['BMI'] == 0)))
        
        if mask.any():
            df.loc[mask, 'BMI'] = (df.loc[mask, 'Weight'] / 
                                  ((df.loc[mask, 'Height'] / 100) ** 2))
    
    # 利用可能なIDグループを取得
    available_ids = sorted(df['ID'].dropna().unique())
    
    # サイドバーでの設定
    st.sidebar.header("分析設定")
    
    # IDグループ選択
    selected_id = st.sidebar.selectbox(
        "分析対象IDグループ",
        available_ids,
        help="比較する選手のIDグループを選択"
    )
    
    # 該当IDグループの選手のみフィルタ（重複排除処理を強化）
    id_group_data = df[(df['ID'] == selected_id) & (df['名前'] != '目標値')].copy()
    
    # 同名選手の重複処理：最新の測定日のデータのみを保持
    if '測定日' in id_group_data.columns and not id_group_data.empty:
        # 測定日を確実にdatetime型に変換
        id_group_data['測定日'] = pd.to_datetime(id_group_data['測定日'], errors='coerce')
        
        # NaN値を持つ行を除外してから重複排除
        id_group_data_clean = id_group_data.dropna(subset=['名前', '測定日'])
        
        # 各選手の最新データのみを取得（より厳密な処理）
        latest_data = (id_group_data_clean
                      .sort_values(['名前', '測定日'], ascending=[True, False])
                      .groupby('名前', as_index=False)
                      .first())
        
        # 重複排除済みのデータを使用
        id_group_data = latest_data
        id_group_players = sorted(latest_data['名前'].unique())
        
    else:
        # 測定日がない場合の処理も改善
        id_group_players = sorted(list(set(id_group_data['名前'].dropna().tolist())))
        # この場合もid_group_dataを重複排除済みに更新
        unique_names = id_group_data['名前'].dropna().drop_duplicates()
        id_group_data = id_group_data[id_group_data['名前'].isin(unique_names)]
    
    # 選手選択（デフォルトで全選手選択）
    selected_players = st.sidebar.multiselect(
        f"比較する選手（最大50名まで対応）",
        id_group_players,
        default=id_group_players,  # 全選手をデフォルト選択
        help="比較したい選手を選択してください。多数の選手を同時に比較できます。"
    )
    
    # 利用可能なメトリクスを取得
    all_metrics = ['Height', 'Weight', 'BMI', 'Fat%', 'LBM/m', '20m Sprint(s)', 
                   'Pro Agility', 'CODD', 'Sprint Momentum', 'CMJ', 'BJ', 'RJ', 
                   '20m Mulch', 'BW*20m Mulch', 'BSQ', 'BP']
    
    available_metrics = []
    for metric in all_metrics:
        if metric in df.columns:
            if not id_group_data[metric].isna().all():
                available_metrics.append(metric)
    
    # メトリクス選択
    selected_metrics = st.sidebar.multiselect(
        "分析する項目",
        available_metrics,
        default=available_metrics[:6] if len(available_metrics) >= 6 else available_metrics,
        help="比較したい測定項目を選択"
    )
    
    if not selected_players:
        st.warning("比較する選手を選択してください。")
        return
    
    if not selected_metrics:
        st.warning("分析する項目を選択してください。")
        return
    
    # 選手情報表示
    st.success(f"選択: {len(selected_players)}名の選手, {len(selected_metrics)}項目を分析")
    
    # IDグループ概要の表示
    st.markdown('<div class="section-header">IDグループ概要</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("総選手数", len(id_group_players))
    with col2:
        st.metric("選択選手数", len(selected_players))
    with col3:
        total_measurements = len(df[(df['ID'] == selected_id) & (df['名前'].isin(selected_players))])
        st.metric("総測定回数", total_measurements)
    with col4:
        unique_dates = df[(df['ID'] == selected_id) & (df['名前'].isin(selected_players))]['測定日'].dropna().nunique()
        st.metric("測定日数", unique_dates)
    
    # 詳細グラフセクション
    st.markdown('<div class="section-header">詳細分析グラフ</div>', unsafe_allow_html=True)
    
    # 選択された項目ごとにグラフを作成
    create_detailed_analysis_charts(df, selected_players, selected_id, selected_metrics)

def create_detailed_analysis_charts(df, selected_players, id_group, selected_metrics):
    """選択された各項目の絶対値と変化量のグラフを作成（ID別グルーピング対応版）"""
    if not PLOTLY_AVAILABLE:
        st.warning("Plotlyが利用できないため、グラフを表示できません。")
        return
    
    for metric in selected_metrics:
        st.markdown(f"### {metric}")
        
        # 各選手のデータを収集
        players_data = {}
        changes_data = {}
        
        for player_name in selected_players:
            # 該当選手の全データを取得（項目別の有効データのみ、IDでフィルタ）
            player_all_data = df[(df['名前'] == player_name) & (df['ID'] == id_group)]
            
            if player_all_data.empty or metric not in player_all_data.columns:
                continue
            
            # その項目で有効な値があるデータのみフィルター
            valid_data = player_all_data[
                player_all_data[metric].notna() & 
                (player_all_data[metric] != '') & 
                (player_all_data[metric] != 'null')
            ].copy()
            
            if valid_data.empty:
                continue
            
            # 測定日でソートして時系列データを作成
            if '測定日' in valid_data.columns:
                valid_data['測定日'] = pd.to_datetime(valid_data['測定日'], errors='coerce')
                valid_data = valid_data.dropna(subset=['測定日']).sort_values('測定日')
            
            if len(valid_data) == 0:
                continue
            
            # 絶対値データ
            players_data[player_name] = {
                'dates': valid_data['測定日'].tolist() if '測定日' in valid_data.columns else list(range(len(valid_data))),
                'values': valid_data[metric].tolist()
            }
            
            # 変化量データ（前回から今回への変化）
            if len(valid_data) > 1:
                changes = []
                change_dates = []
                values = valid_data[metric].tolist()
                dates = valid_data['測定日'].tolist() if '測定日' in valid_data.columns else list(range(len(valid_data)))
                
                for i in range(1, len(values)):
                    change = values[i] - values[i-1]
                    changes.append(change)
                    change_dates.append(dates[i])
                
                if changes:
                    changes_data[player_name] = {
                        'dates': change_dates,
                        'changes': changes
                    }
        
        # グラフを縦に2つ並べて表示（横幅フル活用）
        # 絶対値の折れ線グラフ
        abs_chart = create_absolute_values_chart(players_data, metric)
        if abs_chart:
            st.plotly_chart(abs_chart, use_container_width=True, config={'displayModeBar': False})
        
        # 変化量の棒グラフ
        change_chart = create_changes_bar_chart(changes_data, metric)
        if change_chart:
            st.plotly_chart(change_chart, use_container_width=True, config={'displayModeBar': False})
        
        # その項目の詳細テーブルを追加
        metric_detail_table = create_metric_detail_table(df, selected_players, id_group, metric)
        if not metric_detail_table.empty:
            st.markdown(f"**{metric} - 詳細データ**")
            
            # スタイリングされたHTMLテーブルとして表示
            metric_table_html = create_metric_table_html(metric_detail_table, metric)
            st.markdown(metric_table_html, unsafe_allow_html=True)
        
        st.markdown("---")  # 項目間の区切り線

def create_metric_detail_table(df, selected_players, id_group, metric):
    """特定の項目の詳細テーブルを作成（ID別グルーピング対応版）"""
    table_data = []
    
    for player_name in selected_players:
        # 項目ごとの最新・前回データを取得
        latest_val, previous_val, latest_date, previous_date = safe_get_latest_and_previous_for_player(
            df, player_name, id_group, metric
        )
        
        # 選手のIDを取得
        player_all_data = df[(df['名前'] == player_name) & (df['ID'] == id_group)]
        player_id = safe_get_value(player_all_data, 'ID', '') if not player_all_data.empty else ''
        
        # 変化を計算
        if latest_val is not None and previous_val is not None:
            diff = latest_val - previous_val
            if metric == 'Fat%':
                if diff > 0:
                    change_display = f"+{diff * 100:.2f}%"
                elif diff < 0:
                    change_display = f"{diff * 100:.2f}%"
                else:
                    change_display = "0.00%"
            else:
                if diff > 0:
                    change_display = f"+{diff:.2f}"
                elif diff < 0:
                    change_display = f"{diff:.2f}"
                else:
                    change_display = "0.00"
        else:
            change_display = "-"
        
        # スコア計算
        if latest_val is not None:
            id_group_data = df[(df['ID'] == id_group) & (df['名前'] != '目標値')]
            score = calculate_z_score(latest_val, id_group_data, metric)
        else:
            score = "-"
        
        table_data.append({
            '選手名': player_name,
            'ID': player_id if player_id != '' else '-',
            '最新値': format_value(latest_val, "", metric) if latest_val is not None else "-",
            '最新測定日': latest_date,
            '前回値': format_value(previous_val, "", metric) if previous_val is not None else "-",
            '前回測定日': previous_date,
            '変化': change_display,
            'スコア': score
        })
    
    return pd.DataFrame(table_data)

def create_metric_table_html(df, metric):
    """項目別詳細テーブルのHTMLを作成"""
    if df.empty:
        return "<p>データがありません</p>"
    
    # テーブルの開始
    html = """
    <style>
    .metric-detail-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0 20px 0;
        font-size: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .metric-detail-table th {
        background: linear-gradient(135deg, #475569 0%, #64748B 100%);
        color: white;
        padding: 8px 6px;
        text-align: center;
        border: 1px solid #64748B;
        font-weight: 600;
        font-size: 11px;
    }
    .metric-detail-table td {
        padding: 6px;
        text-align: center;
        border: 1px solid #E2E8F0;
        background-color: white;
    }
    .metric-detail-table tr:nth-child(even) td {
        background-color: #F8FAFC;
    }
    .metric-detail-table tr:hover td {
        background-color: #EEF2FF;
    }
    .metric-player-name {
        background-color: #F1F5F9 !important;
        font-weight: 600;
        text-align: left !important;
        padding-left: 10px !important;
    }
    .metric-score-excellent {
        color: #DC2626;
        font-weight: bold;
    }
    .metric-change-positive {
        color: #059669;
        font-weight: 600;
    }
    .metric-change-negative {
        color: #DC2626;
        font-weight: 600;
    }
    .metric-sprint-change-positive {
        color: #DC2626;
        font-weight: 600;
    }
    .metric-sprint-change-negative {
        color: #059669;
        font-weight: 600;
    }
    </style>
    <table class="metric-detail-table">
    """
    
    # ヘッダー行
    html += """<thead><tr>
        <th>選手名</th>
        <th>ID</th>
        <th>最新値</th>
        <th>前回値</th>
        <th>変化</th>
    </tr></thead>"""
    
    # データ行
    html += "<tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        
        # 選手名
        html += f"<td class='metric-player-name'>{row['選手名']}</td>"
        
        # ID
        html += f"<td>{row['ID']}</td>"
        
        # 最新値
        html += f"<td>{row['最新値']}</td>"
        
        # 前回値
        html += f"<td>{row['前回値']}</td>"
        
        # 変化（色付き）
        change_val = row['変化']
        change_class = ""
        if change_val != "-" and change_val != "0.00" and change_val != "0.00%":
            if metric in ['20m Sprint(s)', 'Pro Agility', 'CODD']:
                # Sprint系は値が下がると良い
                if change_val.startswith('+'):
                    change_class = "metric-sprint-change-positive"  # 悪化（赤）
                elif change_val.startswith('-'):
                    change_class = "metric-sprint-change-negative"  # 改善（緑）
            else:
                # その他は値が上がると良い
                if change_val.startswith('+'):
                    change_class = "metric-change-positive"  # 改善（緑）
                elif change_val.startswith('-'):
                    change_class = "metric-change-negative"  # 悪化（赤）
        
        html += f"<td class='{change_class}'>{change_val}</td>"
        
        html += "</tr>"
    
    html += "</tbody></table>"
    
    return html

def create_absolute_values_chart(players_data, metric):
    """絶対値の折れ線グラフを作成（目標値ライン付き）"""
    if not players_data:
        return None
    
    fig = go.Figure()
    
    # 50人対応の色パレット
    colors = [
        '#4B5563', '#EF4444', '#10B981', '#7C3AED', '#F59E0B', 
        '#EC4899', '#14B8A6', '#F97316', '#6366F1', '#84CC16',
        '#F87171', '#34D399', '#A78BFA', '#FBBF24', '#F472B6',
        '#4DD0E1', '#FF8A65', '#9575CD', '#81C784', '#FFB74D',
        '#64B5F6', '#E57373', '#4DB6AC', '#DCE775', '#F06292',
        '#90A4AE', '#A1887F', '#FFA726', '#26C6DA', '#AB47BC',
        '#66BB6A', '#5C6BC0', '#FF7043', '#42A5F5', '#EC407A',
        '#8BC34A', '#7E57C2', '#FFA000', '#00ACC1', '#D81B60',
        '#7CB342', '#3F51B5', '#FB8C00', '#0097A7', '#C2185B',
        '#689F38', '#303F9F', '#F57C00', '#00838F', '#AD1457'
    ]
    
    for i, (player_name, data) in enumerate(players_data.items()):
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['values'],
            mode='lines+markers',
            name=player_name,
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color, line=dict(width=2, color='white')),
            hovertemplate=f'<b>{player_name}</b><br>日付: %{{x}}<br>{metric}: %{{y}}<extra></extra>'
        ))
    
    # 目標値ラインを追加
    target_values = {
        'LBM/m': 42,
        'BMI': 25,
        '20m Sprint(s)': 2.9,
        'Sprint Momentum': 600,
        'Pro Agility': 4.5,
        'CODD': 1.5,
        'BW*20m Mulch': 12000,
        'CMJ': 55,
        'BJ': 3,
        'BSQ': None,
        'BP': None,
        'Height': None,
        'Weight': None,
        'Fat%': None,
        '20m Mulch': None,
        'RJ': None
    }
    
    goal_val = target_values.get(metric)
    if goal_val is not None:
        fig.add_hline(
            y=goal_val,
            line_dash="dash",
            line_color="#DC2626",
            line_width=3,
            annotation_text=f"目標値: {goal_val}",
            annotation_position="top right",
            annotation=dict(
                font=dict(size=12, color="#DC2626"),
                bgcolor="rgba(220, 38, 38, 0.1)",
                bordercolor="#DC2626",
                borderwidth=1
            )
        )
    
    fig.update_layout(
        title=dict(
            text=f'{metric} - 絶対値推移',
            x=0.5,
            font=dict(size=14, color='#1F2937')
        ),
        xaxis=dict(title="測定日"),
        yaxis=dict(title=metric),
        height=400,
        showlegend=True,
        legend=dict(
            font=dict(size=10),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='closest',
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return fig

def create_changes_bar_chart(changes_data, metric):
    """変化量の棒グラフを作成（最新の変化のみ）"""
    if not changes_data:
        return None
    
    fig = go.Figure()
    
    # 各選手の最新の変化量のみを取得
    players = []
    latest_changes = []
    bar_colors = []
    
    # Sprint系項目は色の意味が逆転
    is_sprint_metric = metric in ['20m Sprint(s)', 'Pro Agility', 'CODD']
    
    for player_name, data in changes_data.items():
        if data['changes']:
            # 最新の変化量（リストの最後の要素）
            latest_change = data['changes'][-1]
            players.append(player_name)
            latest_changes.append(latest_change)
            
            # 色を決定
            if abs(latest_change) < 0.001:  # 変化なし
                bar_colors.append('#94A3B8')  # グレー
            elif is_sprint_metric:
                # Sprint系は値が下がると良い（緑）、上がると悪い（赤）
                if latest_change < 0:
                    bar_colors.append('#10B981')  # 緑（改善）
                else:
                    bar_colors.append('#EF4444')  # 赤（悪化）
            else:
                # その他は値が上がると良い（緑）、下がると悪い（赤）
                if latest_change > 0:
                    bar_colors.append('#10B981')  # 緑（改善）
                else:
                    bar_colors.append('#EF4444')  # 赤（悪化）
    
    if not players:
        return None
    
    fig.add_trace(go.Bar(
        x=players,
        y=latest_changes,
        marker=dict(
            color=bar_colors,
            line=dict(width=1, color='#1F2937')
        ),
        hovertemplate='<b>%{x}</b><br>変化: %{y:.2f}<extra></extra>',
        showlegend=False
    ))
    
    # ゼロ線を追加
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
    
    fig.update_layout(
        title=dict(
            text=f'{metric} - 最新変化量',
            x=0.5,
            font=dict(size=14, color='#1F2937')
        ),
        xaxis=dict(
            title="選手名",
            tickangle=45 if len(players) > 8 else 0
        ),
        yaxis=dict(title=f"{metric} 変化量"),
        height=400,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=60, b=80)
    )
    
    return fig

def create_dual_axis_chart(historical_data, primary_metric, secondary_metric, title, goal_data=None):
    """2軸グラフを作成"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if len(historical_data) < 1:
        return None
    
    try:
        historical_data = historical_data.copy()
        
        if '測定日' in historical_data.columns:
            historical_data['測定日'] = pd.to_datetime(historical_data['測定日'], errors='coerce')
            historical_data = historical_data.dropna(subset=['測定日'])
        
        if len(historical_data) < 1:
            return None
            
        historical_data = historical_data.sort_values('測定日')
        
        primary_data = historical_data.dropna(subset=[primary_metric])
        secondary_data = historical_data.dropna(subset=[secondary_metric])
        
        if len(primary_data) >= 1:
            primary_data = primary_data.copy()
            primary_data[primary_metric] = pd.to_numeric(primary_data[primary_metric], errors='coerce')
            primary_data = primary_data.dropna(subset=[primary_metric])
        
        if len(secondary_data) >= 1:
            secondary_data = secondary_data.copy()
            secondary_data[secondary_metric] = pd.to_numeric(secondary_data[secondary_metric], errors='coerce')
            secondary_data = secondary_data.dropna(subset=[secondary_metric])
        
        if len(primary_data) < 1 and len(secondary_data) < 1:
            return None
        
        fig = go.Figure()
        
        if len(primary_data) >= 1:
            fig.add_trace(
                go.Scatter(
                    x=primary_data['測定日'],
                    y=primary_data[primary_metric],
                    mode='lines+markers',
                    name=str(primary_metric),
                    line=dict(color='#4B5563', width=4),
                    marker=dict(size=10, color='#4B5563'),
                    yaxis='y',
                    hovertemplate=f'<b>{primary_metric}</b><br>日付: %{{x}}<br>値: %{{y}}<extra></extra>'
                )
            )
        
        if len(secondary_data) >= 1:
            fig.add_trace(
                go.Scatter(
                    x=secondary_data['測定日'],
                    y=secondary_data[secondary_metric],
                    mode='lines+markers',
                    name=str(secondary_metric),
                    line=dict(color='#EF4444', width=4),
                    marker=dict(size=10, color='#EF4444'),
                    yaxis='y2',
                    hovertemplate=f'<b>{secondary_metric}</b><br>日付: %{{x}}<br>値: %{{y}}<extra></extra>'
                )
            )
        
        fig.update_layout(
            title=str(title),
            xaxis_title="測定日",
            yaxis=dict(
                title=str(primary_metric),
                side='left',
                color='#4B5563'
            ),
            yaxis2=dict(
                title=str(secondary_metric),
                side='right',
                overlaying='y',
                color='#EF4444'
            ),
            height=400,
            showlegend=True,
            hovermode='closest',
            template='plotly_white'
        )
        
        return fig
        
    except Exception:
        return None

def create_triple_axis_chart(historical_data, primary_metric, secondary_metric, tertiary_metric, title, goal_data=None):
    """3軸グラフを作成（20mスプリント、アジリティ、CODD用）"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if len(historical_data) < 1:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    primary_data = historical_data.dropna(subset=[primary_metric])
    if len(primary_data) >= 1:
        fig.add_trace(
            go.Scatter(
                x=primary_data['測定日'],
                y=primary_data[primary_metric],
                mode='lines+markers',
                name=primary_metric,
                line=dict(color='#4B5563', width=4),
                marker=dict(size=10, color='#4B5563')
            ),
            secondary_y=False
        )
    
    secondary_data = historical_data.dropna(subset=[secondary_metric])
    if len(secondary_data) >= 1:
        fig.add_trace(
            go.Scatter(
                x=secondary_data['測定日'],
                y=secondary_data[secondary_metric],
                mode='lines+markers',
                name=secondary_metric,
                line=dict(color='#EF4444', width=4),
                marker=dict(size=10, color='#EF4444')
            ),
            secondary_y=False
        )
    
    tertiary_data = historical_data.dropna(subset=[tertiary_metric])
    if len(tertiary_data) >= 1:
        fig.add_trace(
            go.Scatter(
                x=tertiary_data['測定日'],
                y=tertiary_data[tertiary_metric],
                mode='lines+markers',
                name=tertiary_metric,
                line=dict(color='#10B981', width=4),
                marker=dict(size=10, color='#10B981')
            ),
            secondary_y=True
        )
    
    fig.update_yaxes(title_text=f"{primary_metric} / {secondary_metric} (秒)", secondary_y=False)
    fig.update_yaxes(title_text=f"{tertiary_metric} (秒)", secondary_y=True)
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1F2937')
        ),
        xaxis=dict(title="測定日"),
        height=300,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=60, b=40)
    )
    
    return fig

def create_single_chart(historical_data, metric, title, goal_data=None):
    """単一メトリクス用のチャート（Sprint MomentumとBW*20m Mulch用の特別処理を追加）"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if len(historical_data) < 1:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = go.Figure()
    
    if metric in ['Sprint Momentum', 'BW*20m Mulch']:
        if metric == 'Sprint Momentum' and all(col in historical_data.columns for col in ['Weight', '20m Sprint(s)']):
            calculated_data = historical_data.dropna(subset=['Weight', '20m Sprint(s)'])
            if len(calculated_data) >= 1:
                calculated_data = calculated_data.copy()
                calculated_data[metric] = calculated_data['Weight'] * calculated_data['20m Sprint(s)']
                
                fig.add_trace(go.Scatter(
                    x=calculated_data['測定日'],
                    y=calculated_data[metric],
                    mode='lines+markers',
                    name=metric,
                    line=dict(
                        color=CHART_COLOR, 
                        width=4,
                        shape='spline',
                        smoothing=0.3
                    ),
                    marker=dict(
                        size=12, 
                        line=dict(width=3, color='white'),
                        symbol='circle',
                        color=CHART_COLOR
                    ),
                ))
        
        elif metric == 'BW*20m Mulch' and all(col in historical_data.columns for col in ['Weight', '20m Mulch']):
            calculated_data = historical_data.dropna(subset=['Weight', '20m Mulch'])
            if len(calculated_data) >= 1:
                calculated_data = calculated_data.copy()
                calculated_data[metric] = calculated_data['Weight'] * calculated_data['20m Mulch']
                
                fig.add_trace(go.Scatter(
                    x=calculated_data['測定日'],
                    y=calculated_data[metric],
                    mode='lines+markers',
                    name=metric,
                    line=dict(
                        color=CHART_COLOR, 
                        width=4,
                        shape='spline',
                        smoothing=0.3
                    ),
                    marker=dict(
                        size=12, 
                        line=dict(width=3, color='white'),
                        symbol='circle',
                        color=CHART_COLOR
                    ),
                ))
    else:
        data_with_values = historical_data.dropna(subset=[metric])
        if len(data_with_values) >= 1:
            fig.add_trace(go.Scatter(
                x=data_with_values['測定日'],
                y=data_with_values[metric],
                mode='lines+markers',
                name=metric,
                line=dict(
                    color=CHART_COLOR, 
                    width=4,
                    shape='spline',
                    smoothing=0.3
                ),
                marker=dict(
                    size=12, 
                    line=dict(width=3, color='white'),
                    symbol='circle',
                    color=CHART_COLOR
                ),
            ))
        
        if goal_data is not None and not goal_data.empty:
            goal_val = safe_get_value(goal_data, metric)
            if goal_val is not None:
                fig.add_hline(
                    y=goal_val,
                    line_dash="dash",
                    line_color="#DC2626",
                    line_width=3,
                    annotation_text=f"目標値: {goal_val:.1f}",
                    annotation_position="top right"
                )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18, color='#1F2937')
        ),
        xaxis=dict(title="測定日"),
        yaxis=dict(title=metric),
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_strength_chart(historical_data, title, goal_data=None):
    """ストレングス専用チャート（BSQ & BP）"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if len(historical_data) < 1:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = go.Figure()
    
    bsq_data = historical_data.dropna(subset=['BSQ'])
    if len(bsq_data) >= 1:
        fig.add_trace(go.Scatter(
            x=bsq_data['測定日'],
            y=bsq_data['BSQ'],
            mode='lines+markers',
            name='BSQ',
            line=dict(color='#4B5563', width=4),
            marker=dict(size=10, color='#4B5563'),
        ))
        
        if goal_data is not None and not goal_data.empty:
            goal_val = safe_get_value(goal_data, 'BSQ')
            if goal_val is not None:
                fig.add_hline(
                    y=goal_val,
                    line_dash="dash",
                    line_color="#DC2626",
                    line_width=2,
                    annotation_text=f"BSQ目標: {goal_val:.1f}kg",
                    annotation_position="top left"
                )
    
    bp_data = historical_data.dropna(subset=['BP'])
    if len(bp_data) >= 1:
        fig.add_trace(go.Scatter(
            x=bp_data['測定日'],
            y=bp_data['BP'],
            mode='lines+markers',
            name='BP',
            line=dict(color='#EF4444', width=4),
            marker=dict(size=10, color='#EF4444'),
        ))
        
        if goal_data is not None and not goal_data.empty:
            goal_val = safe_get_value(goal_data, 'BP')
            if goal_val is not None:
                fig.add_hline(
                    y=goal_val,
                    line_dash="dash",
                    line_color="#F59E0B",
                    line_width=2,
                    annotation_text=f"BP目標: {goal_val:.1f}kg",
                    annotation_position="top right"
                )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1F2937')
        ),
        xaxis=dict(title="測定日"),
        yaxis=dict(title="重量 (kg)"),
        height=300,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=60, b=40)
    )
    
    return fig

def show_welcome_screen():
    """ウェルカム画面を表示"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">SR SHIBUYA 測定データ</div>
        <div class="welcome-subtitle">選手のパフォーマンスデータを分析・可視化</div>
        <p style="color: #64748B; font-size: 1rem; margin-top: 1rem;">
            サイドバーで選手名を入力してください
        </p>
    </div>
    """, unsafe_allow_html=True)

def generate_individual_feedback(player_data, comparison_data, player_name):
    """個別選手のフィードバックコメントを生成"""
    try:
        # 3つの指標のスコアを計算
        key_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        scores = {}
        
        for metric in key_metrics:
            player_val = safe_get_value(player_data, metric)
            if player_val is not None:
                score = calculate_z_score(player_val, comparison_data, metric)
                scores[metric] = score
            else:
                scores[metric] = 3  # デフォルト値
        
        # スコアを日本語名でマッピング
        japanese_scores = {
            'スプリント勢い': scores.get('Sprint Momentum', 3),
            '持久力': scores.get('BW*20m Mulch', 3),
            '筋力': scores.get('LBM/m', 3)
        }
        
        # 総合評価の計算
        valid_scores = [s for s in scores.values() if s > 0]
        overall_avg = np.mean(valid_scores) if valid_scores else 3
        
        feedback_parts = []
        
        # 導入部分
        if overall_avg >= 4.5:
            intro = f"{player_name}選手は、非常に優れたフィジカル能力を示しており、競技レベルでの更なる活躍が大いに期待できます。"
        elif overall_avg >= 4:
            intro = f"{player_name}選手は、優秀なフィジカル能力を持っており、さらなる専門性向上により一層の成長が期待できます。"
        elif overall_avg >= 3:
            intro = f"{player_name}選手は、各分野において安定した基礎能力を有しており、継続的なトレーニングで着実な成長が期待できます。"
        else:
            intro = f"{player_name}選手は、豊富な成長ポテンシャルがあり、継続的なトレーニングで確実に向上していきます。"
        
        feedback_parts.append(intro)
        
        # 優れている分野の特定
        strengths = []
        for area, score in japanese_scores.items():
            if score >= 4:
                strengths.append(area)
        
        if strengths:
            if len(strengths) == 1:
                feedback_parts.append(f"特に{strengths[0]}において優秀な能力を発揮しており、この強みを活かした競技力向上が期待できます。")
            else:
                feedback_parts.append(f"特に{strengths[0]}と{strengths[1]}において優秀な能力を発揮しており、これらの強みを軸とした更なる発展が見込まれます。")
        
        # 改善が必要な分野の特定と具体的なアドバイス
        weaknesses = []
        improvement_suggestions = []
        
        for area, score in japanese_scores.items():
            if score <= 2:
                weaknesses.append(area)
                
                if area == 'スプリント勢い':
                    improvement_suggestions.append({
                        'area': 'スプリント能力',
                        'methods': 'スタートダッシュの技術向上、股関節の可動域改善、体重移動の最適化',
                        'details': '地面からの反発力を最大限活用するため、足首の可動域を広げ、推進力を高める動作の習得'
                    })
                elif area == '持久力':
                    improvement_suggestions.append({
                        'area': '持久力',
                        'methods': '心肺機能向上トレーニング、筋持久力強化、効率的な動作パターンの習得',
                        'details': '長時間のパフォーマンス維持のため、呼吸法の改善と疲労に負けない体幹強化'
                    })
                elif area == '筋力':
                    improvement_suggestions.append({
                        'area': '筋力',
                        'methods': 'スクワットのフォーム確立、胸椎の可動域改善、全身連動性の向上',
                        'details': '基礎筋力の向上に加えて、動作の質を高めることで効率的な力発揮を実現'
                    })
        
        # 改善点のフィードバック
        if weaknesses:
            if len(weaknesses) == 1:
                feedback_parts.append(f"{weaknesses[0]}に課題が見られるため、この部分を強化することが今後の成長ポイントです。")
            else:
                feedback_parts.append(f"{weaknesses[0]}と{weaknesses[1]}に課題が見られるため、これらの部分を強化することが今後の成長ポイントです。")
            
            # 具体的なトレーニング提案
            if improvement_suggestions:
                main_suggestion = improvement_suggestions[0]
                feedback_parts.append(f"{main_suggestion['area']}の向上には{main_suggestion['methods']}が必要と考えています。特に、{main_suggestion['details']}が重要です。これらは競技パフォーマンスを向上させる基盤となります。")
        
        # バランスの取れた選手への提案（スコアが3の場合）
        balanced_areas = [area for area, score in japanese_scores.items() if score == 3]
        if len(balanced_areas) >= 2 and not weaknesses:
            feedback_parts.append("現在は各能力がバランス良く発達している段階であり、どの分野も向上の余地があります。継続的なトレーニングでさらなる成長を目指しましょう。")
        
        # 励ましのまとめ
        if weaknesses:
            primary_weakness = weaknesses[0]
            if primary_weakness == 'スプリント勢い':
                closing = "これからは、フォームの確認や可動域を高めるトレーニングに積極的に取り組み、爆発的なスプリント能力を身につけた選手へと成長していきましょう。"
            elif primary_weakness == '持久力':
                closing = "これからは、持続的な運動能力を高めるトレーニングに取り組み、試合を通じて安定したパフォーマンスを発揮できる選手へと成長していきましょう。"
            elif primary_weakness == '筋力':
                closing = "これからは、基礎筋力向上と動作の質を高めるトレーニングに積極的に取り組み、力強い動作を実現できる選手へと成長していきましょう。"
            else:
                closing = "これからは、課題となる分野を重点的に強化し、バランスの取れた総合的な能力を持つ選手へと成長していきましょう。"
        else:
            closing = "現在の優れた能力をさらに伸ばしつつ、総合的なフィジカル能力の向上を目指して取り組んでいきましょう。"
        
        feedback_parts.append(closing)
        feedback_parts.append("努力の積み重ねが必ず成果につながります。")
        
        return " ".join(feedback_parts)
        
    except Exception as e:
        return f"{player_name}選手の個別分析を実施しています。継続的なトレーニングで着実な向上を目指していきましょう。"

def main():
    # データ読み込み
    df = load_data()
    if df.empty:
        st.error("データが読み込めませんでした。SR_physicaldata.xlsxファイルが存在することを確認してください。")
        st.stop()
    
    # ページ選択を追加
    page = st.sidebar.selectbox(
        "ページ選択",
        ["個人分析", "比較分析"],
        help="分析モードを選択してください"
    )
    
    if page == "比較分析":
        show_team_analysis(df)
        return
    
    # 個人分析の場合
    st.markdown('<div class="main-header">SR SHIBUYA 測定データ</div>', 
                unsafe_allow_html=True)
    
    # サイドバー
    st.sidebar.header("選手選択")
    
    # 名前入力フィールド
    input_name = st.sidebar.text_input(
        "選手名を入力してください", 
        placeholder="例: 田中太郎",
        help="正確な選手名を入力してください"
    )
    
    if not input_name or input_name.strip() == "":
        show_welcome_screen()
        return
    
    # 名前の検証
    is_valid, message = validate_player_name(df, input_name.strip())
    
    if not is_valid:
        st.sidebar.error(message)
        show_welcome_screen()
        return
    
    # 実際の選手名を取得
    available_names = df[df['名前'] != '目標値']['名前'].dropna().unique()
    selected_name = None
    
    if input_name in available_names:
        selected_name = input_name
    else:
        for name in available_names:
            if input_name in str(name) or str(name) in input_name:
                selected_name = name
                break
    
    if not selected_name:
        st.sidebar.error("選手が見つかりませんでした。")
        return
    
    st.sidebar.success("✓ 選手が見つかりました")
    
    # 選択した選手の利用可能カテゴリーを取得
    player_categories = sorted(df[df['名前'] == selected_name]['カテゴリー'].dropna().unique())
    if len(player_categories) == 0:
        st.error(f"選手 '{selected_name}' のカテゴリーデータが見つかりません。")
        return
    
    # カテゴリー選択
    if len(player_categories) == 1:
        selected_category = player_categories[0]
        st.sidebar.info(f"カテゴリー: {selected_category}")
    else:
        selected_category = st.sidebar.selectbox("カテゴリーを選択", player_categories)
    
    # 選択された選手とカテゴリーのデータを取得
    player_data = df[(df['名前'] == selected_name) & (df['カテゴリー'] == selected_category)]
    
    if player_data.empty:
        st.error(f"選手 '{selected_name}' の {selected_category} データが見つかりません。")
        return
    
    # 設定取得
    config = get_category_config(selected_category)
    
    # 比較データ（同カテゴリーの選手データ）
    category_avg = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]
    goal_data = df[df['名前'] == '目標値']
    
    # 選手情報表示
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="player-title">{selected_name} ({selected_category})</div>', unsafe_allow_html=True)
    with col2:
        all_dates = player_data['測定日'].dropna().sort_values(ascending=False)
        if not all_dates.empty:
            latest_date = all_dates.iloc[0]
            oldest_date = all_dates.iloc[-1]
            measurement_count = len(all_dates)
            st.markdown(f'<div class="date-info">測定回数: {measurement_count}回<br>期間: {oldest_date} ～ {latest_date}</div>', unsafe_allow_html=True)
    
    # 包括的概要テーブル
    st.markdown('<div class="section-header">測定データ概要</div>', unsafe_allow_html=True)
    summary_table = create_comprehensive_summary_table(player_data, category_avg, goal_data, config)
    st.markdown(summary_table.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Key Indicators（レーダーチャート付き）
    st.markdown('<div class="key-indicator-title">Key Indicators</div>', unsafe_allow_html=True)
    
    # メトリクスとレーダーチャートを横に並べる
    col_metrics, col_radar = st.columns([3, 2])
    
    # 3つのKey Indicators
    key_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
    metric_units = {'Sprint Momentum': '', 'BW*20m Mulch': '', 'LBM/m': ''}
    
    with col_metrics:
        highlight_cols = st.columns(len(key_metrics))
        for i, metric in enumerate(key_metrics):
            with highlight_cols[i]:
                player_val = safe_get_value(player_data, metric)
                
                # スコア計算
                score = 3  # デフォルト値
                if player_val is not None:
                    score = calculate_z_score(player_val, category_avg, metric)
                
                # 表示値の準備
                display_val = format_value(player_val, metric_units.get(metric, ''), metric)
                
                # スコアに応じた色設定
                if score <= 2:
                    color_style = 'color: #DC2626; text-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);'
                elif score >= 4:
                    color_style = 'color: #059669; text-shadow: 0 2px 4px rgba(5, 150, 105, 0.3);'
                else:
                    color_style = 'color: white;'
                
                display_val_styled = f'<span style="{color_style}">{display_val}</span>'
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{metric}</div>
                    <div class="highlight-metric">{display_val_styled}</div>
                    <div class="comparison-text">スコア: {score}/5</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_radar:
        # レーダーチャートを表示
        radar_chart = create_radar_chart(player_data, category_avg, config)
        if radar_chart:
            st.plotly_chart(radar_chart, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("""
            <p style="text-align: center; color: #64748B; padding: 2rem;">
                データが不足しているため、<br>レーダーチャートを表示できません
            </p>
            """, unsafe_allow_html=True)
    
    # PDF機能
    st.write("---")
    st.write("### PDF機能")
    
    # PDFライブラリの確認
    if PDF_AVAILABLE:
        if st.button("📄 個人PDFレポート生成", type="primary", key="individual_pdf_report"):
            try:
                with st.spinner('PDFレポートを生成中...'):
                    pdf_bytes = generate_pdf_report(
                        selected_name, 
                        player_data, 
                        category_avg, 
                        config
                    )
                    
                    if pdf_bytes:
                        clean_name = selected_name.replace(" ", "_").replace("　", "_")
                        filename = f"{clean_name}_SR_SHIBUYA_レポート.pdf"
                        
                        download_link = create_download_link(pdf_bytes, filename)
                        st.markdown(download_link, unsafe_allow_html=True)
                        st.success("PDFレポートが生成されました！")
                    else:
                        st.error("PDFレポートの生成に失敗しました。")
                        
            except Exception as e:
                st.error(f"PDF生成エラー: {str(e)}")
    else:
        st.error("reportlabライブラリがインストールされていません")
        st.code("pip install reportlab")
    
    st.write("---")
    
    # 個別フィードバックコメント
    st.markdown('<div class="section-header">個別フィードバック</div>', unsafe_allow_html=True)
    
    # 3つのKey Indicatorsに基づくフィードバック生成
    generated_feedback = generate_individual_feedback(player_data, category_avg, selected_name)
    
    # セッションステートでフィードバックを管理
    feedback_key = f"feedback_{selected_name}_{selected_category}"
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = generated_feedback
    
    # 編集機能の表示
    col1, col2 = st.columns([1, 4])
    with col1:
        edit_mode = st.checkbox("編集モード", key=f"edit_{feedback_key}")
    with col2:
        if edit_mode:
            if st.button("自動生成に戻す", key=f"reset_{feedback_key}"):
                st.session_state[feedback_key] = generated_feedback
                st.rerun()
    
    if edit_mode:
        # 編集可能なテキストエリア
        edited_feedback = st.text_area(
            "フィードバック内容を編集してください：",
            value=st.session_state[feedback_key],
            height=200,
            key=f"textarea_{feedback_key}",
            help="このテキストは自由に編集できます。変更は自動的に保存されます。"
        )
        
        # 変更を保存
        if edited_feedback != st.session_state[feedback_key]:
            st.session_state[feedback_key] = edited_feedback
        
        # 編集中の表示
        st.info("編集モードが有効です。上記のテキストエリアで内容を変更できます。")
    
    # フィードバックコメントの表示
    final_feedback = st.session_state[feedback_key]
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #FEF3C7 0%, #FCD34D 30%, #F59E0B 100%);
        padding: 2rem;
        border-radius: 12px;
        border-left: 5px solid #D97706;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.15);
        line-height: 1.8;
        color: #92400E;
        font-size: 1rem;
        font-weight: 500;
    ">
        {final_feedback}
    </div>
    """, unsafe_allow_html=True)
    
    # 統合グラフセクション（セクション分けして表示）
    st.markdown('<div class="section-header">測定推移グラフ</div>', unsafe_allow_html=True)
    
    # Body Composition セクション
    st.markdown("### Body Composition")
    col1, col2 = st.columns(2)
    with col1:
        if all(col in player_data.columns for col in ['Weight', 'Fat%']):
            weight_fat_chart = create_dual_axis_chart(player_data, 'Weight', 'Fat%', 'Weight & Fat%', goal_data)
            if weight_fat_chart:
                st.plotly_chart(weight_fat_chart, use_container_width=True, config={'displayModeBar': False})
        
        if 'BMI' in player_data.columns:
            bmi_chart = create_single_chart(player_data, 'BMI', 'BMI', goal_data)
            if bmi_chart:
                st.plotly_chart(bmi_chart, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        if 'Height' in player_data.columns:
            height_chart = create_single_chart(player_data, 'Height', 'Height', goal_data)
            if height_chart:
                st.plotly_chart(height_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Quickness セクション
    st.markdown("### Quickness")
    if all(col in player_data.columns for col in ['20m Sprint(s)', 'Pro Agility', 'CODD']):
        sprint_agility_chart = create_triple_axis_chart(
            player_data, '20m Sprint(s)', 'Pro Agility', 'CODD', 
            'Sprint & Agility', goal_data
        )
        if sprint_agility_chart:
            st.plotly_chart(sprint_agility_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Jump セクション
    st.markdown("### Jump")
    col1, col2 = st.columns(2)
    with col1:
        if all(col in player_data.columns for col in ['CMJ', 'RJ']):
            jump_chart = create_dual_axis_chart(player_data, 'CMJ', 'RJ', 'CMJ & RJ', goal_data)
            if jump_chart:
                st.plotly_chart(jump_chart, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("2軸グラフの作成に失敗したため、個別グラフで表示します")
                
                cmj_data = player_data.dropna(subset=['CMJ'])
                if len(cmj_data) > 0:
                    cmj_chart = create_single_chart(player_data, 'CMJ', 'CMJ', goal_data)
                    if cmj_chart:
                        st.plotly_chart(cmj_chart, use_container_width=True, config={'displayModeBar': False})
                
                rj_data = player_data.dropna(subset=['RJ'])
                if len(rj_data) > 0:
                    rj_chart = create_single_chart(player_data, 'RJ', 'RJ', goal_data)
                    if rj_chart:
                        st.plotly_chart(rj_chart, use_container_width=True, config={'displayModeBar': False})
        else:
            missing_cols = [col for col in ['CMJ', 'RJ'] if col not in player_data.columns]
            st.warning(f"必要な列が見つかりません: {missing_cols}")
    
    with col2:
        if 'BJ' in player_data.columns:
            bj_chart = create_single_chart(player_data, 'BJ', 'BJ', goal_data)
            if bj_chart:
                st.plotly_chart(bj_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Endurance セクション
    st.markdown("### Endurance")
    if all(col in player_data.columns for col in ['20m Mulch', 'BW*20m Mulch']):
        endurance_chart = create_dual_axis_chart(
            player_data, '20m Mulch', 'BW*20m Mulch', 
            'Endurance (20m Mulch & BW*20m Mulch)', goal_data
        )
        if endurance_chart:
            st.plotly_chart(endurance_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Strength セクション
    st.markdown("### Strength")
    if all(col in player_data.columns for col in ['BSQ', 'BP']):
        strength_chart = create_strength_chart(player_data, 'Strength (BSQ & BP)', goal_data)
        if strength_chart:
            st.plotly_chart(strength_chart, use_container_width=True, config={'displayModeBar': False})

def generate_pdf_report(player_name, player_data, category_data, config):
    """個人レポートのPDF生成（黄色テーマ）"""
    if not PDF_AVAILABLE:
        return None
    
    try:
        buffer = io.BytesIO()
        
        # 日本語フォント対応
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
            japanese_font = 'HeiseiKakuGo-W5'
            english_font = 'Helvetica'
        except:
            japanese_font = 'Helvetica'
            english_font = 'Helvetica'
        
        # PDF文書の作成
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            topMargin=0.5*cm,
            bottomMargin=0.5*cm,
            leftMargin=0.6*cm, 
            rightMargin=0.6*cm,
            allowSplitting=1,
            title="SR SHIBUYA Physical Report",
            author="SR SHIBUYA"
        )
        story = []
        
        # 黄色系カラー定義
        yellow_primary = colors.Color(0.9, 0.8, 0.0)  # 濃い黄色
        yellow_secondary = colors.Color(1.0, 0.9, 0.3)  # 明るい黄色
        yellow_light = colors.Color(1.0, 0.95, 0.7)  # 薄い黄色
        
        # スタイル設定（黄色テーマ）
        title_style = ParagraphStyle(
            'CustomTitle', 
            fontName=japanese_font,
            fontSize=13,
            spaceAfter=4,
            alignment=TA_CENTER, 
            textColor=colors.Color(0.6, 0.5, 0.0)  # 濃い黄色
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading', 
            fontName=japanese_font, 
            fontSize=10,
            spaceAfter=3,
            spaceBefore=4,
            textColor=colors.Color(0.4, 0.3, 0.0),
            wordWrap='CJK'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal', 
            fontName=japanese_font, 
            fontSize=10,
            spaceAfter=2,
            leading=12,
            wordWrap='CJK'
        )
        
        # ヘッダー部分
        story.append(Paragraph("SR SHIBUYA", title_style))
        story.append(Paragraph("Physical Performance Report", title_style))
        story.append(Spacer(1, 15))
        
        # 氏名とID
        player_id = safe_get_value(player_data, 'ID', '')
        if player_id and str(player_id) != '' and str(player_id) != 'nan':
            player_info = f"Player Name: {player_name} (ID: {player_id})"
        else:
            player_info = f"Player Name: {player_name}"
        story.append(Paragraph(player_info, normal_style))
        story.append(Spacer(1, 6))
        
        # Key Indicators用の3つの指標のスコア計算
        key_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        section_scores = {}
        
        for metric in key_metrics:
            player_val = safe_get_value(player_data, metric)
            if player_val is not None:
                score = calculate_z_score(player_val, category_data, metric)
                section_scores[metric] = score
            else:
                section_scores[metric] = 3  # デフォルト値
        
        # 総合スコア計算
        valid_scores = [s for s in section_scores.values() if s > 0]
        overall_score = round(np.mean(valid_scores)) if valid_scores else 3
        
        # フィジカルスコア表示
        story.append(Paragraph("Physical Score", heading_style))
        story.append(Spacer(1, 6))
        
        # 横並びのスコア表（黄色テーマ）
        score_data = []
        score_row = []
        
        # 英語表示名のマッピング
        metric_names = {
            'Sprint Momentum': 'Sprint Momentum',
            'BW*20m Mulch': 'BW x 20m Shuttle',
            'LBM/m': 'LBM/Height'
        }
        
        for metric in key_metrics:
            display_name = metric_names.get(metric, metric)
            score = section_scores.get(metric, 3)
            score_row.extend([display_name, str(score)])
        
        score_row.extend(['Overall Score', str(overall_score)])
        score_data.append(score_row)
        
        score_table = Table([score_data[0]], colWidths=[2*cm, 1.2*cm, 2*cm, 1.2*cm, 2*cm, 1.2*cm, 2*cm, 1.2*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), yellow_light),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), japanese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, yellow_primary),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, yellow_secondary),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 8))
        
        # フィジカルバランス（三角形レーダーチャート）
        radar_chart = create_triangle_radar_chart_yellow(section_scores, overall_score)
        if radar_chart:
            chart_table = Table([[radar_chart]], colWidths=[5.7*cm])
            chart_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(chart_table)
            story.append(Spacer(1, -17))
        
        # 測定データ
        story.append(Paragraph("Measurement Data", heading_style))
        
        # 主要な測定項目（英語名に変更）- データが存在しない項目は除外
        all_key_display_metrics = [
            ('Height', 'Height', 'cm'),
            ('Weight', 'Weight', 'kg'),
            ('BMI', 'BMI', ''),
            ('Fat%', 'Body Fat%', '%'),
            ('LBM/m', 'LBM/Height', ''),
            ('20m Sprint(s)', '20m Sprint', 'sec'),
            ('Pro Agility', 'Pro Agility', 'sec'),
            ('CODD', 'CODD', 'sec'),
            ('Sprint Momentum', 'Sprint Momentum', ''),
            ('CMJ', 'CMJ', 'cm'),
            ('BJ', 'BJ', 'm'),
            ('RJ', 'RJ', ''),
            ('20m Mulch', '20m Shuttle', 'reps'),
            ('BW*20m Mulch', 'BW x 20m Shuttle', '')
        ]
        
        # データが存在する項目のみを選択
        key_display_metrics = []
        for metric_key, metric_name, unit in all_key_display_metrics:
            # プレイヤーデータまたはカテゴリーデータに存在するかチェック
            player_has_data = metric_key in player_data.columns and safe_get_value(player_data, metric_key) is not None
            category_has_data = metric_key in category_data.columns and not category_data[metric_key].isna().all()
            
            if player_has_data or category_has_data:
                key_display_metrics.append((metric_key, metric_name, unit))
        
        detail_data = [['Measurement Item', 'Latest Value', 'Previous Value', 'Change', 'Score', 'Target', 'Category Average']]
        
        # 目標値の定義（アップロードされたExcelファイルの値）
        target_values = {
            'LBM/m': 42,
            'BMI': 25,
            '20m Sprint(s)': 2.9,
            'Sprint Momentum': 600,
            'Pro Agility': 4.5,
            'CODD': 1.5,
            'BW*20m Mulch': 12000,
            'CMJ': 55,
            'BJ': 3
        }
        
        for metric_key, metric_name, unit in key_display_metrics:
            if metric_key not in player_data.columns:
                continue
                
            player_val = safe_get_value(player_data, metric_key)
            previous_val = safe_get_previous_value(player_data, metric_key)
            
            # 目標値を取得（アップロードされたファイルの値を使用）
            goal_val = target_values.get(metric_key)
            
            # 変化を計算
            change_display = ""
            if player_val is not None and previous_val is not None:
                diff = player_val - previous_val
                if metric_key == 'Fat%':
                    # Fat%の場合は×100して表示
                    if diff > 0:
                        change_display = f"+{diff * 100:.2f}%"
                    elif diff < 0:
                        change_display = f"{diff * 100:.2f}%"
                    else:
                        change_display = "0.00%"
                else:
                    # その他の項目は通常の差分表示
                    if diff > 0:
                        change_display = f"+{diff:.2f}"
                    elif diff < 0:
                        change_display = f"{diff:.2f}"
                    else:
                        change_display = "0.00"
            else:
                change_display = "-"
            
            # スコア計算
            if player_val is not None:
                score = calculate_z_score(player_val, category_data, metric_key)
                score_display = str(score)
            else:
                score_display = "N/A"
            
            # カテゴリー平均
            category_values = []
            for _, row in category_data.iterrows():
                val = safe_get_value(pd.DataFrame([row]), metric_key)
                if val is not None:
                    category_values.append(val)
            
            category_avg = np.mean(category_values) if category_values else None
            
            # Fat%の特別処理
            if metric_key == 'Fat%':
                if player_val is not None:
                    player_val_display = f"{player_val * 100:.1f}%"
                else:
                    player_val_display = "N/A"
                if previous_val is not None:
                    previous_val_display = f"{previous_val * 100:.1f}%"
                else:
                    previous_val_display = "N/A"
                if goal_val is not None:
                    goal_val_display = f"{goal_val * 100:.1f}%"
                else:
                    goal_val_display = "-"
                if category_avg is not None:
                    category_avg_display = f"{category_avg * 100:.1f}%"
                else:
                    category_avg_display = "N/A"
            else:
                player_val_display = f"{format_value(player_val)}{unit}"
                previous_val_display = f"{format_value(previous_val)}{unit}"
                goal_val_display = f"{format_value(goal_val)}{unit}" if goal_val is not None else "-"
                category_avg_display = f"{format_value(category_avg)}{unit}"
            
            detail_data.append([
                metric_name,
                player_val_display,
                previous_val_display,
                change_display,
                score_display,
                goal_val_display,
                category_avg_display
            ])
        
        detail_table = Table(detail_data, colWidths=[2.2*cm, 1.8*cm, 1.8*cm, 1.3*cm, 1.3*cm, 1.8*cm, 1.8*cm])
        
        # テーブルスタイル（黄色テーマ）
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), yellow_secondary),
            ('FONTNAME', (0, 0), (-1, -1), japanese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 5),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, yellow_primary),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, yellow_secondary),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ]
        
        # 変化列の色付けのみ適用
        for i, (metric_key, metric_name, unit) in enumerate(key_display_metrics, 1):
            if metric_key not in player_data.columns:
                continue
                
            player_val = safe_get_value(player_data, metric_key)
            previous_val = safe_get_previous_value(player_data, metric_key)
            
            # 変化列（4列目）の色付け
            if player_val is not None and previous_val is not None:
                try:
                    current_num = float(player_val)
                    previous_num = float(previous_val)
                    diff = current_num - previous_num
                    
                    if diff != 0:
                        # Sprint、Agility、CODDは値が下がると良い（赤色で改善を示す）
                        if metric_key in ['20m Sprint(s)', 'Pro Agility', 'CODD']:
                            if diff < 0:  # 値が下がった（改善）
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.red))
                            elif diff > 0:  # 値が上がった（悪化）
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.blue))
                        else:
                            # その他の項目は値が上がると良い
                            if diff > 0:  # 値が上がった（改善）
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.red))
                            elif diff < 0:  # 値が下がった（悪化）
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.blue))
                except (ValueError, TypeError):
                    pass
        
        detail_table.setStyle(TableStyle(table_style))
        story.append(detail_table)
        story.append(Spacer(1, 11))
        
        # 個別フィードバックセクションを追加
        story.append(Paragraph("個別フィードバック", heading_style))
        story.append(Spacer(1, 6))
        
        # フィードバック内容を取得（セッションステートから、または自動生成）
        feedback_key = f"feedback_{player_name}_{player_data['カテゴリー'].iloc[0] if not player_data.empty else 'unknown'}"
        
        # セッションステートからフィードバックを取得、存在しない場合は自動生成
        if hasattr(st, 'session_state') and feedback_key in st.session_state:
            feedback_text = st.session_state[feedback_key]
        else:
            # 自動生成フィードバックを使用
            feedback_text = generate_individual_feedback(player_data, category_data, player_name)
        
        # フィードバック用のスタイル
        feedback_style = ParagraphStyle(
            'FeedbackStyle', 
            fontName=japanese_font, 
            fontSize=9,
            spaceAfter=3,
            leading=13,
            alignment=TA_LEFT,
            wordWrap='CJK',
            leftIndent=0.2*cm,
            rightIndent=0.2*cm
        )
        
        # フィードバックテキストを段落に分割して追加
        feedback_paragraphs = feedback_text.split('。')
        for paragraph in feedback_paragraphs:
            if paragraph.strip():
                # 句点を追加して表示
                paragraph_text = paragraph.strip() + '。' if not paragraph.strip().endswith('。') else paragraph.strip()
                story.append(Paragraph(paragraph_text, feedback_style))
        
        story.append(Spacer(1, 32))
        
        # Key Indicators説明
        story.append(Paragraph("Key Indicators説明", heading_style))
        story.append(Spacer(1, 6))
        
        item_style = ParagraphStyle(
            'ItemStyle', 
            fontName=japanese_font, 
            fontSize=7,
            spaceAfter=1,
            leading=9,
            alignment=TA_LEFT,
            leftIndent=0.3*cm,
            wordWrap='CJK'
        )
        
        try:
            story.append(Paragraph("Sprint momentum：コンタクトの強さを表します。体重×速度（20mスプリントのタイムから算出）", item_style))
            story.append(Paragraph("　　　　　　　　　　U18卒団までに600以上が目標。", item_style))
            story.append(Spacer(1, 3))
            story.append(Paragraph("LBM/m：身長に対する除脂肪体重（脂肪以外の体重）の割合を示します。", item_style))
            story.append(Paragraph("　　　　  U18卒団までに42以上が目標。", item_style))
            story.append(Spacer(1, 3))
            story.append(Paragraph("BW*20m Mulch：体重×20mマルチシャトルランの値を示しています。体重が選手は20mマルチシャトルランが不利になるので、体重との積で評価します。", item_style))
            story.append(Paragraph("　　　　　　　　　 U18卒団までに12000以上が目標。", item_style))
        except:
            story.append(Paragraph("Key Indicators explanation (Japanese text)", item_style))
        
        # フッター
        story.append(Spacer(1, 8))
        footer_style = ParagraphStyle(
            'Footer', 
            fontName=english_font,
            fontSize=6,
            alignment=TA_CENTER, 
            textColor=colors.Color(0.4, 0.3, 0.0)
        )
        
        story.append(Paragraph("©2025 SR SHIBUYA ALL RIGHTS RESERVED", footer_style))
        
        # PDF生成
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except Exception as e:
        st.error(f"PDF生成エラー: {str(e)}")
        return None

def create_triangle_radar_chart_yellow(section_scores, overall_score):
    """黄色テーマの三角形レーダーチャートを作成"""
    try:
        from reportlab.graphics.shapes import Drawing, Polygon, String
        from reportlab.lib import colors as rl_colors
        import math
        
        # チャートサイズ
        chart_width = 5.7*cm
        chart_height = 3.3*cm
        
        drawing = Drawing(chart_width, chart_height)
        
        # 三角形の中心点と半径
        center_x = chart_width / 2
        center_y = chart_height / 2 - 0.08*cm
        radius = 1.3*cm
        
        # 三角形の頂点を計算（上向き三角形）
        angles = [90, 210, 330]  # 度数
        triangle_points = []
        for angle in angles:
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            triangle_points.extend([x, y])
        
        # レーダーチャートの外枠（5段階、黄色系）
        for level in range(1, 6):
            scale = level / 5.0
            scaled_points = []
            for i in range(0, len(triangle_points), 2):
                base_x = triangle_points[i]
                base_y = triangle_points[i+1]
                scaled_x = center_x + (base_x - center_x) * scale
                scaled_y = center_y + (base_y - center_y) * scale
                scaled_points.extend([scaled_x, scaled_y])
            
            # 三角形の描画（黄色系）
            if level < 5:
                color = rl_colors.Color(0.9, 0.8, 0.0, alpha=0.2)  # 薄い黄色
            else:
                color = rl_colors.Color(0.7, 0.6, 0.0, alpha=0.4)  # 濃い黄色
            
            triangle = Polygon(scaled_points)
            triangle.fillColor = None
            triangle.strokeColor = color
            triangle.strokeWidth = 1
            drawing.add(triangle)
        
        # データポイントの計算
        metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        scores = [
            section_scores.get('Sprint Momentum', 3),  # 上
            section_scores.get('BW*20m Mulch', 3),    # 左下  
            section_scores.get('LBM/m', 3)            # 右下
        ]
        
        data_points = []
        for i, score in enumerate(scores):
            if score > 0:
                scale = score / 5.0
                angle_rad = math.radians(angles[i])
                x = center_x + radius * scale * math.cos(angle_rad)
                y = center_y + radius * scale * math.sin(angle_rad)
                data_points.extend([x, y])
            else:
                data_points.extend([center_x, center_y])
        
        # データ三角形の描画（黄色系）
        if len(data_points) == 6:
            data_triangle = Polygon(data_points)
            data_triangle.fillColor = rl_colors.Color(0.9, 0.8, 0.0, alpha=0.3)  # 黄色系
            data_triangle.strokeColor = rl_colors.Color(0.7, 0.6, 0.0)
            data_triangle.strokeWidth = 2
            drawing.add(data_triangle)
        
        # ラベルの追加
        labels = ['Sprint Momentum', 'BW×20mシャトル', 'LBM/身長比', '総合スコア']
        scores_for_labels = [
            section_scores.get('Sprint Momentum', 3),
            section_scores.get('BW*20m Mulch', 3),
            section_scores.get('LBM/m', 3),
            overall_score
        ]
        label_positions = [
            (center_x, center_y + radius + 0.25*cm),      # 上
            (center_x - radius - 0.5*cm, center_y - radius/2),  # 左下
            (center_x + radius + 0.5*cm, center_y - radius/2),   # 右下
            (center_x, center_y - radius + 0.37*cm)       # 下部
        ]
        
        for i, (label, (x, y)) in enumerate(zip(labels, label_positions)):
            score = scores_for_labels[i]
            text = f"{label} ({score})"
            label_text = String(x, y, text)
            try:
                label_text.fontName = 'HeiseiKakuGo-W5'
            except:
                label_text.fontName = 'Helvetica'
            label_text.fontSize = 5
            label_text.textAnchor = 'middle'
            label_text.fillColor = rl_colors.Color(0.4, 0.3, 0.0)  # 濃い黄色系
            drawing.add(label_text)
        
        return drawing
        
    except Exception as e:
        return None

def create_download_link(pdf_bytes, filename):
    """PDFダウンロードリンクを作成（黄色テーマ）"""
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="text-decoration: none;">'
    href += '<div style="background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%); '
    href += 'color: white; padding: 12px 24px; border-radius: 8px; text-align: center; '
    href += 'font-weight: bold; margin: 10px 0; display: inline-block; '
    href += 'box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">'
    href += '📄 PDFレポートをダウンロード</div></a>'
    return href

if __name__ == "__main__":
    main()