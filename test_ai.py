import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from market_ai import MarketAI

print("=== بدء اختبار محرك الذكاء الاصطناعي ===")

# 1. ⚠️ هام جداً: استبدل النص أدناه بمفتاح API الحقيقي الخاص بك
# يمكنك الحصول عليه مجاناً من: https://aistudio.google.com/app/apikey
API_KEY = "AQ.Ab8RN6JNmZ-uTGkBvWJCD9SdcKmFofG4MCUgRAyK3rxQWcrLnw" 

if API_KEY == "ضع_مفتاح_API_الخاص_بك_هنا":
    print("\n⚠️ تنبيه: لم تقم بتغيير مفتاح API الافتراضي!")
    print("يرجى فتح ملف test_ai.py واستبدال 'ضع_مفتاح_API_الخاص_بك_هنا' بمفتاحك الحقيقي.")
    print("💡 نصيحة: إذا لم يكن لديك مفتاح بعد، يمكنك تخطي هذا الاختبار الآن، وسنقوم ببناء واجهة Streamlit لتسمح لك بإدخال المفتاح من المتصفح مباشرة لاحقاً.")
else:
    try:
        print("\nجاري تهيئة نموذج Gemini...")
        ai_engine = MarketAI(api_key=API_KEY)
        
        # بيانات تجريبية
        mock_reviews = """
        التطبيق بطيء جداً ويغلق فجأة عند فتح الكاميرا.
        لا يوجد وضع ليلي، هذا أمر محبط جداً.
        أتمنى لو تضيفون ميزة المزامنة مع السحابة.
        واجهة المستخدم معقدة جداً، لا أستطيع إيجاد زر التسجيل.
        فقدت بياناتي بعد التحديث الأخير، كارثة!
        """
        
        print("جاري إرسال التقييمات للتحليل (قد يستغرق بضع ثوانٍ)...")
        result = ai_engine.analyze_market_gaps(mock_reviews, "تطبيق منافس تجريبي")
        
        if result.get("status") == "success":
            print("\n✅ تم التحليل بنجاح!\n")
            print(result["analysis"])
        else:
            print(f"\n❌ فشل التحليل: {result.get('analysis')}")
            
    except Exception as e:
        print(f"\n❌ حدث خطأ غير متوقع: {e}")

print("\n=== انتهى الاختبار ===")