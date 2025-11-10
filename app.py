import streamlit as st
from PIL import Image
import numpy as np
import io
from pyzbar.pyzbar import decode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.title("👨‍🎓 学生用 VSS 出席アプリ（OpenCV 不使用）")

# --- Google スプレッドシート設定 ---
st.sidebar.header("Google スプレッドシート設定")
sheet_key = st.sidebar.text_input("スプレッドシートキー（URLの/d/.../部分）")
credentials_file = st.sidebar.file_uploader("サービスアカウント JSON", type=["json"])

# --- ファイルアップロード ---
shareA_file = st.file_uploader("教員の ShareA.png を選択", type=["png"])
shareB_file = st.file_uploader("自分の ShareB.png を選択", type=["png"])
student_id = st.text_input("学生IDを入力")

if shareA_file and shareB_file and student_id:
    # 画像を読み込み
    imgA = Image.open(shareA_file).convert("L")
    imgB = Image.open(shareB_file).convert("L")
    imgB = imgB.resize(imgA.size, Image.NEAREST)

    # VSS 復号 (XOR)
    arrA = np.array(imgA)
    arrB = np.array(imgB)
    binA = 1 - (arrA // 255)
    binB = 1 - (arrB // 255)
    reconstructed = np.bitwise_xor(binA, binB)
    original = 1 - reconstructed
    decoded_img = Image.fromarray((original*255).astype(np.uint8))
    st.image(decoded_img, caption="復号結果", width=300)

    # QRコード読み取り (pyzbar)
    decoded_objects = decode(decoded_img)
    if decoded_objects:
        qr_data = decoded_objects[0].data.decode()
        st.success(f"QRコード読み取り成功！\nフォームURL: {qr_data}")
    else:
        st.warning("QRコードの読み取りに失敗しました。")
        qr_data = None

    # Google スプレッドシートに書き込み
    if qr_data and sheet_key and credentials_file:
        credentials_file.seek(0)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.load(credentials_file),
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_key)
        worksheet = sh.sheet1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        worksheet.append_row([student_id, timestamp, qr_data])
        st.success("出席が記録されました ✅")
