import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บให้เป็นแบบเต็มจอ และใช้ธีมที่สบายตา
st.set_page_config(page_title="ระบบคลังเงินห้องเรียน Pro", page_icon="💰", layout="wide")

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
    ]

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
# 🔐 หน้าต่างล็อกอิน (Sidebar ด้านซ้าย)
# ==========================================
with st.sidebar:
    st.markdown("### 🔐 ศูนย์บัญชาการผู้ดูแล")
    if st.session_state.logged_in_user is None:
        st.info("💡 สมาชิกทั่วไปเปิดดูข้อมูลได้ทันที หากต้องการ แก้ไข/ลบ/บันทึกเงิน กรุณาเข้าสู่ระบบ")
        username_input = st.text_input("ชื่อผู้ใช้งาน (Username)", placeholder="กรอกสิทธิ์ผู้ดูแล")
        password_input = st.text_input("รหัสผ่าน (Password)", type="password", placeholder="••••••••")
        
        if st.button("🚪 เข้าสู่ระบบ", use_container_width=True):
            if username_input in st.session_state.users:
                if st.session_state.users[username_input]["password"] == password_input:
                    st.session_state.logged_in_user = username_input
                    st.toast(f"🎉 ยินดีต้อนรับคุณ {st.session_state.users[username_input]['name']}", icon="🔓")
                    st.rerun()
                else:
                    st.error("รหัสผ่านไม่ถูกต้อง")
            else:
                st.error("ไม่พบชื่อผู้ใช้งานนี้")
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
            
        st.markdown("---")
        
        # ฟีเจอร์สร้างบัญชีผู้ดูแลเพิ่ม
        if is_authorized:
            st.markdown("### ➕ สร้างบัญชีผู้ดูแลเพิ่ม")
            with st.expander("เปิดฟอร์มสร้างบัญชี"):
                new_admin_user = st.text_input("ตั้ง Username ใหม่")
                new_admin_name = st.text_input("ชื่อ-นามสกุล ผู้ดูแล")
                new_admin_pass = st.text_input("ตั้ง Password", type="password")
                new_admin_role = st.selectbox("เลือกตำแหน่ง", ["เหรัญญิก", "ผู้ควบคุมใหญ่สุด"])
                
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("ยืนยันสร้างบัญชี", use_container_width=True):
                        if new_admin_user and new_admin_name and new_admin_pass:
                            if new_admin_user in st.session_state.users:
                                st.error("Username นี้มีในระบบแล้ว")
                            else:
                                st.session_state.users[new_admin_user] = {
                                    "password": new_admin_pass, "name": new_admin_name, "role": new_admin_role
                                }
                                st.toast(f"สร้างบัญชี {new_admin_user} สำเร็จ!", icon="✅")
                                st.rerun()
                        else:
                            st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
                with c_btn2:
                    if st.button("↩️ ย้อนกลับ", key="cancel_add_admin", use_container_width=True):
                        st.rerun()

# ==========================================
# 🎨 หน้าจอหลักของ Web App
# ==========================================
st.title("📊 ระบบคลังเงินกองกลาง & จัดการห้องเรียน")
st.markdown("---")

# ดึงชื่อห้องเรียนมาแสดงใน Dropdown เสมอ
if st.session_state.classes:
    selected_global_class = st.selectbox("🎯 กรุณาเลือกห้องเรียนที่คุณต้องการตรวจสอบข้อมูล:", st.session_state.classes)
else:
    selected_global_class = None

# สร้างแท็บถาวร 3 แท็บ เพื่อไม่ให้หน้าจอว่างเปล่าเมื่อไม่มีห้องเรียน
tab1, tab2, tab3 = st.tabs(["💵 ข้อมูลการเงินประจำห้อง", "👥 สมาชิกนักศึกษา", "⚙️ ตัวควบคุมระบบ"])

# ==========================================
# แท็บที่ 1: ข้อมูลการเงินประจำห้อง
# ==========================================
with tab1:
    if selected_global_class:
        st.header(f"💰 ภาพรวมเงินกองกลางห้อง {selected_global_class}")
        df_trans = pd.DataFrame(st.session_state.transactions)
        df_trans_filtered = df_trans[df_trans["class"] == selected_global_class] if not df_trans.empty else pd.DataFrame()
        
        total_income = df_trans_filtered[df_trans_filtered["type"] == "รายรับ"]["amount"].sum() if not df_trans_filtered.empty else 0.0
        total_expense = df_trans_filtered[df_trans_filtered["type"] == "รายจ่าย"]["amount"].sum() if not df_trans_filtered.empty else 0.0
        room_balance = total_income + total_expense
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="💰 เงินคงเหลือสุทธิ (Net Balance)", value=f"{room_balance:,.2f} บาท")
        with m2:
            st.metric(label="📈 รายรับรวมทั้งหมด", value=f"{total_income:,.2f} บาท")
        with m3:
            st.metric(label="📉 รายจ่ายรวมทั้งหมด", value=f"{abs(total_expense):,.2f} บาท")
            
        st.markdown("---")
        st.subheader("🔍 ค้นหาและตรวจสอบรายการเงิน")
        search_query = st.text_input("ใส่รหัสนักศึกษา หรือ ชื่อ เพื่อค้นหา:", placeholder="พิมพ์เพื่อค้นหาประวัติ...")
        
        display_trans_df = df_trans_filtered.copy()
        if search_query and not display_trans_df.empty:
            display_trans_df = display_trans_df[
                display_trans_df["detail"].str.contains(search_query, case=False, na=False) | 
                display_trans_df["student_id"].str.contains(search_query, case=False, na=False)
            ]
            
        if not display_trans_df.empty:
            st.dataframe(display_trans_df[["time", "type", "student_id", "detail", "amount"]], use_container_width=True)
        else:
            st.info("ไม่พบข้อมูลประวัติการเดินบัญชีในเงื่อนไขนี้")
            
        if is_authorized:
            st.markdown("---")
            st.subheader("🛠️ ส่วนควบคุมของเหรัญญิก (จัดการรายการเงิน)")
            col_action1, col_action2 = st.columns(2)
            
            with col_action1:
                st.markdown("##### 💸 บันทึกรายจ่ายของห้อง")
                exp_detail = st.text_input("รายละเอียดรายจ่าย", placeholder="เช่น ค่าชีทบทเรียน, ค่าน้ำดื่มกิจกรรม")
                exp_amount = st.number_input("จำนวนเงินที่จ่ายออก", min_value=0.0, step=10.0)
                
                btn_exp1, btn_exp2 = st.columns(2)
                with btn_exp1:
                    if st.button("➕ บันทึกรายจ่าย", use_container_width=True):
                        if exp_detail and exp_amount > 0:
                            new_id = max([t["id"] for t in st.session_state.transactions]) + 1 if st.session_state.transactions else 1
                            st.session_state.transactions.append({
                                "id": new_id, "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "type": "รายจ่าย", "student_id": "-", "detail": exp_detail,
                                "amount": -exp_amount, "class": selected_global_class
                            })
                            st.toast("บันทึกรายจ่ายเรียบร้อย!", icon="💸")
                            st.rerun()
                with btn_exp2:
                    if st.button("↩️ ย้อนกลับ/ล้างฟอร์ม", key="clear_exp", use_container_width=True):
                        st.rerun()
            
            with col_action2:
                if not display_trans_df.empty:
                    st.markdown("##### ⚙️ แก้ไขหรือลบธุรกรรมการเงิน")
                    select_trans_id = st.selectbox("เลือกรหัส ID ธุรกรรมที่จะจัดการ:", display_trans_df["id"].tolist())
                    
                    sub_c1, sub_c2 = st.columns(2)
                    with sub_c1:
                        with st.expander("✏️ แก้ไขข้อมูล"):
                            new_trans_detail = st.text_input("ชื่อรายการใหม่")
                            new_trans_amount = st.number_input("จำนวนเงินใหม่", value=0.0)
                            
                            b_edit1, b_edit2 = st.columns(2)
                            with b_edit1:
                                if st.button("💾 บันทึกแก้ไข", use_container_width=True):
                                    for t in st.session_state.transactions:
                                        if t["id"] == select_trans_id:
                                            if new_trans_detail: t["detail"] = new_trans_detail
                                            if new_trans_amount != 0.0: t["amount"] = new_trans_amount
                                            st.toast("แก้ไขข้อมูลสำเร็จ", icon="📝")
                                            st.rerun()
                            with b_edit2:
                                if st.button("↩️ ย้อนกลับ", key="cancel_trans_edit", use_container_width=True):
                                    st.rerun()
                    with sub_c2:
                        if st.button("🗑️ ลบรายการนี้", type="primary", use_container_width=True):
                            st.session_state.transactions = [t for t in st.session_state.transactions if t["id"] != select_trans_id]
                            st.toast("ลบข้อมูลสำเร็จ", icon="🗑️")
                            st.rerun()
    else:
        st.warning("⚠️ กรุณาไปที่แท็บ '⚙️ ตัวควบคุมระบบ' เพื่อสร้างห้องเรียนเริ่มต้นระบบก่อนครับ")

# ==========================================
# แท็บที่ 2: รายชื่อนักศึกษา
# ==========================================
with tab2:
    if selected_global_class:
        st.header(f"👥 สมาชิกนักศึกษาห้อง {selected_global_class}")
        df_stu = pd.DataFrame(st.session_state.students)
        df_stu_filtered = df_stu[df_stu["class"] == selected_global_class] if not df_stu.empty else pd.DataFrame()
        
        col_view, col_manage = st.columns([3, 2])
        with col_view:
            st.markdown("##### 📋 ตารางรายชื่อนักศึกษาปัจจุบัน")
            if not df_stu_filtered.empty:
                st.dataframe(df_stu_filtered[["id", "name", "status"]], use_container_width=True, height=400)
            else:
                st.info(f"ห้อง {selected_global_class} ยังไม่มีรายชื่อเพื่อน")
                
        with col_manage:
            if is_authorized and not df_stu_filtered.empty:
                st.markdown("##### 🛑 1. เช็กสถานะรับเงินกองกลาง")
                unpaid_list = df_stu_filtered[df_stu_filtered["status"] == "❌ ยังไม่จ่าย"]
                
                if not unpaid_list.empty:
                    target_stu_name = st.selectbox("เลือกรายชื่อคนที่นำเงินมาจ่าย:", unpaid_list["name"].tolist())
                    income_amount = st.number_input("ยอดเงินกองกลางที่เก็บ (บาท)", value=500.0, step=50.0)
                    
                    btn_inc1, btn_inc2 = st.columns(2)
                    with btn_inc1:
                        if st.button("✅ ยืนยันการรับเงิน", use_container_width=True):
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
                            st.toast(f"บันทึกยอดเงินกองกลางของคุณ {target_stu_name} เรียบร้อย!", icon="💰")
                            st.rerun()
                    with btn_inc2:
                        if st.button("↩️ ย้อนกลับ/ล้างค่า", key="clear_inc", use_container_width=True):
                            st.rerun()
                else:
                    st.success("🎉 ทุกคนในห้องนี้ชำระเงินครบหมดแล้ว!")
                    
                st.markdown("---")
                st.markdown("##### ⚙️ 2. จัดการ/แก้ไข/ลบ รายชื่อนักศึกษา")
                select_stu_id = st.selectbox("เลือกรหัสนักศึกษาที่จะแก้ไข/ลบ:", df_stu_filtered["id"].tolist())
                
                sc1, sc2 = st.columns(2)
                with sc1:
                    with st.expander("✏️ แก้ไขประวัติ"):
                        edit_name = st.text_input("ชื่อ-นามสกุลใหม่")
                        edit_status = st.selectbox("สถานะเงิน", ["❌ ยังไม่จ่าย", "✅ จ่ายแล้ว"])
                        
                        b_stu1, b_stu2 = st.columns(2)
                        with b_stu1:
                            if st.button("💾 บันทึกนักศึกษา", use_container_width=True):
                                for s in st.session_state.students:
                                    if s["id"] == select_stu_id:
                                        if edit_name: s["name"] = edit_name
                                        s["status"] = edit_status
                                        st.toast("แก้ไขข้อมูลสำเร็จ", icon="👤")
                                        st.rerun()
                        with b_stu2:
                            if st.button("↩️ ย้อนกลับ", key="cancel_stu_edit", use_container_width=True):
                                st.rerun()
                with sc2:
                    if st.button("🗑️ ลบรายชื่อนี้", type="primary", use_container_width=True):
                        st.session_state.students = [s for s in st.session_state.students if s["id"] != select_stu_id]
                        st.toast("ลบรายชื่อเรียบร้อย", icon="🗑️")
                        st.rerun()
    else:
        st.warning("⚠️ กรุณาไปที่แท็บ '⚙️ ตัวควบคุมระบบ' เพื่อสร้างห้องเรียนเริ่มต้นระบบก่อนครับ")

# ==========================================
# แท็บที่ 3: ตั้งค่าระบบ (แก้ไขสิทธิ์เปิดให้แอดมินมองเห็นฟอร์มถาวรแล้ว)
# ==========================================
with tab3:
    if is_authorized:
        st.header("⚙️ แผงควบคุมโครงสร้างข้อมูลระบบ")
        col_setup1, col_setup2 = st.columns(2)
        
        with col_setup1:
            st.markdown("### 🏫 จัดการห้องเรียน")
            new_room = st.text_input("ระบุชื่อห้องเรียนใหม่ (เช่น IT-C)", placeholder="ระบุชื่อห้อง...")
            if st.button("➕ เพิ่มห้องเรียนใหม่", use_container_width=True):
                if new_room:
                    if new_room in st.session_state.classes:
                        st.error("ห้องเรียนนี้มีอยู่แล้วในระบบ")
                    else:
                        st.session_state.classes.append(new_room)
                        st.toast(f"สร้างห้องเรียน {new_room} สำเร็จ!", icon="🏫")
                        st.rerun()
                else:
                    st.error("กรุณากรอกชื่อห้องเรียน")
                        
            st.markdown("---")
            if st.session_state.classes:
                del_room = st.selectbox("เลือกห้องเรียนที่ต้องการลบออกจากระบบ:", st.session_state.classes)
                if st.button("🗑️ ลบห้องเรียนนี้เด็ดขาด", type="primary", use_container_width=True):
                    st.session_state.classes.remove(del_room)
                    st.session_state.students = [s for s in st.session_state.students if s["class"] != del_room]
                    st.toast(f"ลบห้อง {del_room} ออกจากระบบแล้ว", icon="🗑️")
                    st.rerun()

        with col_setup2:
            st.markdown("### 👤 เพิ่มรายชื่อนักศึกษาใหม่")
            stu_id_input = st.text_input("กรอกรหัสนักศึกษา")
            stu_name_input = st.text_input("กรอกชื่อ - นามสกุล")
            
            if st.session_state.classes:
                stu_class_select = st.selectbox("เลือกห้องเรียนของนักศึกษา:", st.session_state.classes, key="add_stu_box")
                
                b_add1, b_add2 = st.columns(2)
                with b_add1:
                    if st.button("👤 ยืนยันเพิ่มรายชื่อ", use_container_width=True):
                        if stu_id_input and stu_name_input and stu_class_select:
                            if any(s["id"] == stu_id_input for s in st.session_state.students):
                                st.error("รหัสนักศึกษานี้มีอยู่ในระบบแล้ว")
                            else:
                                st.session_state.students.append({
                                    "id": stu_id_input, "name": stu_name_input,
                                    "class": stu_class_select, "status": "❌ ยังไม่จ่าย"
                                })
                                st.toast(f"เพิ่มคุณ {stu_name_input} เรียบร้อย!", icon="👤")
                                st.rerun()
                        else:
                            st.error("กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
                with b_add2:
                    if st.button("↩️ ล้างฟอร์ม", key="clear_add_stu", use_container_width=True):
                        st.rerun()
            else:
                st.info("ℹ️ กรุณาสร้างห้องเรียนฝั่งซ้ายมือก่อน จึงจะเพิ่มรายชื่อเพื่อนเข้าห้องได้ครับ")
    else:
        st.warning("🔒 เฉพาะเหรัญญิกหรือผู้ควบคุมระบบเท่านั้นที่สามารถเข้าถึงแผงตั้งค่านี้ได้")
