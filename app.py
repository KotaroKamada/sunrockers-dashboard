import streamlit as st
import pandas as pd
import numpy as np
import warnings
import base64
import io
from datetime import datetime
warnings.filterwarnings('ignore')

# Google Sheets integration libraries
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    st.warning("Google Sheets integration libraries are not installed. Loading from Excel file.")

# Check if Plotly is available
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("Plotly library not found. Graph features will be disabled. Please add plotly to requirements.txt.")

# Check PDF libraries
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

# Page configuration
st.set_page_config(
    page_title="SR SHIBUYA Measurement Data",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (responsive design and modern styling)
st.markdown("""
<style>
    /* Basic responsive design settings */
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
        padding: 1.2rem;
        border-radius: 0px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        font-weight: 700;
        font-size: 1.8rem;
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
    
    /* Improved DataFrame styling */
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
    
    /* Improved sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }
    
    /* Sidebar multiselect in gray tones */
    [data-baseweb="select"] {
        background-color: #F8FAFC;
    }
    
    [data-baseweb="select"] > div {
        background-color: #F8FAFC;
        border-color: #334155;
    }
    
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #334155 !important;
        color: white !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] span[role="img"] {
        color: white !important;
    }
    
    /* Improved title area */
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
    
    /* Improved graph section */
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
    
    /* Responsive graph support */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    @media screen and (max-width: 768px) {
        .js-plotly-plot {
            height: 400px !important;
        }
    }
    
    /* Summary table styling */
    .summary-table {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* Radar chart styling */
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

# Unified color palette
CHART_COLOR = '#4B5563'  # Gray 600
CHART_COLORS = [CHART_COLOR] * 6

# Color palette for team analysis
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

# Simple access control by name input
def validate_player_name(df, input_name):
    """Check if the entered name exists"""
    if not input_name or input_name.strip() == "":
        return False, "Please enter a name"
    
    available_names = df[df['名前'] != 'Target']['名前'].dropna().unique()
    
    if input_name in available_names:
        return True, "Authentication successful"
    
    for name in available_names:
        if input_name in str(name) or str(name) in input_name:
            return True, f"Recognized as '{name}'"
    
    return False, f"Player name '{input_name}' not found"

@st.cache_data(ttl=300)  # Cache for 5 minutes (to reflect data updates)
def load_data():
    """Function to load data from Google Spreadsheet or Excel file"""
    
    # First, try loading from Google Spreadsheet
    if GSPREAD_AVAILABLE:
        try:
            # Get credentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Check if Streamlit Secrets is available (Streamlit Cloud environment)
            try:
                if 'gcp_service_account' in st.secrets:
                    # Streamlit Cloud environment: load from secrets
                    credentials_dict = dict(st.secrets["gcp_service_account"])
                    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                        credentials_dict, 
                        scope
                    )
                    SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "1haqC1GhKMj5KJvIUyAvTwpr9CKQtMa7hr6qGcGagSrc")
                else:
                    raise KeyError("Secrets not configured")
            except (KeyError, FileNotFoundError):
                # Local environment: load from credentials.json
                import os
                
                # Specify path to credentials.json
                credentials_path = 'credentials.json'
                
                # If not found, try absolute path
                if not os.path.exists(credentials_path):
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    credentials_path = os.path.join(current_dir, 'credentials.json')
                
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    credentials_path, 
                    scope
                )
                
                # Set spreadsheet ID
                SPREADSHEET_ID = "1haqC1GhKMj5KJvIUyAvTwpr9CKQtMa7hr6qGcGagSrc"
            
            if not SPREADSHEET_ID or SPREADSHEET_ID == "your_spreadsheet_id":
                raise ValueError("Spreadsheet ID not set")
            
            # Connect to spreadsheet
            gc = gspread.authorize(credentials)
            worksheet = gc.open_by_key(SPREADSHEET_ID).sheet1
            
            # Get data and convert to DataFrame
            data = worksheet.get_all_values()
            
            if not data or len(data) < 2:
                raise ValueError("No data in spreadsheet")
            
            # Separate headers and data
            headers = data[0]
            rows = data[1:]
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
        except Exception as e:
            st.warning(f"⚠️ Google Spreadsheet loading error: {str(e)}")
            st.info("Falling back to loading from Excel file...")
            df = load_from_excel()
            
    else:
        # If gspread is not available, load from Excel
        df = load_from_excel()
    
    if df.empty:
        return df
    
    # Data type conversion
    df.columns = df.columns.astype(str)
    
    for col in df.columns:
        if col not in ['名前', 'カテゴリー', '測定日']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # BMI calculation
    if all(col in df.columns for col in ['Height', 'Weight']):
        if 'BMI' not in df.columns:
            df['BMI'] = np.nan
        
        mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
               (df['Height'] > 0) & (df['Weight'] > 0))
        
        recalc_mask = mask & (pd.isna(df['BMI']) | (df['BMI'] == 0))
        
        if recalc_mask.any():
            df.loc[recalc_mask, 'BMI'] = (df.loc[recalc_mask, 'Weight'] / 
                                         ((df.loc[recalc_mask, 'Height'] / 100) ** 2))
    
    # BW*20m Mulch calculation
    if all(col in df.columns for col in ['Weight', '20m Mulch']):
        mask = pd.isna(df['BW*20m Mulch']) & pd.notna(df['Weight']) & pd.notna(df['20m Mulch'])
        df.loc[mask, 'BW*20m Mulch'] = df.loc[mask, 'Weight'] * df.loc[mask, '20m Mulch']
    
    # Process measurement date
    if '測定日' in df.columns:
        df['測定日'] = pd.to_datetime(df['測定日'], errors='coerce')
        df['測定日'] = df['測定日'].dt.strftime('%Y-%m-%d')
    
    return df

def load_from_excel():
    """Fallback function to load from Excel file"""
    try:
        df = pd.read_excel('SR_physicaldata.xlsx', sheet_name=0)
        return df
    except Exception as e:
        st.error(f"❌ Excel file loading error: {str(e)}")
        st.error("Please confirm that the SR_physicaldata.xlsx file exists.")
        return pd.DataFrame()

def get_category_config(category):
    """Get configuration by category"""
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
                    'units': {'20m Sprint(s)': 'sec', 'Pro Agility': 'sec', 'CODD': 'sec', 'Sprint Momentum': ''}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch', 'BW*20m Mulch'],
                    'units': {'20m Mulch': 'reps', 'BW*20m Mulch': ''}
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
                    'units': {'20m Sprint(s)': 'sec', 'Pro Agility': 'sec', 'CODD': 'sec', 'Sprint Momentum': ''}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch', 'BW*20m Mulch'],
                    'units': {'20m Mulch': 'reps', 'BW*20m Mulch': ''}
                }
            }
        },
        'U12': {
            'highlight': {
                'Weight': 'kg',
                '20m Sprint(s)': 'sec',
                'CMJ': 'cm'
            },
            'sections': {
                'Body Composition': {
                    'metrics': ['Height', 'Weight', 'BMI', 'Maturity', 'LBM/m'],
                    'units': {'Height': 'cm', 'Weight': 'kg', 'BMI': '', 'Maturity': 'year', 'LBM/m': ''}
                },
                'Quickness': {
                    'metrics': ['20m Sprint(s)', 'Pro Agility', 'CODD', 'Side Hop(R)', 'Side Hop(L)', 'Sprint Momentum'],
                    'units': {'20m Sprint(s)': 'sec', 'Pro Agility': 'sec', 'CODD': 'sec', 'Side Hop(R)': 'reps', 'Side Hop(L)': 'reps', 'Sprint Momentum': ''}
                },
                'Jump': {
                    'metrics': ['CMJ', 'BJ', 'RJ'],
                    'units': {'CMJ': 'cm', 'BJ': 'm', 'RJ': 'm'}
                },
                'Endurance': {
                    'metrics': ['20m Mulch', 'BW*20m Mulch'],
                    'units': {'20m Mulch': 'reps', 'BW*20m Mulch': ''}
                }
            }
        }
    }
    return config.get(category, config['U18'])

def safe_get_value(data, column, default=None):
    """Function to safely get values (retrieve latest data retroactively for each item) - includes Sprint Momentum and BW*20m Mulch calculations"""
    try:
        if column not in data.columns or data.empty:
            # Try calculating Sprint Momentum or BW*20m Mulch
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
        
        # Filter only data with valid values for that item
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if valid_data.empty:
            # Try calculating Sprint Momentum or BW*20m Mulch
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
        
        # If there's a measurement date, get the latest data for that item
        if '測定日' in valid_data.columns:
            # Sort by measurement date and get the latest data
            latest_valid = valid_data.sort_values('測定日', ascending=False).iloc[0]
            value = latest_valid[column]
        else:
            value = valid_data.iloc[0][column]
        
        if pd.isna(value):
            return default
        
        # For numeric types
        if isinstance(value, (int, float, np.number)):
            if np.isfinite(value):
                return float(value)
        
        # Processing for strings
        if isinstance(value, str):
            try:
                if column == 'Fat%':
                    # For Fat%, remove % sign and convert to numeric
                    clean_value = value.strip().replace('%', '')
                    num_val = float(clean_value)
                    if np.isfinite(num_val):
                        return num_val
                else:
                    # For others, convert directly to numeric
                    num_val = float(value.strip())
                    if np.isfinite(num_val):
                        return num_val
            except (ValueError, TypeError):
                # If numeric conversion fails, return as is (for string data)
                return str(value)
        
        # If none of the above apply, return as is
        return value
        
    except Exception as e:
        return default

def safe_get_previous_value(data, column, default=None):
    """Function to safely get previous measurement value (get previous data for each item)"""
    try:
        if column not in data.columns or data.empty:
            return default
        
        # Filter only data with valid values for that item
        valid_data = data[data[column].notna() & (data[column] != '') & (data[column] != 'null')]
        
        if len(valid_data) < 2:
            return default
        
        if '測定日' in valid_data.columns:
            sorted_data = valid_data.sort_values('測定日', ascending=False)
            # Get second newest data (previous value for that item)
            previous_value = sorted_data.iloc[1][column]
        else:
            previous_value = valid_data.iloc[1][column]
        
        if pd.isna(previous_value):
            return default
        
        # For numeric types
        if isinstance(previous_value, (int, float, np.number)):
            if np.isfinite(previous_value):
                return float(previous_value)
        
        # Processing for strings
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
    """Get latest and previous values for a specific item for a specific player (ID grouping supported version)"""
    try:
        # Get all data for the player (filtered by ID group)
        player_all_data = df[(df['名前'] == player_name) & (df['ID'] == id_group)]
        
        if player_all_data.empty or metric not in player_all_data.columns:
            return None, None, "-", "-"
        
        # Filter only data with valid values for that item
        valid_data = player_all_data[
            player_all_data[metric].notna() & 
            (player_all_data[metric] != '') & 
            (player_all_data[metric] != 'null')
        ].copy()
        
        if valid_data.empty:
            return None, None, "-", "-"
        
        # Sort by measurement date
        if '測定日' in valid_data.columns:
            valid_data['測定日'] = pd.to_datetime(valid_data['測定日'], errors='coerce')
            valid_data = valid_data.dropna(subset=['測定日']).sort_values('測定日', ascending=False)
        
        # Get latest value and measurement date
        latest_val = None
        latest_date = "-"
        if len(valid_data) > 0:
            latest_row = valid_data.iloc[0]
            latest_val = latest_row[metric]
            if '測定日' in latest_row and pd.notna(latest_row['測定日']):
                latest_date = latest_row['測定日'].strftime('%Y-%m-%d')
        
        # Get previous value and measurement date
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
    """Safely calculate mean value"""
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
    """Evaluate player's value with Z-score based on comparison data mean (5-level evaluation)
    
    Args:
        player_val: Player's value
        comparison_data: Comparison target data (category data for individual analysis, ID group data for comparison analysis)
        column: Item name to evaluate
    """
    try:
        if player_val is None or comparison_data.empty or column not in comparison_data.columns:
            return 3  # Default value
        
        # Get valid values from comparison data
        valid_values = []
        for _, row in comparison_data.iterrows():
            val = safe_get_value(pd.DataFrame([row]), column)
            if val is not None:
                valid_values.append(val)
        
        if len(valid_values) < 2:
            return 3  # Return median if insufficient data
        
        group_mean = np.mean(valid_values)
        group_std = np.std(valid_values, ddof=1)
        
        if group_std == 0:
            return 3
        
        z_score = (player_val - group_mean) / group_std
        
        # Reverse evaluation for Sprint, Agility, CODD as lower is better
        reverse_score_metrics = ['20m Sprint(s)', 'Pro Agility', 'CODD']
        
        if column in reverse_score_metrics:
            # Items where lower is better: 1 if +1.5SD or more, 2 if +1.5~0.5SD, 3 if +0.5SD~-0.5SD, 4 if -0.5~-1.5SD, 5 if -1.5SD or less
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
            # Items where higher is better: conventional method
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
    """Create radar chart for Key Indicators (using Sprint Momentum, BW*20m Mulch, LBM/m)"""
    if not PLOTLY_AVAILABLE:
        return None
    
    try:
        # Fixed use of 3 indicators
        radar_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        
        # Calculate values and Z-scores for each metric
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
        
        # If data is insufficient
        if len(radar_data['metrics']) < 2:
            return None
        
        # Create radar chart
        fig = go.Figure()
        
        # Player's data
        fig.add_trace(go.Scatterpolar(
            r=radar_data['z_scores'],
            theta=radar_data['metrics'],
            fill='toself',
            name='Current Level',
            line=dict(color='#4B5563', width=3),
            fillcolor='rgba(75, 85, 99, 0.3)',
            marker=dict(size=8, color='#4B5563')
        ))
        
        # Layout settings
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                    tickvals=[1, 2, 3, 4, 5],
                    ticktext=['1 (Needs Improvement)', '2 (Below Average)', '3 (Average)', '4 (Good)', '5 (Excellent)'],
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
    """Safely format value (multiply Fat% by 100 and display as %, N/A as blank)"""
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
    """Get measurement date for specific item"""
    try:
        if column not in data.columns or data.empty:
            return "-"
        
        # First basic filtering
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
    """Create comprehensive summary table including all items"""
    table_data = []
    
    all_metrics = []
    for section_data in config['sections'].values():
        all_metrics.extend(section_data['metrics'])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_metrics = []
    for metric in all_metrics:
        if metric not in seen and metric in player_data.columns:
            seen.add(metric)
            unique_metrics.append(metric)
    
    for metric in unique_metrics:
        # Get latest and previous values
        current_val = safe_get_value(player_data, metric)
        previous_val = safe_get_previous_value(player_data, metric)
        avg_val = safe_mean(category_avg[metric]) if metric in category_avg.columns else None
        goal_val = safe_get_value(goal_data, metric) if not goal_data.empty else None
        
        # Calculate change (colored, Fat% displayed as ×100)
        change = ""
        if current_val is not None and previous_val is not None:
            diff = current_val - previous_val
            if metric == 'Fat%':
                # For Fat%, display as ×100
                if diff > 0:
                    change = f'<span style="color: #DC2626;">↑ +{diff * 100:.1f}%</span>'  # Red
                elif diff < 0:
                    change = f'<span style="color: #2563EB;">↓ {diff * 100:.1f}%</span>'   # Blue
                else:
                    change = "→ 0.0%"
            else:
                # For other items, display normal difference
                if diff > 0:
                    change = f'<span style="color: #DC2626;">↑ +{diff:.1f}</span>'  # Red
                elif diff < 0:
                    change = f'<span style="color: #2563EB;">↓ {diff:.1f}</span>'   # Blue
                else:
                    change = "→ 0.0"
        
        # Get measurement date
        measurement_date = get_measurement_date(player_data, metric)
        
        # Color by comparison with target value
        latest_val_display = format_value(current_val, "", metric)
        
        table_data.append({
            'Item': metric,
            'Latest Value': latest_val_display,
            'Previous Value': format_value(previous_val, "", metric),
            'Change': change,
            'Category Average': format_value(avg_val, "", metric),
            'Target Value': format_value(goal_val, "", metric) if goal_val is not None else "",
            'Latest Measurement Date': measurement_date
        })
    
    return pd.DataFrame(table_data)

def show_team_analysis(df):
    """Display comparison analysis screen (ID grouping version)"""
    st.markdown('<div class="main-header">SR SHIBUYA Comparative Analysis</div>', unsafe_allow_html=True)
    
    # Data preprocessing: BMI recalculation
    if all(col in df.columns for col in ['Height', 'Weight', 'BMI']):
        mask = (pd.notna(df['Height']) & pd.notna(df['Weight']) & 
               (df['Height'] > 0) & (df['Weight'] > 0) & 
               (pd.isna(df['BMI']) | (df['BMI'] == 0)))
        
        if mask.any():
            df.loc[mask, 'BMI'] = (df.loc[mask, 'Weight'] / 
                                  ((df.loc[mask, 'Height'] / 100) ** 2))
    
    # Get available ID groups
    available_ids = sorted(df['ID'].dropna().unique())
    
    # Settings in sidebar
    st.sidebar.header("Analysis Settings")
    
    # ID group selection
    selected_id = st.sidebar.selectbox(
        "Target ID Group for Analysis",
        available_ids,
        help="Select the ID group of players to compare"
    )
    
    # Filter only players in the ID group (enhanced duplicate removal processing)
    id_group_data = df[(df['ID'] == selected_id) & (df['名前'] != 'Target')].copy()
    
    # Duplicate handling for same-name players: keep only data with latest measurement date
    if '測定日' in id_group_data.columns and not id_group_data.empty:
        # Ensure measurement date is converted to datetime type
        id_group_data['測定日'] = pd.to_datetime(id_group_data['測定日'], errors='coerce')
        
        # Remove rows with NaN values, then remove duplicates
        id_group_data_clean = id_group_data.dropna(subset=['名前', '測定日'])
        
        # Get only latest data for each player (more rigorous processing)
        latest_data = (id_group_data_clean
                      .sort_values(['名前', '測定日'], ascending=[True, False])
                      .groupby('名前', as_index=False)
                      .first())
        
        # Use deduplicated data
        id_group_data = latest_data
        id_group_players = sorted(latest_data['名前'].unique())
        
    else:
        # Improved processing when measurement date is not available
        id_group_players = sorted(list(set(id_group_data['名前'].dropna().tolist())))
        # Update id_group_data to deduplicated version in this case too
        unique_names = id_group_data['名前'].dropna().drop_duplicates()
        id_group_data = id_group_data[id_group_data['名前'].isin(unique_names)]
    
    # Player selection (all players selected by default)
    selected_players = st.sidebar.multiselect(
        f"Players to Compare (up to 50 players supported)",
        id_group_players,
        default=id_group_players,  # All players selected by default
        help="Select the players you want to compare. You can compare multiple players simultaneously."
    )
    
    # Get available metrics
    all_metrics = ['Height', 'Weight', 'BMI', 'Fat%', 'LBM/m', '20m Sprint(s)', 
                   'Pro Agility', 'CODD', 'Sprint Momentum', 'CMJ', 'BJ', 'RJ', 
                   '20m Mulch', 'BW*20m Mulch', 'BSQ', 'BP']
    
    available_metrics = []
    for metric in all_metrics:
        if metric in df.columns:
            if not id_group_data[metric].isna().all():
                available_metrics.append(metric)
    
    # Metric selection
    selected_metrics = st.sidebar.multiselect(
        "Items to Analyze",
        available_metrics,
        default=available_metrics[:6] if len(available_metrics) >= 6 else available_metrics,
        help="Select measurement items to compare"
    )
    
    if not selected_players:
        st.warning("Please select players to compare.")
        return
    
    if not selected_metrics:
        st.warning("Please select items to analyze.")
        return
    
    # Detailed graph section
    st.markdown('<div class="section-header">Detailed Analysis Graphs</div>', unsafe_allow_html=True)
    
    # Create graphs for each selected item
    create_detailed_analysis_charts(df, selected_players, selected_id, selected_metrics)

def create_detailed_analysis_charts(df, selected_players, id_group, selected_metrics):
    """Create absolute value and change graphs for each selected item (ID grouping supported version)"""
    if not PLOTLY_AVAILABLE:
        st.warning("Plotly is not available, so graphs cannot be displayed.")
        return
    
    for metric in selected_metrics:
        st.markdown(f"### {metric}")
        
        # Collect data for each player
        players_data = {}
        changes_data = {}
        
        for player_name in selected_players:
            # Get all data for the player (only valid data for each item, filtered by ID)
            player_all_data = df[(df['名前'] == player_name) & (df['ID'] == id_group)]
            
            if player_all_data.empty or metric not in player_all_data.columns:
                continue
            
            # Filter only data with valid values for that item
            valid_data = player_all_data[
                player_all_data[metric].notna() & 
                (player_all_data[metric] != '') & 
                (player_all_data[metric] != 'null')
            ].copy()
            
            if valid_data.empty:
                continue
            
            # Sort by measurement date to create time series data
            if '測定日' in valid_data.columns:
                valid_data['測定日'] = pd.to_datetime(valid_data['測定日'], errors='coerce')
                valid_data = valid_data.dropna(subset=['測定日']).sort_values('測定日')
            
            if len(valid_data) == 0:
                continue
            
            # Absolute value data
            players_data[player_name] = {
                'dates': valid_data['測定日'].tolist() if '測定日' in valid_data.columns else list(range(len(valid_data))),
                'values': valid_data[metric].tolist()
            }
            
            # Change data (change from previous to current)
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
        
        # Display 2 graphs vertically (full use of horizontal width)
        # Line graph of absolute values
        abs_chart = create_absolute_values_chart(players_data, metric)
        if abs_chart:
            st.plotly_chart(abs_chart, use_container_width=True, config={'displayModeBar': False})
        
        # Bar graph of changes
        change_chart = create_changes_bar_chart(changes_data, metric)
        if change_chart:
            st.plotly_chart(change_chart, use_container_width=True, config={'displayModeBar': False})
        
        # Add detailed table for that item
        metric_detail_table = create_metric_detail_table(df, selected_players, id_group, metric)
        if not metric_detail_table.empty:
            st.markdown(f"**{metric} - Detailed Data**")
            
            # Display as styled HTML table
            metric_table_html = create_metric_table_html(metric_detail_table, metric)
            st.markdown(metric_table_html, unsafe_allow_html=True)
        
        st.markdown("---")  # Separator line between items

def create_metric_detail_table(df, selected_players, id_group, metric):
    """Create detailed table for specific item (ID grouping supported version)"""
    table_data = []
    
    for player_name in selected_players:
        # Get latest and previous data for each item
        latest_val, previous_val, latest_date, previous_date = safe_get_latest_and_previous_for_player(
            df, player_name, id_group, metric
        )
        
        # Get player's ID
        player_all_data = df[(df['名前'] == player_name) & (df['ID'] == id_group)]
        player_id = safe_get_value(player_all_data, 'ID', '') if not player_all_data.empty else ''
        
        # Calculate change
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
        
        # Calculate score
        if latest_val is not None:
            id_group_data = df[(df['ID'] == id_group) & (df['名前'] != 'Target')]
            score = calculate_z_score(latest_val, id_group_data, metric)
        else:
            score = "-"
        
        table_data.append({
            'Player Name': player_name,
            'ID': player_id if player_id != '' else '-',
            'Latest Value': format_value(latest_val, "", metric) if latest_val is not None else "-",
            'Latest Date': latest_date,
            'Previous Value': format_value(previous_val, "", metric) if previous_val is not None else "-",
            'Previous Date': previous_date,
            'Change': change_display,
            'Score': score
        })
    
    return pd.DataFrame(table_data)

def create_metric_table_html(df, metric):
    """Create HTML for item-specific detail table"""
    if df.empty:
        return "<p>No data available</p>"
    
    # Start of table
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
    
    # Header row
    html += """<thead><tr>
        <th>Player Name</th>
        <th>ID</th>
        <th>Latest Value</th>
        <th>Previous Value</th>
        <th>Change</th>
    </tr></thead>"""
    
    # Data rows
    html += "<tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        
        # Player name
        html += f"<td class='metric-player-name'>{row['Player Name']}</td>"
        
        # ID
        html += f"<td>{row['ID']}</td>"
        
        # Latest value
        html += f"<td>{row['Latest Value']}</td>"
        
        # Previous value
        html += f"<td>{row['Previous Value']}</td>"
        
        # Change (colored)
        change_val = row['Change']
        change_class = ""
        if change_val != "-" and change_val != "0.00" and change_val != "0.00%":
            if metric in ['20m Sprint(s)', 'Pro Agility', 'CODD']:
                # For Sprint metrics, lower values are better
                if change_val.startswith('+'):
                    change_class = "metric-sprint-change-positive"  # Worse (red)
                elif change_val.startswith('-'):
                    change_class = "metric-sprint-change-negative"  # Better (green)
            else:
                # For others, higher values are better
                if change_val.startswith('+'):
                    change_class = "metric-change-positive"  # Better (green)
                elif change_val.startswith('-'):
                    change_class = "metric-change-negative"  # Worse (red)
        
        html += f"<td class='{change_class}'>{change_val}</td>"
        
        html += "</tr>"
    
    html += "</tbody></table>"
    
    return html

def create_absolute_values_chart(players_data, metric):
    """Create line graph of absolute values (with target value line)"""
    if not players_data:
        return None
    
    fig = go.Figure()
    
    # Color palette for 50 players
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
            hovertemplate=f'<b>{player_name}</b><br>Date: %{{x}}<br>{metric}: %{{y}}<extra></extra>'
        ))
    
    # Add target value line
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
            annotation_text=f"Target: {goal_val}",
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
            text=f'{metric} - Absolute Value Trend',
            x=0.5,
            font=dict(size=14, color='#1F2937')
        ),
        xaxis=dict(title="Measurement Date"),
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
    """Create bar graph of changes (latest change only)"""
    if not changes_data:
        return None
    
    fig = go.Figure()
    
    # Get only latest change for each player
    players = []
    latest_changes = []
    bar_colors = []
    
    # For sprint metrics, color meaning is reversed
    is_sprint_metric = metric in ['20m Sprint(s)', 'Pro Agility', 'CODD']
    
    for player_name, data in changes_data.items():
        if data['changes']:
            # Latest change (last element of list)
            latest_change = data['changes'][-1]
            players.append(player_name)
            latest_changes.append(latest_change)
            
            # Determine color
            if abs(latest_change) < 0.001:  # No change
                bar_colors.append('#94A3B8')  # Gray
            elif is_sprint_metric:
                # For sprint metrics, lower is better (green), higher is worse (red)
                if latest_change < 0:
                    bar_colors.append('#10B981')  # Green (improved)
                else:
                    bar_colors.append('#EF4444')  # Red (worsened)
            else:
                # For others, higher is better (green), lower is worse (red)
                if latest_change > 0:
                    bar_colors.append('#10B981')  # Green (improved)
                else:
                    bar_colors.append('#EF4444')  # Red (worsened)
    
    if not players:
        return None
    
    fig.add_trace(go.Bar(
        x=players,
        y=latest_changes,
        marker=dict(
            color=bar_colors,
            line=dict(width=1, color='#1F2937')
        ),
        hovertemplate='<b>%{x}</b><br>Change: %{y:.2f}<extra></extra>',
        showlegend=False
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1)
    
    fig.update_layout(
        title=dict(
            text=f'{metric} - Latest Change',
            x=0.5,
            font=dict(size=14, color='#1F2937')
        ),
        xaxis=dict(
            title="Player Name",
            tickangle=45 if len(players) > 8 else 0
        ),
        yaxis=dict(title=f"{metric} Change"),
        height=400,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=60, b=80)
    )
    
    return fig

def create_dual_axis_chart(historical_data, primary_metric, secondary_metric, title, goal_data=None):
    """Create dual-axis graph"""
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
                    hovertemplate=f'<b>{primary_metric}</b><br>Date: %{{x}}<br>Value: %{{y}}<extra></extra>'
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
                    hovertemplate=f'<b>{secondary_metric}</b><br>Date: %{{x}}<br>Value: %{{y}}<extra></extra>'
                )
            )
        
        fig.update_layout(
            title=str(title),
            xaxis_title="Measurement Date",
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
    """Create triple-axis graph (for 20m Sprint, Agility, CODD)"""
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
    
    fig.update_yaxes(title_text=f"{primary_metric} / {secondary_metric} (sec)", secondary_y=False)
    fig.update_yaxes(title_text=f"{tertiary_metric} (sec)", secondary_y=True)
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1F2937')
        ),
        xaxis=dict(title="Measurement Date"),
        height=300,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=60, b=40)
    )
    
    return fig

def create_single_chart(historical_data, metric, title, goal_data=None):
    """Chart for single metric (with special handling for Sprint Momentum and BW*20m Mulch)"""
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
                    annotation_text=f"Target: {goal_val:.1f}",
                    annotation_position="top right"
                )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=18, color='#1F2937')
        ),
        xaxis=dict(title="Measurement Date"),
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
    """Dedicated strength chart (BSQ & BP)"""
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
                    annotation_text=f"BSQ Target: {goal_val:.1f}kg",
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
                    annotation_text=f"BP Target: {goal_val:.1f}kg",
                    annotation_position="top right"
                )
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1F2937')
        ),
        xaxis=dict(title="Measurement Date"),
        yaxis=dict(title="Weight (kg)"),
        height=300,
        showlegend=True,
        plot_bgcolor='rgba(248, 250, 252, 0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        margin=dict(l=50, r=50, t=60, b=40)
    )
    
    return fig

def show_welcome_screen():
    """Display welcome screen"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">SR SHIBUYA Measurement Data</div>
        <div class="welcome-subtitle">Analyze and visualize player performance data</div>
        <p style="color: #64748B; font-size: 1rem; margin-top: 1rem;">
            Please enter a player name in the sidebar
        </p>
    </div>
    """, unsafe_allow_html=True)

def generate_individual_feedback(player_data, comparison_data, player_name):
    """Generate feedback comments for individual players"""
    try:
        # Calculate scores for 3 indicators
        key_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        scores = {}
        
        for metric in key_metrics:
            player_val = safe_get_value(player_data, metric)
            if player_val is not None:
                score = calculate_z_score(player_val, comparison_data, metric)
                scores[metric] = score
            else:
                scores[metric] = 3  # Default value
        
        # Map scores to English names
        english_scores = {
            'Speed Power': scores.get('Sprint Momentum', 3),
            'Endurance': scores.get('BW*20m Mulch', 3),
            'Strength': scores.get('LBM/m', 3)
        }
        
        # Calculate overall evaluation
        valid_scores = [s for s in scores.values() if s > 0]
        overall_avg = np.mean(valid_scores) if valid_scores else 3
        
        feedback_parts = []
        
        # Introduction
        if overall_avg >= 4.5:
            intro = f"{player_name} demonstrates exceptional physical capabilities and shows great potential for further success at the competitive level."
        elif overall_avg >= 4:
            intro = f"{player_name} possesses excellent physical abilities and can be expected to achieve further growth through enhanced specialization."
        elif overall_avg >= 3:
            intro = f"{player_name} has stable foundational abilities in each area and can be expected to achieve steady growth through continuous training."
        else:
            intro = f"{player_name} has abundant growth potential and will surely improve through continuous training."
        
        feedback_parts.append(intro)
        
        # Identify strengths
        strengths = []
        for area, score in english_scores.items():
            if score >= 4:
                strengths.append(area)
        
        if strengths:
            if len(strengths) == 1:
                feedback_parts.append(f"Particularly showing excellent abilities in {strengths[0]}, further competitive improvement can be expected by leveraging this strength.")
            else:
                feedback_parts.append(f"Particularly showing excellent abilities in {strengths[0]} and {strengths[1]}, further development centered on these strengths is anticipated.")
        
        # Identify areas needing improvement and specific advice
        weaknesses = []
        improvement_suggestions = []
        
        for area, score in english_scores.items():
            if score <= 2:
                weaknesses.append(area)
                
                if area == 'Speed Power':
                    improvement_suggestions.append({
                        'area': 'Sprint ability',
                        'methods': 'improving start dash technique, enhancing hip joint mobility, optimizing weight transfer',
                        'details': 'acquiring movements that maximize propulsion by maximizing ground reaction force, expanding ankle mobility and enhancing propulsive power'
                    })
                elif area == 'Endurance':
                    improvement_suggestions.append({
                        'area': 'endurance',
                        'methods': 'cardiopulmonary function improvement training, muscular endurance strengthening, learning efficient movement patterns',
                        'details': 'improving breathing techniques for long-term performance maintenance and core strengthening to resist fatigue'
                    })
                elif area == 'Strength':
                    improvement_suggestions.append({
                        'area': 'strength',
                        'methods': 'establishing squat form, improving thoracic spine mobility, enhancing whole-body coordination',
                        'details': 'realizing efficient force exertion by improving movement quality in addition to basic strength improvement'
                    })
        
        # Feedback on areas for improvement
        if weaknesses:
            if len(weaknesses) == 1:
                feedback_parts.append(f"Challenges are seen in {weaknesses[0]}, so strengthening this area will be a key growth point going forward.")
            else:
                feedback_parts.append(f"Challenges are seen in {weaknesses[0]} and {weaknesses[1]}, so strengthening these areas will be key growth points going forward.")
            
            # Specific training proposals
            if improvement_suggestions:
                main_suggestion = improvement_suggestions[0]
                feedback_parts.append(f"For improving {main_suggestion['area']}, we believe {main_suggestion['methods']} are necessary. In particular, {main_suggestion['details']} are important. These will become the foundation for improving competitive performance.")
        
        # Proposals for well-balanced players (when score is 3)
        balanced_areas = [area for area, score in english_scores.items() if score == 3]
        if len(balanced_areas) >= 2 and not weaknesses:
            feedback_parts.append("Currently at a stage where each ability is developing in a well-balanced manner, with room for improvement in any area. Let's aim for further growth through continuous training.")
        
        # Encouraging summary
        if weaknesses:
            primary_weakness = weaknesses[0]
            if primary_weakness == 'Speed Power':
                closing = "Going forward, let's actively work on form checking and training to increase range of motion, and grow into a player with explosive sprint ability."
            elif primary_weakness == 'Endurance':
                closing = "Going forward, let's work on training to enhance sustained exercise capacity and grow into a player who can demonstrate stable performance throughout matches."
            elif primary_weakness == 'Strength':
                closing = "Going forward, let's actively work on training to improve basic strength and movement quality, and grow into a player who can realize powerful movements."
            else:
                closing = "Going forward, let's focus intensively on strengthening areas that are challenges and grow into a player with well-balanced comprehensive abilities."
        else:
            closing = "Let's aim to further develop current excellent abilities while improving overall physical capacity."
        
        feedback_parts.append(closing)
        feedback_parts.append("Accumulated efforts will surely lead to results.")
        
        return " ".join(feedback_parts)
        
    except Exception as e:
        return f"Conducting individual analysis of {player_name}. Let's aim for steady improvement through continuous training."

def main():
    # Load data
    df = load_data()
    if df.empty:
        st.error("Could not load data. Please confirm that the SR_physicaldata.xlsx file exists.")
        st.stop()
    
    # Add page selection
    page = st.sidebar.selectbox(
        "Page Selection",
        ["Comparative Analysis", "Individual Analysis"],
        help="Select analysis mode"
    )
    
    if page == "Individual Analysis":
        show_individual_analysis(df)
        return
    
    # Comparative analysis is main
    show_team_analysis(df)

def show_individual_analysis(df):
    """Display individual analysis screen"""
    st.markdown('<div class="main-header">SR SHIBUYA Measurement Data</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("Player Selection")
    
    # Add analysis mode selection
    analysis_mode = st.sidebar.radio(
        "Analysis Mode",
        ["Individual Player Analysis", "Batch PDF Report Generation"],
        help="Individual Player Analysis: Detailed analysis of one player\nBatch PDF Report Generation: Generate PDFs for all players by specifying category and date"
    )
    
    if analysis_mode == "Batch PDF Report Generation":
        show_batch_pdf_generation(df)
        return
    
    # Get available player name list
    available_names = sorted(df[df['名前'] != 'Target']['名前'].dropna().unique())
    
    if not available_names:
        st.error("No player data found.")
        return
    
    # Select player with dropdown
    selected_name = st.sidebar.selectbox(
        "Select a player",
        options=available_names,
        help="Select the player you want to analyze"
    )
    
    # Get available categories for selected player
    player_categories = sorted(df[df['名前'] == selected_name]['カテゴリー'].dropna().unique())
    if len(player_categories) == 0:
        st.error(f"No category data found for player '{selected_name}'.")
        return
    
    # Category selection
    if len(player_categories) == 1:
        selected_category = player_categories[0]
        st.sidebar.info(f"Category: {selected_category}")
    else:
        selected_category = st.sidebar.selectbox("Select Category", player_categories)
    
    # Get data for selected player and category
    player_data = df[(df['名前'] == selected_name) & (df['カテゴリー'] == selected_category)]
    
    if player_data.empty:
        st.error(f"No {selected_category} data found for player '{selected_name}'.")
        return
    
    # Get configuration
    config = get_category_config(selected_category)
    
    # Comparison data (player data in same category)
    category_avg = df[(df['カテゴリー'] == selected_category) & (df['名前'] != 'Target')]
    goal_data = df[df['名前'] == 'Target']
    
    # Display player information
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="player-title">{selected_name} ({selected_category})</div>', unsafe_allow_html=True)
    with col2:
        all_dates = player_data['測定日'].dropna().sort_values(ascending=False)
        if not all_dates.empty:
            latest_date = all_dates.iloc[0]
            oldest_date = all_dates.iloc[-1]
            measurement_count = len(all_dates)
            st.markdown(f'<div class="date-info">Measurements: {measurement_count} times<br>Period: {oldest_date} - {latest_date}</div>', unsafe_allow_html=True)
    
    # Comprehensive summary table
    st.markdown('<div class="section-header">Measurement Data Summary</div>', unsafe_allow_html=True)
    summary_table = create_comprehensive_summary_table(player_data, category_avg, goal_data, config)
    st.markdown(summary_table.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Key Indicators (with radar chart)
    st.markdown('<div class="key-indicator-title">Key Indicators</div>', unsafe_allow_html=True)
    
    # Place metrics and radar chart side by side
    col_metrics, col_radar = st.columns([3, 2])
    
    # 3 Key Indicators
    key_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
    metric_units = {'Sprint Momentum': '', 'BW*20m Mulch': '', 'LBM/m': ''}
    
    with col_metrics:
        highlight_cols = st.columns(len(key_metrics))
        for i, metric in enumerate(key_metrics):
            with highlight_cols[i]:
                player_val = safe_get_value(player_data, metric)
                
                # Calculate score
                score = 3  # Default value
                if player_val is not None:
                    score = calculate_z_score(player_val, category_avg, metric)
                
                # Prepare display value
                display_val = format_value(player_val, metric_units.get(metric, ''), metric)
                
                # Color setting according to score
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
                    <div class="comparison-text">Score: {score}/5</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_radar:
        # Display radar chart
        radar_chart = create_radar_chart(player_data, category_avg, config)
        if radar_chart:
            st.plotly_chart(radar_chart, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("""
            <p style="text-align: center; color: #64748B; padding: 2rem;">
                Insufficient data to<br>display radar chart
            </p>
            """, unsafe_allow_html=True)
    
    # Integrated graph section (displayed by section)
    st.markdown('<div class="section-header">Measurement Trend Graphs</div>', unsafe_allow_html=True)
    
    # Body Composition section
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
    
    # Quickness section
    st.markdown("### Quickness")
    if all(col in player_data.columns for col in ['20m Sprint(s)', 'Pro Agility', 'CODD']):
        sprint_agility_chart = create_triple_axis_chart(
            player_data, '20m Sprint(s)', 'Pro Agility', 'CODD', 
            'Sprint & Agility', goal_data
        )
        if sprint_agility_chart:
            st.plotly_chart(sprint_agility_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Jump section
    st.markdown("### Jump")
    col1, col2 = st.columns(2)
    with col1:
        if all(col in player_data.columns for col in ['CMJ', 'RJ']):
            jump_chart = create_dual_axis_chart(player_data, 'CMJ', 'RJ', 'CMJ & RJ', goal_data)
            if jump_chart:
                st.plotly_chart(jump_chart, use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("Failed to create dual-axis graph, displaying as individual graphs")
                
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
            st.warning(f"Required columns not found: {missing_cols}")
    
    with col2:
        if 'BJ' in player_data.columns:
            bj_chart = create_single_chart(player_data, 'BJ', 'BJ', goal_data)
            if bj_chart:
                st.plotly_chart(bj_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Endurance section
    st.markdown("### Endurance")
    if all(col in player_data.columns for col in ['20m Mulch', 'BW*20m Mulch']):
        endurance_chart = create_dual_axis_chart(
            player_data, '20m Mulch', 'BW*20m Mulch', 
            'Endurance (20m Mulch & BW*20m Mulch)', goal_data
        )
        if endurance_chart:
            st.plotly_chart(endurance_chart, use_container_width=True, config={'displayModeBar': False})
    
    # Strength section
    st.markdown("### Strength")
    if all(col in player_data.columns for col in ['BSQ', 'BP']):
        strength_chart = create_strength_chart(player_data, 'Strength (BSQ & BP)', goal_data)
        if strength_chart:
            st.plotly_chart(strength_chart, use_container_width=True, config={'displayModeBar': False})
    
    # PDF function
    st.write("---")
    st.write("### PDF Function")
    
    # Check PDF libraries
    if PDF_AVAILABLE:
        if st.button("📄 Generate Individual PDF Report", type="primary", key="individual_pdf_report"):
            try:
                with st.spinner('Generating PDF report...'):
                    pdf_bytes = generate_pdf_report(
                        selected_name, 
                        player_data, 
                        category_avg, 
                        config
                    )
                    
                    if pdf_bytes:
                        clean_name = selected_name.replace(" ", "_").replace("　", "_")
                        filename = f"{clean_name}_SR_SHIBUYA_Report.pdf"
                        
                        download_link = create_download_link(pdf_bytes, filename)
                        st.markdown(download_link, unsafe_allow_html=True)
                        st.success("PDF report generated successfully!")
                    else:
                        st.error("Failed to generate PDF report.")
                        
            except Exception as e:
                st.error(f"PDF generation error: {str(e)}")
    else:
        st.error("reportlab library is not installed")
        st.code("pip install reportlab")
    
    st.write("---")
    
    # Individual feedback comments
    st.markdown('<div class="section-header">Individual Feedback</div>', unsafe_allow_html=True)
    
    # Generate feedback based on 3 Key Indicators
    generated_feedback = generate_individual_feedback(player_data, category_avg, selected_name)
    
    # Manage feedback with session state
    feedback_key = f"feedback_{selected_name}_{selected_category}"
    if feedback_key not in st.session_state:
        st.session_state[feedback_key] = generated_feedback
    
    # Display edit function
    col1, col2 = st.columns([1, 4])
    with col1:
        edit_mode = st.checkbox("Edit Mode", key=f"edit_{feedback_key}")
    with col2:
        if edit_mode:
            if st.button("Return to Auto-Generated", key=f"reset_{feedback_key}"):
                st.session_state[feedback_key] = generated_feedback
                st.rerun()
    
    if edit_mode:
        # Editable text area
        edited_feedback = st.text_area(
            "Edit feedback content:",
            value=st.session_state[feedback_key],
            height=200,
            key=f"textarea_{feedback_key}",
            help="This text can be freely edited. Changes are saved automatically."
        )
        
        # Save changes
        if edited_feedback != st.session_state[feedback_key]:
            st.session_state[feedback_key] = edited_feedback
        
        # Display during editing
        st.info("Edit mode is enabled. You can modify the content in the text area above.")
    
    # Display feedback comments
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

def generate_pdf_report(player_name, player_data, category_data, config):
    """Generate PDF for individual report (yellow theme)"""
    if not PDF_AVAILABLE:
        return None
    
    try:
        buffer = io.BytesIO()
        
        # Japanese font support
        try:
            pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
            japanese_font = 'HeiseiKakuGo-W5'
            english_font = 'Helvetica'
        except:
            japanese_font = 'Helvetica'
            english_font = 'Helvetica'
        
        # Create PDF document
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
        
        # Yellow color definition
        yellow_primary = colors.Color(0.9, 0.8, 0.0)  # Dark yellow
        yellow_secondary = colors.Color(1.0, 0.9, 0.3)  # Bright yellow
        yellow_light = colors.Color(1.0, 0.95, 0.7)  # Light yellow
        
        # Style settings (yellow theme)
        title_style = ParagraphStyle(
            'CustomTitle', 
            fontName=japanese_font,
            fontSize=13,
            spaceAfter=4,
            alignment=TA_CENTER, 
            textColor=colors.Color(0.6, 0.5, 0.0)  # Dark yellow
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
        
        # Header section
        story.append(Paragraph("SR SHIBUYA", title_style))
        story.append(Paragraph("Physical Performance Report", title_style))
        story.append(Spacer(1, 15))
        
        # Name and ID
        player_id = safe_get_value(player_data, 'ID', '')
        if player_id and str(player_id) != '' and str(player_id) != 'nan':
            player_info = f"Player Name: {player_name} (ID: {player_id})"
        else:
            player_info = f"Player Name: {player_name}"
        story.append(Paragraph(player_info, normal_style))
        story.append(Spacer(1, 6))
        
        # Calculate scores for 3 indicators for Key Indicators
        key_metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        section_scores = {}
        
        for metric in key_metrics:
            player_val = safe_get_value(player_data, metric)
            if player_val is not None:
                score = calculate_z_score(player_val, category_data, metric)
                section_scores[metric] = score
            else:
                section_scores[metric] = 3  # Default value
        
        # Calculate overall score
        valid_scores = [s for s in section_scores.values() if s > 0]
        overall_score = round(np.mean(valid_scores)) if valid_scores else 3
        
        # Display physical score
        story.append(Paragraph("Physical Score", heading_style))
        story.append(Spacer(1, 6))
        
        # Horizontal score table (yellow theme)
        score_data = []
        score_row = []
        
        # English display name mapping
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
        
        # Physical balance (triangle radar chart)
        radar_chart = create_triangle_radar_chart_yellow(section_scores, overall_score)
        if radar_chart:
            chart_table = Table([[radar_chart]], colWidths=[5.7*cm])
            chart_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(chart_table)
            story.append(Spacer(1, -17))
        
        # Measurement data
        story.append(Paragraph("Measurement Data", heading_style))
        
        # Major measurement items (changed to English names) - exclude items without data
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
        
        # Select only items with data
        key_display_metrics = []
        for metric_key, metric_name, unit in all_key_display_metrics:
            # Check if exists in player data or category data
            player_has_data = metric_key in player_data.columns and safe_get_value(player_data, metric_key) is not None
            category_has_data = metric_key in category_data.columns and not category_data[metric_key].isna().all()
            
            if player_has_data or category_has_data:
                key_display_metrics.append((metric_key, metric_name, unit))
        
        detail_data = [['Measurement Item', 'Latest Value', 'Previous Value', 'Change', 'Score', 'Target', 'Category Average']]
        
        # Target value definition (values from uploaded Excel file)
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
            
            # Get target value (use values from uploaded file)
            goal_val = target_values.get(metric_key)
            
            # Calculate change
            change_display = ""
            if player_val is not None and previous_val is not None:
                diff = player_val - previous_val
                if metric_key == 'Fat%':
                    # For Fat%, display as ×100
                    if diff > 0:
                        change_display = f"+{diff * 100:.2f}%"
                    elif diff < 0:
                        change_display = f"{diff * 100:.2f}%"
                    else:
                        change_display = "0.00%"
                else:
                    # For other items, display normal difference
                    if diff > 0:
                        change_display = f"+{diff:.2f}"
                    elif diff < 0:
                        change_display = f"{diff:.2f}"
                    else:
                        change_display = "0.00"
            else:
                change_display = "-"
            
            # Calculate score
            if player_val is not None:
                score = calculate_z_score(player_val, category_data, metric_key)
                score_display = str(score)
            else:
                score_display = "N/A"
            
            # Category average
            category_values = []
            for _, row in category_data.iterrows():
                val = safe_get_value(pd.DataFrame([row]), metric_key)
                if val is not None:
                    category_values.append(val)
            
            category_avg = np.mean(category_values) if category_values else None
            
            # Special handling for Fat%
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
        
        # Table style (yellow theme)
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
        
        # Apply coloring only to change column
        for i, (metric_key, metric_name, unit) in enumerate(key_display_metrics, 1):
            if metric_key not in player_data.columns:
                continue
                
            player_val = safe_get_value(player_data, metric_key)
            previous_val = safe_get_previous_value(player_data, metric_key)
            
            # Color change column (4th column)
            if player_val is not None and previous_val is not None:
                try:
                    current_num = float(player_val)
                    previous_num = float(previous_val)
                    diff = current_num - previous_num
                    
                    if diff != 0:
                        # For Sprint, Agility, CODD, lower values are better (show improvement in red)
                        if metric_key in ['20m Sprint(s)', 'Pro Agility', 'CODD']:
                            if diff < 0:  # Value decreased (improved)
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.red))
                            elif diff > 0:  # Value increased (worsened)
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.blue))
                        else:
                            # For other items, higher values are better
                            if diff > 0:  # Value increased (improved)
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.red))
                            elif diff < 0:  # Value decreased (worsened)
                                table_style.append(('TEXTCOLOR', (3, i), (3, i), colors.blue))
                except (ValueError, TypeError):
                    pass
        
        detail_table.setStyle(TableStyle(table_style))
        story.append(detail_table)
        story.append(Spacer(1, 11))
        
        # Add individual feedback section
        story.append(Paragraph("Individual Feedback", heading_style))
        story.append(Spacer(1, 6))
        
        # Get feedback content (from session state, or auto-generate)
        feedback_key = f"feedback_{player_name}_{player_data['カテゴリー'].iloc[0] if not player_data.empty else 'unknown'}"
        
        # Get feedback from session state, auto-generate if doesn't exist
        if hasattr(st, 'session_state') and feedback_key in st.session_state:
            feedback_text = st.session_state[feedback_key]
        else:
            # Use auto-generated feedback
            feedback_text = generate_individual_feedback(player_data, category_data, player_name)
        
        # Style for feedback
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
        
        # Split feedback text into paragraphs and add
        feedback_paragraphs = feedback_text.split('。')
        for paragraph in feedback_paragraphs:
            if paragraph.strip():
                # Add period for display
                paragraph_text = paragraph.strip() + '。' if not paragraph.strip().endswith('。') else paragraph.strip()
                story.append(Paragraph(paragraph_text, feedback_style))
        
        story.append(Spacer(1, 32))
        
        # Key Indicators explanation
        story.append(Paragraph("Key Indicators Explanation", heading_style))
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
            story.append(Paragraph("Sprint momentum: Represents contact strength. Body weight × speed (calculated from 20m sprint time)", item_style))
            story.append(Paragraph("　　　　　　　　　　Target of 600+ by U18 graduation.", item_style))
            story.append(Spacer(1, 3))
            story.append(Paragraph("LBM/m: Shows ratio of lean body mass (body weight minus fat) to height.", item_style))
            story.append(Paragraph("　　　　  Target of 42+ by U18 graduation.", item_style))
            story.append(Spacer(1, 3))
            story.append(Paragraph("BW*20m Mulch: Shows value of body weight × 20m multi-shuttle run. Evaluated with body weight product as heavier players are disadvantaged in 20m multi-shuttle run.", item_style))
            story.append(Paragraph("　　　　　　　　　 Target of 12000+ by U18 graduation.", item_style))
        except:
            story.append(Paragraph("Key Indicators explanation (text content)", item_style))
        
        # Footer
        story.append(Spacer(1, 8))
        footer_style = ParagraphStyle(
            'Footer', 
            fontName=english_font,
            fontSize=6,
            alignment=TA_CENTER, 
            textColor=colors.Color(0.4, 0.3, 0.0)
        )
        
        story.append(Paragraph("©2025 SR SHIBUYA ALL RIGHTS RESERVED", footer_style))
        
        # Generate PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return None

def create_triangle_radar_chart_yellow(section_scores, overall_score):
    """Create triangular radar chart with yellow theme"""
    try:
        from reportlab.graphics.shapes import Drawing, Polygon, String
        from reportlab.lib import colors as rl_colors
        import math
        
        # Chart size
        chart_width = 5.7*cm
        chart_height = 3.3*cm
        
        drawing = Drawing(chart_width, chart_height)
        
        # Triangle center point and radius
        center_x = chart_width / 2
        center_y = chart_height / 2 - 0.08*cm
        radius = 1.3*cm
        
        # Calculate triangle vertices (upward triangle)
        angles = [90, 210, 330]  # Degrees
        triangle_points = []
        for angle in angles:
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            triangle_points.extend([x, y])
        
        # Radar chart outer frame (5 levels, yellow tones)
        for level in range(1, 6):
            scale = level / 5.0
            scaled_points = []
            for i in range(0, len(triangle_points), 2):
                base_x = triangle_points[i]
                base_y = triangle_points[i+1]
                scaled_x = center_x + (base_x - center_x) * scale
                scaled_y = center_y + (base_y - center_y) * scale
                scaled_points.extend([scaled_x, scaled_y])
            
            # Draw triangle (yellow tones)
            if level < 5:
                color = rl_colors.Color(0.9, 0.8, 0.0, alpha=0.2)  # Light yellow
            else:
                color = rl_colors.Color(0.7, 0.6, 0.0, alpha=0.4)  # Dark yellow
            
            triangle = Polygon(scaled_points)
            triangle.fillColor = None
            triangle.strokeColor = color
            triangle.strokeWidth = 1
            drawing.add(triangle)
        
        # Calculate data points
        metrics = ['Sprint Momentum', 'BW*20m Mulch', 'LBM/m']
        scores = [
            section_scores.get('Sprint Momentum', 3),  # Top
            section_scores.get('BW*20m Mulch', 3),    # Bottom left  
            section_scores.get('LBM/m', 3)            # Bottom right
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
        
        # Draw data triangle (yellow tones)
        if len(data_points) == 6:
            data_triangle = Polygon(data_points)
            data_triangle.fillColor = rl_colors.Color(0.9, 0.8, 0.0, alpha=0.3)  # Yellow tones
            data_triangle.strokeColor = rl_colors.Color(0.7, 0.6, 0.0)
            data_triangle.strokeWidth = 2
            drawing.add(data_triangle)
        
        # Add labels
        labels = ['Sprint Momentum', 'BW×20m Shuttle', 'LBM/Height', 'Overall Score']
        scores_for_labels = [
            section_scores.get('Sprint Momentum', 3),
            section_scores.get('BW*20m Mulch', 3),
            section_scores.get('LBM/m', 3),
            overall_score
        ]
        label_positions = [
            (center_x, center_y + radius + 0.25*cm),      # Top
            (center_x - radius - 0.5*cm, center_y - radius/2),  # Bottom left
            (center_x + radius + 0.5*cm, center_y - radius/2),   # Bottom right
            (center_x, center_y - radius + 0.37*cm)       # Bottom
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
            label_text.fillColor = rl_colors.Color(0.4, 0.3, 0.0)  # Dark yellow tones
            drawing.add(label_text)
        
        return drawing
        
    except Exception as e:
        return None

def create_download_link(pdf_bytes, filename):
    """Create PDF download link (yellow theme)"""
    b64_pdf = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{filename}" style="text-decoration: none;">'
    href += '<div style="background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%); '
    href += 'color: white; padding: 12px 24px; border-radius: 8px; text-align: center; '
    href += 'font-weight: bold; margin: 10px 0; display: inline-block; '
    href += 'box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);">'
    href += '📄 Download PDF Report</div></a>'
    return href

def show_batch_pdf_generation(df):
    """Batch PDF report generation screen"""
    st.markdown('<div class="section-header">Batch PDF Report Generation</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); 
                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                border-left: 4px solid #4F46E5;">
        <h4 style="color: #4F46E5; margin-top: 0;">📋 Batch PDF Report Generation</h4>
        <p style="color: #1F2937; margin-bottom: 0;">
            Select a category and measurement date to generate PDF reports for all applicable players at once.
            Generated PDFs will be compiled into a single ZIP file for download.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check PDF library
    if not PDF_AVAILABLE:
        st.error("❌ reportlab library is not installed")
        st.code("pip install reportlab")
        return
    
    # Category selection
    available_categories = sorted(df[df['名前'] != 'Target']['カテゴリー'].dropna().unique())
    
    if not available_categories:
        st.error("No category data found.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_category = st.selectbox(
            "📊 Select Category",
            available_categories,
            help="Select the player category for PDF report generation"
        )
    
    # Get measurement dates for selected category
    category_data = df[(df['カテゴリー'] == selected_category) & (df['名前'] != 'Target')]
    
    if category_data.empty:
        st.warning(f"No data found for {selected_category}.")
        return
    
    # Get list of measurement dates
    if '測定日' in category_data.columns:
        category_data['測定日'] = pd.to_datetime(category_data['測定日'], errors='coerce')
        available_dates = sorted(category_data['測定日'].dropna().dt.strftime('%Y-%m-%d').unique(), reverse=True)
    else:
        st.error("Measurement date column not found.")
        return
    
    if not available_dates:
        st.warning(f"No measurement date data found for {selected_category}.")
        return
    
    with col2:
        selected_date = st.selectbox(
            "📅 Select Measurement Date",
            available_dates,
            help="Select the measurement date for PDF report generation"
        )
    
    # Display list of target players
    target_players_data = df[
        (df['カテゴリー'] == selected_category) & 
        (df['名前'] != 'Target') &
        (df['測定日'] == selected_date)
    ]
    
    target_players = sorted(target_players_data['名前'].dropna().unique())
    
    st.markdown("---")
    
    # Display target players
    st.markdown(f"### Target Players ({len(target_players)} players)")
    
    if target_players:
        # Display player names in 3 columns
        cols = st.columns(3)
        for idx, player_name in enumerate(target_players):
            with cols[idx % 3]:
                st.markdown(f"• {player_name}")
    else:
        st.warning("No applicable players found.")
        return
    
    st.markdown("---")
    
    # Generation options
    st.markdown("### Generation Options")
    
    col1, col2 = st.columns(2)
    with col1:
        include_feedback = st.checkbox(
            "Include Individual Feedback",
            value=True,
            help="Include auto-generated feedback comments in each player's PDF"
        )
    
    with col2:
        zip_filename = st.text_input(
            "ZIP Filename",
            value=f"{selected_category}_{selected_date}_Reports.zip",
            help="Specify the name of the ZIP file to download"
        )
    
    st.markdown("---")
    
    # Generation button
    if st.button("🚀 Generate Batch PDF Reports", type="primary", use_container_width=True):
        try:
            with st.spinner(f'Generating PDF reports for {len(target_players)} players...'):
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Create ZIP file
                import zipfile
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Generate PDF for each player
                    for idx, player_name in enumerate(target_players):
                        status_text.text(f"Generating: {player_name} ({idx + 1}/{len(target_players)})")
                        
                        # Get player data
                        player_data = df[
                            (df['名前'] == player_name) & 
                            (df['カテゴリー'] == selected_category)
                        ]
                        
                        # Category average data
                        category_avg = df[
                            (df['カテゴリー'] == selected_category) & 
                            (df['名前'] != 'Target')
                        ]
                        
                        # Get configuration
                        config = get_category_config(selected_category)
                        
                        # Generate PDF
                        pdf_bytes = generate_pdf_report(
                            player_name,
                            player_data,
                            category_avg,
                            config
                        )
                        
                        if pdf_bytes:
                            # Create filename (Japanese character support)
                            clean_name = player_name.replace(" ", "_").replace("　", "_")
                            pdf_filename = f"{clean_name}_{selected_date}_Report.pdf"
                            
                            # Add to ZIP
                            zip_file.writestr(pdf_filename, pdf_bytes)
                        
                        # Update progress bar
                        progress_bar.progress((idx + 1) / len(target_players))
                
                progress_bar.empty()
                status_text.empty()
                
                # Create ZIP file download link
                zip_buffer.seek(0)
                zip_bytes = zip_buffer.getvalue()
                
                b64_zip = base64.b64encode(zip_bytes).decode()
                href = f'<a href="data:application/zip;base64,{b64_zip}" download="{zip_filename}" style="text-decoration: none;">'
                href += '<div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); '
                href += 'color: white; padding: 16px 32px; border-radius: 12px; text-align: center; '
                href += 'font-weight: bold; font-size: 1.1rem; margin: 20px 0; display: inline-block; '
                href += 'box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);">'
                href += f'📦 Download ZIP File ({len(target_players)} PDF Reports)</div></a>'
                
                st.markdown(href, unsafe_allow_html=True)
                st.success(f"✅ Successfully generated PDF reports for {len(target_players)} players!")
                
                # Generated file details
                with st.expander("📋 List of Generated Files"):
                    for player_name in target_players:
                        clean_name = player_name.replace(" ", "_").replace("　", "_")
                        st.text(f"• {clean_name}_{selected_date}_Report.pdf")
                
        except Exception as e:
            st.error(f"❌ PDF generation error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())



if __name__ == "__main__":
    main()