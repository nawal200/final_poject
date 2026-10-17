from market_engine import MarketEngine

# إنشاء كائن من المحرك
engine = MarketEngine()

# اختبار البحث
print("=== اختبار البحث ===")
apps = engine.search_apps("fitness tracker", num_results=5)
for app in apps:
    print(f"- {app['title']} ({app['developer']}) - Rating: {app['rating']}")

# اختبار جلب التقييمات
if apps:
    print("\n=== اختبار جلب التقييمات ===")
    app_id = apps[0]['app_id']
    print(f"جلب التقييمات لـ {apps[0]['title']}")
    
    reviews_df = engine.scrape_reviews(app_id, count=50)
    print(f"تم جلب {len(reviews_df)} تقييم")
    
    # اختبار تحليل المشاعر
    print("\n=== اختبار تحليل المشاعر ===")
    processed_df = engine.process_reviews(reviews_df)
    print(processed_df[['content', 'sentiment', 'polarity']].head())
    
    # اختبار الحفظ في قاعدة البيانات
    print("\n=== اختبار حفظ البيانات ===")
    apps_df = pd.DataFrame(apps)
    engine.save_to_database(apps_df, processed_df)
    print("تم الحفظ بنجاح!")