import streamlit as st
import cv2
import numpy as np
from pyzbar.pydcode import decode
from PIL import Image

st.set_page_config(page_title="QR Fake Detector")
st.title("🔍 Fake QR Code Detector - CRYPTATHON")
st.write("Upload QR Code to check if Fake or Real")

uploaded = st.file_uploader("Upload QR Image", type=["png","jpg","jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded QR")
    
    # Decode QR
    decoded = decode(np.array(img))
    if decoded:
        data = decoded[0].data.decode()
        st.success(f"QR Data: {data}")
        
        # Simple Fake Check
        if "http" in data:
            if len(data) > 100 or "@" in data or data.count(".") > 3:
                st.error("⚠️ FAKE QR - Suspicious URL Detected!")
            else:
                st.success("✅ REAL QR - Looks Safe")
        else:
            st.info("QR contains text - Not URL")
    else:
        st.error("Could not read QR - Try clear image")
else:
    st.info("Please upload QR image")
