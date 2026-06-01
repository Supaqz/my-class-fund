import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าจอแอปพลิเคชันหลัก
st.set_page_config(page_title="ระบบออมเงิน FN A&B 68", page_icon="💰", layout="wide")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1BpxPfO-hTJNhd9wCBi1_GFEUulp2PQ-QkxCwSUYA3P8/edit?gid=0#gid=0"

# 🔌 เชื่อมต่อเข้า Google Sheets โดยตรง
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("🔌 ตรวจพบข้อผิดพลาดในการเชื่อมต่อคีย์ กรุณาเช็กกล่อง Secrets ของ Streamlit Cloud ครับ")

# ฟังก์ชันอ่านข้อมูลจากคลาวด์ชีทแบบปลอดภัย
def safe_read_sheet(worksheet_name, default_cols):
    try:
        df = conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet=worksheet_name, ttl="0m")
        if df.empty or len(df.columns) == 0:
            return pd.DataFrame(columns=default_cols)
        return df
    except Exception:
        return pd.DataFrame(columns=default_cols)

# กำหนดหัวตารางมาตรฐานตามที่โจทย์ระบุ
cols_stu = ["รหัสนักศึกษา", "ชื่อ-นามสกุล", "ชั้นเรียน"]
cols_dep = ["วันที่ฝาก", "จำนวนเงินที่ฝาก", "ผู้ฝากเงิน", "หมายเหตุเพิ่มเติม"]
cols_wd  = ["วันที่ถอน", "จำนวนเงินที่ถอน", "ผู้ถอนเงิน", "หมายเหตุเพิ่มเติม"]

# โดนดึงข้อมูลจริงจากคลาวด์มาสแตนด์บายในแอป
df_cloud_stu = safe_read_sheet("Students", cols_stu)
df_cloud_dep = safe_read_sheet("Deposits", cols_dep)
df_cloud_wd  = safe_read_sheet("Withdrawals", cols_wd)

if "students" not in st.session_state:
    st.session_state.students = df_cloud_stu.to_dict(orient="records")
if "deposits" not in st.session_state:
    st.session_state.deposits = df_cloud_dep.to_dict(orient="records")
if "withdrawals" not in st.session_state:
    st.session_state.withdrawals = df_cloud_wd.to_dict(orient="records")

# ==========================================
# 🎨 การจัดแสดงหน้าต่างและปุ่มควบคุมหลัก
# ==========================================
st.title("💰 ระบบบันทึกการเงินและข้อมูลนักศึกษา สาขาการเงิน FN A&B 68")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["💵 ฝากเงิน", "💸 ถอนเงิน", "📊 สรุปภาพรวม", "👤 ฟอร์มกรอกข้อมูลนักศึกษา"])

# สร้างรายชื่อนักศึกษาสำหรับใช้ใน Dropdown ของฟอร์มฝาก-ถอน
student_options = [f"{s['รหัสนักศึกษา']} - {s['ชื่อ-นามสกุล']}" for s in st.session_state.students]

# ------------------------------------------
# หน้าต่างที่ 1: ฝากเงิน
# ------------------------------------------
with tab1:
    st.header("แบบฟอร์มบันทึกเงินฝากนักศึกษา")
    if not student_options:
        st.warning("⚠️ ไม่พบข้อมูลนักศึกษาในระบบ โปรดไปกรอกข้อมูลนักศึกษาที่หน้าต่างที่ 4 เป็นอันดับแรกก่อนครับ")
    else:
        with st.form("dep_form_sheet"):
            dep_date = st.date_input("วันที่ฝากเงิน", datetime.now())
            dep_amount = st.number_input("จำนวนเงินที่ฝาก", min_value=0.0, step=100.0)
            dep_user = st.selectbox("ผู้ฝากเงิน", student_options)
            dep_note = st.text_input("หมายเหตุเพิ่มเติม")
            
            if st.form_submit_button("บันทึกข้อมูลการฝากเงินในGoogle Sheet", use_container_width=True):
                if dep_amount > 0:
                    st.session_state.deposits.append({
                        "วันที่ฝาก": dep_date.strftime("%Y-%m-%d"), "จำนวนเงินที่ฝาก": dep_amount,
                        "ผู้ฝากเงิน": dep_user, "หมายเหตุเพิ่มเติม": dep_note
                    })
                    # สั่งเขียนบันทึกลง Google Sheet ทันที
                    conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="Deposits", data=pd.DataFrame(st.session_state.deposits))
                    st.success("บันทึกข้อมูลการฝากเงินในGoogle Sheetเรียบร้อย")
                    st.rerun()
                else: st.error("กรุณากรอกจำนวนเงินที่ฝากให้ถูกต้อง")

    # ปุ่มท้ายแท็บตามโจทย์สั่ง
    if st.button("📊 เรียกดูข้อมูลจาก Google Sheet", key="view_dep_data", use_container_width=True):
        st.dataframe(pd.DataFrame(st.session_state.deposits), use_container_width=True)
    st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_URL, use_container_width=True)

# ------------------------------------------
# หน้าต่างที่ 2: ถอนเงิน
# ------------------------------------------
with tab2:
    st.header("แบบฟอร์มบันทึกการถอนเงินนักศึกษา")
    if not student_options:
        st.warning("⚠️ ไม่พบข้อมูลนักศึกษาในระบบ โปรดไปกรอกข้อมูลนักศึกษาที่หน้าต่างที่ 4 เป็นอันดับแรกก่อนครับ")
    else:
        with st.form("wd_form_sheet"):
            wd_date = st.date_input("วันที่ถอนเงิน", datetime.now())
            wd_amount = st.number_input("จำนวนเงินที่ถอน", min_value=0.0, step=100.0)
            wd_user = st.selectbox("ผู้ถอนเงิน", student_options)
            wd_note = st.text_input("หมายเหตุเพิ่มเติม (ถ้ามี)")
            
            if st.form_submit_button("บันทึกข้อมูลการถอนเงินในGoogle Sheet", use_container_width=True):
                if wd_amount > 0:
                    st.session_state.withdrawals.append({
                        "วันที่ถอน": wd_date.strftime("%Y-%m-%d"), "จำนวนเงินที่ถอน": wd_amount,
                        "ผู้ถอนเงิน": wd_user, "หมายเหตุเพิ่มเติม": wd_note
                    })
                    conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="Withdrawals", data=pd.DataFrame(st.session_state.withdrawals))
                    st.success("บันทึกข้อมูลการฝากเงินในGoogle Sheetเรียบร้อย") # ล็อกคำแสดงผลสำเร็จตามโจทย์ฝั่งถอนเงิน
                    st.rerun()
                else: st.error("กรุณากรอกจำนวนเงินที่ต้องการถอนให้ถูกต้อง")

    if st.button("📊 เรียกดูข้อมูลจาก Google Sheet", key="view_wd_data", use_container_width=True):
        st.dataframe(pd.DataFrame(st.session_state.withdrawals), use_container_width=True)
    st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_URL, use_container_width=True)

# ------------------------------------------
# หน้าต่างที่ 3: สรุปภาพรวม
# ------------------------------------------
with tab3:
    st.header("📊 รายงานสรุปสถานะทางการเงินประจำคลังห้อง")
    df_d = pd.DataFrame(st.session_state.deposits)
    df_w = pd.DataFrame(st.session_state.withdrawals)
    
    total_all_dep = df_d["จำนวนเงินที่ฝาก"].astype(float).sum() if not df_d.empty else 0.0
    total_all_wd  = df_w["จำนวนเงินที่ถอน"].astype(float).sum() if not df_w.empty else 0.0
    total_all_bal = total_all_dep - total_all_wd
    
    # 1. สรุปยอดรวมของทั้งห้อง
    st.subheader("🏫 สรุป ยอดรวมเงินฝาก,ยอดรวมการถอน,ยอดเงินคงเหลือของทั้งห้อง")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric(label="ยอดรวมเงินฝากของทั้งห้อง", value=f"{total_all_dep:,.2f} บาท")
    mc2.metric(label="ยอดรวมการถอนของทั้งห้อง", value=f"{total_all_wd:,.2f} บาท")
    mc3.metric(label="ยอดเงินคงเหลือของทั้งห้อง", value=f"{total_all_bal:,.2f} บาท")
    
    st.markdown("---")
    
    # 2. สรุปยอดรวมรายบุคคล
    st.subheader("👤 สรุป ยอดรวมเงินฝาก,ยอดรวมการถอน,ยอดเงินคงเหลือของนักศึกษาแต่ละคน")
    if not st.session_state.students:
        st.info("ระบบยังไม่มีฐานข้อมูลรายชื่อนักศึกษาสำหรับใช้ในการคำนวณแยกบุคคล")
    else:
        summary_list = []
        for student in st.session_state.students:
            s_match = f"{student['รหัสนักศึกษา']} - {student['ชื่อ-นามสกุล']}"
            
            # คำนวณยอดเงินส่วนตัวจากประวัติคลาวด์
            s_dep = df_d[df_d["ผู้ฝากเงิน"] == s_match]["จำนวนเงินที่ฝาก"].astype(float).sum() if not df_d.empty else 0.0
            s_wd  = df_w[df_w["ผู้ถอนเงิน"] == s_match]["จำนวนเงินที่ถอน"].astype(float).sum() if not df_w.empty else 0.0
            s_bal = s_dep - s_wd
            
            summary_list.append({
                "รหัสนักศึกษา": student["รหัสนักศึกษา"], "ชื่อ - นามสกุล": student["ชื่อ-นามสกุล"], "ชั้นเรียน": student["ชั้นเรียน"],
                "ยอดรวมเงินฝาก (บาท)": f"{s_dep:,.2f}", "ยอดรวมการถอน (บาท)": f"{s_wd:,.2f}", "ยอดเงินคงเหลือคงคลัง (บาท)": f"{s_bal:,.2f}"
            })
        st.dataframe(pd.DataFrame(summary_list), use_container_width=True)

# ------------------------------------------
# หน้าต่างที่ 4: ฟอร์มกรอกข้อมูลนักศึกษา
# ------------------------------------------
with tab4:
    st.header("บันทึกข้อมูลนักศึกษา")
    
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1: s_id_in = st.text_input("รหัสประจำตัวนักศึกษา")
    with c_f2: s_name_in = st.text_input("ชื่อ–นามสกุล")
    with c_f3: s_class_in = st.selectbox("ชั้นเรียน", ["FN A 68", "FN B 68"])
        
    st.markdown("##### ⚙️ ปุ่มควบคุมจัดการฐานข้อมูลนักศึกษา")
    b_col1, b_col2, b_col3 = st.columns(3)
    
    with b_col1:
        if st.button("➕ ปุ่มเพิ่มข้อมูลนักศึกษา", use_container_width=True):
            if s_id_in and s_name_in:
                if any(s["รหัสนักศึกษา"] == s_id_in for s in st.session_state.students): st.error("รหัสนักศึกษานี้มีอยู่แล้ว")
                else:
                    st.session_state.students.append({"รหัสนักศึกษา": s_id_in, "ชื่อ-นามสกุล": s_name_in, "ชั้นเรียน": s_class_in})
                    st.success("เพิ่มข้อมูลเรียบร้อยแล้ว")
            else: st.error("กรุณากรอกรหัสประจำตัวและชื่อ-นามสกุล")
            
    with b_col2:
        if st.button("✏️ ปุ่มแก้ไขข้อมูล", use_container_width=True):
            if s_id_in:
                edited = False
                for s in st.session_state.students:
                    if s["รหัสนักศึกษา"] == s_id_in:
                        if s_name_in: s["ชื่อ-นามสกุล"] = s_name_in
                        s["ชั้นเรียน"] = s_class_in
                        edited = True
                if edited: st.success("แก้ไขข้อมูลสำเร็จ")
                else: st.error("ไม่พบรหัสนักศึกษาคนนี้")
            else: st.error("กรุณากรอกรหัสนักศึกษาที่จะทำการแก้ไขข้อมูล")
            
    with b_col3:
        if st.button("🗑️ ปุ่มลบข้อมูลนักศึกษา", type="primary", use_container_width=True):
            if s_id_in:
                before_len = len(st.session_state.students)
                st.session_state.students = [s for s in st.session_state.students if s["รหัสนักศึกษา"] != s_id_in]
                if len(st.session_state.students) < before_len: st.success("ลบข้อมูลสำเร็จ")
                else: st.error("ไม่พบข้อมูลนักศึกษาที่จะทำการลบ")
            else: st.error("กรุณากรอกรหัสนักศึกษาที่จะทำการลบ")
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("บันทึกข้อมูลนักศึกษาในGoogle Sheet", use_container_width=True, type="secondary"):
        conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet="Students", data=pd.DataFrame(st.session_state.students))
        st.success("บันทึกข้อมูลนักศึกษาในGoogle Sheetเรียบร้อย")
        st.rerun()

    if st.button("📊 เรียกดูข้อมูลจาก Google Sheet", key="view_stu_data", use_container_width=True):
        st.dataframe(pd.DataFrame(st.session_state.students), use_container_width=True)
    st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_URL, use_container_width=True)
