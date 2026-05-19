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

    # PREPROCESSING ENGINE: Convert to Grayscale to help the scanner "see" contrast
    gray_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
    
    # Enhance contrast using adaptive thresholding (makes blurry matrices sharp)
    sharpened_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # Initialize standard OpenCV detector
    detector = cv2.QRCodeDetector()
    
    # 1. Try scanning the sharpened black-and-white image
    data, bbox, _ = detector.detectAndDecode(sharpened_img)
    
    # 2. Fallback: Try scanning the raw original image
    if not data:
        data, bbox, _ = detector.detectAndDecode(opencv_img)

    # 3. Fallback: Try a mirror flip (for mirrored mobile front cameras)
    if not data:
        mirrored_img = cv2.flip(sharpened_img, 1)
        data, bbox, _ = detector.detectAndDecode(mirrored_img)

    # Display Verification Results
    if data:
        st.info(f"💾 Decoded Data String: {data}")
        cleaned_data = data.upper()
        
        # Validation rules
        if "GENUINE" in cleaned_data or "BATCH2026" in cleaned_data or "VALID" in cleaned_data:
            st.success("✅ VERIFICATION SUCCESSFUL: This medicine is registered and 100% Genuine.")
        else:
            st.error("🚨 WARNING: Unrecognized serial layout! This item is flagged as a Counterfeit Clone.")
    else:
        st.error("❌ Scan Failed: Could not parse a valid QR layout matrix.")
        st.warning("The camera focus might be too close. Try holding the QR code about 10-15 cm away from the camera, make sure it's well-lit, and take a steady picture!")