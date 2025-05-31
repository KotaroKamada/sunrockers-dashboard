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
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（モダンなデザイン）
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        padding: 2.5rem;
        border-radius: 0px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 2.8rem;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.25);
        border-left: 6px solid #4F46E5;
    }
    
    .section-header {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        padding: 1.2rem 2rem;
        border-radius: 0px;
        color: white;
        font-weight: 600;
        margin: 2rem 0 1.5rem 0;
        font-size: 1.4rem;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.2);
        border-left: 4px solid #3730A3;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        padding: 2rem;
        border-radius: 0px;
        margin: 0.75rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.25);
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
        border-bottom: 3px solid #6366F1;
    }
    
    .date-info {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        padding: 1rem;
        border-radius: 8px;
        color: #3730A3;
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
        border-left: 4px solid #6366F1;
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
        color: #6366F1 !important;
    }
</style>
""", unsafe_allow_html=True)

# データ読み込み関数
@st.cache_data
def load_data():
    """CSVファイルを読み込む関数"""
    try:
        df = pd.read_csv('data.csv')
        
        # 計算列の処理
        if all(col in df.columns for col in ['Weight', '20m Mulch']):
            mask = df['BW*20m Mulch'].isna() & df['Weight'].notna() & df['20m Mulch'].notna()
            df.loc[mask, 'BW*20m Mulch'] = df.loc[mask, 'Weight'] * df.loc[mask, '20m Mulch']
        
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
        
        # Fat%の特別処理
        if column == 'Fat%':
            valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
            valid_data = valid_data[valid_data[column].astype(str).str.contains('%', na=False)]
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
        
        # 文字列の場合（Fat%のように%付きの場合も対応）
        if isinstance(value, str):
            try:
                # %記号を除去して数値変換
                clean_value = value.strip().replace('%', '')
                num_val = float(clean_value)
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
    numeric_series = pd.to_numeric(series, errors='coerce')
    clean_series = numeric_series.dropna()
    return clean_series.mean() if len(clean_series) > 0 else None

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

def create_trend_chart(historical_data, metrics, title):
    """単一項目用のトレンドチャートを作成（改善版）"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if len(historical_data) < 2:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = go.Figure()
    colors = ['#6366F1', '#8B5CF6', '#EC4899', '#06B6D4', '#10B981']
    
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
                        color=colors[i % len(colors)], 
                        width=4,
                        shape='spline',
                        smoothing=0.3
                    ),
                    marker=dict(
                        size=12, 
                        line=dict(width=3, color='white'),
                        symbol='circle'
                    ),
                    fill='tonexty' if i > 0 else None,
                    fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.1)',
                    hovertemplate='<b>%{fullData.name}</b><br>日付: %{x}<br>値: %{y:.1f}<extra></extra>'
                ))
                
                # データポイントのアノテーション追加（最新値のみ）
                latest_point = data_with_values.iloc[-1]
                latest_value = latest_point[metric]
                
                # 値を安全にフォーマット
                try:
                    if pd.isna(latest_value):
                        display_text = "N/A"
                    else:
                        # 数値に変換してフォーマット
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
                    arrowcolor=colors[i % len(colors)],
                    bgcolor="white",
                    bordercolor=colors[i % len(colors)],
                    borderwidth=2,
                    font=dict(size=12, color=colors[i % len(colors)])
                )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=22, color='#1E293B', family='Arial Black'),
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
        height=500,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(l=70, r=70, t=100, b=70),
        font=dict(family="Arial")
    )
    
    return fig

def create_multi_trend_chart(historical_data, metrics, title, units):
    """複数メトリクスのトレンドチャートを作成（改善版）"""
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
    
    rows = (len(available_metrics) + 1) // 2
    cols = min(2, len(available_metrics))
    
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=[f"<b>{metric}</b>" for metric in available_metrics],
        vertical_spacing=0.18,
        horizontal_spacing=0.15
    )
    
    colors = ['#6366F1', '#8B5CF6', '#EC4899', '#06B6D4', '#10B981', '#F59E0B']
    
    for i, metric in enumerate(available_metrics):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
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
                        color=colors[i % len(colors)], 
                        width=4,
                        shape='spline',
                        smoothing=0.3
                    ),
                    marker=dict(
                        size=10, 
                        line=dict(width=3, color='white'),
                        symbol='circle'
                    ),
                    showlegend=False,
                    hovertemplate='<b>%{fullData.name}</b><br>日付: %{x}<br>値: %{y:.1f}<extra></extra>'
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
                    # 数値に変換してフォーマット
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
                arrowcolor=colors[i % len(colors)],
                bgcolor="white",
                bordercolor=colors[i % len(colors)],
                borderwidth=2,
                font=dict(size=11, color=colors[i % len(colors)]),
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
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=22, color='#1E293B', family='Arial Black'),
            pad=dict(t=20)
        ),
        height=400 * rows,
        showlegend=False,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        margin=dict(l=70, r=70, t=100, b=70),
        font=dict(family="Arial"),
        hovermode='x unified'
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

def main():
    # ヘッダー
    st.markdown('<div class="main-header">SR SHIBUYA 測定データ</div>', 
                unsafe_allow_html=True)
    
    # データ読み込み
    df = load_data()
    if df.empty:
        st.error("データが読み込めませんでした。")
        st.stop()
    
    # サイドバー
    st.sidebar.header("選手選択")
    
    # 選手名選択
    available_names = df[df['名前'] != '目標値']['名前'].dropna().unique()
    if len(available_names) == 0:
        st.error("選手データが見つかりません。")
        st.stop()
    
    selected_name = st.sidebar.selectbox("選手名を選択", available_names)
    
    # 選択した選手の利用可能カテゴリーを取得
    player_categories = df[df['名前'] == selected_name]['カテゴリー'].dropna().unique()
    if len(player_categories) == 0:
        st.error(f"選手 '{selected_name}' のカテゴリーデータが見つかりません。")
        st.stop()
    
    # カテゴリー選択
    selected_category = st.sidebar.selectbox("カテゴリーを選択", player_categories)
    
    # デバッグ情報をサイドバーに表示
    with st.sidebar.expander("選手情報"):
        st.write(f"選択中: {selected_name} ({selected_category})")
        st.write(f"利用可能カテゴリー: {list(player_categories)}")
        
        matching_data = df[(df['名前'] == selected_name) & (df['カテゴリー'] == selected_category)]
        st.write(f"データ件数: {len(matching_data)}件")
    
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
            st.markdown(f'<div class="date-info">測定期間: {oldest_date} ~ {latest_date}</div>', unsafe_allow_html=True)
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
                        trend_fig = create_trend_chart(player_data, metrics_with_trend_data, f"{section_name} - {metrics_with_trend_data[0]} の推移")
                    else:
                        # 複数項目の場合
                        trend_fig = create_multi_trend_chart(player_data, metrics_with_trend_data, f"{section_name} の推移", section_data['units'])
                    
                    if trend_fig:
                        st.plotly_chart(trend_fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        if PLOTLY_AVAILABLE:
                            st.info("グラフの生成ができませんでした。")
                        else:
                            st.info("グラフ機能を使用するにはplotlyライブラリが必要です")
            else:
                st.info(f"推移グラフには2回以上の測定データが必要です。")
        else:
            st.info(f"{section_name} のデータがありません。")
    
    # 統計情報
    with st.expander("データ統計"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("総選手数", len(df[df['名前'] != '目標値']['名前'].unique()))
        with col2:
            st.metric("選手の測定回数", len(player_data))
        with col3:
            category_count = len(df[df['カテゴリー'] == selected_category])
            st.metric(f"{selected_category} 総測定数", category_count)

if __name__ == "__main__":
    main()