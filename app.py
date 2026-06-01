import streamlit as st
import pandas as pd
from datetime import datetime
import json

# ตั้งค่าหน้าเว็บหลัก
st.set_page_config(page_title="ระบบออมเงิน FN A&B 68", page_icon="💰", layout="wide")

# 🔗 ลิงก์ปลายทางฐานข้อมูลตัวใหม่ของคุณ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwN68SHFe5WS6mX5u8RmiAXDt2-_24OuawdUV9FQWwbAyAok4kBzW9dgzeiEgHw9gpY/exec"
GOOGLE_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1BpxPfO-hTJNhd9wCBi1_GFEUulp2PQ-QkxCwSUYA3P8/edit?gid=0#gid=0"

# ==========================================
# 🗃️ ระบบฐานข้อมูลในตัวแอป (Session State)
# ==========================================
if "students" not in st.session_state: st.session_state.students = []
if "deposits" not in st.session_state: st.session_state.deposits = []
if "withdrawals" not in st.session_state: st.session_state.withdrawals = []

# ==========================================
# 🪄 ส่วนจำลองการทำงาน JSONP & SweetAlert
# ==========================================
def run_jsonp_sweetalert(action_type, payload_dict):
    """ฟังก์ชันยิงคำสั่ง JSONP ไปยัง Google Apps Script พร้อมเรียกใช้ SweetAlert2"""
    payload_json = json.dumps(payload_dict, ensure_ascii=False)
    js_code = f"""
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    <script>
    function executeJSONP() {{
        Swal.fire({{
            title: 'กำลังเชื่อมต่อกับ Google Sheet...',
            text: 'กรุณารอการบันทึกข้อมูลสักครู่',
            allowOutsideClick: false,
            didOpen: () => {{ Swal.showLoading(); }}
        }});
        const script = document.createElement('script');
        const encodedData = encodeURIComponent('{payload_json}');
        script.src = "{WEB_APP_URL}?action=" + "{action_type}" + "&data=" + encodedData + "&callback=handleResponse";
        document.body.appendChild(script);
    }}
    function handleResponse(response) {{
        if(response.status === "success") {{
            Swal.fire({{ icon: 'success', title: 'บันทึกสำเร็จ!', text: response.message, confirmButtonColor: '#3085d6' }});
        }} else {{
            Swal.fire({{ icon: 'error', title: 'เกิดข้อผิดพลาด', text: response.message }});
        }}
    }}
    executeJSONP();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# ==========================================
# 🎨 การจัดแสดงสไตล์ปุ่มและการลิงก์เว็บภายนอก
# ==========================================
def render_common_buttons(sheet_df, info_text):
    """ปุ่มเรียกดูข้อมูล และปุ่มแสดงไฟล์ Google Sheet ประจำทุกหน้าต่าง"""
    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📊 เรียกดูข้อมูลจาก Google Sheet", use_container_width=True):
            st.write(f"📝 **ข้อมูลอัปเดตปัจจุบัน ({info_text}):**")
            if not sheet_df.empty: st.dataframe(sheet_df, use_container_width=True)
            else: st.info("ไม่พบรายการที่ถูกบันทึกในฐานข้อมูล")
    with col_b2:
        st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_LINK, use_container_width=True)

# หัวข้อระบบขนาดใหญ่
st.title("💰 ระบบบันทึกการเงินและข้อมูลนักศึกษา สาขาการเงิน FN A&B 68")
st.markdown("---")

# แบ่งหน้าต่างแอปด้วย 4 แท็บเมนูหลัก
tab1, tab2, tab3, tab4 = st.tabs(["💵 ฝากเงิน", "💸 ถอนเงิน", "📊 สรุปภาพรวม", "👤 ฟอร์มกรอกข้อมูลนักศึกษา"])

# ดึงข้อมูลนักศึกษาปัจจุบันมาทำตัวเลือก Dropdown
student_list = [f"{s['id']} - {s['name']}" for s in st.session_state.students]

# ==========================================
# หน้าต่างที่ 1: ฝากเงิน
# ==========================================
with tab1:
    st.header("📋 แบบฟอร์มบันทึกเงินฝากนักศึกษา")
    if not student_list:
        st.warning("⚠️ โปรดไปที่หน้าต่างที่ 4 เพื่อเพิ่มรายชื่อนักศึกษาก่อนใช้งานฟอร์มฝากเงิน")
    else:
        with st.form("deposit_form"):
            dep_date = st.date_input("วันที่ฝากเงิน", datetime.now())
            dep_amount = st.number_input("จำนวนเงินที่ฝาก", min_value=0.0, step=50.0)
            dep_user = st.selectbox("ผู้ฝากเงิน", student_list)
            dep_note = st.text_input("หมายเหตุเพิ่มเติม (ถ้ามี)", placeholder="ระบุเหตุผลการฝาก...")
            
            submit_dep = st.form_submit_button("💾 บันทึกข้อมูลการฝากเงินใน Google Sheet", use_container_width=True)
            if submit_dep:
                if dep_amount <= 0:
                    st.error("กรุณาระบุจำนวนเงินที่มากกว่า 0 บาท")
                else:
                    stu_id, stu_name = dep_user.split(" - ")[0], dep_user.split(" - ")[1]
                    new_dep = {
                        "id": len(st.session_state.deposits) + 1, "date": dep_date.strftime("%Y-%m-%d"),
                        "student_id": stu_id, "name": stu_name, "amount": dep_amount, "note": dep_note
                    }
                    st.session_state.deposits.append(new_dep)
                    st.success("บันทึกข้อมูลการฝากเงินใน Google Sheet เรียบร้อย")
                    run_jsonp_sweetalert("addDeposit", new_dep)

        df_dep_view = pd.DataFrame(st.session_state.deposits) if st.session_state.deposits else pd.DataFrame()
        render_common_buttons(df_dep_view, "ประวัติการฝากเงิน")

# ==========================================
# หน้าต่างที่ 2: ถอนเงิน
# ==========================================
with tab2:
    st.header("📋 แบบฟอร์มบันทึกการถอนเงินนักศึกษา")
    if not student_list:
        st.warning("⚠️ โปรดไปที่หน้าต่างที่ 4 เพื่อเพิ่มรายชื่อนักศึกษาก่อนใช้งานฟอร์มถอนเงิน")
    else:
        with st.form("withdraw_form"):
            wd_date = st.date_input("วันที่ถอนเงิน", datetime.now())
            wd_amount = st.number_input("จำนวนเงินที่ถอน", min_value=0.0, step=50.0)
            wd_user = st.selectbox("ผู้ถอนเงิน", student_list)
            wd_note = st.text_input("หมายเหตุเพิ่มเติม (ถ้ามี)")
            
            submit_wd = st.form_submit_button("💸 บันทึกข้อมูลการถอนเงินใน Google Sheet", use_container_width=True)
            if submit_wd:
                if wd_amount <= 0:
                    st.error("กรุณาระบุจำนวนเงินที่มากกว่า 0 บาท")
                else:
                    stu_id, stu_name = wd_user.split(" - ")[0], wd_user.split(" - ")[1]
                    new_wd = {
                        "id": len(st.session_state.withdrawals) + 1, "date": wd_date.strftime("%Y-%m-%d"),
                        "student_id": stu_id, "name": stu_name, "amount": wd_amount, "note": wd_note
                    }
                    st.session_state.withdrawals.append(new_wd)
                    st.success("บันทึกข้อมูลการฝากเงินใน Google Sheet เรียบร้อย")
                    run_jsonp_sweetalert("addWithdrawal", new_wd)

        df_wd_view = pd.DataFrame(st.session_state.withdrawals) if st.session_state.withdrawals else pd.DataFrame()
        render_common_buttons(df_wd_view, "ประวัติการถอนเงิน")

# ==========================================
# หน้าต่างที่ 3: สรุปภาพรวม
# ==========================================
with tab3:
    st.header("📊 สรุปภาพรวมระบบบัญชีคลังห้อง")
    total_room_dep = sum(d["amount"] for d in st.session_state.deposits)
    total_room_wd = sum(w["amount"] for w in st.session_state.withdrawals)
    room_balance = total_room_dep - total_room_wd
    
    st.subheader("🏫 1. สรุปยอดรวมของทั้งห้อง")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric(label="ยอดรวมเงินฝากทั้งห้อง", value=f"{total_room_dep:,.2f} บาท")
    mc2.metric(label="ยอดรวมการถอนทั้งห้อง", value=f"{total_room_wd:,.2f} บาท")
    mc3.metric(label="ยอดเงินคงเหลือของทั้งห้อง", value=f"{room_balance:,.2f} บาท")
    
    st.markdown("---")
    st.subheader("👤 2. ยอดคงเหลือของนักศึกษาแต่ละคน")
    if not st.session_state.students:
        st.info("ยังไม่มีข้อมูลนักศึกษาในระบบสำหรับการสรุปยอด")
    else:
        summary_records = []
        for student in st.session_state.students:
            s_id = student["id"]
            s_dep = sum(d["amount"] for d in st.session_state.deposits if d["student_id"] == s_id)
            s_wd = sum(w["amount"] for w in st.session_state.withdrawals if w["student_id"] == s_id)
            s_bal = s_dep - s_wd
            summary_records.append({
                "รหัสนักศึกษา": s_id, "ชื่อ - นามสกุล": student["name"], "ชั้นเรียน": student["class"],
                "ยอดรวมเงินฝาก (บาท)": f"{s_dep:,.2f}", "ยอดรวมการถอน (บาท)": f"{s_wd:,.2f}", "ยอดเงินคงเหลือคงคลัง (บาท)": f"{s_bal:,.2f}"
            })
        st.dataframe(pd.DataFrame(summary_records), use_container_width=True)

# ==========================================
# หน้าต่างที่ 4: ฟอร์มกรอกข้อมูลนักศึกษา
# ==========================================
with tab4:
    st.header("👤 บันทึกข้อมูลนักศึกษา")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1: s_id_input = st.text_input("รหัสประจำตัวนักศึกษา")
    with col_f2: s_name_input = st.text_input("ชื่อ–นามสกุล")
    with col_f3: s_class_input = st.selectbox("ชั้นเรียน", ["FN A 68", "FN B 68"])
        
    st.markdown("##### ⚙️ ปุ่มควบคุมจัดการฐานข้อมูลนักศึกษาชั่วคราว")
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    
    with c_btn1:
        if st.button("➕ ปุ่มเพิ่มข้อมูลนักศึกษา", use_container_width=True):
            if s_id_input and s_name_input:
                if any(s["id"] == s_id_input for s in st.session_state.students): st.error("รหัสนักศึกษานี้มีอยู่แล้วในระบบ")
                else:
                    st.session_state.students.append({"id": s_id_input, "name": s_name_input, "class": s_class_input})
                    st.success("เพิ่มข้อมูลเรียบร้อยแล้ว")
            else: st.error("กรุณากรอกรหัสและชื่อนักศึกษา")
            
    with c_btn2:
        if st.button("✏️ ปุ่มแก้ไขข้อมูล", use_container_width=True):
            if s_id_input:
                found = False
                for s in st.session_state.students:
                    if s["id"] == s_id_input:
                        if s_name_input: s["name"] = s_name_input
                        s["class"] = s_class_input
                        found = True
                if found: st.success("แก้ไขข้อมูลสำเร็จ")
                else: st.error("ไม่พบรหัสนักศึกษาที่จะทำการแก้ไข")
            else: st.error("กรุณาระบุรหัสนักศึกษาที่ต้องการแก้ไขข้อมูล")
            
    with c_btn3:
        if st.button("🗑️ ปุ่มลบข้อมูลนักศึกษา", type="primary", use_container_width=True):
            if s_id_input:
                initial_count = len(st.session_state.students)
                st.session_state.students = [s for s in st.session_state.students if s["id"] != s_id_input]
                if len(st.session_state.students) < initial_count: st.success("ลบข้อมูลสำเร็จ")
                else: st.error("ไม่พบรหัสนักศึกษานี้ในระบบ")
            else: st.error("กรุณาระบุรหัสนักศึกษาที่ต้องการลบ")
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🌐 บันทึกข้อมูลนักศึกษาใน Google Sheet", use_container_width=True, type="secondary"):
        if st.session_state.students:
            st.success("บันทึกข้อมูลนักศึกษาใน Google Sheet เรียบร้อย")
            run_jsonp_sweetalert("syncStudents", st.session_state.students)
        else: st.error("ไม่มีข้อมูลนักศึกษาสำหรับซิงค์คลาวด์")
            
    df_stu_view = pd.DataFrame(st.session_state.students) if st.session_state.students else pd.DataFrame()
    render_common_buttons(df_stu_view, "ทำเนียบรายชื่อนักศึกษา")
