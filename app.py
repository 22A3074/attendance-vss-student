import streamlit as st
from PIL import Image
import numpy as np
import io
import cv2

st.title("👨‍🎓 学生用復号アプリ（QR自動読み取り）")

shareA_file = st.file_uploader("教員の ShareA.png を選択", type=["png"])
shareB_file = st.file_uploader("自分の ShareB.png を選択", type=["png"])

if shareA_file and shareB_file:
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
    st.image(decoded_img, caption="復号結果", width=300)

    # ダウンロード
    buf = io.BytesIO()
    decoded_img.save(buf, format="PNG")
    st.download_button("📥 復号画像をダウンロード", buf.getvalue(), "decoded.png")

    # OpenCVでQRコード読み取り
    cv_img = np.array(decoded_img)
    qr_detector = cv2.QRCodeDetector()
    data, bbox, _ = qr_detector.detectAndDecode(cv_img)
    if data:
        st.success(f"QRコード読み取り成功！\nフォームURL: {data}")
        st.markdown(f"[📄 フォームに移動]({data})")
    else:
        st.warning("QRコードの読み取りに失敗しました。")
