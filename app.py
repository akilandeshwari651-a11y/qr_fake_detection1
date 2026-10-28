import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="QR Fake Detector", page_icon="🔍")
st.title("🔍 Fake QR Code Detector - CRYPTATHON")
st.write("Upload QR Code to check Fake or Real")

uploaded = st.file_uploader("Upload QR Image", type=["png","jpg","jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded QR", use_column_width=True)
    
    # Convert to OpenCV
    img_cv = np.array(img.convert('RGB'))
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img_cv)
    
    if data:
        st.success(f"QR Data: {data}")
        # Fake check logic
        if "http" in data.lower():
            suspicious = ["@", "bit.ly", "tinyurl", "free", "login", "verify"]
            is_fake = len(data) > 100 or data.count(".") > 3 or any(x in data.lower() for x in suspicious)
            if is_fake:
                st.error("⚠️ FAKE QR - Suspicious URL!")
                st.write("Reason: Too long / many dots / suspicious keyword")
            else:
                st.success("✅ REAL QR - Looks Safe")
        else:
            st.info("QR contains plain text")
    else:
        st.error("Could not read QR - Upload clear QR image")
else:
    st.info("Please upload a QR image to test")
    st.write("Try with google.com QR for testing")
