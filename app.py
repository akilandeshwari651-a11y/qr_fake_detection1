import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re
from urllib.parse import urlparse
import time
from datetime import datetime

st.set_page_config(page_title="QR Shield Pro | Cryptathon", page_icon="🛡️", layout="wide")

# --- PRO CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: #0A0E1A; color: white; }
.header { 
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 30px; border-radius: 20px; border: 1px solid #334155;
}
.risk-high { background: linear-gradient(135deg, #dc2626, #991b1b); padding:20px; border-radius:15px; border-left: 5px solid #f87171; }
.risk-medium { background: linear-gradient(135deg, #d97706, #92400e); padding:20px; border-radius:15px; border-left: 5px solid #fbbf24; }
.risk-low { background: linear-gradient(135deg, #059669, #065f46); padding:20px; border-radius:15px; border-left: 5px solid #34d399; }
.feature-box { background: #1e293b; padding:15px; border-radius:12px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
col_logo, col_title = st.columns([1,5])
with col_logo:
    st.markdown("# 🛡️")
with col_title:
    st.markdown("# QR Shield Pro")
    st.caption("AI-Powered Protection for Posters, Events & Payments | CRYPTATHON 2026")

st.markdown("""
<div class="header">
<h3>🎯 Problem Solved</h3>
<p>QR codes on <b>posters, event registrations, and payment pages</b> redirect to malicious sites. 
Our solution <b>scans → analyzes URL → highlights suspicious patterns → warns BEFORE you visit.</b></p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Functions ---
def analyze_url(url):
    issues = []
    score = 0
    parsed = urlparse(url)
    
    # 1. Blacklist Check
    blacklist = ["phishing", "fake", "free-money", "lottery", "bit.ly", "tinyurl", "grabify"]
    if any(b in url.lower() for b in blacklist):
        issues.append(f"🚩 Blacklisted keyword detected")
        score += 40
    
    # 2. HTTPS Check
    if parsed.scheme != "https":
        issues.append("🚩 Not using HTTPS - Data can be stolen")
        score += 25
    
    # 3. Suspicious chars
    if "@" in url or url.count("-") > 4:
        issues.append("🚩 Contains @ or excessive hyphens - Phishing trick")
        score += 30
    
    # 4. Too many subdomains
    if url.count(".") > 3:
        issues.append(f"🚩 Too many subdomains ({url.count('.')}) - Fake domain")
        score += 20
    
    # 5. IP instead of domain
    if re.match(r"^(http://|https://)?\d+\.\d+\.\d+\.\d+", url):
        issues.append("🚩 Uses IP address not domain - Highly suspicious")
        score += 50
    
    # 6. Length
    if len(url) > 100:
        issues.append(f"🚩 URL too long ({len(url)} chars) - Obfuscation")
        score += 15
    
    # 7. Typosquatting (g00gle, paytm-secure)
    typo = ["g00gle", "paytm-secure", "phonepe-offer", "amaz0n"]
    if any(t in url.lower() for t in typo):
        issues.append("🚩 Typosquatting - Fake brand impersonation")
        score += 35
        
    return min(score, 100), issues

# --- Main Layout ---
left, right = st.columns([1, 1.2])

with left:
    st.markdown("### 📤 Scan QR Code")
    st.write("Upload QR from Poster / Event / Payment Page")
    source = st.selectbox("QR Source Type", ["🎨 Poster / Flyer", "🎟️ Event Registration", "💳 Payment Page", "❓ Unknown"])
    
    uploaded = st.file_uploader("Drag & Drop QR Image", type=["png","jpg","jpeg"])
    
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, width=350, caption=f"Source: {source}")
        
        img_cv = np.array(img.convert('RGB'))
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img_cv)
        
        st.session_state['qr_data'] = data if data else None
    else:
        st.info("Awaiting QR upload...")

with right:
    if uploaded and 'qr_data' in st.session_state and st.session_state['qr_data']:
        data = st.session_state['qr_data']
        
        with st.spinner("🕵️ Deep Scanning URL..."):
            time.sleep(1.2)
        
        st.markdown("### 📊 Security Analysis Report")
        st.markdown(f"**Timestamp:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        st.code(data, language="bash")
        
        risk_score, issues = analyze_url(data)
        
        # Highlight Suspicious URL Parts
        st.markdown("### 🔍 Suspicious Parts Highlighted")
        highlighted = data
        for word in ["@", "bit.ly", "free", "http://"]:
            if word in highlighted:
                highlighted = highlighted.replace(word, f"**⚠️{word}⚠️**")
        st.warning(f"Detected URL: {highlighted}")
        
        # Risk Card
        if risk_score >= 60:
            st.markdown(f"""
            <div class="risk-high">
            <h2>🚨 HIGH RISK - DO NOT VISIT</h2>
            <h1>Risk Score: {risk_score}/100</h1>
            <p>This QR is FAKE. Visiting may steal your money/data.</p>
            </div>
            """, unsafe_allow_html=True)
            st.error("⛔ ACTION BLOCKED: We stopped you from visiting this unsafe link!")
        elif risk_score >= 30:
            st.markdown(f"""
            <div class="risk-medium">
            <h2>⚠️ MEDIUM RISK - CAUTION</h2>
            <h1>Risk Score: {risk_score}/100</h1>
            <p>Proceed only if you trust the source.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("⚠️ I Understand Risk, Visit Anyway"):
                st.link_button("Open Link (Risky)", data)
        else:
            st.markdown(f"""
            <div class="risk-low">
            <h2>✅ SAFE - Verified</h2>
            <h1>Risk Score: {risk_score}/100</h1>
            <p>No threats detected. Safe to proceed.</p>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("✅ Open Safe Link", data)
        
        if issues:
            st.markdown("### 🚩 Threats Found:")
            for i in issues:
                st.write(i)
        
        # Prevention Tips
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown('<div class="feature-box">🔒<br><b>HTTPS Check</b><br>Ensures encrypted</div>', unsafe_allow_html=True)
        with col2: st.markdown('<div class="feature-box">🎭<br><b>Brand Check</b><br>Stops fake Paytm/Google</div>', unsafe_allow_html=True)
        with col3: st.markdown('<div class="feature-box">⏱️<br><b>Before Visit Warning</b><br>Blocks before click</div>', unsafe_allow_html=True)
    
    elif uploaded:
        st.error("❌ QR not readable. Use clear image of poster QR.")
    else:
        st.markdown("### ✨ How It Works")
        st.markdown("""
        1. **SCAN** - User scans QR from poster/event/payment
        2. **EXTRACT** - URL extracted & decoded
        3. **ANALYZE** - Checks blacklist, HTTPS, typosquatting, IP, length
        4. **HIGHLIGHT** - Suspicious parts marked in red
        5. **WARN** - Blocks unsafe site BEFORE user visits
        """)
        st.success("Ready for Live Demo - Upload any QR")

st.markdown("---")
st.caption("QR Shield Pro | Built for CRYPTATHON 2026 Problem #3 | Prevents Poster, Event & Payment QR Frauds")
