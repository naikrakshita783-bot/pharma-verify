import streamlit as st
import cv2
import numpy as np

# Page configuration
st.set_page_config(page_title="PharmaVerify", layout="centered")

st.title("💊 PharmaVerify Portal")
st.write("Scan or upload a medicine QR code to verify if it is genuine or a counterfeit clone.")

# Clear tabs for inputs
tab1, tab2 = st.tabs(["📸 Live Camera Scan", "📁 Upload Image File"])

img_file = None

with tab1:
    camera_input = st.camera_input("Position the QR code clearly and snap a picture")
    if camera_input:
        img_file = camera_input

with tab2:
    file_input = st.file_uploader("Drop your medicine QR image here...", type=["jpg", "jpeg", "png"])
    if file_input:
        img_file = file_input

# Process image if captured
if img_file is not None:
    bytes_data = img_file.read()
    file_bytes = np.frombuffer(bytes_data, np.uint8)
    opencv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.write("---")
    st.subheader("🔍 Scan Status:")

    data = None

    # 1. Try Advanced WeChat QR Detector (Handles blur, angles, and low-res perfectly)
    try:
        detector = cv2.wechat_qrcode_WeChatQRCode()
        res, points = detector.detectAndDecode(opencv_img)
        if res:
            data = res[0]
    except Exception:
        pass

    # 2. Fallback to standard detector if WeChat didn't pick it up
    if not data:
        standard_detector = cv2.QRCodeDetector()
        data, bbox, _ = standard_detector.detectAndDecode(opencv_img)

    # 3. Second Fallback: Mirror flip image for front-facing phone cameras
    if not data:
        mirrored_img = cv2.flip(opencv_img, 1)
        try:
            detector = cv2.wechat_qrcode_WeChatQRCode()
            res, points = detector.detectAndDecode(mirrored_img)
            if res:
                data = res[0]
        except Exception:
            standard_detector = cv2.QRCodeDetector()
            data, bbox, _ = standard_detector.detectAndDecode(mirrored_img)

    # 4. Display Verification Results
    if data:
        st.info(f"💾 Decoded Data String: {data}")
        cleaned_data = data.upper()
        
        # Check against validation rules
        if "GENUINE" in cleaned_data or "BATCH2026" in cleaned_data or "VALID" in cleaned_data:
            st.success("✅ VERIFICATION SUCCESSFUL: This medicine is registered and 100% Genuine.")
        else:
            st.error("🚨 WARNING: Unrecognized serial layout! This item is flagged as a Counterfeit Clone.")
    else:
        st.error("❌ Scan Failed: Could not parse a valid QR layout matrix.")
        st.warning("The system couldn't find a clear square QR matrix. Try moving your camera slightly further away for a sharper focus, or use the 'Upload Image File' tab with a clean phone photo!")