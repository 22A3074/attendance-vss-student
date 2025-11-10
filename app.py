import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="👨‍🎓 学生用復号アプリ（出席送信対応）")

st.title("👨‍🎓 学生用復号アプリ（出席が自動記録されます）")

# ---- Google Sheets 設定 ----
SPREADSHEET_ID = "15pSdjTDIiYHO8AX6EzPXSM0J4tYMYFsvsTbKjIyBgO0"

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
gc = gspread.authorize(credentials)
ws = gc.open_by_key(SPREADSHEET_ID).sheet1


def record_attendance(student_id, class_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws.append_row([timestamp, student_id, class_id, "present"])


# ---- 入力 ----
student_id = st.text_input("自分の学生IDを入力")
class_id = st.text_input("本日の授業ID（教員が指定）")

shareA_file = st.file_uploader("🖼 教員の ShareA.png を選択", type=["png"])
shareB_file = st.file_uploader("🖼 自分の ShareB.png を選択", type=["png"])

if shareA_file and shareB_file and student_id and class_id:

    # 正しい読み方（ここが今回の修正ポイント）
    imgA = Image.open(io.BytesIO(shareA_file.read())).convert("L")
    imgB = Image.open(io.BytesIO(shareB_file.read())).convert("L")
    imgB = imgB.resize(imgA.size, Image.NEAREST)

    arrA = np.array(imgA)
    arrB = np.array(imgB)

    binA = 1 - (arrA // 255)
    binB = 1 - (arrB // 255)

    reconstructed = np.bitwise_xor(binA, binB)
    result = 1 - reconstructed
    decoded_img = Image.fromarray((result * 255).astype(np.uint8))
    st.image(decoded_img, caption="復号結果", width=300)

    # ---- QRコード読み取り ----
    cv_img = np.array(decoded_img)
    qr_detector = cv2.QRCodeDetector()
    data, bbox, _ = qr_detector.detectAndDecode(cv_img)

    if data:
        st.success("QRコード読み取り成功！データ = " + data)

        # ---- 出席記録 ----
        record_attendance(student_id, class_id)
        st.success(f"出席が記録されました： {student_id} / {class_id}")

        st.markdown(f"[📄 教員が指定したフォームを開く]({data})")

    else:
        st.warning("QRコードが読み取れませんでした。")


else:
    st.info("学生ID・授業ID・ShareA・ShareB の 4つを入力してください。")
