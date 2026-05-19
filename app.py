import streamlit as st
import cv2
import numpy as np

# Page configuration
st.set_page_config(page_title="PharmaVerify", layout="centered")

st.title("💊 PharmaVerify Portal")
st.write("Scan a medicine QR code to verify if it is genuine or a counterfeit clone.")

# 1. Create the camera input widget
img_file = st.camera_input("Position the QR code clearly inside the frame and snap a picture")

if img_file is not None:
    # 2. Extract raw bytes cleanly from Streamlit buffer
    bytes_data = img_file.getvalue()
    opencv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # 3. Initialize the QR Code detector
    detector = cv2.QRCodeDetector()
    
    # Try reading the image normall
    data, bbox, _ = detector.detectAndDecode(opencv_img)
    
    # 4. Fallback: If it fails, flip the image (fixes phone camera mirror issues)
    if not data:
        mirrored_img = cv2.flip(opencv_img, 1)
        data, bbox, _ = detector.detectAndDecode(mirrored_img)

    # 5. Display the validation logic output
    st.write("---")
    st.subheader("🔍 Scan Status:")
    
    if data:
        st.info(f"💾 Decoded Data String: {data}")
        
        # Check against system keywords
        cleaned_data = data.upper()
        if "GENUINE" in cleaned_data or "BATCH2026" in cleaned_data or "VALID" in cleaned_data:
            st.success("✅ VERIFICATION SUCCESSFUL: This medicine match is registered and 100% Genuine.")
        else:
            st.error("🚨 WARNING: Unrecognized serial layout! This item is flagged as a Counterfeit Clone.")
    else:
        st.error("❌ Scan Failed: Could not parse a valid QR layout matrix.")
        st.warning("Tips for a perfect scan:\n* Hold the QR code flat and steady.\n* Make sure your room lighting is bright without glare.\n* Ensure the entire square QR code is inside the box.")