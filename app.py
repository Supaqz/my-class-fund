import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบกองทุนห้องเรียน", page_icon="💰", layout="wide")

# ==========================================
# 🗃️ ฐานข้อมูลจำลอง (Session State)
# ==========================================
# 1. ตารางผู้ใช้งานและตำแหน่ง (ทุกคนสามารถเปลี่ยนรหัสผ่านตัวเองได้)
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "topsecret", "name": "ผู้ควบคุมใหญ่สุด", "role": "ผู้ควบคุมใหญ่สุด"},
        "money1": {"password": "1234", "name": "สมชาย ใจดี (เหรัญญิก)", "role": "เหรัญญิก"},
        "student1": {"password": "student", "name": "สมหญิง รักเรียน", "role": "นักศึกษาทั่วไป"}
    }

if "classes" not in st.session_state:
    st.session_state.classes = ["IT-A", "IT-B"]

if "students" not in st.session_state:
    st.session_state.students = [
        {"id": "660101", "name": "สมชาย ใจดี (เหรัญญิก)", "class": "IT-A", "status": "✅ จ่ายแล้ว", "username": "money1"},
        {"id": "660102", "name": "สมหญิง รักเรียน", "class": "IT-A", "status": "❌ ยังไม่จ่าย", "username": "student1"},
    ]

if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"time": "2026-06-02 10:00", "type": "รายรับ", "detail": "สมชาย (กองกลาง)", "amount": 500.0},
    ]

# ระบบเช็กสถานะการล็อกอิน
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ==========================================
# 🔐 หน้าต่างล็อกอิน (Sidebar ด้านซ้าย)
# ==========================================
with st.sidebar:
    st.header("🔑 ระบบเข้าสู่ระบบ")
    
    if st.session_state.logged_in_user is None:
        username_input = st.text_input("ชื่อผู้ใช้งาน (Username)")
        password_input = st.text_input("รหัสผ่าน (Password)", type="password")
        
        if st.button("เข้าสู่ระบบ"):
            if username_input in st.session_state.users:
                if st.session_state.users[username_input]["password"] == password_input:
                    st.session_state.logged_in_user = username_input
                    st.success(f"ยินดีต้อนรับคุณ {st.session_state.users[username_input]['name']}")
                    st.rerun()
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง")
            else:
                st.error("ไม่พบชื่อผู้ใช้งานนี้")
    else:
        current_user = st.session_state.logged_in_user
        user_info = st.session_state.users[current_user]
        
        st.write(f"👤 **สวัสดี:** {user_info['name']}")
        st.write(f"🎖️ **ตำแหน่ง:** {user_info['role']}")
        
        # ฟังก์ชันเปลี่ยนรหัสผ่านเอง
        with st.expander("⚙️ เปลี่ยนรหัสผ่านตัวเอง"):
            new_pwd = st.text_input("รหัสผ่านใหม่", type="password")
            if st.button("บันทึกรหัสผ่านใหม่"):
                if new_pwd:
                    st.session_state.users[current_user]["password"] = new_pwd
                    st.success("เปลี่ยนรหัสผ่านสำเร็จ!")
                else:
                    st.error("กรุณากรอกรหัสผ่าน")
                    
        if st.button("ออกจากระบบ"):
            st.session_state.logged_in_user = None
            st.rerun()

# ==========================================
# 🎨 ส่วนแสดงผลหน้าเว็บหลัก (UI)
# ==========================================
st.title("ระบบจัดการห้องเรียน & กองทุนห้องส่วนกลาง 🌐")
st.markdown("---")

# ตรวจสอบสิทธิ์การใช้งานเบื้องต้น
user_role = st.session_state.users[st.session_state.logged_in_user]["role"] if st.session_state.logged_in_user else "นักศึกษาทั่วไป"

# สร้างแท็บสลับหน้าจอ (ถ้าเป็นแอดมินใหญ่สุดจะเห็นแท็บที่ 4 เพิ่มขึ้นมา)
tabs_list = ["📊 หน้าแรก & กองทุนห้อง", "👥 ข้อมูลนักศึกษา & จ่ายเงิน", "⚙️ ตั้งค่าระบบ"]
if user_role == "ผู้ควบคุมใหญ่สุด":
    tabs_list.append("👑 จัดการตำแหน่งสิทธิ์ (Admin)")

tabs = st.tabs(tabs_list)

# --- แท็บที่ 1: หน้าแรก & กองทุนห้อง ---
with tabs[0]:
    st.subheader("💰 ภาพรวมเงินกองกลาง")
    balance = sum(t["amount"] for t in st.session_state.transactions)
    st.metric(label="ยอดเงินคงเหลือในคลังทั้งหมด (บาท)", value=f"{balance:,.2f} บาท")
    
    st.markdown("---")
    
    # เฉพาะ แอดมิน หรือ เหรัญญิก ถึงจะเห็นปุ่มบันทึกรายจ่าย
    if user_role in ["ผู้ควบคุมใหญ่สุด", "เหรัญญิก"]:
        st.subheader("🛑 บันทึกรายจ่ายของห้อง (สิทธิ์เหรัญญิก/ผู้ควบคุม)")
        exp_detail = st.text_input("รายละเอียดรายจ่าย (เช่น ค่าชีทเรียน, ค่าหมูกระทะ)")
        exp_amount = st.number_input("จำนวนเงินที่จ่าย (บาท)", min_value=0.0, step=10.0)
        
        if st.button("บันทึกรายจ่ายลงระบบ"):
            if exp_detail and exp_amount > 0:
                st.session_state.transactions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "type": "รายจ่าย",
                    "detail": exp_detail,
                    "amount": -exp_amount
                })
                st.success(f"บันทึกรายจ่ายเรียบร้อยแล้ว!")
                st.rerun()
    else:
        st.info("💡 สมาชิกทั่วไปสามารถดูประวัติการเงินได้อย่างเดียว หากต้องการบันทึกข้อมูลกรุณาล็อกอิน")

    st.markdown("---")
    st.subheader("📜 ประวัติการเดินบัญชีทั้งหมด")
    if st.session_state.transactions:
        st.dataframe(pd.DataFrame(st.session_state.transactions), use_container_width=True)

# --- แท็บที่ 2: ข้อมูลนักศึกษา & จ่ายเงิน ---
with tabs[1]:
    st.subheader("👥 รายชื่อนักศึกษาและการส่งเงินกองกลาง")
    selected_class = st.selectbox("เลือกดูตามห้องเรียน", st.session_state.classes)
    
    df_students = pd.DataFrame(st.session_state.students)
    df_filtered = df_students[df_students["class"] == selected_class] if not df_students.empty else pd.DataFrame()
    
    if not df_filtered.empty:
        st.dataframe(df_filtered[["id", "name", "status"]], use_container_width=True)
    else:
        st.info("ยังไม่มีรายชื่อเพื่อนในห้องเรียนนี้")
        
    # เฉพาะ แอดมิน หรือ เหรัญญิก ถึงจะอัปเดตสถานะเงินได้
    if user_role in ["ผู้ควบคุมใหญ่สุด", "เหรัญญิก"]:
        st.markdown("---")
        st.subheader("🛑 บันทึกการรับเงินกองกลาง")
        unpaid_students = [s for s in st.session_state.students if s["class"] == selected_class and s["status"] == "❌ ยังไม่จ่าย"]
        
        if unpaid_students:
            selected_student_name = st.selectbox("เลือกรายชื่อคนที่มาจ่ายเงิน", [s["name"] for s in unpaid_students])
            income_amount = st.number_input("จำนวนเงินกองกลางที่เก็บ (บาท)", value=500.0, step=50.0)
            
            if st.button("ยืนยันการรับเงิน"):
                for s in st.session_state.students:
                    if s["name"] == selected_student_name:
                        s["status"] = "✅ จ่ายแล้ว"
                
                st.session_state.transactions.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "type": "รายรับ",
                    "detail": f"{selected_student_name} (เงินกองกลาง)",
                    "amount": income_amount
                })
                st.success(f"อัปเดตการจ่ายเงินสำเร็จ!")
                st.rerun()
        else:
            st.success("ทุกคนในห้องนี้จ่ายเงินครบหมดแล้ว! 🎉")

# --- แท็บที่ 3: ตั้งค่าระบบ (เพิ่มห้อง/เพิ่มเพื่อน) ---
with tabs[2]:
    if user_role in ["ผู้ควบคุมใหญ่สุด", "เหรัญญิก"]:
        st.subheader("⚙️ การจัดการโครงสร้างข้อมูล")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏫 เพิ่มห้องเรียน")
            new_class = st.text_input("ชื่อห้องเรียนใหม่")
            if st.button("ยืนยันเพิ่มห้อง"):
                if new_class and new_class not in st.session_state.classes:
                    st.session_state.classes.append(new_class)
                    st.success(f"เพิ่มห้องเรียน {new_class} สำเร็จ!")
                    st.rerun()
                
        with col2:
            st.markdown("### 👤 เพิ่มรายชื่อเพื่อนและสร้างบัญชีล็อกอินให้เพื่อน")
            new_id = st.text_input("รหัสนักศึกษา")
            new_name = st.text_input("ชื่อ-นามสกุล")
            new_user = st.text_input("ตั้ง Username ให้เพื่อน (ภาษาอังกฤษ)")
            new_pass = st.text_input("ตั้ง Password เริ่มต้นให้เพื่อน")
            target_class = st.selectbox("เลือกห้องเรียน", st.session_state.classes)
            
            if st.button("ยืนยันเพิ่มรายชื่อ"):
                if new_id and new_name and new_user and new_pass:
                    # เพิ่มเข้าตารางล็อกอินล็อกอิน
                    st.session_state.users[new_user] = {"password": new_pass, "name": new_name, "role": "นักศึกษาทั่วไป"}
                    # เพิ่มเข้าตารางนักศึกษา
                    st.session_state.students.append({"id": new_id, "name": new_name, "class": target_class, "status": "❌ ยังไม่จ่าย", "username": new_user})
                    st.success(f"เพิ่มคุณ {new_name} เข้าสู่ระบบแล้ว!")
                    st.rerun()
    else:
        st.warning("🔒 หน้านี้สำหรับเหรัญญิกหรือผู้ควบคุมระบบเท่านั้น")

# --- แท็บที่ 4: สำหรับผู้ควบคุมใหญ่สุดเท่านั้น (จัดการตำแหน่ง) ---
if user_role == "ผู้ควบคุมใหญ่สุด":
    with tabs[3]:
        st.subheader("👑 บอร์ดควบคุมตำแหน่งของเพื่อนในระบบ")
        st.write("คุณสามารถเลือกเปลี่ยนสถานะ/ตำแหน่งของสมาชิกทุกคนได้ที่นี่")
        
        # แสดงตารางผู้ใช้งานปัจจุบันทั้งหมด
        df_users_list = pd.DataFrame([
            {"Username": k, "ชื่อ-นามสกุล": v["name"], "ตำแหน่งปัจจุบัน": v["role"]} 
            for k, v in st.session_state.users.items()
        ])
        st.dataframe(df_users_list, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🔄 เปลี่ยนตำแหน่งผู้ใช้งาน")
        
        # เลือกชื่อ User ที่ต้องการเปลี่ยนตำแหน่ง
        user_to_change = st.selectbox("เลือกบัญชีผู้ใช้ที่ต้องการเปลี่ยนตำแหน่ง", list(st.session_state.users.keys()))
        new_role_assigned = st.selectbox("เลือกตำแหน่งใหม่", ["นักศึกษาทั่วไป", "เหรัญญิก", "ผู้ควบคุมใหญ่สุด"])
        
        if st.button("บันทึกการเปลี่ยนตำแหน่ง"):
            st.session_state.users[user_to_change]["role"] = new_role_assigned
            st.success(f"เปลี่ยนตำแหน่งของบัญชี {user_to_change} เป็น '{new_role_assigned}' เรียบร้อยแล้ว!")
            st.rerun()
