import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ページ設定
st.set_page_config(
    page_title="SR SHIBUYA 測定データ",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS（チームカラー：紫と黄色）
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #8B4CF7 0%, #F7DC6F 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 2.5rem;
        box-shadow: 0 4px 15px rgba(139, 76, 247, 0.3);
    }
    .highlight-section {
        background: linear-gradient(135deg, #F7DC6F 0%, #F1C40F 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        color: #2C1810;
        border: 4px solid #8B4CF7;
        box-shadow: 0 8px 25px rgba(139, 76, 247, 0.2);
    }
    .section-header {
        background: linear-gradient(90deg, #6B46C1 0%, #8B4CF7 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        font-size: 1.2rem;
        box-shadow: 0 4px 10px rgba(107, 70, 193, 0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #8B4CF7 0%, #6B46C1 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(139, 76, 247, 0.2);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .highlight-metric {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    .comparison-text {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 0.5rem;
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
        
        # 該当項目で有効なデータがある行を探す
        # Fat%の場合は%付き文字列も有効とする
        if column == 'Fat%':
            valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
            # さらに%付きの文字列をフィルタ
            valid_data = valid_data[valid_data[column].astype(str).str.contains('%', na=False)]
        else:
            valid_data = data.dropna(subset=[column])
        
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
    """単一項目用のトレンドチャートを作成"""
    if len(historical_data) < 2:
        return None
    
    historical_data = historical_data.sort_values('測定日')
    
    fig = go.Figure()
    colors = ['#8B4CF7', '#F7DC6F', '#FF6B6B', '#4ECDC4', '#90EE90']
    
    for i, metric in enumerate(metrics):
        if metric in historical_data.columns:
            data_with_values = historical_data.dropna(subset=[metric])
            if len(data_with_values) > 1:
                fig.add_trace(go.Scatter(
                    x=data_with_values['測定日'],
                    y=data_with_values[metric],
                    mode='lines+markers',
                    name=metric,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))
    
    fig.update_layout(
        title=title,
        xaxis_title="測定日",
        yaxis_title="値",
        hovermode='x unified',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_multi_trend_chart(historical_data, metrics, title, units):
    """複数メトリクスのトレンドチャートを作成"""
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
        subplot_titles=available_metrics,
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    colors = ['#8B4CF7', '#F7DC6F', '#FF6B6B', '#4ECDC4', '#90EE90', '#FFB6C1']
    
    for i, metric in enumerate(available_metrics):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        data_with_values = historical_data.dropna(subset=[metric])
        if len(data_with_values) > 1:
            fig.add_trace(
                go.Scatter(
                    x=data_with_values['測定日'],
                    y=data_with_values[metric],
                    mode='lines+markers',
                    name=metric,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8),
                    showlegend=False
                ),
                row=row, col=col
            )
            
            unit = units.get(metric, '')
            fig.update_yaxes(title_text=f"{metric} ({unit})" if unit else metric, row=row, col=col)
    
    fig.update_layout(
        title=title,
        height=300 * rows,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
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
    st.sidebar.header("🏃‍♂️ 選手選択")
    
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
    with st.sidebar.expander("🔍 選手情報"):
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
        st.title(f"📊 {selected_name} ({selected_category})")
    with col2:
        # データがある期間を表示
        all_dates = player_data['測定日'].dropna().sort_values(ascending=False)
        if not all_dates.empty:
            latest_date = all_dates.iloc[0]
            oldest_date = all_dates.iloc[-1]
            st.info(f"📅 測定期間: {oldest_date} ~ {latest_date}")
        else:
            st.info("📅 測定日: N/A")
    
    # 重要指標を通常のセクションとして表示（黄色い枠なし）
    st.markdown("### 🎯 重要指標")
    
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
        st.markdown(f'<div class="section-header">📈 {section_name}</div>', unsafe_allow_html=True)
        
        # テーブル表示
        metrics = section_data['metrics']
        available_metrics = [m for m in metrics if m in df.columns]
        
        if available_metrics:
            comparison_df = create_comparison_table(
                player_data, category_avg, goal_data, available_metrics, selected_category
            )
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            # デバッグ情報
            st.write("**🔍 グラフ表示デバッグ情報:**")
            metrics_with_trend_data = []
            for metric in available_metrics:
                valid_count = len(player_data.dropna(subset=[metric]))
                st.write(f"- {metric}: {valid_count}回の測定データ")
                if valid_count >= 2:
                    metrics_with_trend_data.append(metric)
            
            st.write(f"グラフ表示対象: {metrics_with_trend_data}")
            
            # トレンドグラフを表示
            if metrics_with_trend_data:
                st.write(f"**📊 {section_name} の推移グラフ**")
                
                if len(metrics_with_trend_data) == 1:
                    # 単一項目の場合
                    trend_fig = create_trend_chart(player_data, metrics_with_trend_data, f"{section_name} - {metrics_with_trend_data[0]} の推移")
                else:
                    # 複数項目の場合
                    trend_fig = create_multi_trend_chart(player_data, metrics_with_trend_data, f"{section_name} の推移", section_data['units'])
                
                if trend_fig:
                    st.plotly_chart(trend_fig, use_container_width=True)
                    st.success("✅ グラフが表示されました")
                else:
                    st.error("❌ グラフの生成に失敗しました")
            else:
                st.info(f"推移グラフには2回以上の測定データが必要です。")
        else:
            st.info(f"{section_name} のデータがありません。")
    
    # 統計情報
    with st.expander("📊 データ統計"):
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