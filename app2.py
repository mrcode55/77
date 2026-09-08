#!/usr/bin/env python3
# أداة Jammer بلوتوث - يعمل بدون Root (محاكاة)
# التشغيل: streamlit run app2.py

import streamlit as st
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
st.markdown("### تشويش مستمر - بدون Root")
st.markdown("---")

st.warning("⚠️ هذا للاستخدام التعليمي فقط.")

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

def send_jam_packet():
    """محاكاة إرسال حزمة تشويش"""
    time.sleep(0.01)
    return random.choice([True, True, True, False])

def continuous_jam(intensity=5, interval=0.1):
    """تشويش مستمر"""
    while st.session_state.jamming:
        success_count = 0
        
        for _ in range(intensity):
            if not st.session_state.jamming:
                break
            if send_jam_packet():
                success_count += 1
                st.session_state.packets_sent += 1
            time.sleep(0.05)
        
        if success_count > 0:
            log_msg = f"📡 تم إرسال {success_count} حزمة تشويش - إجمالي: {st.session_state.packets_sent}"
            st.session_state.log.append(log_msg)
            if len(st.session_state.log) > 50:
                st.session_state.log = st.session_state.log[-50:]
        
        time.sleep(interval)

# ============================================================
# واجهة المستخدم
# ============================================================

st.markdown("### ⚙️ إعدادات التشويش")

col1, col2 = st.columns(2)
with col1:
    intensity = st.slider(
        "شدة التشويش:",
        min_value=1,
        max_value=20,
        value=10
    )
with col2:
    interval = st.slider(
        "السرعة (ثواني):",
        min_value=0.05,
        max_value=1.0,
        value=0.1,
        step=0.05
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
            st.success("🔥 بدأ التشويش")
            
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
# عرض الحالة
# ============================================================

if st.session_state.jamming:
    st.info("🔄 التشويش قيد التنفيذ...")
    st.progress(1.0, text="📡 جاري إرسال حزم التشويش")
    
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
st.markdown("### 📋 السجل")

if st.session_state.log:
    for entry in st.session_state.log[-15:]:
        st.text(entry)
else:
    st.info("لا يوجد سجل بعد")

if st.button("🧹 مسح السجل", use_container_width=True):
    st.session_state.log = []
    st.success("✅ تم مسح السجل")

# ============================================================
# إحصائيات
# ============================================================

st.markdown("---")
st.markdown("### 📊 الإحصائيات")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📦 إجمالي الحزم", st.session_state.packets_sent)
with col2:
    st.metric("⚡ شدة التشويش", intensity)
with col3:
    status = "🟢 نشط" if st.session_state.jamming else "🔴 متوقف"
    st.metric("📡 الحالة", status)

# ============================================================
# تعليمات التشغيل الحقيقي
# ============================================================

st.markdown("---")
st.markdown("### 🔧 للتشغيل الحقيقي (مع صلاحيات)")

st.code("""
# 1. افتح Termux
# 2. اكتب هذه الأوامر:

# تثبيت الأدوات
pkg update
pkg install bluez bluez-utils root-repo tsu

# تشغيل البلوتوث
termux-bluetooth-enable

# تشغيل الأداة بصلاحيات الجذر (إذا كان الهاتف مقرصن)
tsu
streamlit run app2.py
""", language="bash")

# ============================================================
# التذييل
# ============================================================

st.markdown("---")
st.markdown("⚠️ **ملاحظات:**")
st.markdown("1. بدون صلاحيات الجذر، الأداة تعمل في وضع المحاكاة")
st.markdown("2. للعمل الحقيقي، تحتاج إلى Root أو Termux API")
st.markdown("3. بعض الهواتف تمنع استخدام البلوتوث من Termux")

st.markdown("made by @cheifbreef on discord :)")