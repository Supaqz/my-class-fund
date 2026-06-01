import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บให้โมเดิร์นและเต็มจอ
st.set_page_config(page_title="ระบบกระดานเช็กเงินห้องเรียน", page_icon="📝", layout="wide")

SECRET_PASSWORD = "admin123" 

# ==========================================
# 🗃️ ฐานข้อมูลจำลอง (Session State)
# ==========================================
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "topsecret", "name": "ผู้ควบคุมใหญ่สุด", "role": "ผู้ควบคุมใหญ่สุด"},
        "money1": {"password": "1234", "name": "เหรัญญิกหลัก", "role": "เหรัญญิก"},
    }

if "classes" not in st.session_state:
    st.session_state.classes = ["IT-A", "IT-B"]

if "students" not in st.session_state:
    st.session_state.students = [
        {"id": "660101", "name": "สมชาย ใจดี", "class": "IT-A", "status": "✅ จ่ายแล้ว"},
        {"id": "660102", "name": "สมหญิง รักเรียน", "class": "IT-A", "status": "❌ ยังไม่จ่าย"},
        {"id": "660103", "name": "นายกิตติ เรียนดี", "class": "IT-B", "status": "✅ จ่ายแล้ว"},
        {"id": "660104", "name": "นางสาวปิยะนาถ สุขใจ", "class": "IT-A", "status": "❌ ยังไม่จ่าย"},
    ]

if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"time": "2026-06-02 10:00", "type": "รายรับ", "student_id": "660101", "detail": "สมชาย ใจดี (เงินกองกลาง)", "amount": 500.0, "class": "IT-A"},
        {"time": "2026-06-02 11:00", "type": "รายรับ", "student_id": "660103", "detail": "นายกิตติ เรียนดี (เงินกองกลาง)", "amount": 500.0, "class": "IT-B"},
    ]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ตรวจสอบสิทธิ์ปัจจุบัน
current_user = st.session_state.logged_in_user
user_role = st.session_state.users[current_user]["role"] if current_user else "นักศึกษาทั่วไป"
is_authorized = user_role in ["ผู้ควบคุมใหญ่สุด", "เหรัญญิก"]

# ==========================================
# 🔐 หน้าต่างล็อกอิน (Sidebar ด้านซ้าย)
# ==========================================
with st.sidebar:
    st.markdown("### 🔐 ศูนย์บัญชาการผู้ดูแล")
    if st.session_state.logged_in_user is None:
        st.info("💡 เพื่อนๆ ดูสถานะการจ่ายเงินได้ทันที ส่วนเหรัญญิกกรุณาล็อกอินเพื่อทำการเช็กเงิน")
        username_input = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="กรอกสิทธิ์ผู้ดูแล")
        password_input = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="••••••••")
        
        if st.button("🚪 เข้าสู่ระบบ", use_container_width=True):
            if username_input in st.session_state.users:
                if st.session_state.users[username_input]["password"] == password_input:
                    st.session_state.logged_in_user = username_input
                    st.toast(f"🎉 ยินดีต้อนรับ {st.session_state.users[username_input]['name']}", icon="🔓")
                    st.rerun()
                else: st.error("รหัสผ่านไม่ถูกต้อง")
            else: st.error("ไม่พบชื่อผู้ใช้งานนี้")
    else:
        st.markdown(f"""
        <div style="background-color:#1e293b; padding:15px; border-radius:10px; margin-bottom:15px; color:white;">
            <p style='margin:0; font-size:14px; opacity:0.8;'>ผู้ใช้งานปัจจุบัน</p>
            <h4 style='margin:5px 0;'>👤 {st.session_state.users[current_user]['name']}</h4>
            <span style='background-color:#3b82f6; padding:2px 8px; border-radius:12px; font-size:12px;'>🎖️ {user_role}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 ออกจากระบบ", type="primary", use_container_width=True):
            st.session_state.logged_in_user = None
            st.toast("ออกจากระบบเรียบร้อย", icon="🔒")
            st.rerun()

# ==========================================
# 🎨 หน้าจอหลัก: กระดานเช็กเงินกองกลางห้องเรียน
# ==========================================
st.title("📝 กระดานเช็กเงินกองกลางนักศึกษา")
st.markdown("---")

# เลือกห้องเรียนที่จะเช็กชื่อ/เช็กเงิน
if st.session_state.classes:
    selected_room = st.selectbox("🎯 เลือกห้องเรียนที่ต้องการเปิดใบเช็กเงิน:", st.session_state.classes)
else:
    st.warning("⚠️ กรุณาไปที่แท็บ '⚙️ ตั้งค่าระบบ' เพื่อสร้างห้องเรียนก่อนครับ")
    selected_room = None

if selected_room:
    tab1, tab2, tab3 = st.tabs(["📝 ใบเช็กเงินกองกลางห้อง", "💸 บันทึกรายจ่าย & ประวัติ", "⚙️ ตั้งค่าระบบ (เพิ่มห้อง/เพื่อน)"])

    # ==========================================
    # แท็บที่ 1: หน้าใบเช็กเงิน + ระบบค้นหาเรียลไทม์
    # ==========================================
    with tab1:
        st.header(f"📋 ใบรายชื่อเช็กเงินกองกลางประจำห้อง {selected_room}")
        
        # คำนวณเงินห้องปัจจุบัน
        df_t = pd.DataFrame(st.session_state.transactions)
        df_t_room = df_t[df_t["class"] == selected_room] if not df_t.empty else pd.DataFrame()
        room_balance = df_t_room["amount"].sum() if not df_t_room.empty else 0.0
        st.metric(label="💰 ยอดเงินคงเหลือในคลังของห้องตอนนี้", value=f"{room_balance:,.2f} บาท")
        st.markdown("---")
        
        # กรองข้อมูลนักศึกษาเฉพาะห้องนี้
        room_students = [s for s in st.session_state.students if s["class"] == selected_room]
        
        if room_students:
            # 🔍 ช่องค้นหาอัจฉริยะ (พิมพ์ปุ๊บ ค้นหาปั๊บ)
            st.markdown("### 🔍 ค้นหารายชื่อนักศึกษาในใบเช็กชื่อนี้")
            search_query = st.text_input("ระบุ รหัสนักศึกษา หรือ ชื่อ-นามสกุล ที่ต้องการค้นหา:", placeholder="พิมพ์ค้นหาที่นี่...")
            st.markdown("---")
            
            st.markdown("##### 👥 ตารางใบเช็กเงิน")
            
            # หัวตารางจำลองให้ดูสวยงาม
            h1, h2, h3, h4 = st.columns([2, 3, 2, 3])
            h1.markdown("**รหัสนักศึกษา**")
            h2.markdown("**ชื่อ - นามสกุล**")
            h3.markdown("**สถานะการจ่าย**")
            h4.markdown("**การกระทำ (เฉพาะเหรัญญิก)**")
            st.markdown("<hr style='margin:5px 0 15px 0;'>", unsafe_allow_html=True)
            
            # วาดแถวรายชื่อทีละแถว และทำการกรองตามคำค้นหา
            found_any = False
            for idx, student in enumerate(room_students):
                # ตรวจสอบคำค้นหา (ถ้าพิมพ์มาแล้วไม่ตรง ให้ข้ามแถวนี้ไป)
                if search_query:
                    if (search_query.lower() not in student["name"].lower()) and (search_query not in student["id"]):
                        continue
                
                found_any = True
                c1, c2, c3, c4 = st.columns([2, 3, 2, 3])
                c1.write(student["id"])
                c2.write(student["name"])
                
                # แสดงสัญลักษณ์สีตามสถานะเงิน
                if student["status"] == "✅ จ่ายแล้ว":
                    c3.markdown("<span style='color:green; font-weight:bold;'>✅ จ่ายแล้ว</span>", unsafe_allow_html=True)
                else:
                    c3.markdown("<span style='color:red; font-weight:bold;'>❌ ยังไม่จ่าย</span>", unsafe_allow_html=True)
                
                # ปุ่มกดเช็กสถานะเงิน (เหมือนช่องติ๊กใบเช็กชื่อ)
                if is_authorized:
                    if student["status"] == "❌ ยังไม่จ่าย":
                        if c4.button(f"🔄 เช็กว่าจ่ายเงินแล้ว", key=f"pay_{idx}", use_container_width=True):
                            for s in st.session_state.students:
                                if s["id"] == student["id"]:
                                    s["status"] = "✅ จ่ายแล้ว"
                            st.session_state.transactions.append({
                                "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": "รายรับ",
                                "student_id": student["id"], "detail": f"{student['name']} (เงินกองกลาง)",
                                "amount": 500.0, "class": selected_room
                            })
                            st.toast(f"เช็กเงินของคุณ {student['name']} เรียบร้อย!", icon="✅")
                            st.rerun()
                    else:
                        if c4.button(f"↩️ ยกเลิกการจ่าย (กดผิด)", key=f"unpay_{idx}", use_container_width=True, type="secondary"):
                            for s in st.session_state.students:
                                if s["id"] == student["id"]:
                                    s["status"] = "❌ ยังไม่จ่าย"
                            st.session_state.transactions = [
                                t for t in st.session_state.transactions 
                                if not (t["student_id"] == student["id"] and t["type"] == "รายรับ")
                            ]
                            st.toast(f"ยกเลิกสถานะเงินของ {student['name']} แล้ว", icon="ℹ️")
                            st.rerun()
                else:
                    c4.write("🔒 ล็อกอินเพื่อสลับสถานะ")
                st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
                
            if not found_any:
                st.info("🔍 ไม่พบรายชื่อนักศึกษาที่ตรงกับคำค้นหานี้")
        else:
            st.info(f"ห้อง {selected_room} นี้ยังไม่มีรายชื่อเพื่อนนักศึกษา กรุณาไปเพิ่มรายชื่อที่แท็บตั้งค่าระบบ")

    # ==========================================
    # แท็บที่ 2: บันทึกรายจ่าย & ดูประวัติบัญชี
    # ==========================================
    with tab2:
        st.header(f"💸 บัญชีรายรับ-รายจ่ายของห้อง {selected_room}")
        
        if is_authorized:
            st.subheader("🛑 บันทึกการเอาเงินห้องไปใช้ (รายจ่าย)")
            exp_detail = st.text_input("ระบุรายละเอียดรายจ่าย (เช่น ค่าชีทบทที่ 2, ค่าบอร์ดนิทรรศการ)")
            exp_amount = st.number_input("จำนวนเงินที่จ่ายออก (บาท)", min_value=0.0, step=10.0)
            if st.button("💸 บันทึกรายจ่ายส่วนกลาง", use_container_width=True):
                if exp_detail and exp_amount > 0:
                    st.session_state.transactions.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": "รายจ่าย",
                        "student_id": "-", "detail": exp_detail, "amount": -exp_amount, "class": selected_room
                    })
                    st.toast("บันทึกรายจ่ายห้องเรียบร้อย!", icon="💸")
                    st.rerun()
                    
        st.markdown("---")
        st.subheader("📜 ประวัติบันทึกธุรกรรมทั้งหมดทางการเงิน")
        if not df_t_room.empty:
            st.dataframe(df_t_room[["time", "type", "student_id", "detail", "amount"]], use_container_width=True)
        else:
            st.info("ยังไม่มีรายการเดินบัญชีเงินกองกลางในห้องนี้")

    # ==========================================
    # แท็บที่ 3: ตั้งค่าโครงสร้างข้อมูล (เพิ่มห้อง/เพิ่มเพื่อน)
    # ==========================================
    with tab3:
        if is_authorized:
            st.header("⚙️ แผงจัดการจัดการระบบนักศึกษา")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏫 ระบบห้องเรียน")
                new_room = st.text_input("เพิ่มชื่อห้องเรียนใหม่:")
                if st.button("🏫 ยืนยันสร้างห้องเรียนใหม่", use_container_width=True):
                    if new_room and new_room not in st.session_state.classes:
                        st.session_state.classes.append(new_room)
                        st.toast(f"สร้างห้อง {new_room} สำเร็จ", icon="🏫")
                        st.rerun()
                st.markdown("---")
                del_room = st.selectbox("เลือกห้องเรียนที่ต้องการลบออกจากระบบ:", st.session_state.classes)
                if st.button("🗑️ ลบห้องเรียนนี้เด็ดขาด", type="primary", use_container_width=True):
                    st.session_state.classes.remove(del_room)
                    st.session_state.students = [s for s in st.session_state.students if s["class"] != del_room]
                    st.toast(f"ลบห้อง {del_room} สำเร็จ", icon="🗑️")
                    st.rerun()

            with col2:
                st.markdown("### 👤 เพิ่มนักศึกษาเข้าใบเช็กชื่อ")
                stu_id = st.text_input("กรอกรหัสนักศึกษา:")
                stu_name = st.text_input("กรอกชื่อ - นามสกุล:")
                stu_class = st.selectbox("เลือกห้องเรียนปลายทาง (Dropdown):", st.session_state.classes, key="add_stu_key")
                
                if st.button("👤 เพิ่มรายชื่อเพื่อนเข้าตาราง", use_container_width=True):
                    if stu_id and stu_name and stu_class:
                        if any(s["id"] == stu_id for s in st.session_state.students):
                            st.error("รหัสนักศึกษานี้มีอยู่ในระบบแล้ว")
                        else:
                            st.session_state.students.append({
                                "id": stu_id, "name": stu_name, "class": stu_class, "status": "❌ ยังไม่จ่าย"
                            })
                            st.toast(f"เพิ่มชื่อ {stu_name} เข้าใบเช็กเงินแล้ว!", icon="👤")
                            st.rerun()
                    else: st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
        else:
            st.warning("🔒 เฉพาะแอดมินหรือเหรัญญิกเท่านั้นที่ได้รับสิทธิ์ให้ปรับปรุงโครงสร้างรายชื่อนักศึกษา")
