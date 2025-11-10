import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import pandas as pd
from datetime import datetime
import io
import os

st.title("👨‍🎓 学生用 VSS 出席アプリ（CSV版）")

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
        qr_data = "読み取り失敗"

    # CSV に出席記録
    csv_file = "attendance.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"学生ID": student_id, "日時": timestamp, "QR_URL": qr_data}

    # 既存CSVがあれば読み込み、新規なら作成
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(csv_file, index=False, encoding="utf-8")
    st.success("出席がCSVに記録されました ✅")
    st.download_button("📥 出席CSVをダウンロード", df.to_csv(index=False).encode("utf-8"), "attendance.csv")
