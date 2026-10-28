import streamlit as st
import cv2
import numpy as np
from PIL import Image
from urllib.parse import urlparse
import re

st.set_page_config(page_title="QR Shield - Fake QR Detector", page_icon="🛡️", layout="centered")

# --- CLEAN PROFESSIONAL CSS ---
st.markdown("""
<style>
    .stApp { background: #ffffff; }
    .main-title { font-size: 32px; font-weight: 700; color: #111; }
    .sub-text { color: #6B7280; font-size: 16px; }
    .report-box { background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; margin-top: 16px; }
    .safe-box { background: #ECFDF5; border: 1px solid #10B981; border-radius: 12px; padding: 20px; }
    .danger-box { background: #FEF2F2; border: 1px solid #EF4444; border-radius: 12px; padding: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛡️ QR Shield</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Upload any QR code image. Our system will analyze the link inside and tell you if it is safe or fake.</div>', unsafe_allow_html=True)
st.divider()

# --- ANALYSIS ENGINE ---
def analyze_link(url):
    issues = []
    score = 0
    parsed = urlparse(url)

    # Check 1: Protocol
    if parsed.scheme != "https":
        issues.append({"title": "Insecure Protocol", "desc": f"Link uses '{parsed.scheme or 'no protocol'}' instead of HTTPS. Your data can be intercepted."})
        score += 30
    
    # Check 2: @ Symbol
    if "@" in url:
        issues.append({"title": "Contains '@' Symbol", "desc": "Attackers use '@' to hide the real website. Example: google.com@fake.com looks like Google but goes to fake.com"})
        score += 40

    # Check 3: Subdomain count
    if url.count(".") > 3:
        issues.append({"title": "Too Many Subdomains", "desc": f"Found {url.count('.')} dots. Fake sites create long domains like secure.payment.google.com.fake-site.com to confuse you."})
        score += 20

    # Check 4: Shorteners
    if any(x in url.lower() for x in ["bit.ly", "tinyurl", "cutt.ly", "is.gd"]):
        issues.append({"title": "URL Shortener Detected", "desc": "Shortened links hide the real destination. You cannot see where it goes before clicking."})
        score += 30

    # Check 5: Suspicious keywords
    if any(x in url.lower() for x in ["free", "offer", "lottery", "verify", "urgent"]):
        issues.append({"title": "Suspicious Keywords", "desc": "Words like 'free', 'offer', 'verify' are commonly used in phishing to create urgency."})
        score += 20

    # Check 6: IP address
    if re.search(r"\d+\.\d+\.\d+\.\d+", url):
        issues.append({"title": "IP Address Used", "desc": "Legitimate sites use domain names (like google.com), not IP numbers. Using IP is highly suspicious."})
        score += 50

    # Check 7: Length
    if len(url) > 100:
        issues.append({"title": "Unusually Long URL", "desc": f"URL is {len(url)} characters long. Attackers make URLs long to hide malicious parts."})
        score += 10

    return min(score, 100), issues

# --- UPLOAD ---
uploaded = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded Image", width=320)
    
    # Decode QR
    cv_image = np.array(image.convert('RGB'))
    detector = cv2.QRCodeDetector()
    qr_data, _, _ = detector.detectAndDecode(cv_image)
    
    if not qr_data:
        st.error("We could not find a QR code in this image. Please upload a clear QR code image.")
    else:
        st.markdown("### Analysis Result")
        
        # Show decoded text
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.write("**Decoded Content:**")
        st.code(qr_data, language="text")
        st.markdown('</div>', unsafe_allow_html=True)
        
        risk_score, problems = analyze_link(qr_data)
        
        st.write("")
        st.progress(risk_score/100, text=f"Risk Score: {risk_score} / 100")
        
        if risk_score >= 50:
            st.markdown(f"""
            <div class="danger-box">
                <h3 style="color:#B91C1C; margin:0;">🚨 Fake QR Code Detected</h3>
                <p style="margin:8px 0 0 0; color:#7F1D1D;">This QR code is not safe. It contains {len(problems)} suspicious pattern(s). Do not visit this link.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.write("**Why is this marked as fake?**")
            for i, p in enumerate(problems, 1):
                st.markdown(f"""
                **{i}. {p['title']}**
                - {p['desc']}
                """)
            
            st.error("⛔ Action: Link has been blocked to protect you.")
            
        else:
            st.markdown(f"""
            <div class="safe-box">
                <h3 style="color:#065F46; margin:0;">✅ This QR Looks Safe</h3>
                <p style="margin:8px 0 0 0; color:#064E3B;">We checked {len(problems)} security parameters. No major threats found.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if problems:
                st.write("**Minor notes:**")
                for p in problems:
                    st.write(f"- {p['title']}: {p['desc']}")
            
            st.link_button("Open Link", qr_data, use_container_width=True)

else:
    st.info("Please upload a QR code image to start the analysis.")
    st.markdown("""
    **How to test:**
    - Upload a **Safe QR** (like https://google.com) -> Shows SAFE
    - Upload a **Fake QR** (like http://free-offer.bit.ly@fake-payment.com) -> Shows exactly WHY it is fake
    """)

st.divider()
st.caption("QR Shield • AI-powered QR fraud detection • Warns you BEFORE you visit")
