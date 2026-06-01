import streamlit as st
import pandas as pd
from datetime import datetime
import json

# ตั้งค่าหน้าเว็บหลัก
st.set_page_config(page_title="ระบบออมเงิน FN A&B 68", page_icon="💰", layout="wide")

# 🔗 ลิงก์ปลายทางฐานข้อมูลตัวใหม่ของคุณ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbx8B-O26hAvjrllHuW3v_GT7S34J2s-JZ-WbPzRsBk-yhNhCRMgZlJzsVP58D0EnyJv/exec"
GOOGLE_SHEET_LINK = "https://docs.google.com/spreadsheets/d/1BpxPfO-hTJNhd9wCBi1_GFEUulp2PQ-QkxCwSUYA3P8/edit?gid=0#gid=0"

# ==========================================
# 🗃️ ระบบฐานข้อมูลในตัวแอป (Session State)
# ==========================================
if "students" not in st.session_state:
    st.session_state.students = []

if "deposits" not in st.session_state:
    st.session_state.deposits = []

if "withdrawals" not in st.session_state:
    st.session_state.withdrawals = []

# ==========================================
# 🪄 ส่วนจำลองการทำงาน JSONP & SweetAlert (Custom HTML/JS Component)
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
            didOpen: () => {{
                Swal.showLoading();
            }}
        }});

        const script = document.createElement('script');
        const encodedData = encodeURIComponent('{payload_json}');
        script.src = "{WEB_APP_URL}?action={action_type}&data=" + encodedData + "&callback=handleResponse";
        document.body.appendChild(script);
    }}

    function handleResponse(response) {{
        if(response.status === "success") {{
            Swal.fire({{
                icon: 'success',
                title: 'บันทึกสำเร็จ!',
                text: response.message,
                confirmButtonColor: '#3085d6'
            }});
        }} else {{
            Swal.fire({{
                icon: 'error',
                title: 'เกิดข้อผิดพลาด',
                text: response.message
            }});
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
            if not sheet_df.empty:
                st.dataframe(sheet_df, use_container_width=True)
            else:
                st.info("ไม่พบรายการที่ถูกบันทึกในฐานข้อมูล")
    with col_b2:
        st.link_button("🌐 แสดงข้อมูล Google Sheet", GOOGLE_SHEET_LINK, use_container_width=True)

# หัวข้อระบบขนาดใหญ่
st.title("💰 ระบบบันทึกการเงินและข้อมูลนักศึกษา สาขาการเงิน FN A&B 68")
st.markdown("---")

# แบ่งหน้าต่างแอปด้วย 4 แท็บเมนูหลัก
tab1, tab2, tab3, tab4 = st.tabs([
    "💵 ฝากเงิน", 
    "💸 ถอนเงิน", 
    "📊 สรุปภาพรวม", 
    "👤 ฟอร์มกรอกข้อมูลนักศึกษา"
])

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
                    stu_id = dep_user.split(" - ")[0]
                    stu_name = dep_user.split(" - ")[1]
                    new_dep = {
                        "id": len(st.session_state.deposits) + 1,
                        "date": dep_date.strftime("%Y-%m-%d"),
                        "student_id": stu_id,
                        "name": stu_name,
                        "amount": dep_amount,
                        "note": dep_note
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
                    stu_id = wd_user.split(" - ")[0]
                    stu_name = wd_user.split(" - ")[1]
                    new_wd = {
                        "id": len(st.session_state.withdrawals) + 1,
                        "date": wd_date.strftime("%Y-%m-%d"),
                        "student_id": stu_id,
                        "name": stu_name,
                        "amount": wd_amount,
                        "note": wd_note
                    }
                    st.session_state.withdrawals.append(new_wd)
                    st.success("บันทึกข้อมูลการฝากเงินใน Google Sheet เรียบร้อย")  # ล็อกคำแสดงผลตามโจทย์
                    run_jsonp_sweetalert("add
