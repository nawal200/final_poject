import pandas as pd
import sqlite3
from google_play_scraper import search, reviews, Sort
from textblob import TextBlob
import time
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketEngine:
    """محرك جلب ومعالجة بيانات التطبيقات من Google Play"""

    def __init__(self):
        self.db_name = "competitor_intelligence.db"

    def search_apps(self, keyword: str, num_results: int = 20) -> List[Dict]:
        """البحث عن تطبيقات في Google Play"""
        print(f"\n🔍 بدء البحث عن: '{keyword}'")
        print(f"📊 عدد النتائج المطلوبة: {num_results}\n")
        
        try:
            # محاولة البحث
            print("⏳ جاري الاتصال بـ Google Play...")
            results = search(
                keyword,
                n_hits=num_results,
                lang='en',
                country='us',
                timeout=30
            )
            
            print(f"✅ تم استلام {len(results)} نتيجة من Google Play")
            
            if not results:
                print("⚠️ Google Play أرجع قائمة فارغة!")
                return []

            apps = []
            for app in results:
                apps.append({
                    'app_id': app.get('appId', ''),
                    'title': app.get('title', ''),
                    'developer': app.get('developer', ''),
                    'rating': app.get('score', 0),
                    'icon': app.get('icon', ''),
                    'summary': (app.get('summary', '') or '')[:100]
                })
                print(f"  - {app.get('title', 'Unknown')}")

            print(f"\n✅ تم العثور على {len(apps)} تطبيق بنجاح!\n")
            return apps

        except Exception as e:
            print(f"\n❌ خطأ في البحث: {e}")
            print(f" تفاصيل الخطأ: {type(e).__name__}: {str(e)}\n")
            return []

    def scrape_reviews(self, app_id: str, count: int = 200) -> pd.DataFrame:
        """جلب تقييمات تطبيق معين"""
        try:
            logger.info(f"جاري جلب {count} تقييم لـ {app_id}")
            result, _ = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=count,
                filter_score_with=None
            )

            reviews_data = []
            for review in result:
                reviews_data.append({
                    'app_id': app_id,
                    'review_id': review.get('reviewId', ''),
                    'content': review.get('content', '') or '',
                    'score': review.get('score', 0),
                    'at': review.get('at', ''),
                    'thumbs_up': review.get('thumbsUpCount', 0)
                })

            df = pd.DataFrame(reviews_data)
            logger.info(f"تم جلب {len(df)} تقييم")
            return df

        except Exception as e:
            logger.error(f"خطأ في جلب التقييمات: {e}")
            return pd.DataFrame()

    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """تحليل مشاعر النص"""
        if not text or len(text.strip()) == 0:
            return 'Neutral', 0.0

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            sentiment = 'Positive'
        elif polarity < -0.1:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        return sentiment, polarity

    def process_reviews(self, df: pd.DataFrame) -> pd.DataFrame:
        """معالجة التقييمات وإضافة تحليل المشاعر"""
        if df.empty:
            return df

        logger.info("جاري تحليل المشاعر...")

        sentiments = df['content'].apply(self.analyze_sentiment)
        df['sentiment'] = sentiments.apply(lambda x: x[0])
        df['polarity'] = sentiments.apply(lambda x: x[1])

        df = df.dropna(subset=['content'])
        df['content'] = df['content'].str.strip()
        
        # إصلاح مشكلة التاريخ
        df['at'] = pd.to_datetime(df['at'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')

        logger.info(f"تم معالجة {len(df)} تقييم")
        return df

    def save_to_database(self, apps_df: pd.DataFrame, reviews_df: pd.DataFrame):
        """حفظ البيانات في قاعدة بيانات SQLite"""
        try:
            conn = sqlite3.connect(self.db_name)
            apps_df.to_sql('apps', conn, if_exists='replace', index=False)
            reviews_df.to_sql('reviews', conn, if_exists='replace', index=False)
            conn.close()
            logger.info(f"تم حفظ البيانات في {self.db_name}")
        except Exception as e:
            logger.error(f"خطأ في حفظ البيانات: {e}")

    def export_to_excel(self, reviews_df: pd.DataFrame, filename: str = "competitor_report.xlsx"):
        """تصدير التقرير إلى Excel"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                summary_data = reviews_df.groupby('app_id').agg({
                    'content': 'count',
                    'sentiment': lambda x: (x == 'Positive').sum() / len(x) * 100 if len(x) > 0 else 0,
                    'score': 'mean'
                }).reset_index()

                summary_data.columns = ['App ID', 'Total Reviews', 'Positive %', 'Avg Rating']
                summary_data.to_excel(writer, sheet_name='Summary', index=False)

                for app_id in reviews_df['app_id'].unique():
                    app_reviews = reviews_df[reviews_df['app_id'] == app_id]
                    sheet_name = app_id[:31]
                    app_reviews.to_excel(writer, sheet_name=sheet_name, index=False)

            logger.info(f"تم تصدير التقرير إلى {filename}")
        except Exception as e:
            logger.error(f"خطأ في تصدير Excel: {e}")

    def get_negative_reviews(self, app_id: str, max_reviews: int = 50) -> str:
        """جلب التقييمات السلبية لتحليل الفجوات"""
        try:
            conn = sqlite3.connect(self.db_name)
            query = f"""
                SELECT content FROM reviews 
                WHERE app_id = '{app_id}' AND score <= 2
                LIMIT {max_reviews}
            """
            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return ""

            return "\n".join(df['content'].tolist())

        except Exception as e:
            logger.error(f"خطأ في جلب التقييمات السلبية: {e}")
            return ""