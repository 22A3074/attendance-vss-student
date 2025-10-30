import streamlit as st
from PIL import Image
import numpy as np
import io

st.title("👨‍🎓 学生用アプリ（シェア復号）")

st.write("教員から配布されたシェアAと自分のシェアBをアップロードして重ねます。")

shareA_file = st.file_uploader("シェアAをアップロード（教員提供）", type=["png"])
shareB_file = st.file_uploader("シェアBをアップロード（自分用）", type=["png"])

def combine_shares(imgA, imgB):
    """2つのシェア画像を重ねて復号"""
    # サイズを揃える（大きい方にリサイズ）
    w = max(imgA.width, imgB.width)
    h = max(imgA.height, imgB.height)
    imgA = imgA.resize((w, h))
    imgB = imgB.resize((w, h))

    arrA = np.array(imgA.convert("1"), dtype=np.uint8)
    arrB = np.array(imgB.convert("1"), dtype=np.uint8)

    combined = np.minimum(arrA, arrB)  # 黒が出る方を優先
    return Image.fromarray(combined*255)

if shareA_file and shareB_file:
    imgA = Image.open(shareA_file)
    imgB = Image.open(shareB_file)

    combined_img = combine_shares(imgA, imgB)
    st.image(combined_img, caption="復号結果（重ね合わせた画像）", width=300)

    # ダウンロード
    buf = io.BytesIO()
    combined_img.save(buf, format="PNG")
    st.download_button("📥 復号画像をダウンロード", buf.getvalue(), "decoded.png")
