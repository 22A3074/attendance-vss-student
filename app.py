import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
from datetime import datetime
import os

st.title("👨‍🎓 学生用 VSS 出席アプリ（CSV版・QR自動読み取りなし）")

# --- ファイルアップロード ---
shareA_file = st.file_uploader("教員の ShareA.png を選択", type=["png"])
shareB_file = st.file_uploader("自分の ShareB.png を選択", type=["png"])
student_id = st.text_input("学生IDを入力")

# 学生が QR 内容を手入力
qr_text = st.text_input("QRコードに書かれている文字列を入力（復号結果を目視で確認）")

if shareA_file and shareB_file and student_id and qr_text:
    # VSS 復号
    imgA = Image.open(shareA_file).convert("L")
    imgB = Image.open(shareB_file).convert("L")
    imgB = imgB.resize(imgA.size, Image.NEAREST)

    arrA = np.array(imgA)
    arrB = np.array(imgB)
    binA = 1 - (arrA // 255)
    binB = 1 - (arrB // 255)
    reconstructed = np.bitwise_xor(binA, binB)
    original = 1 - reconstructed
    decoded_img = Image.fromarray((original*255).astype(np.uint8))
    
    st.image(decoded_img, caption="復号結果（QRを目視で確認）", width=300)

    if st.button("✅ 出席を記録する"):
        csv_file = "attendance.csv"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = {"学生ID": student_id, "日時": timestamp, "QR情報": qr_text}

        # CSVがあれば追記、なければ作成
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])
        
        df.to_csv(csv_file, index=False, encoding="utf-8")
        st.success("出席がCSVに記録されました ✅")
        st.download_button("📥 出席CSVをダウンロード", df.to_csv(index=False).encode("utf-8"), "attendance.csv")
