# Elmoder-Store — Free Web Deployment

هذه النسخة جاهزة للنشر على Render مع PostgreSQL (Neon أو Supabase).

## 1) تجربة محلية
- شغّل `run_windows.bat`.
- SQLite ستظل مستخدمة إذا لم يوجد `DATABASE_URL`.

## 2) PostgreSQL
أنشئ قاعدة PostgreSQL مجانية على Neon أو Supabase، ثم انسخ رابط الاتصال إلى متغير البيئة `DATABASE_URL`.

عند وجود `DATABASE_URL` يستخدم التطبيق PostgreSQL تلقائيًا. عند عدم وجوده يرجع إلى SQLite.

## 3) Render
- ارفع المجلد إلى GitHub.
- في Render أنشئ Web Service من المستودع.
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`
- Health: `/health`
- أضف `DATABASE_URL` و`ELMODER_SECRET_KEY`.

## 4) البيانات القديمة
النسخة المحلية لا تُرفع تلقائيًا. استخدم `migrate_sqlite_to_postgres.py` بعد وضع رابط PostgreSQL.

## ملاحظة
SQLite مناسبة للنسخة المحلية. PostgreSQL هي قاعدة البيانات المستخدمة عند النشر لتكون البيانات مشتركة بين الموبايل والكمبيوتر.

## أول نشر عملي
1. أنشئ حساب GitHub وارفع هذا المجلد كمستودع جديد.
2. أنشئ قاعدة PostgreSQL مجانية على Neon أو Supabase.
3. انسخ `DATABASE_URL` من قاعدة البيانات.
4. على جهازك، قبل تشغيل migration:
   - `pip install -r requirements.txt`
   - `set DATABASE_URL=YOUR_DATABASE_URL` (Windows CMD)
   - `python migrate_sqlite_to_postgres.py`
5. في Render اربط GitHub repo.
6. ضع نفس `DATABASE_URL` في Environment Variables.
7. Render ستشغل `gunicorn app:app` تلقائيًا.
8. افتح رابط Render من الموبايل.
