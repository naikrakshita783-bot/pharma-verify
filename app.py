import streamlit as st
import cv2
import numpy as np
import re

# Page configurations for the application interface
st.set_page_config(page_title="PharmaVerify - Anti-Counterfeit Portal", page_icon="💊", layout="centered")

# Custom UI styling
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💊 PharmaVerify Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Public Verification Engine for Medicine Serialization Integrity</div>', unsafe_allow_html=True)

# --- Simulated Central Manufacturer Database ---
if 'central_registry' not in st.session_state:
    st.session_state.central_registry = {
        "08901107000028": {
            "X7R9W2M4K1": {"name": "Amoxicillin 500mg Capsule", "batch": "AMX2026", "expiry": "281231", "status": "ACTIVE"},
            "L3P5V8N2M9": {"name": "Lipitor 10mg Tablet", "batch": "LPT9941", "expiry": "270518", "status": "DISPENSED"},
        }
    }

def parse_gs1_string(raw_string):
    """Parses structural Application Identifiers from a standardized GS1 data stream."""
    parsed = {}
    gtin = re.search(r'\(01\)(\d{14})', raw_string)
    serial = re.search(r'\(21\)([A-Z0-9]{10,20})', raw_string)
    batch = re.search(r'\(10\)([A-Z0-9]+)', raw_string)
    expiry = re.search(r'\(17\)(\d{6})', raw_string)

    if gtin: parsed['gtin'] = gtin.group(1)
    if serial: parsed['serial'] = serial.group(1)
    if batch: parsed['batch'] = batch.group(1)
    if expiry: parsed['expiry'] = expiry.group(1)
    return parsed

# --- Interactive User Selection Panel ---
mode = st.radio("Select Input Hardware Layer:", ["📷 Access Live Camera Device", "📤 Upload Image File"])
decoded_text = None

if mode == "📷 Access Live Camera Device":
    camera_img = st.camera_input("Center the medicine barcode inside your camera frame:")
    if camera_img is not None:
        file_bytes = np.asarray(bytearray(camera_img.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        
        # Computer Vision Detection Pass
        detector = cv2.QRCodeDetector()
        decoded_text, _, _ = detector.detectAndDecode(frame)
else:
    uploaded_file = st.file_uploader("Upload crisp image of the barcode...", type=["png", "jpg", "jpeg"])
    
    # PRESENTATION ASSISTANT: Simulation Injection Buttons
    st.markdown("---")
    st.caption("⚙️ **Presentation Mock Control Panel** (Use these to instantly simulate scans without a camera):")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Simulate Genuine Scan"):
            decoded_text = "(01)08901107000028(21)X7R9W2M4K1(10)AMX2026(17)281231"
    with col2:
        if st.button("🚨 Simulate Counterfeit Clone Scan"):
            decoded_text = "(01)08901107000028(21)L3P5V8N2M9(10)LPT9941(17)270518"

    if uploaded_file is not None and not decoded_text:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)
        
        detector = cv2.QRCodeDetector()
        decoded_text, _, _ = detector.detectAndDecode(frame)

# --- Analysis Execution Layer ---
if decoded_text:
    st.markdown("---")
    st.subheader("🔍 Analytical Evaluation Logs")
    st.text_area("Extracted Code Payload:", value=decoded_text, height=70, disabled=True)
    
    parsed_metadata = parse_gs1_string(decoded_text)
    
    # 1. Structural Conformance Verification
    if not all(k in parsed_metadata for k in ['gtin', 'serial', 'batch', 'expiry']):
        st.error("❌ VERDICT: INVALID CRYPTOGRAPHIC FORMAT\n\nThe parsed visual signature fails to meet regulatory serialization layout standards.")
    else:
        gtin = parsed_metadata['gtin']
        serial = parsed_metadata['serial']
        
        # 2. Database Lineage Authentication
        registry = st.session_state.central_registry
        if gtin in registry:
            if serial in registry[gtin]:
                record = registry[gtin][serial]
                
                # 3. Lifecycle State Check (Anti-Cloning Rule)
                if record['status'] == "DISPENSED":
                    st.error(f"🚨 VERDICT: FRAUD SUSPECT - PACKAGING CLONE DETECTED\n\nWarning! This unique serial fingerprint ({serial}) was already scanned and marked as sold at a pharmacy distribution point. This packaging is a counterfeit duplication of a real box.")
                elif record['status'] == "ACTIVE":
                    st.balloons()
                    st.success(f"✅ VERDICT: AUTHENTIC MEDICATION VERIFIED\n\nProduct Profile: {record['name']}\nBatch Code: {record['batch']} | Expiry Log: {record['expiry']}\n\nLineage Check Passed: This product maps perfectly to legitimate factory outputs.")
                    
                    # Transition lifecycle state to prevent reuse fraud
                    st.session_state.central_registry[gtin][serial]['status'] = "DISPENSED"
                    st.caption("🔒 Security Action: This unique serial is now marked as 'DISPENSED' to prevent duplicate printing clones.")
            else:
                st.error("❌ VERDICT: ILLEGITIMATE PRODUCT - FAKE SERIAL ID\n\nThis specific item identity key does not exist in the manufacturer database records.")
        else:
            st.error("❌ VERDICT: UNREGISTERED MANUFACTURER\n\nThe embedded Global Trade Item Number code is unrecognized by central drug controllers.")

elif mode == "📤 Upload Image File" and uploaded_file is not None:
    st.error("❌ Optical verification failure. The algorithm cannot isolate a clean binary image block. Adjust focus or lighting, or use the Mock Panel shortcuts above.")