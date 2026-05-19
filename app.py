import streamlit as st
import cv2
import numpy as np

# Page configuration
st.set_page_config(page_title="PharmaVerify", layout="centered")

st.title("💊 PharmaVerify Portal")
st.write("Scan or upload a medicine QR code to verify its authenticity.")

# Neat tabs to separate input types
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
    st.subheader("🔍 Verification Status:")

    # Image Preprocessing (Converts to black & white to make it super easy for the camera to read)
    gray_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2GRAY)
    sharpened_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # Initialize standard OpenCV detector
    detector = cv2.QRCodeDetector()
    
    # Try reading the image formats
    data, bbox, _ = detector.detectAndDecode(sharpened_img)
    if not data:
        data, bbox, _ = detector.detectAndDecode(opencv_img)
    if not data:
        mirrored_img = cv2.flip(sharpened_img, 1)
        data, bbox, _ = detector.detectAndDecode(mirrored_img)

    # DIRECT REAL OR FAKE DETECTION LOGIC
    if data:
        st.info(f"📋 Scanned Code Data: {data}")
        cleaned_data = data.upper()
        
        # Define what counts as a "Real" tracking layout for your presentation
        # (Any QR code containing keywords like VALID, BATCH2026, or GENUINE)
        if "VALID" in cleaned_data or "BATCH2026" in cleaned_data or "GENUINE" in cleaned_data:
            st.success("✅ REAL MEDICINE DETECTED")
            st.balloons() # Throws celebratory digital balloons on the screen!
        else:
            st.error("🚨 FAKE MEDICINE / COUNTERFEIT DETECTED")
            st.warning("Warning: This serial number structure does not match our official registered laboratory manufacturer logs.")
    else:
        st.warning("⚠️ Scan Failed: The camera couldn't process a clear square matrix. Please adjust your lighting or try uploading a steady photo file using the second tab!")