import streamlit as st
import cv2
import numpy as np
from qreader import QReader

# Page configuration
st.set_page_config(page_title="PharmaVerify", layout="centered")

st.title("💊 PharmaVerify Portal")
st.write("Scan or upload a medicine QR code to verify if it is genuine or a counterfeit clone.")

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
    st.subheader("🔍 Scan Status:")

    # Initialize the pure-python QReader engine
    qreader_engine = QReader()
    
    # QReader expects an RGB image layout, so convert it from BGR
    rgb_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2RGB)
    
    # Read the QR text matrix data
    data = qreader_engine.detect_and_decode(image=rgb_img)

    # Extract the first decoded string if a list is returned
    decoded_text = None
    if data and len(data) > 0 and data[0] is not None:
        decoded_text = data[0]

    # Fallback: Try a horizontal flip if front camera mirrored it
    if not decoded_text:
        mirrored_img = cv2.flip(rgb_img, 1)
        mirror_data = qreader_engine.detect_and_decode(image=mirrored_img)
        if mirror_data and len(mirror_data) > 0 and mirror_data[0] is not None:
            decoded_text = mirror_data[0]

    # Display Verification Results
    if decoded_text:
        st.info(f"💾 Decoded Data String: {decoded_text}")
        cleaned_data = decoded_text.upper()
        
        # Validation rules matching your criteria
        if "GENUINE" in cleaned_data or "BATCH2026" in cleaned_data or "VALID" in cleaned_data:
            st.success("✅ VERIFICATION SUCCESSFUL: This medicine is registered and 100% Genuine.")
        else:
            st.error("🚨 WARNING: Unrecognized serial layout! This item is flagged as a Counterfeit Clone.")
    else:
        st.error("❌ Scan Failed: Could not parse a valid QR layout matrix.")
        st.warning("The system couldn't find a clear square matrix. Try using the 'Upload Image File' tab with a clear photo taken directly from your main mobile camera app!")