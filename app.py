import streamlit as st
from PIL import Image
import numpy as np

st.title("学生用復号アプリ")

shareA_file = st.file_uploader("教員の shareA.png を選択", type=["png"])
shareB_file = st.file_uploader("自分の shareB.png を選択", type=["png"])

if shareA_file and shareB_file:
    imgA = Image.open(shareA_file)
    imgB = Image.open(shareB_file)

    # サイズを揃える
    imgB = imgB.resize(imgA.size, Image.NEAREST)

    # 画像を 0/1 配列に変換
    arrA = np.array(imgA)
    arrB = np.array(imgB)
    binA = 1 - (arrA // 255)  # 保存時に反転されているので戻す
    binB = 1 - (arrB // 255)

    # XOR して復号
    reconstructed = np.bitwise_xor(binA, binB)
    # 教師側が反転しているので、さらに反転して元画像に
    original = 1 - reconstructed

    decoded_img = Image.fromarray((original*255).astype(np.uint8))
    st.image([decoded_img], caption=["復号結果"], width=300)
