import logging
import google.generativeai as genai
from typing import Dict
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarketAI:
    """محرك التحليل الذكي باستخدام Google Gemini API"""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("مفتاح API مطلوب للتحليل الذكي")

        try:
            # تنظيف المفتاح من أي مسافات مخفية
            clean_api_key = api_key.strip().replace('\n', '').replace('\r', '')
            genai.configure(api_key=clean_api_key)
            
            # ✅ استخدام نموذج متاح حالياً
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("✅ تم تهيئة نموذج Gemini 2.0 Flash بنجاح")
            
        except Exception as e:
            logger.error(f"❌ فشل في تهيئة Gemini: {e}")
            raise

    def analyze_multiple_apps(self, apps_data: Dict[str, str]) -> Dict[str, Dict]:
        """تحليل جميع التطبيقات في طلب واحد"""
        
        apps_sections = []
        for app_name, reviews in apps_data.items():
            if reviews and len(reviews.strip()) >= 50:
                apps_sections.append(f"""
### التطبيق: {app_name}
التقييمات السلبية:
{reviews}
---
""")
        
        if not apps_sections:
            return {
                app_name: {
                    "app_name": app_name,
                    "analysis": "لا توجد تقييمات سلبية كافية للتحليل.",
                    "status": "success"
                }
                for app_name in apps_data.keys()
            }

        combined_prompt = f"""
أنت خبير تحليل منتجات وذكاء اصطناعي متخصص في أبحاث السوق لتطبيقات الهواتف الذكية.

مهمتك هي تحليل التقييمات السلبية للتطبيقات المنافسة التالية واستخراج الفجوات السوقية.

{"".join(apps_sections)}

المطلوب: لكل تطبيق على حدة، قم بتحليل تقييماته السلبية واستخرج:

### 🔴 Top Recurring Bugs
أهم 3 شكاوى أو أخطاء فنية متكررة.

### 🟡 Missing Features
أهم 3 ميزات يطلبها المستخدمون ولا توجد في التطبيق.

### 🟢 Strategic Recommendations
توصيتان استراتيجيتان لاستغلال هذه الثغرات.

**مهم جداً:**
- ابدأ كل قسم بعنوان التطبيق بين علامتي ## (مثال: ## Wingstop)
- أجب باللغة العربية بأسلوب احترافي وموجز.
- استخدم تنسيق Markdown واضح.
"""

        try:
            logger.info(f"🤖 جاري إرسال طلب تحليل واحد لـ {len(apps_data)} تطبيقات...")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(combined_prompt)
                    full_analysis = response.text
                    logger.info("✅ تم استلام التحليل بنجاح!")
                    break
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        wait_time = 30 * (attempt + 1)
                        logger.warning(f"⚠️ تجاوز الحد، الانتظار {wait_time} ثانية...")
                        if attempt < max_retries - 1:
                            time.sleep(wait_time)
                        else:
                            raise e
                    else:
                        raise e

            results = self._parse_combined_response(full_analysis, apps_data.keys())
            return results

        except Exception as e:
            logger.error(f"❌ خطأ في التحليل: {e}")
            error_msg = f"️ فشل التحليل بسبب: {str(e)}"
            return {
                app_name: {
                    "app_name": app_name,
                    "analysis": error_msg,
                    "status": "error"
                }
                for app_name in apps_data.keys()
            }

    def _parse_combined_response(self, full_text: str, app_names) -> Dict[str, Dict]:
        """تقسيم الرد المجمع إلى نتائج لكل تطبيق"""
        results = {}
        sections = full_text.split("## ")
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            lines = section.split("\n")
            app_name_in_response = lines[0].strip()
            
            matched_app = None
            for name in app_names:
                if name.lower() in app_name_in_response.lower() or app_name_in_response.lower() in name.lower():
                    matched_app = name
                    break
            
            if matched_app:
                results[matched_app] = {
                    "app_name": matched_app,
                    "analysis": section,
                    "status": "success"
                }
        
        for name in app_names:
            if name not in results:
                results[name] = {
                    "app_name": name,
                    "analysis": full_text,
                    "status": "success"
                }
        
        return results