"""
Market Intelligence Pro - تطبيق ويب احترافي لتحليل المنافسين
يدعم البحث بالعربية والإنجليزية
ملاحظة: لا يحتوي على أي مفاتيح API ثابتة
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os
import sys
import json
import subprocess
from datetime import datetime

try:
    from market_engine import MarketEngine
    from market_ai import MarketAI
except ImportError as e:
    st.error(f"خطأ في استيراد المكتبات: {e}")
    st.stop()

# ==========================================
# إعداد الصفحة
# ==========================================
st.set_page_config(
    page_title="Market Intelligence Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# التصميم
# ==========================================
st.markdown("""
<style>
    .stApp { background: #f8f9fa; }
    .main-header { text-align: center; padding: 2rem 0 1rem 0; }
    .main-header h1 { color: #5b5fc7; font-size: 3rem; font-weight: 800; margin: 0; }
    .main-header p { color: #6c757d; font-size: 1.2rem; margin-top: 0.5rem; }
    .welcome-box { background: white; border-radius: 20px; padding: 3rem; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin: 2rem 0; }
    .welcome-box h2 { color: #5b5fc7; font-size: 2rem; margin-bottom: 1rem; }
    .welcome-box p { color: #6c757d; font-size: 1.1rem; line-height: 1.8; }
    .how-to-start { background: #f8f9fa; border-radius: 15px; padding: 2rem; margin-top: 2rem; }
    .how-to-start h3 { color: #2d3748; font-size: 1.5rem; margin-bottom: 1rem; }
    .how-to-start ol { color: #4a5568; font-size: 1rem; line-height: 2; padding-left: 1.5rem; }
    .how-to-start ol li strong { color: #5b5fc7; }
    section[data-testid="stSidebar"] { background: white; border-right: 1px solid #e2e8f0; }
    .step-box { background: #e3f2fd; border: 2px solid #2196F3; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }
    .step-box h4 { color: #0c5460; margin: 0 0 0.5rem 0; font-weight: 600; }
    .step-box p { color: #0c5460; margin: 0; font-size: 0.9rem; }
    .stButton > button { background: linear-gradient(135deg, #5b5fc7 0%, #7b68ee 100%); color: white; border: none; border-radius: 10px; padding: 12px 24px; font-weight: 600; font-size: 1rem; width: 100%; }
    .stat-card { background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #5b5fc7; }
    .stat-card h3 { color: #5b5fc7; font-size: 2rem; margin: 0; font-weight: 700; }
    .stat-card p { color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem; }
    .footer { text-align: center; color: #6c757d; padding: 2rem 0; margin-top: 3rem; border-top: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# تهيئة الحالة
# ==========================================
if 'apps_found' not in st.session_state: st.session_state.apps_found = []
if 'selected_apps' not in st.session_state: st.session_state.selected_apps = []
if 'reviews_data' not in st.session_state: st.session_state.reviews_data = None
if 'analysis_results' not in st.session_state: st.session_state.analysis_results = None

# ==========================================
# دالة البحث عبر subprocess
# ==========================================
def search_apps_subprocess(keyword: str, num_results: int = 15):
    """البحث عبر subprocess"""
    python_exe = sys.executable
    
    script = f"""
import json, sys
from google_play_scraper import search
try:
    results = search('{keyword}', n_hits={num_results}, lang='en', country='us')
    apps = []
    for app in results:
        apps.append({{
            'app_id': app.get('appId', ''),
            'title': app.get('title', ''),
            'developer': app.get('developer', ''),
            'rating': app.get('score', 0),
            'icon': app.get('icon', ''),
            'summary': (app.get('summary', '') or '')[:150]
        }})
    print(json.dumps(apps))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
    
    try:
        result = subprocess.run(
            [python_exe, '-c', script],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            data = json.loads(output)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'error' in data:
                st.error(f"خطأ في البحث: {data['error']}")
                return []
        else:
            st.error(f"فشل البحث: {result.stderr}")
            return []
    except subprocess.TimeoutExpired:
        st.error("انتهت مهلة البحث")
        return []
    except Exception as e:
        st.error(f"خطأ: {e}")
        return []

# ==========================================
# الهيدر الرئيسي
# ==========================================
st.markdown('<div class="main-header"><h1> Market Intelligence Pro</h1><p>AI-Powered Competitor Analysis & Market Gap Detection</p></div>', unsafe_allow_html=True)

# ==========================================
# الشريط الجانبي
# ==========================================
with st.sidebar:
    st.markdown('<div style="background: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 0.8rem; margin-bottom: 1.5rem; text-align: center;"><strong style="color: #856404;">📝 Studio</strong></div>', unsafe_allow_html=True)
    
    st.markdown('<div style="margin-bottom: 1rem;"><p style="color: #2d3748; font-weight: 600; margin-bottom: 0.5rem;">🔑 Paste your Gemini API Key here</p></div>', unsafe_allow_html=True)
    
    # ✅ المفتاح يُؤخذ من المستخدم فقط - لا يوجد مفتاح ثابت في الكود
    api_key = st.text_input(
        "",
        type="password",
        placeholder="Enter your API key...",
        label_visibility="collapsed",
        help="Get your free key from https://aistudio.google.com/app/apikey"
    )
    
    if api_key:
        st.markdown('<div style="background: #d4edda; border: 1px solid #28a745; border-radius: 8px; padding: 0.8rem; margin: 1rem 0; color: #155724;">✅ API Key saved!</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown('<div class="step-box"><h4>🔍 Step 2: Search for Apps</h4><p>Enter a keyword like: fitness, food delivery, meditation</p></div>', unsafe_allow_html=True)
    
    keyword = st.text_input("Search Keyword", placeholder="e.g., fitness, food delivery, yoga")
    
    if st.button("🚀 Search Apps", use_container_width=True):
        if keyword:
            with st.spinner("🔎 Searching Google Play..."):
                apps = search_apps_subprocess(keyword, num_results=15)
                st.session_state.apps_found = apps
                
                if apps:
                    st.success(f"✅ Found {len(apps)} apps")
                else:
                    st.warning("⚠️ No apps found. Try another keyword.")
        else:
            st.warning("⚠️ Please enter a keyword")
    
    if st.session_state.apps_found:
        st.markdown("---")
        st.markdown('<div style="background: #d4edda; border: 2px solid #28a745; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;"><p style="margin: 0; color: #155724; font-weight: 600;">✅ Step 3: Select 2-4 Apps</p></div>', unsafe_allow_html=True)
        
        selected = []
        for app in st.session_state.apps_found:
            col1, col2 = st.columns([1, 4])
            with col1:
                if app.get('icon'): st.image(app['icon'], width=40)
            with col2:
                checked = st.checkbox(app['title'], key=app['app_id'], help=f"⭐ {app['rating']} | {app['developer']}")
                if checked: selected.append(app)
        
        if 2 <= len(selected) <= 4:
            st.session_state.selected_apps = selected
            st.success(f"✅ {len(selected)} apps selected!")
        elif len(selected) > 4:
            st.error(" Max 4 apps allowed")
        else:
            st.info(f"ℹ️ Selected: {len(selected)} (need 2-4)")
    
    if st.session_state.selected_apps and api_key:
        st.markdown("---")
        if st.button(" Analyze & Report", use_container_width=True, type="primary"):
            with st.spinner(" Processing data..."):
                engine = MarketEngine()
                ai_engine = MarketAI(api_key=api_key)
                all_reviews, apps_data = [], []
                
                for app in st.session_state.selected_apps:
                    reviews_df = engine.scrape_reviews(app['app_id'], count=200)
                    if not reviews_df.empty:
                        reviews_df = engine.process_reviews(reviews_df)
                        all_reviews.append(reviews_df)
                        apps_data.append(app)
                    time.sleep(1)
                
                if all_reviews:
                    combined = pd.concat(all_reviews, ignore_index=True)
                    st.session_state.reviews_data = combined
                    engine.save_to_database(pd.DataFrame(apps_data), combined)
                    engine.export_to_excel(combined, "competitor_report.xlsx")
                    
                    neg_dict = {}
                    for app in apps_data:
                        neg = engine.get_negative_reviews(app['app_id'], max_reviews=50)
                        if neg: neg_dict[app['title']] = neg
                    
                    if neg_dict:
                        st.session_state.analysis_results = ai_engine.analyze_multiple_apps(neg_dict)
                    st.balloons()
                    st.success("✅ Analysis Complete!")

# ==========================================
# الواجهة الرئيسية
# ==========================================
if st.session_state.reviews_data is None:
    st.markdown('<div class="welcome-box">', unsafe_allow_html=True)
    st.markdown('<h2>👋 Welcome to Market Intelligence Pro</h2>', unsafe_allow_html=True)
    st.markdown('<p>Your AI-powered tool to analyze competitors and discover market gaps.</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="how-to-start">', unsafe_allow_html=True)
    st.markdown('<h3>🚀 How to Start:</h3>', unsafe_allow_html=True)
    st.markdown('<ol>', unsafe_allow_html=True)
    st.markdown('<li>Enter your <strong>Gemini API Key</strong> in the sidebar</li>', unsafe_allow_html=True)
    st.markdown('<li>Search for apps using a keyword (e.g., "fitness")</li>', unsafe_allow_html=True)
    st.markdown('<li>Select 2-4 competing apps to compare</li>', unsafe_allow_html=True)
    st.markdown('<li>Click <strong>Analyze & Report</strong></li>', unsafe_allow_html=True)
    st.markdown('</ol>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    df = st.session_state.reviews_data
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><h3>{len(df):,}</h3><p>Total Reviews</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><h3>{df["app_id"].nunique()}</h3><p>Apps Analyzed</p></div>', unsafe_allow_html=True)
    with col3:
        pos_pct = (df['sentiment'] == 'Positive').sum() / len(df) * 100
        st.markdown(f'<div class="stat-card" style="border-top-color: #2ecc71;"><h3 style="color: #2ecc71;">{pos_pct:.1f}%</h3><p>Positive Sentiment</p></div>', unsafe_allow_html=True)
    with col4:
        avg = df['score'].mean()
        st.markdown(f'<div class="stat-card" style="border-top-color: #f39c12;"><h3 style="color: #f39c12;">{avg:.2f}⭐</h3><p>Average Rating</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts", " AI Insights", "📋 Raw Data", "💾 Download"])
    
    with tab1:
        st.markdown("<h3 style='color: #2d3748;'>📊 Sentiment Analysis</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            counts = df['sentiment'].value_counts().reset_index()
            counts.columns = ['Sentiment', 'Count']
            fig = px.pie(counts, values='Count', names='Sentiment', color='Sentiment', 
                        color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'}, hole=0.5)
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#2d3748', size=12))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            by_app = df.groupby(['app_id', 'sentiment']).size().reset_index(name='count')
            fig2 = px.bar(by_app, x='app_id', y='count', color='sentiment', 
                         color_discrete_map={'Positive': '#2ecc71', 'Neutral': '#95a5a6', 'Negative': '#e74c3c'})
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#2d3748', size=12))
            st.plotly_chart(fig2, use_container_width=True)
            
    with tab2:
        st.markdown("<h3 style='color: #2d3748;'> AI Market Insights</h3>", unsafe_allow_html=True)
        if st.session_state.analysis_results:
            for app_name, result in st.session_state.analysis_results.items():
                with st.expander(f" {app_name}", expanded=True):
                    if result['status'] == 'success': st.markdown(result['analysis'])
                    else: st.error(result['analysis'])
        else:
            st.info("No AI analysis available yet.")
        
    with tab3:
        st.markdown("<h3 style='color: #2d3748;'>📋 Raw Data</h3>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=400)
        
    with tab4:
        st.markdown("<h3 style='color: #2d3748;'>💾 Download Reports</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists("competitor_report.xlsx"):
                with open("competitor_report.xlsx", "rb") as f:
                    st.download_button(" Excel Report", f, file_name=f"competitor_report_{datetime.now().strftime('%Y%m%d')}.xlsx", use_container_width=True)
        with col2:
            if os.path.exists("competitor_intelligence.db"):
                with open("competitor_intelligence.db", "rb") as f:
                    st.download_button("📥 Database", f, file_name=f"competitor_intelligence_{datetime.now().strftime('%Y%m%d')}.db", use_container_width=True)

# ==========================================
# الفوتر
# ==========================================
st.markdown('<div class="footer"><p> Market Intelligence Pro | Built with Streamlit, Python & Gemini AI</p><p>📅 October 2026 | Nawal Massa</p></div>', unsafe_allow_html=True)