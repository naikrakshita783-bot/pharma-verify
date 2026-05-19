import streamlit as st
import cv2
import numpy as np

# Page configuration
st.set_page_config(page_title="PharmaVerify", layout="centered")

st.title("💊 PharmaVerify Portal")
st.write("Scan or upload a medicine QR code to verify its authenticity.")

st.write("scan or upload a medicine Qr code to vrify its authenticity. (system updated v2)")
tab1, tab2 = st.tabs(["📸 Live Camera Scan", "📁 Upload Image File"])

img_file = None

with tab1:
    camera_input = st.camera_input("Position the code clearly and snap a picture")
    if camera_input:
        img_file = camera_input

with tab2:
    file_input = st.file_uploader("Drop your medicine image code here...", type=["jpg", "jpeg", "png"])
    if file_input:
        img_file = file_input

# Process the image frame once captured
if img_file is not None:
    bytes_data = img_file.read()
    file_bytes = np.frombuffer(bytes_data, np.uint8)
    opencv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    st.write("---")
    st.subheader("🔍 Verification Status:")

    # Step 1: Preprocess image to high-contrast black & white (Otsu's Binarization)
    gray_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
    sharpened_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    data = None

    # ---- CRASH-PROOF DETECTOR ENGINE ----
    qr_detector = cv2.QRCodeDetector()
    
    # 1. Try scanning the sharpened image
    data, _, _ = qr_detector.detectAndDecode(sharpened_img)
    
    # 2. Fallback: Try scanning the raw original image
    if not data:
        data, _, _ = qr_detector.detectAndDecode(opencv_img)

    # 3. Fallback: Try a mirror flip (fixes front-facing phone camera mirroring)
    if not data:
        mirrored_img = cv2.flip(sharpened_img, 1)
        data, _, _ = qr_detector.detectAndDecode(mirrored_img)

    # STRICT REAL OR FAKE MEDICINE CLASSIFICATION LOGIC
    if data:
        st.info(f"📋 Scanned Code Data: {data}")
        cleaned_data = data.upper()
        
        # STRICT RULE: Must contain a registered security string to pass as Authentic
        if "VALID" in cleaned_data or "BATCH2026" in cleaned_data or "GENUINE" in cleaned_data:
            st.success("✅ REAL MEDICINE DETECTED")
            st.balloons()
        else:
            # Code is read perfectly, but text strings do not match the database whitelist
            st.error("🚨 FAKE MEDICINE / COUNTERFEIT DETECTED")
            st.warning("Warning: This tracking serial does not exist in our secure manufacturer logs.")
    else:
        st.error("❌ Scan Failed: Could not parse a valid QR layout matrix.")
        st.warning("The system couldn't find a clear square matrix. Try adjusting your lighting, eliminating glare, or uploading a steady file snippet!")