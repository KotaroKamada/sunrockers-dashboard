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

@st.cache_data
def load_data():
    """エクセルファイルを読み込む関数"""
    try:
        df = pd.read_excel('SR_physicaldata.xlsx', sheet_name=0)
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
        
        if '測定日' in df.columns:
            df['測定日'] = pd.to_datetime(df['測定日'], errors='coerce')
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
    """安全に値を取得する関数（最新のデータを遡って取得）"""
    try:
        if column not in data.columns or data.empty:
            return default
        
        # まず基本的なフィルタリング（NaN、空文字、null値を除外）
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if valid_data.empty:
            return default
        
        # 測定日がある場合は最新のデータを取得、ない場合は最初のデータ
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
    """前回の測定値を安全に取得する関数"""
    try:
        if column not in data.columns or data.empty:
            return default
        
        # まず基本的なフィルタリング（NaN、空文字、null値を除外）
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if len(valid_data) < 2:
            return default
        
        if '測定日' in valid_data.columns:
            sorted_data = valid_data.sort_values('測定日', ascending=False)
            # 2番目に新しいデータを取得
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

def format_value(value, unit="", column_name=""):
    """値を安全にフォーマット（Fat%は×100して%表記、N/Aは空欄）"""
    if value is None or pd.isna(value):
        return ""  # N/Aを空欄に変更
    try:
        float_val = float(value)
        if column_name == 'Fat%':
            # Fat%の場合は×100して%表記
            return f"{float_val * 100:.1f}%"
        elif unit == '%' and column_name != 'Fat%':
            # 他の%項目の場合はそのまま%を付ける
            return f"{float_val:.1f}%"
        else:
            return f"{float_val:.1f}{unit}"
    except:
        return ""  # N/Aを空欄に変更

def get_measurement_date(data, column):
    """特定の項目の測定日を取得"""
    try:
        if column not in data.columns or data.empty:
            return "N/A"
        
        # まず基本的なフィルタリング
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if valid_data.empty:
            return "N/A"
        
        if '測定日' in valid_data.columns:
            latest_valid = valid_data.sort_values('測定日', ascending=False).iloc[0]
            return latest_valid['測定日']
        
        return "N/A"
        
    except Exception as e:
        return "N/A"

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
        goal_val = safe_get_value(goal_data, metric)
        
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
        
        # 測定日を取得（改善）
        measurement_date = get_measurement_date(player_data, metric)
        
        # 目標値との比較で色付け（シンプル版）
        latest_val_display = format_value(current_val, "", metric)
        
        table_data.append({
            '項目': metric,
            '最新測定値': latest_val_display,
            '前回測定値': format_value(previous_val, "", metric),
            '変化': change,
            'カテゴリー平均': format_value(avg_val, "", metric),
            '目標値': format_value(goal_val, "", metric),
            '最新測定日': measurement_date
        })
    
    return pd.DataFrame(table_data)

def create_dual_axis_chart(historical_data, primary_metric, secondary_metric, title, goal_data=None):
    """2軸グラフを作成"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if len(historical_data) < 1:
        return None
    
    try:
        historical_data = historical_data.sort_values('測定日')
        
        # 両方のメトリクスにデータがあるかチェック
        primary_data = historical_data.dropna(subset=[primary_metric])
        secondary_data = historical_data.dropna(subset=[secondary_metric])
        
        if len(primary_data) < 1 and len(secondary_data) < 1:
            return None
        
        fig = go.Figure()
        
        # プライマリ軸のデータ
        if len(primary_data) >= 1:
            fig.add_trace(
                go.Scatter(
                    x=primary_data['測定日'],
                    y=primary_data[primary_metric],
                    mode='lines+markers',
                    name=primary_metric,
                    line=dict(color='#4B5563', width=4),
                    marker=dict(size=10, color='#4B5563'),
                    yaxis='y'
                )
            )
            
            # 目標値ライン（プライマリ軸）
            if goal_data is not None and not goal_data.empty:
                try:
                    goal_val = safe_get_value(goal_data, primary_metric)
                    if goal_val is not None and pd.notna(goal_val):
                        fig.add_hline(
                            y=float(goal_val),
                            line_dash="dash",
                            line_color="#DC2626",
                            line_width=2,
                            annotation_text=f"{primary_metric}目標: {float(goal_val):.1f}",
                            annotation_position="top left"
                        )
                except:
                    pass  # 目標値ラインの追加に失敗しても継続
        
        # セカンダリ軸のデータ
        if len(secondary_data) >= 1:
            fig.add_trace(
                go.Scatter(
                    x=secondary_data['測定日'],
                    y=secondary_data[secondary_metric],
                    mode='lines+markers',
                    name=secondary_metric,
                    line=dict(color='#EF4444', width=4),
                    marker=dict(size=10, color='#EF4444'),
                    yaxis='y2'
                )
            )
        
        # レイアウト設定（エラーハンドリング強化）
        layout_config = {
            'title': {
                'text': str(title),
                'x': 0.5,
                'font': {'size': 18, 'color': '#1F2937'}
            },
            'xaxis': {'title': "測定日"},
            'yaxis': {
                'title': str(primary_metric),
                'titlefont': {'color': '#4B5563'},
                'tickfont': {'color': '#4B5563'},
                'side': 'left'
            },
            'yaxis2': {
                'title': str(secondary_metric),
                'titlefont': {'color': '#EF4444'},
                'tickfont': {'color': '#EF4444'},
                'side': 'right',
                'overlaying': 'y'
            },
            'height': 400,
            'showlegend': True,
            'plot_bgcolor': 'rgba(248, 250, 252, 0.5)',
            'paper_bgcolor': 'white',
            'hovermode': 'x unified',
            'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50}
        }
        
        fig.update_layout(**layout_config)
        
        return fig
        
    except Exception as e:
        # エラーが発生した場合はNoneを返す
        return None

def create_triple_axis_chart(historical_data, primary_metric, secondary_metric, tertiary_metric, title, goal_data=None):
    """3軸グラフを作成（20mスプリント、アジリティ、CODD用）"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if len(historical_data) < 1:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Primary axis (20m Sprint)
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
    
    # Secondary axis (Pro Agility)
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
    
    # Tertiary metric (CODD) - on secondary y-axis
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
    
    # Y軸のラベル設定
    fig.update_yaxes(title_text=f"{primary_metric} / {secondary_metric} (秒)", secondary_y=False)
    fig.update_yaxes(title_text=f"{tertiary_metric} (秒)", secondary_y=True)
    
    # レイアウト設定
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
    """単一メトリクス用のチャート"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if len(historical_data) < 1:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = go.Figure()
    
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
        
        # 目標値ライン
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
    
    # BSQデータ
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
        
        # BSQ目標値ライン
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
    
    # BPデータ
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
        
        # BP目標値ライン
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

def show_team_analysis(df):
    """比較分析画面を表示"""
    st.markdown('<div class="main-header">SR SHIBUYA 比較分析</div>', unsafe_allow_html=True)
    
    # データの前処理：BMIの再計算
    if all(col in df.columns for col in ['Height', 'Weight', 'BMI']):
        mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
               (df['Height'] > 0) & (df['Weight'] > 0) & 
               (pd.isna(df['BMI']) | (df['BMI'] == 0)))
        
        if mask.any():
            df.loc[mask, 'BMI'] = (df.loc[mask, 'Weight'] / 
                                  ((df.loc[mask, 'Height'] / 100) ** 2))
    
    # 利用可能なカテゴリーを取得
    available_categories = sorted(df['カテゴリー'].dropna().unique())
    
    # サイドバーでの設定
    st.sidebar.header("分析設定")
    
    # カテゴリー選択
    selected_category = st.sidebar.selectbox(
        "分析対象カテゴリー",
        available_categories,
        help="比較する選手のカテゴリーを選択"
    )
    
    # 該当カテゴリーの選手のみフィルタ（重複排除処理を強化）
    category_data = df[(df['カテゴリー'] == selected_category) & (df['名前'] != '目標値')].copy()
    
    # 同名選手の重複処理：最新の測定日のデータのみを保持
    if '測定日' in category_data.columns and not category_data.empty:
        # 測定日を確実にdatetime型に変換
        category_data['測定日'] = pd.to_datetime(category_data['測定日'], errors='coerce')
        
        # NaN値を持つ行を除外してから重複排除
        category_data_clean = category_data.dropna(subset=['名前', '測定日'])
        
        # 各選手の最新データのみを取得（より厳密な処理）
        latest_data = (category_data_clean
                      .sort_values(['名前', '測定日'], ascending=[True, False])
                      .groupby('名前', as_index=False)
                      .first())
        
        # 重複排除済みのデータを使用
        category_data = latest_data
        category_players = sorted(latest_data['名前'].unique())
        
    else:
        # 測定日がない場合の処理も改善
        category_players = sorted(list(set(category_data['名前'].dropna().tolist())))
        # この場合もcategory_dataを重複排除済みに更新
        unique_names = category_data['名前'].dropna().drop_duplicates()
        category_data = category_data[category_data['名前'].isin(unique_names)]
    
    # 選手選択（デフォルトで全選手選択）
    selected_players = st.sidebar.multiselect(
        f"比較する選手（最大50名まで対応）",
        category_players,
        default=category_players,  # 全選手をデフォルト選択
        help="比較したい選手を選択してください。多数の選手を同時に比較できます。"
    )
    
    # 利用可能なメトリクスを取得
    config = get_category_config(selected_category)
    all_metrics = []
    for section_data in config['sections'].values():
        all_metrics.extend(section_data['metrics'])
    
    available_metrics = []
    for metric in all_metrics:
        if metric in df.columns:
            if not category_data[metric].isna().all():
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
    
    # カテゴリー概要の表示
    st.markdown('<div class="section-header">カテゴリー概要</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("総選手数", len(category_players))
    with col2:
        st.metric("選択選手数", len(selected_players))
    with col3:
        total_measurements = len(df[(df['カテゴリー'] == selected_category) & (df['名前'].isin(selected_players))])
        st.metric("総測定回数", total_measurements)
    with col4:
        unique_dates = df[(df['カテゴリー'] == selected_category) & (df['名前'].isin(selected_players))]['測定日'].dropna().nunique()
        st.metric("測定日数", unique_dates)
    
    # セクション別グラフ表示
    display_section_charts(df, selected_players, selected_category, selected_metrics, config)
    
    # 比較テーブルの作成と表示
    st.markdown('<div class="section-header">詳細比較テーブル</div>', unsafe_allow_html=True)
    
    # 比較テーブル用のデータ作成（重複処理を適用）
    comparison_data = []
    
    for player_name in selected_players:
        player_data = df[(df['名前'] == player_name) & (df['カテゴリー'] == selected_category)]
        
        # 同名選手の場合、最新の測定日のデータを使用
        if '測定日' in player_data.columns and len(player_data) > 1:
            player_data = player_data.copy()
            player_data['測定日'] = pd.to_datetime(player_data['測定日'], errors='coerce')
            player_data = player_data.sort_values('測定日', ascending=False).iloc[:1]
        
        row_data = {'選手名': player_name}
        
        for metric in selected_metrics:
            if metric in player_data.columns:
                latest_val = safe_get_value(player_data, metric)
                row_data[metric] = format_value(latest_val, "", metric)
            else:
                row_data[metric] = ""
        
        comparison_data.append(row_data)
    
    # カテゴリー平均も追加
    avg_row_data = {'選手名': f'{selected_category} 平均'}
    
    for metric in selected_metrics:
        if metric in category_data.columns:
            avg_val = safe_mean(category_data[metric])
            avg_row_data[metric] = format_value(avg_val, "", metric)
        else:
            avg_row_data[metric] = ""
    
    comparison_data.append(avg_row_data)
    
    # 目標値も追加
    goal_data = df[df['名前'] == '目標値']
    if not goal_data.empty:
        goal_row_data = {'選手名': '目標値'}
        
        for metric in selected_metrics:
            if metric in goal_data.columns:
                goal_val = safe_get_value(goal_data, metric)
                goal_row_data[metric] = format_value(goal_val, "", metric)
            else:
                goal_row_data[metric] = ""
        
        comparison_data.append(goal_row_data)
    
    # テーブル表示
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

def display_section_charts(df, selected_players, category, selected_metrics, config):
    """セクション別のグラフを表示"""
    
    # Body Composition セクション
    body_metrics = [m for m in selected_metrics if m in config['sections']['Body Composition']['metrics']]
    if body_metrics:
        st.markdown("### Body Composition")
        display_metrics_in_columns(df, selected_players, category, body_metrics)
    
    # Quickness セクション
    quickness_metrics = [m for m in selected_metrics if m in config['sections']['Quickness']['metrics']]
    if quickness_metrics:
        st.markdown("### Quickness")
        display_metrics_in_columns(df, selected_players, category, quickness_metrics)
    
    # Jump セクション
    jump_metrics = [m for m in selected_metrics if m in config['sections']['Jump']['metrics']]
    if jump_metrics:
        st.markdown("### Jump")
        display_metrics_in_columns(df, selected_players, category, jump_metrics)
    
    # Endurance セクション
    endurance_metrics = [m for m in selected_metrics if m in config['sections']['Endurance']['metrics']]
    if endurance_metrics:
        st.markdown("### Endurance")
        display_metrics_in_columns(df, selected_players, category, endurance_metrics)
    
    # Strength セクション（存在する場合のみ）
    if 'Strength' in config['sections']:
        strength_metrics = [m for m in selected_metrics if m in config['sections']['Strength']['metrics']]
        if strength_metrics:
            st.markdown("### Strength")
            display_metrics_in_columns(df, selected_players, category, strength_metrics)

def display_metrics_in_columns(df, selected_players, category, metrics):
    """メトリクスを1行に1つずつ表示（大きなグラフ）"""
    for metric in metrics:
        chart = create_team_comparison_single_metric(df, selected_players, category, metric)
        if chart:
            st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})

def create_team_comparison_single_metric(df, selected_players, category, metric):
    """単一メトリクスの選手比較チャート"""
    if not PLOTLY_AVAILABLE:
        return None
    
    fig = go.Figure()
    
    # 50人対応の色パレット（循環使用）
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
    
    for i, player_name in enumerate(selected_players):
        player_data = df[(df['名前'] == player_name) & (df['カテゴリー'] == category)]
        
        if player_data.empty or metric not in player_data.columns:
            continue
        
        # 有効なデータのみフィルター
        valid_data = player_data.dropna(subset=[metric, '測定日'])
        
        if valid_data.empty:
            continue
        
        # 日付でソート
        valid_data = valid_data.sort_values('測定日')
        
        color = colors[i % len(colors)]
        
        # 線の太さを調整（多数の選手の場合は細くする）
        line_width = 2 if len(selected_players) > 20 else 3
        marker_size = 6 if len(selected_players) > 20 else 8
        
        fig.add_trace(go.Scatter(
            x=valid_data['測定日'],
            y=valid_data[metric],
            mode='lines+markers',
            name=player_name,
            line=dict(color=color, width=line_width),
            marker=dict(size=marker_size, color=color, line=dict(width=1, color='white')),
            hovertemplate=f'<b>{player_name}</b><br>日付: %{{x}}<br>{metric}: %{{y}}<extra></extra>'
        ))
    
    # 目標値ライン
    goal_data = df[df['名前'] == '目標値']
    if not goal_data.empty and metric in goal_data.columns:
        goal_val = safe_get_value(goal_data, metric)
        if goal_val is not None:
            fig.add_hline(
                y=goal_val,
                line_dash="dash",
                line_color="#DC2626",
                line_width=2,
                annotation_text=f"目標: {goal_val:.1f}",
                annotation_position="top right"
            )
    
    # 凡例の設定（多数の場合は調整）
    legend_config = dict(
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='rgba(0,0,0,0.1)',
        borderwidth=1
    )
    
    if len(selected_players) > 15:
        legend_config.update({
            'font': dict(size=10),
            'itemsizing': 'constant',
            'itemwidth': 30
        })
    
    fig.update_layout(
        title=dict(
            text=metric,
            x=0.5,
            font=dict(size=16, color='#1F2937')
        ),
        xaxis=dict(title="測定日"),
        yaxis=dict(title=metric),
        height=400,
        showlegend=True,
        legend=legend_config,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='closest',
        margin=dict(l=50, r=50, t=80, b=50)
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

def main():
    # データ読み込み
    df = load_data()
    if df.empty:
        st.error("データが読み込めませんでした。SR_physicaldata.xlsxファイルが存在することを確認してください。")
        st.stop()
    
    # ページ選択を簡略化（個人分析メイン）
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
    
    # 比較データ
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
    
    # Key Indicators（簡略化）
    st.markdown('<div class="key-indicator-title">Key Indicators</div>', unsafe_allow_html=True)
    
    highlight_cols = st.columns(len(config['highlight']))
    for i, (metric, unit) in enumerate(config['highlight'].items()):
        with highlight_cols[i]:
            player_val = safe_get_value(player_data, metric)
            goal_val = safe_get_value(goal_data, metric)
            
            # Fat%の場合は×100して表示
            if metric == 'Fat%' and player_val is not None:
                display_val = f"{float(player_val) * 100:.1f}%"
            else:
                display_val = format_value(player_val, unit, metric)
            
            # 目標値を超えている場合は赤色で表示
            if player_val is not None and goal_val is not None:
                try:
                    current_num = float(player_val)
                    goal_num = float(goal_val)
                    if current_num >= goal_num:
                        if metric == 'Fat%':
                            display_val = f'<span style="color: #DC2626; text-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);">{current_num * 100:.1f}%</span>'
                        else:
                            display_val = f'<span style="color: #DC2626; text-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);">{format_value(player_val, unit, metric)}</span>'
                except:
                    pass
            
            # 目標値の表示を追加
            goal_display = ""
            if goal_val is not None:
                if metric == 'Fat%':
                    goal_display = f"<br><small style='opacity: 0.7;'>目標: {float(goal_val) * 100:.1f}%</small>"
                else:
                    goal_display = f"<br><small style='opacity: 0.7;'>目標: {format_value(goal_val, unit, metric)}</small>"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{metric}</div>
                <div class="highlight-metric">{display_val}</div>
                <div class="comparison-text">{goal_display}</div>
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

if __name__ == "__main__":
    main()