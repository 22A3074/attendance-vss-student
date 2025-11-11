import streamlit as st
from PIL import Image
import numpy as np
import io

# QR読み取り用 (opencv-python が必要)
try:
    import cv2
    QR_AVAILABLE = True
except Exception:
    QR_AVAILABLE = False

st.set_page_config(page_title="出席確認（学生用）", layout="centered")
st.title("🧑‍🎓 学生用アプリ（出席確認）")

st.write("教員から配布された `shareA.png` と 自分の `shareB.png` をアップロードしてください。")

# --- アップロード ---
shareA_file = st.file_uploader("教員の shareA.png を選択", type=["png", "jpg", "jpeg"])
shareB_file = st.file_uploader("あなたの shareB.png を選択", type=["png", "jpg", "jpeg"])


def pil_to_binary_array(pil_img, size=None, threshold=128):
    """
    PIL画像を受け取り、指定サイズにリサイズしてから
    明確に二値化（0または1の配列）して返す。
    Convention: 黒(pixel <= threshold) -> 1, 白 -> 0
    """
    if size is not None:
        pil_img = pil_img.resize(size, resample=Image.NEAREST)
    gray = pil_img.convert("L")
    arr = np.array(gray)
    bin_arr = np.where(arr <= threshold, 1, 0).astype(np.uint8)
    return bin_arr


if shareA_file and shareB_file:
    imgA = Image.open(shareA_file)
    imgB = Image.open(shareB_file)

    sizeA = imgA.size
    imgB = imgB.resize(sizeA, resample=Image.NEAREST)

    binA = pil_to_binary_array(imgA, size=sizeA, threshold=128)
    binB = pil_to_binary_array(imgB, size=sizeA, threshold=128)

    reconstructed = np.bitwise_xor(binA, binB)
    original = 1 - reconstructed  # invert to recover original secret

    decoded_img = Image.fromarray((original * 255).astype(np.uint8))

    st.image([imgA.convert("RGB"), imgB.convert("RGB"), decoded_img],
             caption=["shareA (教員)", "shareB (あなた)", "復号結果"],
             width=280)

    # -----------------------------
    # ここから 改良版 QRコード読み取り
    # -----------------------------
    if QR_AVAILABLE:
        st.write("🔎 QRコード読み取りを試みます...")

        decoded_arr = np.array(decoded_img.convert("L"))

        detector = cv2.QRCodeDetector()
        data, points, straight_qrcode = detector.detectAndDecode(decoded_arr)

        if data and data.strip() != "":
            st.success(f"QRコード検出: {data}")
            st.markdown(f"[出席フォームへ移動]({data})")
        else:
            st.info("QRコードが見つかりませんでした。画像の黒白が薄い可能性があります。")
    else:
        st.info("OpenCV が利用できません。`requirements.txt` に `opencv-python` を入れてください。")

    st.success("復号処理が完了しました。")
else:
    st.info("shareA と shareB の両方をアップロードしてください。")
