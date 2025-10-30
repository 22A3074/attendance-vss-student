import streamlit as st
from PIL import Image
import numpy as np

st.title("🧑‍🎓 学生用アプリ（出席確認）")

st.write("""
教員から配布された `shareA.png` と  
自分の `shareB.png` をアップロードしてください。
""")

shareA = st.file_uploader("教員から受け取った shareA.png", type=["png"])
shareB = st.file_uploader("自分の shareB.png", type=["png"])

if shareA and shareB:
    imgA = Image.open(shareA).convert("1")
    imgB = Image.open(shareB).convert("1")

    imgB = imgB.resize(imgA.size)
    npA = np.array(imgA)
    npB = np.array(imgB)

    # 合成（AND演算）
    decoded = np.logical_and(npA == 0, npB == 0)
    decoded_img = Image.fromarray(np.uint8(decoded) * 255)

    st.image(decoded_img, caption="復号結果", use_container_width=True)
    st.success("✅ QRコードが復元できた場合は出席確認完了です！")
