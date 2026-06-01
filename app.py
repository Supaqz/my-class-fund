import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าเว็บหลัก
st.set_page_config(page_title="ระบบออมเงิน FN A&B 68 Auto", page_icon="💰", layout="wide")

# ลิงก์ Google Sheet ของคุณ
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1BpxPfO-hTJNhd9wCBi1_GFEUulp2PQ-QkxCwSUYA3P8/edit?gid=0#gid=0"

# ==========================================
# 🔌 เชื่อมต่อ Google Sheets ตรงผ่าน Connector
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("🔌 ยังไม่ได้ตั้งค่า Secrets บน Streamlit Cloud กรุณาตรวจสอบช่อง Secrets ด้านหลังระบบ")

# ฟังก์ชันอัจฉริยะ: ตรวจสอบและสร้างหน้าแท็บให้เองอัตโนมัติหากไม่มีในคลาวด์
def get_or_create_worksheet(worksheet_name, default_headers):
    try:
        # ทดลองอ่านข้อมูลดูว่ามีแท็บนี้อยู่แล้วไหม
        df = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet=worksheet_name)
        # ถ้ามีแท็บแต่ดันเป็นชีทโล่ง ๆ ไม่มีหัวตาราง ให้ใส่หัวตารางให้
        if df.empty or len(df.columns) == 0:
            df_empty = pd.DataFrame(columns=default_headers)
            conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet=worksheet_name, data=df_empty)
            return df_empty
        return df
    except Exception:
        # 🚨 ถ้าไม่เจอหน้าแท็บนี้ ระบบจะทำการสร้างแท็บใหม่และพิมพ์หัวข้อคอลัมน์ให้ทันที!
        st.toast(f"🛠️ ระบบกำลังสร้างหน้าแท็บ '{worksheet_name}' ให้ใน Google Sheet...", icon="⚙️")
        df_new = pd.DataFrame(columns=default_headers)
        conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet=worksheet_name, data=df_new)
        return df_new

# ฟังก์ชันบันทึกข้อมูลกลับลงคลาวด์ชีท
def save_data(df, worksheet_name):
    conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet=worksheet_name, data=df)
    st.toast(f"💾 บันทึกและซิงค์ข้อมูลลงแท็บ {worksheet_name} เรียบร้อยแล้ว!", icon="✅")

# กำหนดหัวข้อคอลัมน์มาตรฐานของระบบ
headers_stu = ["รหัสนักศึกษา", "ชื่อ-นามสกุล", "ชั้นเรียน"]
headers_dep = ["ID", "วันที่ฝาก", "รหัสนักศึกษา", "ชื่อ-นามสกุล", "จำนวนเงินที่ฝาก", "หมายเหตุ"]
headers_wd  = ["ID", "วันที่ถอน", "รหัสนักศึกษา", "ชื่อ-นามสกุล", "จำนวนเงินที่ถอน", "หมายเหตุ"]

# โหลดข้อมูลจริงจากคลาวด์ (ถ้าไม่มี ระบบจะสร้างชีทใหม่ให้เองตรงนี้เลย)
df_cloud_stu = get_or_create_worksheet("Students", headers_stu)
df_cloud_dep = get_or_create_worksheet("Deposits", headers_dep)
df_cloud_wd  = get_or_create_worksheet("Withdrawals", headers_wd)

# ย้ายข้อมูลเข้าสู่หน่วยความจำหน้าเว็บเพื่อประมวลผลด่วน
if "students" not in st.session_state:
    st.session_state.students = df_cloud_stu.to_dict(orient="records")

if "deposits" not in st.session_state:
    st.session_state.deposits = df_cloud_dep.to_dict(orient="records")

if "withdrawals" not in st.session_state:
    st.session_state.withdrawals = df_cloud_wd.to_dict(orient="records")

# ==========================================
# 🎨 ส่วนจัดหน้าจอแอปพลิเคชัน
# ==========================================
st.title("💰 ระบบคลังเงินออม (Auto-Create Sheets) - FN A&B 68")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["💵 ฝากเงิน", "💸 ถอนเงิน", "📊 สรุปภาพรวม", "👤 ฟอร์มกรอกข้อมูลนักศึกษา"])
student_list = [f"{s['รหัสนักศึกษา']} - {s['ชื่อ-นามสกุล']}" for s in st.session_state.students]

# --- หน้าต่างที่ 1: ฝากเงิน ---
with tab1:
    st.header("📋 แบบฟอร์มบันทึกเงินฝากนักศึกษา")
    if not student_list:
        st.warning("⚠️ โปรดไปที่หน้าต่างที่ 4 เพื่อเพิ่มรายชื่อนักศึกษาก่อน")
    else:
        with st.form("deposit_form"):
            dep_date = st.date_input("วันที่ฝากเงิน", datetime.now())
            dep_amount = st.number_input("จำนวนเงินที่ฝาก", min_value=0.0, step=50.0)
            dep_user = st.selectbox("ผู้ฝากเงิน", student_list)
            dep_note = st.text_input("หมายเหตุเพิ่มเติม (ถ้ามี)")
            
            if st.form_submit_button("💾 บันทึกข้อมูลการฝากเงินใน Google Sheet", use_container_width=True):
                if dep_amount > 0:
                    stu_id, stu_name = dep_user.split(" - ")[0], dep_user.split(" - ")[1]
                    st.session_state.deposits.append({
                        "ID": len(st.session_state.deposits) + 1, "วันที่ฝาก": dep_date.strftime("%Y-%m-%d"),
                        "รหัสนักศึกษา": stu_id, "ชื่อ-นามสกุล": stu_name, "จำนวนเงินที่ฝาก": dep_amount, "หมายเหตุ": dep_note
                    })
                    save_data(pd.DataFrame(st.session_state.deposits), "Deposits")
                    st.success("บันทึกข้อมูลการฝากเงินใน Google Sheet เรียบร้อย")
                else: st.error("กรุณากรอกจำนวนเงิน")

    st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_URL, use_container_width=True)

# --- หน้าต่างที่ 2: ถอนเงิน ---
with tab2:
    st.header("📋 แบบฟอร์มบันทึกการถอนเงินนักศึกษา")
    if not student_list:
        st.warning("⚠️ โปรดไปที่หน้าต่างที่ 4 เพื่อเพิ่มรายชื่อนักศึกษาก่อน")
    else:
        with st.form("withdraw_form"):
            wd_date = st.date_input("วันที่ถอนเงิน", datetime.now())
            wd_amount = st.number_input("จำนวนเงินที่ถอน", min_value=0.0, step=50.0)
            wd_user = st.selectbox("ผู้ถอนเงิน", student_list)
            wd_note = st.text_input("หมายเหตุเพิ่มเติม (ถ้ามี)")
            
            if st.form_submit_button("💸 บันทึกข้อมูลการถอนเงินใน Google Sheet", use_container_width=True):
                if wd_amount > 0:
                    stu_id, stu_name = wd_user.split(" - ")[0], wd_user.split(" - ")[1]
                    st.session_state.withdrawals.append({
                        "ID": len(st.session_state.withdrawals) + 1, "วันที่ถอน": wd_date.strftime("%Y-%m-%d"),
                        "รหัสนักศึกษา": stu_id, "ชื่อ-นามสกุล": stu_name, "จำนวนเงินที่ถอน": wd_amount, "หมายเหตุ": wd_note
                    })
                    save_data(pd.DataFrame(st.session_state.withdrawals), "Withdrawals")
                    st.success("บันทึกข้อมูลการฝากเงินใน Google Sheet เรียบร้อย")
                else: st.error("กรุณากรอกจำนวนเงิน")

    st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_URL, use_container_width=True)

# --- หน้าต่างที่ 3: สรุปภาพรวม ---
with tab3:
    st.header("📊 สรุปภาพรวมระบบบัญชีคลังห้อง")
    df_dep = pd.DataFrame(st.session_state.deposits)
    df_wd = pd.DataFrame(st.session_state.withdrawals)
    
    total_room_dep = df_dep["จำนวนเงินที่ฝาก"].sum() if not df_dep.empty else 0.0
    total_room_wd = df_wd["จำนวนเงินที่ถอน"].sum() if not df_wd.empty else 0.0
    room_balance = total_room_dep - total_room_wd
    
    st.subheader("🏫 1. สรุปยอดรวมของทั้งห้อง")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric(label="ยอดรวมเงินฝากทั้งห้อง", value=f"{total_room_dep:,.2f} บาท")
    mc2.metric(label="ยอดรวมการถอนทั้งห้อง", value=f"{total_room_wd:,.2f} บาท")
    mc3.metric(label="ยอดเงินคงเหลือของทั้งห้อง", value=f"{room_balance:,.2f} บาท")
    
    st.markdown("---")
    st.subheader("👤 2. ยอดคงเหลือของนักศึกษาแต่ละคน")
    if not st.session_state.students:
        st.info("ยังไม่มีข้อมูลนักศึกษาในระบบ")
    else:
        summary_records = []
        for student in st.session_state.students:
            s_id = student["รหัสนักศึกษา"]
            s_dep = df_dep[df_dep["รหัสนักศึกษา"] == s_id]["จำนวนเงินที่ฝาก"].sum() if not df_dep.empty else 0.0
            s_wd = df_wd[df_wd["รหัสนักศึกษา"] == s_id]["จำนวนเงินที่ถอน"].sum() if not df_wd.empty else 0.0
            s_bal = s_dep - s_wd
            summary_records.append({
                "รหัสนักศึกษา": s_id, "ชื่อ - นามสกุล": student["ชื่อ-นามสกุล"], "ชั้นเรียน": student["ชั้นเรียน"],
                "ยอดรวมเงินฝาก (บาท)": f"{s_dep:,.2f}", "ยอดรวมการถอน (บาท)": f"{s_wd:,.2f}", "ยอดเงินคงเหลือคงคลัง (บาท)": f"{s_bal:,.2f}"
            })
        st.dataframe(pd.DataFrame(summary_records), use_container_width=True)

# --- หน้าต่างที่ 4: ฟอร์มกรอกข้อมูลนักศึกษา ---
with tab4:
    st.header("👤 บันทึกข้อมูลนักศึกษา")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1: s_id_input = st.text_input("รหัสประจำตัวนักศึกษา")
    with col_f2: s_name_input = st.text_input("ชื่อ–นามสกุล")
    with col_f3: s_class_input = st.selectbox("ชั้นเรียน", ["FN A 68", "FN B 68"])
        
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1:
        if st.button("➕ ปุ่มเพิ่มข้อมูลนักศึกษา", use_container_width=True):
            if s_id_input and s_name_input:
                if any(s["รหัสนักศึกษา"] == s_id_input for s in st.session_state.students):
                    st.error("รหัสนักศึกษานี้มีอยู่ในระบบแล้ว")
                else:
                    st.session_state.students.append({"รหัสนักศึกษา": s_id_input, "ชื่อ-นามสกุล": s_name_input, "ชั้นเรียน": s_class_input})
                    st.success("เพิ่มข้อมูลเรียบร้อยแล้ว")
            else: st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
    with c_btn2:
        if st.button("✏️ ปุ่มแก้ไขข้อมูล", use_container_width=True):
            for s in st.session_state.students:
                if s["รหัสนักศึกษา"] == s_id_input:
                    if s_name_input: s["ชื่อ-นามสกุล"] = s_name_input
                    s["ชั้นเรียน"] = s_class_input
            st.success("แก้ไขข้อมูลสำเร็จ")
    with c_btn3:
        if st.button("🗑️ ปุ่มลบข้อมูลนักศึกษา", type="primary", use_container_width=True):
            st.session_state.students = [s for s in st.session_state.students if s["รหัสนักศึกษา"] != s_id_input]
            st.success("ลบข้อมูลสำเร็จ")
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🌐 บันทึกข้อมูลนักศึกษาใน Google Sheet", use_container_width=True):
        save_data(pd.DataFrame(st.session_state.students), "Students")
        st.success("บันทึกข้อมูลนักศึกษาใน Google Sheet เรียบร้อย")
        st.rerun()
