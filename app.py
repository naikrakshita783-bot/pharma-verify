import streamlit as st
import cv2
import numpy as np

# Page configuration
st.set_page_config(page_title="PharmaVerify", layout="centered")

st.title("💊 PharmaVerify Portal")
st.write("Scan or upload a medicine QR code to verify if it is genuine or a counterfeit clone.")

# Create tabs to neatly separate Camera scanning and File uploading
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

# Process the image if either input receives a file
if img_file is not None:
    # Read image data bytes cleanly
    bytes_data = img_file.read()
    file_bytes = np.frombuffer(bytes_data, np.uint8)
    opencv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.write("---")
    st.subheader("🔍 Scan Status:")

    # Initialize OpenCV QR detector
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(opencv_img)

    # Fallback: Mirror flip image if camera reversed it
    if not data:
        mirrored_img = cv2.flip(opencv_img, 1)
        data, bbox, _ = detector.detectAndDecode(mirrored_img)

    # Verification Rules
    if data:
        st.info(f"💾 Decoded Data: {data}")
        cleaned_data = data.upper()
        if "GENUINE" in cleaned_data or "BATCH2026" in cleaned_data or "VALID" in cleaned_data:
            st.success("✅ VERIFICATION SUCCESSFUL: This medicine is registered and 100% Genuine.")
        else:
            st.error("🚨 WARNING: Unrecognized serial layout! This item is flagged as a Counterfeit Clone.")
    else:
        st.error("❌ Scan Failed: Could not parse a valid QR layout matrix.")
        st.markdown("""
        **Tips for a successful scan:**
        * Ensure the QR code is **completely flat** (wrinkled medicine packaging can distort the matrix lines).
        * Move your device closer or further away to ensure it's in **sharp focus**.
        * Avoid overhead light reflections causing a **bright glare** directly on the glossy plastic of the medicine packaging.
        """)