import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2
import pyzbar.pyzbar as pyzbar

st.title("👨‍🎓 学生用復号アプリ（QR自動読み取り）")

# アップロード
shareA_file = st.file_uploader("教員の ShareA.png を選択", type=["png"])
shareB_file = st.file_uploader("自分の ShareB.png を選択", type=["png"])

if shareA_file and shareB_file:
    # 画像読み込み
    imgA = Image.open(shareA_file).convert("L")
    imgB = Image.open(shareB_file).convert("L")

    # サイズを揃える
    imgB = imgB.resize(imgA.size, Image.NEAREST)

    # 0/1 に変換（教師側反転を戻す）
    arrA = np.array(imgA)
    arrB = np.array(imgB)
    binA = 1 - (arrA // 255)
    binB = 1 - (arrB // 255)

    # XORで復号
    reconstructed = np.bitwise_xor(binA, binB)
    original = 1 - reconstructed  # 教師側の反転を戻す

    decoded_img = Image.fromarray((original*255).astype(np.uint8))
    st.image(decoded_img, caption="復号結果", width=300)

    # ダウンロードボタン
    buf = io.BytesIO()
    decoded_img.save(buf, format="PNG")
    st.download_button("📥 復号画像をダウンロード", buf.getvalue(), "decoded.png")

    # QRコード読み取り
    decoded_data = None
    cv_img = np.array(decoded_img)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2BGR)
    qr_codes = pyzbar.decode(cv_img)

    if qr_codes:
        decoded_data = qr_codes[0].data.decode("utf-8")
        st.success(f"QRコード読み取り成功！\nフォームURL: {decoded_data}")
        st.markdown(f"[📄 フォームに移動]({decoded_data})")
    else:
        st.warning("QRコードの読み取りに失敗しました。")
