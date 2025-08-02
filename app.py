import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Plotlyが利用可能かチェック
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotlyライブラリが見つかりません。グラフ機能は無効になります。requirements.txtにplotlyを追加してください。")

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
    
    .auth-container {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        padding: 3rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        border: 2px solid #F59E0B;
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.15);
    }
    
    .auth-title {
        color: #92400E;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .auth-subtitle {
        color: #B45309;
        font-size: 1.1rem;
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
        margin: 0.75rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(51, 65, 85, 0.15);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(51, 65, 85, 0.25);
    }
    
    .highlight-metric {
        font-size: 2.4rem;
        font-weight: 700;
        margin: 0.8rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .metric-label {
        font-size: 1.2rem;
        margin-bottom: 0.8rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .comparison-text {
        font-size: 1rem;
        opacity: 0.85;
        margin-top: 0.8rem;
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
        font-size: 1.1rem !important;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%) !important;
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        padding: 1rem !important;
        border: none !important;
    }
    
    .stDataFrame td {
        padding: 0.9rem !important;
        font-size: 1.1rem !important;
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
    
    /* メトリックの改善 */
    .stMetric {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #334155;
        margin: 0.5rem 0;
    }
    
    .stMetric > div {
        color: #1E293B !important;
    }
    
    .stMetric [data-testid="metric-container"] > div:first-child {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="metric-container"] > div:last-child {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
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
    
    /* 選手選択エリア */
    .player-select-area {
        background: linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #CBD5E1;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 統一されたカラーパレット（全てHeightの色に統一）
CHART_COLOR = '#4B5563'  # Gray 600 - Heightの色
CHART_COLORS = [CHART_COLOR] * 6  # 全て同じ色に統一

# チーム分析用のカラーパレット（選手別に区別するため）
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
    
    # 目標値は除外
    available_names = df[df['名前'] != '目標値']['名前'].dropna().unique()
    
    # 完全一致チェック
    if input_name in available_names:
        return True, "認証成功"
    
    # 部分一致チェック（ひらがな・カタカナ・漢字対応）
    for name in available_names:
        if input_name in str(name) or str(name) in input_name:
            return True, f"'{name}' として認識しました"
    
    return False, f"選手名 '{input_name}' が見つかりません"

# データ読み込み関数
@st.cache_data
def load_data():
    """エクセルファイルを読み込む関数"""
    try:
        # エクセルファイルを読み込み（最初のシートを使用）
        df = pd.read_excel('SR_physicaldata.xlsx', sheet_name=0)
        
        # 列名のクリーンアップ
        df.columns = df.columns.astype(str)
        
        # データ型の最適化（名前、カテゴリー、測定日以外）
        for col in df.columns:
            if col not in ['名前', 'カテゴリー', '測定日']:
                # 数値列の処理：文字列を数値に変換
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # BMIの計算を強化（HeightとWeightがある行すべてで計算）
        if all(col in df.columns for col in ['Height', 'Weight']):
            # BMI列が存在しない場合は作成
            if 'BMI' not in df.columns:
                df['BMI'] = np.nan
            
            # HeightとWeightが両方存在し、Heightが0でない行を対象
            mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
                   (df['Height'] > 0) & (df['Weight'] > 0))
            
            # BMIが欠損している行、またはすべての行でBMIを再計算
            recalc_mask = mask & (pd.isna(df['BMI']) | (df['BMI'] == 0))
            
            if recalc_mask.any():
                df.loc[recalc_mask, 'BMI'] = (df.loc[recalc_mask, 'Weight'] / 
                                             ((df.loc[recalc_mask, 'Height'] / 100) ** 2))
                
        # その他の計算列の処理
        if all(col in df.columns for col in ['Weight', '20m Mulch']):
            mask = pd.isna(df['BW*20m Mulch']) & pd.notna(df['Weight']) & pd.notna(df['20m Mulch'])
            df.loc[mask, 'BW*20m Mulch'] = df.loc[mask, 'Weight'] * df.loc[mask, '20m Mulch']
        
        # 測定日の処理
        if '測定日' in df.columns:
            df['測定日'] = pd.to_datetime(df['測定日'], errors='coerce')
            # 日付のフォーマット統一
            df['測定日'] = df['測定日'].dt.strftime('%Y-%m-%d')
        
        return df
        
    except Exception as e:
        st.error(f"データ読み込みエラー: {str(e)}")
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
                    'metrics': ['Height', 'Weight', 'BMI', 'Fat%'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Fat%': '%'}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD'],
                    'units': {'20m Sprint(s)': '秒', 'Pro Agility': '秒', 'CODD': '秒'}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch'],
                    'units': {'20m Mulch': '回'}
                },
                'Strength': {
                    'metrics': ['BSQ', 'BP'],
                    'units': {'BSQ': 'kg', 'BP': 'kg'}
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
                    'metrics': ['Height', 'Weight', 'BMI', 'Maturity'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Maturity': 'year'}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD'],
                    'units': {'20m Sprint(s)': '秒', 'Pro Agility': '秒', 'CODD': '秒'}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch'],
                    'units': {'20m Mulch': '回'}
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
                    'metrics': ['Height', 'Weight', 'BMI', 'Maturity'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Maturity': 'year'}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD', 'Side Hop(右)', 'Side Hop(左)'],
                    'units': {'20m Sprint(s)': '秒', 'Pro Agility': '秒', 'CODD': '秒', 'Side Hop(右)': '回', 'Side Hop(左)': '回'}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch'],
                    'units': {'20m Mulch': '回'}
                }
            }
        }
    }
    return config.get(category, config['U18'])

def safe_get_value(data, column, default=None):
    """安全に値を取得する関数（各項目の最新データを取得）"""
    try:
        if column not in data.columns or data.empty:
            return default
        
        # Fat%とBMIの特別処理
        if column == 'Fat%':
            valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
            valid_data = valid_data[valid_data[column].astype(str).str.contains('%', na=False)]
        elif column == 'BMI':
            # BMIの特別処理：数値データとして扱う
            valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
            # 文字列の場合は数値に変換可能なもののみ
            mask = valid_data[column].apply(lambda x: pd.to_numeric(x, errors='coerce') is not pd.NaType and not pd.isna(pd.to_numeric(x, errors='coerce')))
            valid_data = valid_data[mask]
        else:
            # 通常の項目：null、NaN、空文字列を除外
            valid_data = data[data[column].notna()]
            valid_data = valid_data[valid_data[column] != '']
            # 数値型の場合はNaNでないもの
            if data[column].dtype in ['float64', 'int64']:
                valid_data = valid_data[valid_data[column].notna()]
        
        if valid_data.empty:
            return default
        
        # 測定日でソートして最新の有効データを取得
        if '測定日' in valid_data.columns:
            latest_valid = valid_data.sort_values('測定日', ascending=False).iloc[0]
            value = latest_valid[column]
        else:
            value = valid_data.iloc[0][column]
        
        # 値の検証
        if pd.isna(value):
            return default
        
        # 数値型の場合
        if isinstance(value, (int, float, np.number)):
            if np.isfinite(value):
                return float(value)
        
        # 文字列の場合の処理
        if isinstance(value, str):
            try:
                # Fat%の場合：%記号を除去して数値変換
                if column == 'Fat%':
                    clean_value = value.strip().replace('%', '')
                    num_val = float(clean_value)
                    if np.isfinite(num_val):
                        return num_val
                # BMIや他の数値項目の場合：直接数値変換
                else:
                    num_val = float(value.strip())
                    if np.isfinite(num_val):
                        return num_val
            except (ValueError, TypeError):
                pass
        
        return default
        
    except Exception as e:
        return default

def safe_mean(series):
    """安全に平均値を計算"""
    if series.empty:
        return None
    
    # 数値に変換可能な値のみを抽出
    numeric_values = []
    for value in series:
        if pd.notna(value) and value != '' and value != 'null':
            try:
                # 文字列の場合は数値変換を試行
                if isinstance(value, str):
                    # %記号を除去してから変換
                    clean_value = str(value).strip().replace('%', '')
                    numeric_val = float(clean_value)
                else:
                    numeric_val = float(value)
                
                if np.isfinite(numeric_val):
                    numeric_values.append(numeric_val)
            except (ValueError, TypeError):
                continue
    
    return np.mean(numeric_values) if len(numeric_values) > 0 else None

def format_value(value, unit=""):
    """値を安全にフォーマット"""
    if value is None or pd.isna(value):
        return "N/A"
    try:
        return f"{float(value):.1f}{unit}"
    except:
        return "N/A"

def create_comparison_table(player_data, category_avg, goal_data, metrics, category):
    """比較テーブルを作成（各項目の最新データを使用）"""
    table_data = []
    
    for metric in metrics:
        # 各項目ごとに最新の有効データを取得
        player_val = safe_get_value(player_data, metric)
        avg_val = safe_mean(category_avg[metric]) if metric in category_avg.columns else None
        goal_val = safe_get_value(goal_data, metric)
        
        # 測定日も取得（その項目の最新測定日）
        measurement_date = "N/A"
        if player_val is not None:
            valid_data = player_data.dropna(subset=[metric])
            if not valid_data.empty and '測定日' in valid_data.columns:
                latest_valid = valid_data.sort_values('測定日', ascending=False).iloc[0]
                measurement_date = latest_valid['測定日']
        
        table_data.append({
            '項目': metric,
            '測定値': format_value(player_val),
            '測定日': measurement_date,
            f'{category}平均': format_value(avg_val),
            '目標値': format_value(goal_val)
        })
    
    return pd.DataFrame(table_data)

def create_trend_chart(historical_data, metrics, title, goal_data=None):
    """単一項目用のトレンドチャートを作成（ダークグレー、目標値ライン付き）"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if len(historical_data) < 2:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = go.Figure()
    
    for i, metric in enumerate(metrics):
        if metric in historical_data.columns:
            data_with_values = historical_data.dropna(subset=[metric])
            if len(data_with_values) > 1:
                # トレンドラインの追加
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
                    hovertemplate='<b>%{fullData.name}</b><br>日付: %{x}<br>値: %{y:.1f}<extra></extra>'
                ))
                
                # 目標値ラインの追加
                if goal_data is not None and not goal_data.empty:
                    goal_val = safe_get_value(goal_data, metric)
                    if goal_val is not None:
                        fig.add_hline(
                            y=goal_val,
                            line_dash="dash",
                            line_color="#DC2626",  # Red 600
                            line_width=3,
                            annotation_text=f"目標値: {goal_val:.1f}",
                            annotation_position="top right",
                            annotation=dict(
                                font=dict(size=12, color="#DC2626"),
                                bgcolor="rgba(255,255,255,0.8)",
                                bordercolor="#DC2626",
                                borderwidth=1
                            )
                        )
                
                # データポイントのアノテーション追加（最新値のみ）
                latest_point = data_with_values.iloc[-1]
                latest_value = latest_point[metric]
                
                # 値を安全にフォーマット
                try:
                    if pd.isna(latest_value):
                        display_text = "N/A"
                    else:
                        numeric_value = float(latest_value)
                        display_text = f"{numeric_value:.1f}"
                except (ValueError, TypeError):
                    display_text = str(latest_value)
                
                fig.add_annotation(
                    x=latest_point['測定日'],
                    y=latest_value,
                    text=display_text,
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=CHART_COLOR,
                    bgcolor="white",
                    bordercolor=CHART_COLOR,
                    borderwidth=2,
                    font=dict(size=12, color=CHART_COLOR)
                )
    
    # レスポンシブ対応の高さ設定
    base_height = 500
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20, color='#1F2937', family='Arial Black'),
            pad=dict(t=20)
        ),
        xaxis=dict(
            title="測定日",
            gridcolor='rgba(0,0,0,0.08)',
            linecolor='rgba(0,0,0,0.2)',
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=12),
            showspikes=True,
            spikecolor="gray",
            spikesnap="cursor",
            spikemode="across"
        ),
        yaxis=dict(
            title="値",
            gridcolor='rgba(0,0,0,0.08)',
            linecolor='rgba(0,0,0,0.2)',
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=12),
            showspikes=True,
            spikecolor="gray",
            spikesnap="cursor",
            spikemode="across"
        ),
        hovermode='x unified',
        height=base_height,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        font=dict(family="Arial"),
        # レスポンシブ対応
        autosize=True
    )
    
    return fig

def create_multi_trend_chart(historical_data, metrics, title, units, goal_data=None):
    """複数メトリクスのトレンドチャートを作成（ダークグレー、目標値ライン付き）"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if len(historical_data) < 2:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    available_metrics = []
    for metric in metrics:
        if metric in historical_data.columns:
            data_with_values = historical_data.dropna(subset=[metric])
            if len(data_with_values) > 1:
                available_metrics.append(metric)
    
    if not available_metrics:
        return None
    
    # レスポンシブ対応：スマホでは1列表示
    cols = min(2, len(available_metrics))
    rows = (len(available_metrics) + cols - 1) // cols
    
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=[f"<b>{metric}</b>" for metric in available_metrics],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    for i, metric in enumerate(available_metrics):
        row = (i // cols) + 1
        col = (i % cols) + 1
        
        data_with_values = historical_data.dropna(subset=[metric])
        if len(data_with_values) > 1:
            # メイントレンド
            fig.add_trace(
                go.Scatter(
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
                        size=10, 
                        line=dict(width=3, color='white'),
                        symbol='circle',
                        color=CHART_COLOR
                    ),
                    showlegend=False,
                    hovertemplate='<b>%{fullData.name}</b><br>日付: %{x}<br>値: %{y:.1f}<extra></extra>'
                ),
                row=row, col=col
            )
            
            # 目標値ラインの追加
            if goal_data is not None and not goal_data.empty:
                goal_val = safe_get_value(goal_data, metric)
                if goal_val is not None:
                    # 各サブプロットの日付範囲を取得
                    date_range = data_with_values['測定日']
                    
                    fig.add_trace(
                        go.Scatter(
                            x=[date_range.min(), date_range.max()],
                            y=[goal_val, goal_val],
                            mode='lines',
                            name=f'目標値 ({goal_val:.1f})',
                            line=dict(
                                color='#DC2626',  # Red 600
                                width=3,
                                dash='dash'
                            ),
                            showlegend=False,
                            hovertemplate=f'目標値: {goal_val:.1f}<extra></extra>'
                        ),
                        row=row, col=col
                    )
            
            # 最新値のアノテーション
            latest_point = data_with_values.iloc[-1]
            latest_value = latest_point[metric]
            
            # 値を安全にフォーマット
            try:
                if pd.isna(latest_value):
                    display_text = "N/A"
                else:
                    numeric_value = float(latest_value)
                    display_text = f"{numeric_value:.1f}"
            except (ValueError, TypeError):
                display_text = str(latest_value)
            
            fig.add_annotation(
                x=latest_point['測定日'],
                y=latest_value,
                text=display_text,
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=CHART_COLOR,
                bgcolor="white",
                bordercolor=CHART_COLOR,
                borderwidth=2,
                font=dict(size=11, color=CHART_COLOR),
                row=row, col=col
            )
            
            unit = units.get(metric, '')
            fig.update_yaxes(
                title_text=f"{unit}" if unit else "値",
                row=row, col=col,
                gridcolor='rgba(0,0,0,0.08)',
                linecolor='rgba(0,0,0,0.2)',
                title_font=dict(size=12, color='#374151'),
                tickfont=dict(size=10),
                showspikes=True,
                spikecolor="lightgray",
                spikesnap="cursor"
            )
            fig.update_xaxes(
                row=row, col=col,
                gridcolor='rgba(0,0,0,0.08)',
                linecolor='rgba(0,0,0,0.2)',
                tickfont=dict(size=10),
                showspikes=True,
                spikecolor="lightgray",
                spikesnap="cursor"
            )
    
    # レスポンシブ対応の高さ設定
    base_height = 350 * rows
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=20, color='#1F2937', family='Arial Black'),
            pad=dict(t=20)
        ),
        height=base_height,
        showlegend=False,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=80, b=50),
        font=dict(family="Arial"),
        hovermode='x unified',
        # レスポンシブ対応
        autosize=True
    )
    
    # サブプロットのタイトルスタイリング
    for i, annotation in enumerate(fig['layout']['annotations']):
        if 'text' in annotation and annotation['text'] in [f"<b>{metric}</b>" for metric in available_metrics]:
            annotation.update(
                font=dict(size=14, color='#374151', family='Arial Black'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.1)',
                borderwidth=1
            )
    
    return fig

def create_team_comparison_chart(df, selected_players, selected_metrics, selected_category):
    """チーム分析用比較チャートを作成（折れ線グラフ）"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if not selected_players or not selected_metrics:
        return None
    
    # 各選手のデータを準備
    player_data_dict = {}
    
    for player in selected_players:
        if player == f"{selected_category}平均":
            # カテゴリー平均の場合
            category_data = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]
            player_data_dict[player] = category_data
        else:
            # 個別選手の場合
            player_df = df[(df['名前'] == player) & (df['カテゴリー'] == selected_category)]
            if not player_df.empty:
                player_data_dict[player] = player_df
    
    # グラフの作成（複数メトリックの場合は各メトリックごとに個別グラフ）
    if len(selected_metrics) == 1:
        # 単一メトリックの場合は推移グラフ
        metric = selected_metrics[0]
        fig = go.Figure()
        
        for i, (player, data) in enumerate(player_data_dict.items()):
            color = TEAM_COLORS[i % len(TEAM_COLORS)]
            
            if player == f"{selected_category}平均":
                # カテゴリー平均の推移を計算
                if '測定日' in data.columns and metric in data.columns:
                    # 各測定日ごとに平均値を計算（数値変換を含む）
                    date_groups = data.groupby('測定日')[metric].apply(lambda x: safe_mean(x)).reset_index()
                    date_groups.columns = ['測定日', metric]
                    date_groups = date_groups.dropna()
                    date_groups = date_groups.sort_values('測定日')
                    
                    if len(date_groups) > 0:
                        fig.add_trace(go.Scatter(
                            x=date_groups['測定日'],
                            y=date_groups[metric],
                            mode='lines+markers',
                            name=player,
                            line=dict(color=color, width=3, dash='dash'),
                            marker=dict(size=8, color=color),
                            hovertemplate=f'<b>{player}</b><br>日付: %{{x}}<br>{metric}: %{{y:.1f}}<extra></extra>'
                        ))
            else:
                # 個別選手の推移
                if '測定日' in data.columns and metric in data.columns:
                    # データを取得して数値変換
                    data_processed = data[['測定日', metric]].copy()
                    # 数値変換
                    if metric == 'BMI':
                        data_processed[metric] = pd.to_numeric(data_processed[metric], errors='coerce')
                    elif metric == 'Fat%':
                        data_processed[metric] = data_processed[metric].astype(str).str.replace('%', '').replace('', np.nan)
                        data_processed[metric] = pd.to_numeric(data_processed[metric], errors='coerce')
                    else:
                        data_processed[metric] = pd.to_numeric(data_processed[metric], errors='coerce')
                    
                    data_with_values = data_processed.dropna(subset=[metric, '測定日'])
                    data_with_values = data_with_values.sort_values('測定日')
                    
                    if len(data_with_values) > 0:
                        fig.add_trace(go.Scatter(
                            x=data_with_values['測定日'],
                            y=data_with_values[metric],
                            mode='lines+markers',
                            name=player,
                            line=dict(color=color, width=3),
                            marker=dict(size=8, color=color),
                            hovertemplate=f'<b>{player}</b><br>日付: %{{x}}<br>{metric}: %{{y:.1f}}<extra></extra>'
                        ))
        
        # 目標値ラインの追加
        goal_data = df[df['名前'] == '目標値']
        if not goal_data.empty:
            goal_val = safe_get_value(goal_data, metric)
            if goal_val is not None:
                fig.add_hline(
                    y=goal_val,
                    line_dash="dot",
                    line_color="#DC2626",
                    line_width=2,
                    annotation_text=f"目標値: {goal_val:.1f}",
                    annotation_position="top right"
                )
        
        fig.update_layout(
            title=dict(
                text=f"{metric} の推移比較 ({selected_category})",
                x=0.5,
                font=dict(size=20, color='#1F2937', family='Arial Black')
            ),
            xaxis_title="測定日",
            yaxis_title=metric,
            height=500,
            showlegend=True,
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            hovermode='x unified'
        )
        
        return fig
    
    else:
        # 複数メトリックの場合は各メトリックごとにサブプロット
        rows = (len(selected_metrics) + 1) // 2  # 2列レイアウト
        cols = 2 if len(selected_metrics) > 1 else 1
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=[f"<b>{metric}</b>" for metric in selected_metrics],
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        # 目標値データを取得
        goal_data = df[df['名前'] == '目標値']
        
        for idx, metric in enumerate(selected_metrics):
            row = (idx // cols) + 1
            col = (idx % cols) + 1
            
            for i, (player, data) in enumerate(player_data_dict.items()):
                color = TEAM_COLORS[i % len(TEAM_COLORS)]
                
                if player == f"{selected_category}平均":
                    # カテゴリー平均の推移
                    if '測定日' in data.columns and metric in data.columns:
                        # 各測定日ごとに平均値を計算
                        date_groups = data.groupby('測定日')[metric].apply(lambda x: safe_mean(x)).reset_index()
                        date_groups.columns = ['測定日', metric]
                        date_groups = date_groups.dropna()
                        date_groups = date_groups.sort_values('測定日')
                        
                        if len(date_groups) > 0:
                            fig.add_trace(
                                go.Scatter(
                                    x=date_groups['測定日'],
                                    y=date_groups[metric],
                                    mode='lines+markers',
                                    name=player,
                                    line=dict(color=color, width=3, dash='dash'),
                                    marker=dict(size=6, color=color),
                                    showlegend=(idx == 0),  # 最初のグラフでのみ凡例表示
                                    hovertemplate=f'<b>{player}</b><br>日付: %{{x}}<br>{metric}: %{{y:.1f}}<extra></extra>'
                                ),
                                row=row, col=col
                            )
                else:
                    # 個別選手の推移
                    if '測定日' in data.columns and metric in data.columns:
                        # データを取得して数値変換
                        data_processed = data[['測定日', metric]].copy()
                        # 特定の項目の数値変換
                        if metric == 'BMI':
                            data_processed[metric] = pd.to_numeric(data_processed[metric], errors='coerce')
                        elif metric == 'Fat%':
                            data_processed[metric] = data_processed[metric].astype(str).str.replace('%', '').replace('', np.nan)
                            data_processed[metric] = pd.to_numeric(data_processed[metric], errors='coerce')
                        else:
                            data_processed[metric] = pd.to_numeric(data_processed[metric], errors='coerce')
                        
                        data_with_values = data_processed.dropna(subset=[metric, '測定日'])
                        data_with_values = data_with_values.sort_values('測定日')
                        
                        if len(data_with_values) > 0:
                            fig.add_trace(
                                go.Scatter(
                                    x=data_with_values['測定日'],
                                    y=data_with_values[metric],
                                    mode='lines+markers',
                                    name=player,
                                    line=dict(color=color, width=3),
                                    marker=dict(size=6, color=color),
                                    showlegend=(idx == 0),  # 最初のグラフでのみ凡例表示
                                    hovertemplate=f'<b>{player}</b><br>日付: %{{x}}<br>{metric}: %{{y:.1f}}<extra></extra>'
                                ),
                                row=row, col=col
                            )
            
            # 目標値ラインの追加
            if not goal_data.empty:
                goal_val = safe_get_value(goal_data, metric)
                if goal_val is not None:
                    # 各サブプロットの日付範囲を取得
                    all_dates = []
                    for player, data in player_data_dict.items():
                        if '測定日' in data.columns and metric in data.columns:
                            dates = data.dropna(subset=[metric, '測定日'])['測定日']
                            all_dates.extend(dates.tolist())
                    
                    if all_dates:
                        min_date = min(all_dates)
                        max_date = max(all_dates)
                        
                        fig.add_trace(
                            go.Scatter(
                                x=[min_date, max_date],
                                y=[goal_val, goal_val],
                                mode='lines',
                                name=f'目標値',
                                line=dict(color='#DC2626', width=2, dash='dot'),
                                showlegend=(idx == 0),
                                hovertemplate=f'目標値: {goal_val:.1f}<extra></extra>'
                            ),
                            row=row, col=col
                        )
            
            # 各サブプロットの軸設定
            fig.update_xaxes(title_text="測定日", row=row, col=col)
            fig.update_yaxes(title_text=metric, row=row, col=col)
        
        fig.update_layout(
            title=dict(
                text=f"チーム推移比較 - {', '.join(selected_metrics)} ({selected_category})",
                x=0.5,
                font=dict(size=20, color='#1F2937', family='Arial Black')
            ),
            height=400 * rows,
            showlegend=True,
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='white',
            hovermode='x unified'
        )
        
        return fig

def show_team_analysis(df):
    """比較分析画面を表示"""
    st.markdown('<div class="main-header">SR SHIBUYA 比較分析</div>', unsafe_allow_html=True)
    
    # データの前処理：BMIの再計算を確実に実行
    if all(col in df.columns for col in ['Height', 'Weight', 'BMI']):
        # HeightとWeightがあるがBMIが欠損している行を特定
        mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
               (df['Height'] > 0) & (df['Weight'] > 0) & 
               (pd.isna(df['BMI']) | (df['BMI'] == 0)))
        
        if mask.any():
            df.loc[mask, 'BMI'] = (df.loc[mask, 'Weight'] / 
                                  ((df.loc[mask, 'Height'] / 100) ** 2))
            st.sidebar.info(f"BMIを{mask.sum()}件再計算しました")
    
    # 利用可能な選手とカテゴリーを取得
    available_players = sorted(df[df['名前'] != '目標値']['名前'].dropna().unique())
    available_categories = sorted(df['カテゴリー'].dropna().unique())
    
    # サイドバーでの設定
    st.sidebar.header("分析設定")
    
    # カテゴリー選択
    selected_category = st.sidebar.selectbox(
        "分析対象カテゴリー",
        available_categories,
        help="比較する選手のカテゴリーを選択"
    )
    
    # 該当カテゴリーの選手のみフィルタ
    category_players = sorted(df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]['名前'].dropna().unique())
    
    # 選手選択（カテゴリー平均も含む）
    player_options = [f"{selected_category}平均"] + list(category_players)
    selected_players = st.sidebar.multiselect(
        "比較する選手",
        player_options,
        default=[f"{selected_category}平均"] if player_options else [],
        help="比較したい選手を複数選択（カテゴリー平均も選択可能）"
    )
    
    # 利用可能なメトリクスを取得
    config = get_category_config(selected_category)
    all_metrics = []
    for section_data in config['sections'].values():
        all_metrics.extend(section_data['metrics'])
    
    # データが存在するメトリクスのみフィルタ（より柔軟な条件）
    available_metrics = []
    for metric in all_metrics:
        if metric in df.columns:
            # そのメトリックでデータが存在するかチェック
            category_data = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]
            if not category_data[metric].isna().all():
                available_metrics.append(metric)
    
    # メトリクス選択
    selected_metrics = st.sidebar.multiselect(
        "分析する項目",
        available_metrics,
        default=available_metrics[:3] if len(available_metrics) >= 3 else available_metrics,
        help="比較したい測定項目を選択"
    )
    
    # デバッグ情報をサイドバーに表示
    with st.sidebar.expander("デバッグ情報"):
        st.write(f"**利用可能項目数:** {len(available_metrics)}")
        st.write(f"**選択項目:** {selected_metrics}")
        if 'BMI' in available_metrics:
            bmi_data = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]['BMI']
            valid_bmi = bmi_data.dropna()
            st.write(f"**BMI有効データ数:** {len(valid_bmi)}/{len(bmi_data)}")
            if len(valid_bmi) > 0:
                st.write(f"**BMI範囲:** {valid_bmi.min():.1f} - {valid_bmi.max():.1f}")
    
    # 選択内容の確認
    if not selected_players:
        st.warning("比較する選手を選択してください。")
        return
    
    if not selected_metrics:
        st.warning("分析する項目を選択してください。")
        return
    
    # 比較チャートの作成
    comparison_fig = create_team_comparison_chart(df, selected_players, selected_metrics, selected_category)
    
    if comparison_fig:
        st.plotly_chart(
            comparison_fig,
            use_container_width=True,
            config={'displayModeBar': False, 'responsive': True}
        )
    else:
        st.error("チャートを作成できませんでした。")
    
    # 詳細データテーブル
    st.markdown('<div class="section-header">詳細データ</div>', unsafe_allow_html=True)
    
    table_data = []
    for player in selected_players:
        row = {'選手名': player}
        
        if player == f"{selected_category}平均":
            # カテゴリー平均の場合
            category_data = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]
            for metric in selected_metrics:
                if metric in category_data.columns:
                    avg_val = safe_mean(category_data[metric])
                    row[metric] = format_value(avg_val)
                else:
                    row[metric] = "N/A"
        else:
            # 個別選手の場合
            player_df = df[(df['名前'] == player) & (df['カテゴリー'] == selected_category)]
            for metric in selected_metrics:
                val = safe_get_value(player_df, metric)
                row[metric] = format_value(val)
        
        table_data.append(row)
    
    comparison_df = pd.DataFrame(table_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # 統計情報
    with st.expander("分析統計"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("対象カテゴリー総選手数", len(category_players))
        with col2:
            total_measurements = len(df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')])
            st.metric("総測定数", total_measurements)
        with col3:
            st.metric("利用可能項目数", len(available_metrics))

def show_welcome_screen():
    """ウェルカム画面を表示"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">SR SHIBUYA 測定データ</div>
        <div class="welcome-subtitle">選手のパフォーマンスデータを分析・可視化</div>
        <p style="color: #64748B; font-size: 1rem; margin-top: 1rem;">
            サイドバーでページと選手名を選択してください
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # ページ選択
    page = st.sidebar.selectbox(
        "ページ選択",
        ["個人分析", "比較分析"],
        help="分析モードを選択してください"
    )
    
    # データ読み込み
    df = load_data()
    if df.empty:
        st.error("データが読み込めませんでした。SR_physicaldata.xlsxファイルが存在することを確認してください。")
        st.stop()
    
    if page == "比較分析":
        show_team_analysis(df)
        return
    
    # 個人分析の場合（既存のコード）
    # ヘッダー
    st.markdown('<div class="main-header">SR SHIBUYA 測定データ</div>', 
                unsafe_allow_html=True)
    
    # データの基本情報表示
    with st.expander("データ概要"):
        st.write(f"**総データ数:** {len(df):,} 件")
        st.write(f"**選手数:** {len(df[df['名前'] != '目標値']['名前'].dropna().unique())} 名")
        st.write(f"**カテゴリー:** {', '.join(df['カテゴリー'].dropna().unique())}")
        if '測定日' in df.columns:
            date_range = df['測定日'].dropna()
            if not date_range.empty:
                st.write(f"**測定期間:** {date_range.min()} ～ {date_range.max()}")
    
    # サイドバー
    st.sidebar.header("選手選択")
    
    # 名前入力フィールド
    input_name = st.sidebar.text_input(
        "選手名を入力してください", 
        placeholder="例: 田中太郎",
        help="正確な選手名を入力してください（部分一致も可能）"
    )
    
    # 名前が入力されていない場合はウェルカム画面を表示
    if not input_name or input_name.strip() == "":
        show_welcome_screen()
        return
    
    # 名前の検証
    is_valid, message = validate_player_name(df, input_name.strip())
    
    if not is_valid:
        st.sidebar.error(message)
        show_welcome_screen()
        
        # 類似の名前を提案
        available_names = df[df['名前'] != '目標値']['名前'].dropna().unique()
        suggestions = [name for name in available_names if input_name.lower() in str(name).lower()]
        
        if suggestions:
            with st.sidebar.expander("💡 もしかして？"):
                st.write("**似ている名前:**")
                for suggestion in suggestions[:5]:
                    st.write(f"• {suggestion}")
        
        return
    
    # 名前が有効な場合、実際の選手名を取得
    available_names = df[df['名前'] != '目標値']['名前'].dropna().unique()
    selected_name = None
    
    # 完全一致を優先
    if input_name in available_names:
        selected_name = input_name
    else:
        # 部分一致から選択
        for name in available_names:
            if input_name in str(name) or str(name) in input_name:
                selected_name = name
                break
    
    if not selected_name:
        st.sidebar.error("選手が見つかりませんでした。")
        return
    
    # 成功メッセージ
    if selected_name != input_name:
        st.sidebar.success(f"'{selected_name}' のデータを表示します")
    else:
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
    
    # 選手情報をサイドバーに表示
    with st.sidebar.expander("選手情報"):
        st.write(f"**選手名:** {selected_name}")
        st.write(f"**カテゴリー:** {selected_category}")
        st.write(f"**利用可能カテゴリー:** {', '.join(player_categories)}")
        
        matching_data = df[(df['名前'] == selected_name) & (df['カテゴリー'] == selected_category)]
        st.write(f"**データ件数:** {len(matching_data)}件")
        
        if '測定日' in matching_data.columns:
            measurement_dates = matching_data['測定日'].dropna().sort_values()
            if not measurement_dates.empty:
                st.write(f"**最初の測定:** {measurement_dates.iloc[0]}")
                st.write(f"**最新の測定:** {measurement_dates.iloc[-1]}")
    
    # 選択された選手とカテゴリーのデータを取得
    player_data = df[(df['名前'] == selected_name) & (df['カテゴリー'] == selected_category)]
    
    if player_data.empty:
        st.error(f"選手 '{selected_name}' の {selected_category} データが見つかりません。")
        return
    
    # 設定取得
    config = get_category_config(selected_category)
    
    # 比較データ
    category_avg = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')]
    goal_data = df[df['名前'] == '目標値']
    
    # 選手情報表示
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="player-title">{selected_name} ({selected_category})</div>', unsafe_allow_html=True)
    with col2:
        # データがある期間を表示
        all_dates = player_data['測定日'].dropna().sort_values(ascending=False)
        if not all_dates.empty:
            latest_date = all_dates.iloc[0]
            oldest_date = all_dates.iloc[-1]
            measurement_count = len(all_dates)
            st.markdown(f'<div class="date-info">測定回数: {measurement_count}回<br>期間: {oldest_date} ～ {latest_date}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="date-info">測定日: N/A</div>', unsafe_allow_html=True)
    
    # Key Indicator
    st.markdown('<div class="key-indicator-title">Key Indicator</div>', unsafe_allow_html=True)
    
    highlight_cols = st.columns(len(config['highlight']))
    for i, (metric, unit) in enumerate(config['highlight'].items()):
        with highlight_cols[i]:
            # 各項目の最新データを取得
            player_val = safe_get_value(player_data, metric)
            avg_val = safe_mean(category_avg[metric]) if metric in category_avg.columns else None
            goal_val = safe_get_value(goal_data, metric)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{metric}</div>
                <div class="highlight-metric">{format_value(player_val, unit)}</div>
                <div class="comparison-text">
                    平均: {format_value(avg_val, unit)} | 目標: {format_value(goal_val, unit)}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 各セクション
    for section_name, section_data in config['sections'].items():
        st.markdown(f'<div class="section-header">{section_name}</div>', unsafe_allow_html=True)
        
        # テーブル表示
        metrics = section_data['metrics']
        available_metrics = [m for m in metrics if m in df.columns]
        
        if available_metrics:
            comparison_df = create_comparison_table(
                player_data, category_avg, goal_data, available_metrics, selected_category
            )
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            # トレンドグラフ用のデータがある項目を確認
            metrics_with_trend_data = []
            for metric in available_metrics:
                # その項目で複数のデータポイントがあるかチェック
                valid_data = player_data.dropna(subset=[metric])
                if len(valid_data) >= 2:  # 2回以上の測定データがある場合のみグラフ表示
                    metrics_with_trend_data.append(metric)
            
            # トレンドグラフを表示
            if metrics_with_trend_data:
                st.markdown(f'<div class="graph-title">{section_name} の推移グラフ</div>', unsafe_allow_html=True)
                
                graph_container = st.container()
                with graph_container:
                    if len(metrics_with_trend_data) == 1:
                        # 単一項目の場合
                        trend_fig = create_trend_chart(player_data, metrics_with_trend_data, f"{section_name} - {metrics_with_trend_data[0]} の推移", goal_data)
                    else:
                        # 複数項目の場合
                        trend_fig = create_multi_trend_chart(player_data, metrics_with_trend_data, f"{section_name} の推移", section_data['units'], goal_data)
                    
                    if trend_fig:
                        st.plotly_chart(
                            trend_fig, 
                            use_container_width=True, 
                            config={
                                'displayModeBar': False,
                                'responsive': True
                            }
                        )
                    else:
                        if PLOTLY_AVAILABLE:
                            st.info("グラフの生成ができませんでした。")
                        else:
                            st.info("グラフ機能を使用するにはplotlyライブラリが必要です")
            else:
                st.info(f"推移グラフには2回以上の測定データが必要です。現在の測定回数: {len(player_data)}回")
        else:
            st.info(f"{section_name} のデータがありません。")
    
    # 統計情報
    with st.expander("データ統計"):
        col1, col2, col3 = st.columns(3)
        with col1:
            unique_players = len(df[df['名前'] != '目標値']['名前'].dropna().unique())
            st.metric("総選手数", unique_players)
        with col2:
            st.metric("選手の測定回数", len(player_data))
        with col3:
            category_count = len(df[df['カテゴリー'] == selected_category])
            st.metric(f"{selected_category} 総測定数", category_count)
    
    # フッター
    st.markdown("---")
    st.markdown(f"**選手:** {selected_name} | **データソース:** SR_physicaldata.xlsx")

if __name__ == "__main__":
    main()