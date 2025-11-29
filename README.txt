AF IMPERIYA · DEMO AI500 VERSIYASI
==================================

Bu demo loyiha Flask asosida qurilgan va quyidagi modullarni ko'rsatadi:

- Dashboard (statistik kartalar + 3 ta grafik):
  * Topshiriqlar holati (doughnut chart)
  * Solar energiya (real + AI forecast)
  * Xodim activity bar-chart (heatmap o'rniga soddalashtirilgan)

- Topshiriqlar moduli:
  * Yaratish
  * Holatni o'zgartirish
  * Ustuvorlik
  * Kimga biriktirish
  * Aziz AI mini-tavsiyasi

- Ijro moduli:
  * Muddatga qarab rangli indikator
  * Qolgan kunlar hisoblash

- Solar moduli:
  * Kunlik energiya grafiki + forecast

- Xodim activity:
  * Kunlik bajarilgan topshiriqlar grafigi

DEMO LOGIN:
-----------

Admin:  admin@example.com / admin123
Rahbar: rahbar@example.com / rahbar123
Xodim:  xodim@example.com / xodim123

QANDAY ISHGA TUSHIRISH:
-----------------------

1) Virtual environment (ixtiyoriy, lekin tavsiya etiladi):

   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows

2) Kerakli kutubxonalarni o'rnatish:

   pip install -r requirements.txt

3) Demo bazani tayyorlash:

   flask --app app.py init-demo

   yoki:

   python app.py   # birinchi ishga tushganda o'zi create qiladi

4) Serverni ishga tushirish:

   flask --app app.py run

   yoki:

   python app.py

5) Brauzerda oching:

   http://127.0.0.1:5000

   Login sahifa chiqadi. Yuqoridagi demo loginlardan birini kiriting.

Eslatma:
--------

Bu demo loyiha AI500 musobaqasi uchun "showcase" maqsadida soddalashtirilgan.
Real produktsiya uchun security (CSRF, real AI API, Telegram integratsiyasi va boshqalar)
alohida qo'shilishi kerak bo'ladi.
