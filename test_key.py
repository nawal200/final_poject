import google.generativeai as genai

# ⚠️ ضعي مفتاحك الجديد هنا بين علامتي التنصيص، وتأكد من عدم وجود مسافات
MY_API_KEY = "AIzaSy........................................" 

# تنظيف المفتاح من أي مسافات أو أسطر جديدة مخفية
clean_key = MY_API_KEY.strip().replace('\n', '').replace('\r', '')

try:
    print("جاري الاتصال بـ Google Gemini...")
    genai.configure(api_key=clean_key)
    
    # اختبار بسيط
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("قل مرحباً")
    
    print("✅ نجح الاتصال بنجاح!")
    print(f"رد النموذج: {response.text}")
    
except Exception as e:
    print(f"❌ فشل الاتصال. الخطأ: {e}")
    print("💡 تأكد من أن المفتاح صحيح ولم يحتوي على مسافات عند النسخ.")