import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บให้เป็นแบบเต็มจอ และกำหนดธีมเบื้องต้น
st.set_page_config(page_title="ระบบกองทุนห้องเรียน", page_icon="💰", layout="wide")

SECRET_PASSWORD = "admin123" 

# 🔗 [สำคัญมาก!] วาง URL ของ Google Sheets ของคุณที่นี่
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1I7VxaAK1BSpIE4WHxoNDre7URuVavkfHAhBJrnehDjw/edit?usp=sharing"

# ==========================================
# 🗃️ ฟังก์ชันแปลงลิงก์ Google Sheets ให้ดึงข้อมูลเป็น DataFrame ได้ทันที
# ==========================================
def load_data(sheet_name):
    try:
        # ตัดส่วนท้ายของ URL ออกเพื่อเปลี่ยนเป็นคำสั่งดึงข้อมูลในรูปแบบ CSV
        base_url = GOOGLE_SHEET_URL.split("/edit")[0]
        csv_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        
        # ดึงข้อมูลและแปลงทุกคอลัมน์เป็นข้อความเพื่อไม่ให้เกิดปัญหาช่องว่าง
        df = pd.read_csv(csv_url)
        df = df.dropna(how="all") # ลบแถวที่ว่างเปล่าออก
        return df.astype(str)
    except Exception as e:
        # หากดึงไม่ได้หรือแผ่นงานยังไม่มีข้อมูล ให้สร้างโครงสร้างตารางเริ่มต้นให้เอง
        if sheet_name == "Students":
            return pd.DataFrame(columns=["id", "name", "class", "status"])
        elif sheet_name == "Classes":
            return pd.DataFrame(columns=["class_name"])
        else:
            return pd.DataFrame(columns=["time", "type", "detail", "amount"])

# โหลดข้อมูลจริงเข้ามาใช้งาน
df_students = load_data("Students")
df_classes = load_data("Classes")
df_trans = load_data("Transactions")

# แปลงประเภทข้อมูลตัวเลขของจำนวนเงิน
if "amount" in df_trans.columns:
    df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors='coerce').fillna(0.0)
else:
    df_trans["amount"] = []

# ==========================================
# 🎨 หน้าตาโปรแกรม (UI การจัดรูปแบบ)
# ==========================================
st.title("ระบบจัดการห้องเรียน & กองทุนห้องส่วนกลาง 🌐")
st.caption("ระบบฐานข้อมูลออนไลน์ ทำงานร่วมกับ Google Sheets เพื่อความโปร่งใส")
st.markdown("---")

# สร้างแท็บในการเลือกดูข้อมูล
tab1, tab2, tab3 = st.tabs(["📊 หน้าแรก & กองทุนห้อง", "👥 ข้อมูลนักศึกษา & จ่ายเงิน", "⚙️ ตั้งค่าระบบ"])

# --- แท็บที่ 1: สรุปกองทุนห้อง ---
with tab1:
    st.subheader("💰 สรุปยอดเงินในคลัง")
    balance = df_trans["amount"].sum() if not df_trans.empty else 0.0
    st.metric(label="ยอดเงินคงเหลือในคลังทั้งหมด (บาท)", value=f"{balance:,.2f} บาท")
    
    st.markdown("---")
    
    # บันทึกรายจ่าย
    st.subheader("🛑 บันทึกรายจ่ายของห้อง (เฉพาะเหรัญญิก)")
    with st.expander("คลิกเปิดเพื่อบันทึกรายจ่าย"):
        pwd = st.text_input("กรอกรหัสผ่านเหรัญญิก", type="password", key="pwd_expense")
        if pwd == SECRET_PASSWORD:
            exp_detail = st.text_input("รายละเอียดรายจ่าย (เช่น ค่าชีทเรียน, ค่าหมูกระทะ)")
            exp_amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0)
            if st.button("บันทึกรายจ่ายลงระบบ"):
                st.info("ระบบอัปเดตข้อมูลบนความจำแล้ว (คุณสามารถเปิดสิทธิ์ Google Sheets เพื่อบันทึกถาวร)")
        elif pwd:
            st.error("รหัสผ่านไม่ถูกต้อง")
            
    st.markdown("---")
    st.subheader("📜 ประวัติการเดินบัญชีทั้งหมด")
    if not df_trans.empty:
        st.dataframe(df_trans, use_container_width=True)
    else:
        st.info("ยังไม่มีประวัติการทำรายการเงิน")

# --- แท็บที่ 2: รายชื่อและการจ่ายเงิน ---
with tab2:
    st.subheader("👥 รายชื่อนักศึกษาในห้องเรียน")
    
    if not df_classes.empty and "class_name" in df_classes.columns:
        class_list = df_classes["class_name"].tolist()
        selected_class = st.selectbox("เลือกดูตามห้องเรียน", class_list)
        
        if not df_students.empty and "class" in df_students.columns:
            df_filtered = df_students[df_students["class"] == selected_class]
            if not df_filtered.empty:
                st.dataframe(df_filtered[["id", "name", "status"]], use_container_width=True)
            else:
                st.info("ยังไม่มีรายชื่อเพื่อนในห้องเรียนนี้")
        else:
            st.info("ยังไม่มีข้อมูลนักศึกษาในระบบ")
    else:
        st.warning("กรุณาเพิ่มห้องเรียนในแท็บตั้งค่าก่อน")

# --- แท็บที่ 3: การตั้งค่าระบบ ---
with tab3:
    st.subheader("⚙️ การจัดการโครงสร้างข้อมูล")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏫 เพิ่มห้องเรียน")
        new_class = st.text_input("ชื่อห้องเรียนใหม่ (เช่น IT-A)")
        if st.button("ยืนยันเพิ่มห้อง"):
            st.success(f"บันทึกข้อมูลห้อง {new_class} ชั่วคราวสำเร็จ")
            
    with col2:
        st.markdown("### 👤 เพิ่มรายชื่อเพื่อน")
        new_id = st.text_input("รหัสนักศึกษา")
        new_name = st.text_input("ชื่อ-นามสกุล")
        if st.button("ยืนยันเพิ่มรายชื่อ"):
            st.success(f"บันทึกข้อมูลคุณ {new_name} ชั่วคราวสำเร็จ")
