import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import io

st.title("🎓 出席確認（視覚復号型秘密分散）")

st.write("""
このアプリは、視覚復号型秘密分散法 (Visual Secret Sharing) を用いて、
出席確認を安全に行うデモです。
""")

# --- モード選択 ---
mode = st.radio("モードを選択してください", ["教員側（シェア生成）", "学生側（復号）"])

# ============================================================
# 教員モード：shareA を自動生成
# ============================================================
if mode == "教員側（シェア生成）":
    uploaded = st.file_uploader("元画像をアップロードしてください（例：出席コード画像など）", type=["png", "jpg"])
    if uploaded:
        base = Image.open(uploaded).convert("1")  # 白黒化
        base = ImageOps.invert(base)  # 黒白反転（秘密画像の黒部分を処理）
        np_base = np.array(base)

        # ランダムにシェアAを生成
        shareA = np.random.randint(0, 2, np_base.shape, dtype=np.uint8)
        # シェアBをXORで生成（1→黒）
        shareB = np_base ^ shareA

        imgA = Image.fromarray((1 - shareA) * 255)
        imgB = Image.fromarray((1 - shareB) * 255)

        st.image([imgA, imgB], caption=["教員用シェアA", "学生用シェアB"], width=250)

        # ダウンロードボタン
        bufA = io.BytesIO()
        bufB = io.BytesIO()
        imgA.save(bufA, format="PNG")
        imgB.save(bufB, format="PNG")
        st.download_button("📥 シェアAをダウンロード", bufA.getvalue(), "shareA.png")
        st.download_button("📥 シェアBをダウンロード（学生へ配布）", bufB.getvalue(), "shareB.png")

# ============================================================
# 学生モード：復号
# ============================================================
else:
    shareA = st.file_uploader("教員から配布された shareA.png をアップロード", type=["png"])
    shareB = st.file_uploader("自分の shareB.png をアップロード", type=["png"])

    if shareA and shareB:
        imgA = Image.open(shareA).convert("1")
        imgB = Image.open(shareB).convert("1")

        # サイズ調整
        imgB = imgB.resize(imgA.size)

        npA = np.array(imgA)
        npB = np.array(imgB)

        # 重ね合わせ (AND演算)
        decoded = np.logical_and(npA == 0, npB == 0)
        decoded_img = Image.fromarray(np.uint8(decoded) * 255)

        st.image(decoded_img, caption="復号結果", use_container_width=True)
