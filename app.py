# student_app.py
import streamlit as st
from PIL import Image
import numpy as np
import io, os, hashlib, datetime, json, pandas as pd

st.set_page_config(page_title="👨‍🎓 学生用：出席 (復号して送信)", layout="centered")
st.title("👨‍🎓 学生用アプリ（ShareB 固定、授業の ShareA を取り込み復号→出席登録）")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
ATT_CSV = os.path.join(DATA_DIR, "attendance_records.csv")
CLASSES_JSON = os.path.join(DATA_DIR, "classes_index.json")

def stable_seed_from_str(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")

def img_to_binarr(img: Image.Image, threshold: int):
    g = img.convert("L")
    arr = np.array(g)
    return (arr < threshold).astype(np.uint8)

def binarr_to_image(binarr: np.ndarray):
    return Image.fromarray((255 * (1 - binarr)).astype(np.uint8))

def gen_shareB_from_id(sid: str, shape, threshold:int):
    # 同じロジックで学生側でも固定 shareB を再生成（教師が配布した PNG が無くとも動く）
    seed = stable_seed_from_str("B:"+sid)
    rng = np.random.default_rng(seed=seed)
    arr = rng.integers(0,2,size=shape, dtype=np.uint8)
    return arr

st.header("使い方（概要）")
st.write("1) 学生ID を入力 → 固定 ShareB は内部で同じ方法で生成します。 2) 教員がその授業で生成した **ShareA** をアップロードしてください（教員は授業で ShareA を配布する or ダウンロードボタンを渡す想定）。 3) 複合して base と一致すれば出席が記録されます。")

sid = st.text_input("学生ID（例: s001）")
st.write("---")
st.write("授業情報（教員が配布したフォルダ metadata.json をアップすると自動で検証できます）")
meta_upload = st.file_uploader("授業フォルダの metadata.json（教師が作成）をアップロード（任意）", type=["json"])
shareA_upload = st.file_uploader("教員が配布したあなた用 shareA 画像をアップロード（PNG）", type=["png","jpg","jpeg"])
base_upload = st.file_uploader("（検証用）教師の base.png をアップロード（任意: 教師が公開する場合）", type=["png","jpg","jpeg"])
threshold = st.slider("閾値（2値化）", 1, 254, 128, key="th_student")

if st.button("複合して出席を送信"):
    if not sid:
        st.error("学生ID を入力してください。")
    elif not shareA_upload:
        st.error("あなた用の ShareA（教員が作成）をアップしてください。")
    else:
        try:
            imgA = Image.open(shareA_upload).convert("L")
            arrA = img_to_binarr(imgA, threshold)
            # 生成する shareB は、教師と同じ形に合わせる必要あり
            shape = arrA.shape
            shareB_arr = gen_shareB_from_id(sid, shape, threshold)
            recon = arrA ^ shareB_arr
            recon_img = binarr_to_image(recon)
            st.image(recon_img, caption="複合結果（復号画像）", width=300)

            # 検証方法:
            # - 1) 教師提供の base.png がアップロードされていればハッシュ比較で照合
            # - 2) metadata.json がある場合は base_hash と比較
            verified = False
            class_id = None
            if meta_upload:
                meta = json.load(meta_upload)
                # meta must contain base_hash
                if "base_hash" in meta:
                    mhash = meta["base_hash"]
                    # compute hash of recon_img bytes
                    buf = io.BytesIO(); recon_img.save(buf, format="PNG")
                    rhash = hashlib.sha256(buf.getvalue()).hexdigest()
                    if rhash == mhash:
                        verified = True
                        class_id = meta.get("class_id", "unknown")
            if not verified and base_upload:
                # compare byte-hash of recon vs uploaded base image
                base_img = Image.open(base_upload).convert("L")
                base_arr = img_to_binarr(base_img, threshold)
                if base_arr.shape != recon.shape:
                    base_img = base_img.resize((recon.shape[1], recon.shape[0]))
                    base_arr = img_to_binarr(base_img, threshold)
                # Compare exact equality
                if np.array_equal(base_arr, recon):
                    verified = True
                    class_id = f"base_{datetime.date.today().isoformat()}"

            if verified:
                st.success("✅ 復号が一致しました。出席を記録します。")
                # append to CSV
                row = {"timestamp": datetime.datetime.now().isoformat(), "student_id": sid, "class_id": class_id}
                import pandas as pd
                if os.path.exists(ATT_CSV):
                    df = pd.read_csv(ATT_CSV)
                    df = df.append(row, ignore_index=True)
                else:
                    df = pd.DataFrame([row])
                df.to_csv(ATT_CSV, index=False)
                st.write("送信完了。教員アプリで反映されます。")
            else:
                st.error("復号画像が教師提供の base と一致しませんでした。ShareA が間違っているか、ShareB が別人のものです。")
        except Exception as e:
            st.error(f"エラー: {e}")
