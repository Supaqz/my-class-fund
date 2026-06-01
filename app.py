import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบกองทุนห้องเรียน (Google Sheets)", page_icon="💰", layout="wide")

SECRET_PASSWORD = "admin123" 

# 🔗 วาง URL ของ Google Sheets ของคุณที่นี่ (ต้องเปิดสิทธิ์ให้เป็น Editor ด้วยนะครับ)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1I7VxaAK1BSpIE4WHxoNDre7URuVavkfHAhBJrnehDjw/edit?usp=sharing"

# ==========================================
# 🗃️ การเชื่อมต่อกับ Google Sheets
# ==========================================
# สร้างการเชื่อมต่อ
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    """ดึงข้อมูลจาก Google Sheets ตามชื่อหน้า"""
    try:
        return conn.read(spreadsheet=GOOGLE_SHEET_URL, worksheet=sheet_name, ttl=0).astype(str)
    except:
        # หากหน้าเว็บว่างเปล่า ให้ส่งค่า DataFrame เปล่าที่มีคอลัมน์กลับไป
        if sheet_name == "Students":
            return pd.DataFrame(columns=["id", "name", "class", "status"])
        elif sheet_name == "Classes":
            return pd.DataFrame(columns=["class_name"])
        else:
            return pd.DataFrame(columns=["time", "type", "detail", "amount"])

def save_data(df, sheet_name):
    """อัปเดตและบันทึกข้อมูลกลับไปยัง Google Sheets"""
    conn.update(spreadsheet=GOOGLE_SHEET_URL, worksheet=sheet_name, data=df)
    # รีเฟรชแคชของ Streamlit
    st.cache_data.clear()

# ==========================================
# 💻 ส่วนควบคุมหน้าเว็บ (UI)
# ==========================================
st.title("ระบบจัดการห้องเรียน & กองทุนห้องส่วนกลาง (Google Sheets Cloud) 🌐")
st.write("ระบบฐานข้อมูลออนไลน์ ทำงานร่วมกับ Google Sheets แบบ Real-time")
st.markdown("---")

# โหลดข้อมูลอัปเดตล่าสุดจาก Google Sheets
df_students = load_data("Students")
df_classes = load_data("Classes")
df_trans = load_data("Transactions")

# แปลงประเภทข้อมูลคอลัมน์เงินให้เป็นตัวเลข เพื่อเอาไปคำนวณ
df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors='coerce').fillna(0.0)

# สร้าง แท็บ สลับหน้าจอ
tab1, tab2, tab3 = st.tabs(["📊 หน้าแรก & กองทุนห้อง", "👥 ข้อมูลนักศึกษา & จ่ายเงิน", "⚙️ ตั้งค่า (เพิ่มห้อง/นักศึกษา)"])

# ==========================================
# แท็บที่ 1: หน้าแรก & กองทุนห้อง
# ==========================================
with tab1:
    st.header("ภาพรวมเงินกองกลาง")
    
    # คำนวณเงินคงเหลือรวม
    balance = df_trans["amount"].sum()
    st.metric(label="💰 ยอดเงินคงเหลือในคลังทั้งหมด", value=f"{balance:,.2f} บาท")
    
    st.markdown("---")
    
    st.subheader("🛑 ส่วนของเหรัญญิก: บันทึกรายจ่ายของห้อง")
    with st.expander("คลิกเพื่อบันทึกรายจ่าย (ต้องใช้รหัสผ่าน)"):
        pwd = st.text_input("กรอกรหัสผ่านเหรัญญิก", type="password", key="pwd_expense")
        if pwd == SECRET_PASSWORD:
            exp_detail = st.text_input("รายละเอียดรายจ่าย (เช่น ค่าถ่ายเอกสาร, ค่าหมูกระทะ)")
            exp_amount = st.number_input("จำนวนเงินที่จ่าย (บาท)", min_value=0.0, step=50.0)
            
            if st.button("บันทึกรายจ่าย"):
                if exp_detail and exp_amount > 0:
                    new_row = pd.DataFrame([{
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "type": "รายจ่าย",
                        "detail": exp_detail,
                        "amount": -exp_amount
                    }])
                    df_trans_updated = pd.concat([df_trans, new_row], ignore_index=True)
                    save_data(df_trans_updated, "Transactions")
                    
                    st.success("บันทึกรายจ่ายขึ้น Google Sheets สำเร็จ!")
                    st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
        elif pwd:
            st.error("รหัสผ่านไม่ถูกต้อง")

    st.markdown("---")
    st.subheader("📜 ประวัติการเดินบัญชี (ดึงสดจาก Google Sheets)")
    st.dataframe(df_trans, use_container_width=True)

# ==========================================
# แท็บที่ 2: ข้อมูลนักศึกษา & จ่ายเงิน
# ==========================================
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
            
        st.markdown("---")
        
        st.subheader("🛑 ส่วนของเหรัญญิก: อัปเดตการจ่ายเงินของนักศึกษา")
        with st.expander("คลิกเพื่อบันทึกการรับเงิน (ต้องใช้รหัสผ่าน)"):
            pwd2 = st.text_input("กรอกรหัสผ่านเหรัญญิก", type="password", key="pwd_income")
            if pwd2 == SECRET_PASSWORD:
                unpaid_students = df_filtered_students[df_filtered_students["status"] == "❌ ยังไม่จ่าย"]
                
                if not unpaid_students.empty:
                    selected_student_name = st.selectbox("เลือกรายชื่อคนที่มาจ่ายเงิน", unpaid_students["name"].tolist())
                    income_amount = st.number_input("จำนวนเงินกองกลางที่เก็บ (บาท)", value=500.0, step=100.0)
                    
                    if st.button("ยืนยันการรับเงิน"):
                        # อัปเดตสถานะในตารางนักศึกษา
                        df_students.loc[df_students["name"] == selected_student_name, "status"] = "✅ จ่ายแล้ว"
                        save_data(df_students, "Students")
                        
                        # บันทึกประวัติการรับเงิน
                        new_trans = pd.DataFrame([{
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "type": "รายรับ",
                            "detail": f"{selected_student_name} (เงินกองกลาง)",
                            "amount": income_amount
                        }])
                        df_trans_updated = pd.concat([df_trans, new_trans], ignore_index=True)
                        save_data(df_trans_updated, "Transactions")
                        
                        st.success(f"อัปเดตเงินกองกลางของ {selected_student_name} เรียบร้อย!")
                        st.rerun()
                else:
                    st.success("ทุกคนในห้องนี้จ่ายเงินครบหมดแล้ว! 🎉")
            elif pwd2:
                st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        st.warning("กรุณาเพิ่มห้องเรียนในแท็บตั้งค่าก่อนใช้งาน")

# ==========================================
# แท็บที่ 3: ตั้งค่าระบบ (เพิ่มห้อง/นักศึกษา)
# ==========================================
with tab3:
    st.header("⚙️ การจัดการโครงสร้างข้อมูล")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏫 เพิ่มห้องเรียน")
        new_class = st.text_input("ระบุชื่อห้องเรียนใหม่ (เช่น IT-C)")
        if st.button("เพิ่มห้องเรียน"):
            if new_class:
                if new_class in df_classes["class_name"].tolist():
                    st.error("ห้องเรียนนี้มีอยู่แล้ว!")
                else:
                    new_class_df = pd.DataFrame([{"class_name": new_class}])
                    df_classes_updated = pd.concat([df_classes, new_class_df], ignore_index=True)
                    save_data(df_classes_updated, "Classes")
                    st.success(f"เพิ่มห้องเรียน {new_class} ขึ้นระบบ Cloud สำเร็จ!")
                    st.rerun()
            else:
                st.error("กรุณากรอกชื่อห้องเรียน")
                
    with col2:
        st.subheader("👤 เพิ่มนักศึกษาใหม่")
        new_id = st.text_input("รหัสนักศึกษา")
        new_name = st.text_input("ชื่อ-นามสกุล")
        class_list = df_classes["class_name"].tolist()
        
        if class_list:
            target_class = st.selectbox("เลือกห้องเรียนให้เพื่อน", class_list, key="add_stu_class")
            if st.button("เพิ่มรายชื่อนักศึกษา"):
                if new_id and new_name:
                    if new_id in df_students["id"].astype(str).tolist():
                        st.error("รหัสนักศึกษานี้มีอยู่ในระบบแล้ว!")
                    else:
                        new_student = pd.DataFrame([{
                            "id": new_id,
                            "name": new_name,
                            "class": target_class,
                            "status": "❌ ยังไม่จ่าย"
                        }])
                        df_students_updated = pd.concat([df_students, new_student], ignore_index=True)
                        save_data(df_students_updated, "Students")
                        st.success(f"เพิ่มคุณ {new_name} เข้าฐานข้อมูลออนไลน์เรียบร้อย!")
                        st.rerun()
                else:
                    st.error("กรุณากรอกข้อมูลให้ครบถ้วน")
        else:
            st.info("กรุณาเพิ่มห้องเรียนก่อนเพิ่มนักศึกษา")
