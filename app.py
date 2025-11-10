# attendance_vss_student.py
import streamlit as st
from PIL import Image
import numpy as np, io, hashlib, requests
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="👨‍🎓 学生用復号アプリ", layout="centered")
st.title("👨‍🎓 学生用復号アプリ（QR自動読み取り + 出席送信）")

st.write("注意: 教員の配布した ShareB（自分専用）をあらかじめ保存し、授業ごとに配布される教員側の ShareA を使って復号します。")

shareA_file = st.file_uploader("教員の ShareA（授業ごと）を選択", type=["png"])
shareB_file = st.file_uploader("自分の ShareB（配布済み）を選択", type=["png"])
student_id = st.text_input("Student ID（学籍番号）")
teacher_api_url = st.text_input("教員の API エンドポイント URL")

if shareA_file and shareB_file:
    imgA = Image.open(shareA_file).convert("L")
    imgB = Image.open(shareB_file).convert("L").resize(imgA.size, Image.NEAREST)

    arrA = np.array(imgA)
    arrB = np.array(imgB)
    binA = 1 - (arrA // 255)
    binB = 1 - (arrB // 255)

    reconstructed = np.bitwise_xor(binA, binB)
    original = 1 - reconstructed
    decoded_img = Image.fromarray((original * 255).astype(np.uint8))
    st.image(decoded_img, caption="復号結果（QR）", width=350)

    buf = io.BytesIO()
    decoded_img.save(buf, format="PNG")
    st.download_button("📥 復号画像をダウンロード", buf.getvalue(), "decoded.png")

    # === QR 読み取り（pyzbar版） ===
    decoded = decode(decoded_img)
    if decoded:
        data = decoded[0].data.decode("utf-8")
        st.success("QRコード読み取り成功！")
        st.write("QR の内容:")
        st.code(data)

        parsed = urlparse(data)
        q = parse_qs(parsed.query)
        class_id = q.get("class", ["unknown"])[0]
        st.write(f"検出された class_id: {class_id}")

        shareB_file.seek(0)
        shareb_bytes = shareB_file.read()
        sha = hashlib.sha256(shareb_bytes).hexdigest()
        st.write(f"自分の ShareB SHA256: `{sha}`")

        if st.button("✅ 出席送信"):
            if not student_id:
                st.error("student_id を入力してください。")
            elif not teacher_api_url:
                st.error("教員の API URL を入力してください。")
            else:
                payload = {
                    "student_id": student_id,
                    "shareb_hash": sha,
                    "class_id": class_id,
                    "source_url": data
                }
                try:
                    resp = requests.post(teacher_api_url, json=payload, timeout=10)
                    if resp.ok:
                        st.success("出席記録完了。教員側で確認できます。")
                        st.json(resp.json())
                    else:
                        st.error(f"サーバーエラー: {resp.status_code} {resp.text}")
                except Exception as e:
                    st.error(f"送信に失敗しました: {e}")
    else:
        st.warning("QRコードの読み取りに失敗しました。")
