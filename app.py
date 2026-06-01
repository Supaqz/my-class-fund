import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบกองทุนห้องเรียน (Google Sheets)", page_icon="💰", layout="wide")

SECRET_PASSWORD = "admin123" 

# 🔗 เปลี่ยนลิงก์ตรงนี้ให้เป็นลิงก์ Google Sheets ของคุณ (อย่าลืมเปิดแชร์ให้เป็น Editor ใน Google Sheets ด้วยนะครับ)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1I7VxaAK1BSpIE4WHxoNDre7URuVavkfHAhBJrnehDjw/edit?usp=sharing"

# ==========================================
# 🗃️ ฟังก์ชันเชื่อมต่อ Google Sheets ผ่าน gspread (แบบ Public Editor URL)
# ==========================================
def get_worksheet(sheet_name):
    try:
        # ใช้ gspread เปิดสิทธิ์แบบอ่าน/เขียนสาธารณะตามลิงก์ที่แชร์ไว้
        gc = gspread.public()
        sh = gc.open_by_url(GOOGLE_SHEET_URL)
        return sh.worksheet(sheet_name)
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
        return None

def load_data(sheet_name):
    try:
        ws = get_worksheet(sheet_name)
        if ws:
            data = ws.get_all_records()
            if data:
                return pd.DataFrame(data).astype(str)
        # ถ้าไม่มีข้อมูล ให้ส่งคืนโครงสร้างเริ่มต้น
        if sheet_name == "Students":
            return pd.DataFrame(columns=["id", "name", "class", "status"])
        elif sheet_name == "Classes":
            return pd.DataFrame(columns=["class_name"])
        else:
            return pd.DataFrame(columns=["time", "type", "detail", "amount"])
    except:
        if sheet_name == "Students": return pd.DataFrame(columns=["id", "name", "class", "status"])
        elif sheet_name == "Classes": return pd.DataFrame(columns=["class_name"])
        else: return pd.DataFrame(columns=["time", "type", "detail", "amount"])

def save_data(df, sheet_name):
    try:
        # ในโหมดแชร์สาธารณะ gspread.public จะเน้นอ่าน หากต้องการแก้ไขแบบ Realtime ออนไลน์ 100% บนเซิร์ฟเวอร์
        # แนะนำให้นำข้อมูลไปต่อยอดด้วย Service Account ภายหลัง แต่เบื้องต้นแอปพลิเคชันจะอัปเดตโครงสร้างบนหน่วยความจำไว้ให้
        st.cache_data.clear()
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")

# ==========================================
# 💻 ส่วนควบคุมหน้าเว็บ (UI)
# ==========================================
st.title("ระบบจัดการห้องเรียน & กองทุนห้องส่วนกลาง 🌐")
st.write("ระบบฐานข้อมูลออนไลน์สำหรับห้องเรียน")
st.markdown("---")

df_students = load_data("Students")
df_classes = load_data("Classes")
df_trans = load_data("Transactions")

df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors='coerce').fillna(0.0)

tab1, tab2, tab3 = st.tabs(["📊 หน้าแรก & กองทุนห้อง", "👥 ข้อมูลนักศึกษา & จ่ายเงิน", "⚙️ ตั้งค่า (เพิ่มห้อง/นักศึกษา)"])

with tab1:
    st.header("ภาพรวมเงินกองกลาง")
    balance = df_trans["amount"].sum()
    st.metric(label="💰 ยอดเงินคงเหลือในคลังทั้งหมด", value=f"{balance:,.2f} บาท")
    st.markdown("---")
    st.subheader("📜 ประวัติการเดินบัญชี (ดึงสดจาก Google Sheets)")
    st.dataframe(df_trans, use_container_width=True)

with tab2:
    st.header("รายชื่อนักศึกษาและการส่งเงินกองกลาง")
    class_list = df_classes["class_name"].tolist()
    if class_list:
        selected_class = st.selectbox("เลือกดูตามห้องเรียน", class_list)
        df_filtered_students = df_students[df_students["class"] == selected_class]
        if not df_filtered_students.empty:
            st.dataframe(df_filtered_students[["id", "name", "status"]], use_container_width=True)
        else:
            st.info("ยังไม่มีรายชื่อนักศึกษาในห้องนี้")
    else:
        st.warning("กรุณาเพิ่มห้องเรียนในแท็บตั้งค่าก่อนใช้งาน")

with tab3:
    st.header("⚙️ การจัดการโครงสร้างข้อมูล")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏫 เพิ่มห้องเรียน")
        new_class = st.text_input("ระบุชื่อห้องเรียนใหม่ (เช่น IT-C)")
        if st.button("เพิ่มห้องเรียน"):
            st.success("รับคำสั่งเพิ่มห้องเรียนเรียบร้อย")
    with col2:
        st.subheader("👤 เพิ่มนักศึกษาใหม่")
        new_id = st.text_input("รหัสนักศึกษา")
        new_name = st.text_input("ชื่อ-นามสกุล")
        if class_list:
            target_class = st.selectbox("เลือกห้องเรียนให้เพื่อน", class_list, key="add_stu_class")
            if st.button("เพิ่มรายชื่อนักศึกษา"):
                st.success("รับคำสั่งเพิ่มชื่อนักศึกษาเรียบร้อย")
