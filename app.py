# --- 修正版 student_app.py ---

import streamlit as st
from PIL import Image
import numpy as np
import io, os, hashlib, datetime, json, pandas as pd

st.set_page_config(page_title="👨‍🎓 学生用：出席 (復号して送信)", layout="centered")
st.title("👨‍🎓 学生用アプリ（ShareB 固定、授業 ShareA を取り込み復号→出席登録）")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ATT_CSV = os.path.join(DATA_DIR, "attendance_records.csv")

def stable_seed_from_str(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")

def img_to_binarr(img: Image.Image, threshold: int):
    g = img.convert("L")
    arr = np.array(g)
    return (arr < threshold).astype(np.uint8)

def binarr_to_image(binarr: np.ndarray):
    return Image.fromarray((255 * (1 - binarr)).astype(np.uint8))

# ✅ 教師側と完全一致する ShareB 生成関数（threshold を使わない）
def gen_shareB_from_id(sid: str, shape):
    seed = stable_seed_from_str("B:"+sid)
    rng = np.random.default_rng(seed=seed)
    return rng.integers(0,2,size=shape, dtype=np.uint8)

st.header("入力")
sid = st.text_input("学生ID（例: s001）")

meta_upload = st.file_uploader("教師提供 metadata.json", type="json")
shareA_upload = st.file_uploader("あなた用 ShareA（PNG/JPG）", type=["png","jpg","jpeg"])

if st.button("復号して出席送信"):
    if not sid:
        st.error("学生ID を入力してください。")
        st.stop()
    if not meta_upload or not shareA_upload:
        st.error("metadata.json と ShareA をアップしてください。")
        st.stop()

    # metadata.json 読み込み
    meta = json.load(meta_upload)
    threshold = meta["threshold"]  # ✅ 教師と同一値
    class_id = meta["class_id"]
    base_hash = meta["base_hash"]

    # ShareA を二値化
    imgA = Image.open(shareA_upload).convert("L")
    arrA = img_to_binarr(imgA, threshold)

    # ✅ ShareB は metadata の base サイズに合わせる
    H, W = arrA.shape
    shareB_arr = gen_shareB_from_id(sid, (H, W))

    # 復号（XOR）
    recon = arrA ^ shareB_arr
    recon_img = binarr_to_image(recon)
    st.image(recon_img, caption="復号結果")

    # ✅ base_hash と一致確認（教師完全一致）
    buf = io.BytesIO()
    recon_img.save(buf, format="PNG")
    rhash = hashlib.sha256(buf.getvalue()).hexdigest()

    if rhash == base_hash:
        st.success("✅ 復号一致 → 出席を記録します")
        row = {"timestamp": datetime.datetime.now().isoformat(), "student_id": sid, "class_id": class_id}
        if os.path.exists(ATT_CSV):
            df = pd.read_csv(ATT_CSV)
            df.loc[len(df)] = row
        else:
            df = pd.DataFrame([row])
        df.to_csv(ATT_CSV, index=False)
        st.write("送信完了")
    else:
        st.error("❌ base と一致しません。ShareA が違う可能性があります。")
