import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบกองทุนห้องเรียน Pro", page_icon="💰", layout="wide")

# ==========================================
# 🗃️ ฐานข้อมูลจำลอง (Session State)
# ==========================================
# 1. ระบบบัญชีผู้ใช้
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": {"password": "topsecret", "name": "ผู้ควบคุมใหญ่สุด", "role": "ผู้ควบคุมใหญ่สุด"},
        "money1": {"password": "1234", "name": "เหรัญญิกหลัก", "role": "เหรัญญิก"},
    }

# 2. ระบบห้องเรียน
if "classes" not in st.session_state:
    st.session_state.classes = ["IT-A", "IT-B"]

# 3. ระบบข้อมูลนักศึกษา
if "students" not in st.session_state:
    st.session_state.students = [
        {"id": "660101", "name": "สมชาย ใจดี", "class": "IT-A", "status": "✅ จ่ายแล้ว"},
        {"id": "660102", "name": "สมหญิง รักเรียน", "class": "IT-A", "status": "❌ ยังไม่จ่าย"},
        {"id": "660103", "name": "นายกิตติ เรียนดี", "class": "IT-B", "status": "✅ จ่ายแล้ว"},
    ]

# 4. ระบบบัญชีรายรับ-รายจ่าย
if "transactions" not in st.session_state:
    st.session_state.transactions = [
        {"id": 1, "time": "2026-06-02 10:00", "type": "รายรับ", "student_id": "660101", "detail": "สมชาย ใจดี (เงินกองกลาง)", "amount": 500.0, "class": "IT-A"},
        {"id": 2, "time": "2026-06-02 11:00", "type": "รายรับ", "student_id": "660103", "detail": "นายกิตติ เรียนดี (เงินกองกลาง)", "amount": 500.0, "class": "IT-B"},
    ]

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ตรวจสอบสิทธิ์ปัจจุบัน
current_user = st.session_state.logged_in_user
user_role = st.session_state.users[current_user]["role"] if current_user else "นักศึกษาทั่วไป"
is_authorized = user_role in ["ผู้ควบคุมใหญ่สุด", "เหรัญญิก"]

# ==========================================
# 🔐 หน้าต่างล็อกอิน & สร้างบัญชีผู้ดูแล (Sidebar ด้านซ้าย)
# ==========================================
with st.sidebar:
    st.header("🔑 ระบบบัญชีผู้ใช้งาน")
    
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
        st.write(f"👤 **ผู้ใช้งาน:** {st.session_state.users[current_user]['name']}")
        st.write(f"🎖️ **ตำแหน่ง:** {user_role}")
        
        if st.button("ออกจากระบบ"):
            st.session_state.logged_in_user = None
            st.rerun()
            
        st.markdown("---")
        
        # 👑 ฟีเจอร์พิเศษ: ผู้ที่ได้รับอนุญาตสามารถสร้างบัญชีแอดมิน/เหรัญญิกเพิ่มเองได้
        if is_authorized:
            st.subheader("➕ สร้างบัญชีผู้ดูแลเพิ่ม")
            with st.expander("เปิดฟอร์มสร้างบัญชี"):
                new_admin_user = st.text_input("ตั้ง Username ใหม่")
                new_admin_name = st.text_input("ชื่อ-นามสกุล ผู้ดูแล")
                new_admin_pass = st.text_input("ตั้ง Password", type="password")
                new_admin_role = st.selectbox("เลือกตำแหน่ง", ["เหรัญญิก", "ผู้ควบคุมใหญ่สุด"])
                
                if st.button("ยืนยันสร้างบัญชีผู้ดูแล"):
                    if new_admin_user and new_admin_name and new_admin_pass:
                        if new_admin_user in st.session_state.users:
                            st.error("Username นี้มีในระบบแล้ว")
                        else:
                            st.session_state.users[new_admin_user] = {
                                "password": new_admin_pass,
                                "name": new_admin_name,
                                "role": new_admin_role
                            }
                            st.success(f"สร้างบัญชี {new_admin_user} สำเร็จ!")
                            st.rerun()
                    else:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วน")

# ==========================================
# 🎨 หน้าจอหลักของ Web App
# ==========================================
st.title("ระบบจัดการห้องเรียน & กองทุนห้องส่วนกลาง 🌐")
st.markdown("---")

# แบ่งหน้าจอแยกรายห้องอย่างเด็ดขาดที่หน้าแรก
if st.session_state.classes:
    selected_global_class = st.selectbox("🎯 เลือกห้องเรียนหลักที่ต้องการเข้าถึงข้อมูล:", st.session_state.classes)
else:
    st.warning("⚠️ กรุณาไปที่แท็บ '⚙️ ตั้งค่าระบบ' เพื่อสร้างห้องเรียนเป็นอันดับแรกก่อนใช้งานระบบ")
    selected_global_class = None

if selected_global_class:
    tab1, tab2, tab3 = st.tabs(["📊 หน้าแรก & การเงินห้อง", "👥 รายชื่อนักศึกษา", "⚙️ ตั้งค่าระบบ"])

    # ==========================================
    # แท็บที่ 1: หน้าแรก & การเงินห้อง (แยกรายห้องเด็ดขาด)
    # ==========================================
    with tab1:
        st.header(f"📊 ข้อมูลการเงินประจำห้อง {selected_global_class}")
        
        # กรองข้อมูลธุรกรรมเฉพาะห้องที่เลือก
        df_trans = pd.DataFrame(st.session_state.transactions)
        df_trans_filtered = df_trans[df_trans["class"] == selected_global_class] if not df_trans.empty else pd.DataFrame()
        
        # คำนวณเงินคงเหลือประจำห้อง
        room_balance = df_trans_filtered["amount"].sum() if not df_trans_filtered.empty else 0.0
        st.metric(label=f"💰 ยอดเงินคงเหลือรวมห้อง {selected_global_class}", value=f"{room_balance:,.2f} บาท")
        
        st.markdown("---")
        
        # ค้นหาประวัติการเงิน
        st.subheader("🔍 ค้นหาประวัติธุรกรรมเงิน")
        search_query = st.text_input("ใส่รหัสนักศึกษา หรือ ชื่อ เพื่อค้นหาประวัติการเงิน:")
        
        display_trans_df = df_trans_filtered.copy()
        if search_query and not display_trans_df.empty:
            display_trans_df = display_trans_df[
                display_trans_df["detail"].str.contains(search_query, case=False, na=False) | 
                display_trans_df["student_id"].str.contains(search_query, case=False, na=False)
            ]
            
        if not display_trans_df.empty:
            st.dataframe(display_trans_df[["time", "type", "student_id", "detail", "amount"]], use_container_width=True)
        else:
            st.info("ไม่พบประวัติการเงินที่ตรงกับคำค้นหา")
            
        # ระบบแก้ไข/ลบ ธุรกรรมการเงิน (เฉพาะแอดมิน/เหรัญญิก)
        if is_authorized and not display_trans_df.empty:
            st.markdown("### 🛠️ การจัดการธุรกรรม (สิทธิ์ผู้ดูแล)")
            select_trans_id = st.selectbox("เลือกรหัสธุรกรรมที่ต้องการจัดการ (ดู ID จากแถวซ้ายสุดในตาราง):", display_trans_df["id"].tolist())
            
            col_edit, col_del = st.columns(2)
            with col_edit:
                with st.expander("✏️ แก้ไขธุรกรรม"):
                    new_trans_detail = st.text_input("แก้ไขรายละเอียดรายการ")
                    new_trans_amount = st.number_input("แก้ไขจำนวนเงิน (บาท)", value=0.0)
                    if st.button("บันทึกการแก้ไขธุรกรรม"):
                        for t in st.session_state.transactions:
                            if t["id"] == select_trans_id:
                                if new_trans_detail: t["detail"] = new_trans_detail
                                if new_trans_amount != 0.0: t["amount"] = new_trans_amount
                                st.success("แก้ไขประวัติการเงินเรียบร้อย!")
                                st.rerun()
            with col_del:
                if st.button("🗑️ ลบธุรกรรมนี้เด็ดขาด", type="primary"):
                    st.session_state.transactions = [t for t in st.session_state.transactions if t["id"] != select_trans_id]
                    st.success("ลบรายการประวัติการเงินเรียบร้อย!")
                    st.rerun()

        # เพิ่มบันทึกรายจ่ายห้องเรียน
        if is_authorized:
            st.markdown("---")
            st.subheader("🛑 บันทึกรายจ่ายส่วนกลางของห้อง")
            exp_detail = st.text_input("รายละเอียดรายจ่าย (เช่น ค่าชีทเรียนห้อง, ค่าน้ำดื่มกิจกรรม)")
            exp_amount = st.number_input("จำนวนเงินที่จ่ายออก (บาท)", min_value=0.0, step=10.0)
            if st.button("บันทึกรายจ่ายห้อง"):
                if exp_detail and exp_amount > 0:
                    new_id = max([t["id"] for t in st.session_state.transactions]) + 1 if st.session_state.transactions else 1
                    st.session_state.transactions.append({
                        "id": new_id, "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "type": "รายจ่าย", "student_id": "-", "detail": exp_detail,
                        "amount": -exp_amount, "class": selected_global_class
                    })
                    st.success("บันทึกรายจ่ายห้องเรียบร้อย!")
                    st.rerun()

    # ==========================================
    # แท็บที่ 2: รายชื่อนักศึกษาและการส่งเงิน (แยกรายห้องเด็ดขาด)
    # ==========================================
    with tab2:
        st.header(f"👥 รายชื่อนักศึกษาห้อง {selected_global_class}")
        
        # กรองแสดงผลนักศึกษาเฉพาะห้องที่เลือก
        df_stu = pd.DataFrame(st.session_state.students)
        df_stu_filtered = df_stu[df_stu["class"] == selected_global_class] if not df_stu.empty else pd.DataFrame()
        
        if not df_stu_filtered.empty:
            st.dataframe(df_stu_filtered[["id", "name", "status"]], use_container_width=True)
        else:
            st.info(f"ห้อง {selected_global_class} ยังไม่มีรายชื่อนักศึกษาในระบบ")
            
        # ส่วนแก้ไขและลบรายชื่อนักศึกษา (เฉพาะแอดมิน/เหรัญญิก)
        if is_authorized and not df_stu_filtered.empty:
            st.markdown("---")
            st.subheader("🛠️ การจัดการข้อมูลนักศึกษา (สิทธิ์ผู้ดูแล)")
            select_stu_id = st.selectbox("เลือก รหัสนักศึกษา ที่ต้องการจัดการ:", df_stu_filtered["id"].tolist())
            
            col_stu_edit, col_stu_del = st.columns(2)
            with col_stu_edit:
                with st.expander("✏️ แก้ไขข้อมูลนักศึกษา"):
                    edit_name = st.text_input("แก้ไข ชื่อ-นามสกุล")
                    edit_status = st.selectbox("แก้ไขสถานะการจ่ายเงิน", ["❌ ยังไม่จ่าย", "✅ จ่ายแล้ว"])
                    if st.button("บันทึกการแก้ไขข้อมูลนักศึกษา"):
                        for s in st.session_state.students:
                            if s["id"] == select_stu_id:
                                if edit_name: s["name"] = edit_name
                                s["status"] = edit_status
                                st.success("อัปเดตข้อมูลนักศึกษาเรียบร้อยแล้ว!")
                                st.rerun()
            with col_stu_del:
                if st.button("🗑️ ลบรายชื่อนักศึกษานี้", type="primary"):
                    st.session_state.students = [s for s in st.session_state.students if s["id"] != select_stu_id]
                    st.success("ลบข้อมูลนักศึกษาเรียบร้อย!")
                    st.rerun()

        # ส่วนบันทึกการรับเงินกองกลาง
        if is_authorized and not df_stu_filtered.empty:
            st.markdown("---")
            st.subheader("🛑 บันทึกการรับเงินกองกลางประจำเดือน")
            unpaid_list = df_stu_filtered[df_stu_filtered["status"] == "❌ ยังไม่จ่าย"]
            
            if not unpaid_list.empty():
                target_stu_name = st.selectbox("เลือกชื่อเพื่อนที่นำเงินมาจ่าย:", unpaid_list["name"].tolist())
                income_amount = st.number_input("จำนวนเงินที่เก็บ (บาท)", value=500.0, step=50.0)
                
                if st.button("ยืนยันการรับเงิน"):
                    target_id = ""
                    for s in st.session_state.students:
                        if s["name"] == target_stu_name and s["class"] == selected_global_class:
                            s["status"] = "✅ จ่ายแล้ว"
                            target_id = s["id"]
                    
                    new_id = max([t["id"] for t in st.session_state.transactions]) + 1 if st.session_state.transactions else 1
                    st.session_state.transactions.append({
                        "id": new_id, "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "type": "รายรับ", "student_id": target_id, "detail": f"{target_stu_name} (เงินกองกลาง)",
                        "amount": income_amount, "class": selected_global_class
                    })
                    st.success(f"บันทึกยอดเงินของ {target_stu_name} เรียบร้อย!")
                    st.rerun()
            else:
                st.success("🎉 ทุกคนในห้องนี้ชำระเงินกองกลางครบทั้งหมดแล้ว!")

    # ==========================================
    # แท็บที่ 3: ตั้งค่าระบบ (สร้างห้องก่อน แล้วดึงไปเป็น Dropdown ในการเพิ่มรายชื่อ)
    # ==========================================
    with tab3:
        if is_authorized:
            st.header("⚙️ การจัดการโครงสร้างข้อมูลระบบ")
            col_setup1, col_setup2 = st.columns(2)
            
            # 1. ฟอร์มสร้างห้องเรียน
            with col_setup1:
                st.subheader("🏫 เพิ่ม/ลบ ห้องเรียน")
                new_room = st.text_input("ระบุชื่อห้องเรียนใหม่ (เช่น IT-C)")
                if st.button("เพิ่มห้องเรียน"):
                    if new_room:
                        if new_room in st.session_state.classes:
                            st.error("ห้องเรียนนี้มีอยู่แล้วในระบบ")
                        else:
                            st.session_state.classes.append(new_room)
                            st.success(f"สร้างห้องเรียน {new_room} สำเร็จ!")
                            st.rerun()
                    else:
                        st.error("กรุณากรอกชื่อห้องเรียน")
                        
                st.markdown("---")
                if st.session_state.classes:
                    del_room = st.selectbox("เลือกห้องเรียนที่ต้องการลบ:", st.session_state.classes)
                    if st.button("ลบห้องเรียนนี้เด็ดขาด", type="primary"):
                        st.session_state.classes.remove(del_room)
                        # ลบนักศึกษาที่อยู่ในห้องนั้นออกด้วยเพื่อไม่ให้ข้อมูลค้าง
                        st.session_state.students = [s for s in st.session_state.students if s["class"] != del_room]
                        st.success(f"ลบห้อง {del_room} เรียบร้อย!")
                        st.rerun()

            # 2. ฟอร์มเพิ่มนักศึกษา (ดึงห้องเรียนมาเป็น Dropdown บังคับเลือก)
            with col_setup2:
                st.subheader("👤 เพิ่มนักศึกษาใหม่เข้าระบบ")
                stu_id_input = st.text_input("รหัสนักศึกษา")
                stu_name_input = st.text_input("ชื่อ - นามสกุล")
                
                # Dropdown เลือกห้องเรียนที่สร้างไว้แล้วเท่านั้น
                stu_class_select = st.selectbox("เลือกห้องเรียนของนักศึกษา (Dropdown):", st.session_state.classes, key="add_stu_box")
                
                if st.button("ยืนยันเพิ่มรายชื่อนักศึกษา"):
                    if stu_id_input and stu_name_input and stu_class_select:
                        # เช็ครหัสซ้ำ
                        if any(s["id"] == stu_id_input for s in st.session_state.students):
                            st.error("รหัสนักศึกษานี้มีอยู่ในระบบแล้ว")
                        else:
                            st.session_state.students.append({
                                "id": stu_id_input,
                                "name": stu_name_input,
                                "class": stu_class_select,
                                "status": "❌ ยังไม่จ่าย"
                            })
                            st.success(f"เพิ่มคุณ {stu_name_input} เข้าสู่ห้อง {stu_class_select} สำเร็จ!")
                            st.rerun()
                    else:
                        st.error("กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
        else:
            st.warning("🔒 สิทธิ์ของคุณคือ นักศึกษาทั่วไป ไม่สามารถเข้าถึงหน้านี้ได้")
