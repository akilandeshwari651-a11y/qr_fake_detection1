import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re
import urllib.parse
import tldextract

# --- SECURITY CHECK LOGIC ---
SUS_TLDS = {'.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.zip', '.mov', '.work'}
SHORTENERS = {'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly', 'is.gd', 'buff.ly', 'cutt.ly'}
PHISH_WORDS = ['login', 'verify', 'secure', 'account', 'update', 'banking', 'wallet', 'password', 'kyc', 'free']
BRANDS = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'facebook', 'instagram', 'sbi', 'hdfc', 'phonepe', 'paytm']

def decode_qr(image):
    # No pyzbar - only OpenCV, so no 404 error
    img = np.array(image.convert('RGB'))
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)
    if data:
        return data
    return None

def analyze_url(url):
    findings = []
    score = 0
    
    # Clean URL
    clean_url = url if '://' in url else 'http://' + url
    parsed = urllib.parse.urlparse(clean_url)
    domain = parsed.netloc.lower().split(':')[0]
    if not domain:
        domain = parsed.path.split('/')[0].lower()
    
    ext = tldextract.extract(domain)
    full_path = (parsed.path + parsed.query).lower()

    if parsed.scheme == 'http':
        findings.append(("⚠️ No HTTPS", "Data not encrypted - Risky")); score += 15
    
    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', domain):
        findings.append(("🚨 IP Address Used", "Scammers use IP instead of name")); score += 40

    if f".{ext.suffix}" in SUS_TLDS:
        findings.append((f"⚠️ Risky Domain .{ext.suffix}", "Often used for fake sites")); score += 25

    if any(s in domain for s in SHORTENERS):
        findings.append(("⚠️ Short Link", "Real site is hidden")); score += 15

    for brand in BRANDS:
        if brand in domain and ext.domain != brand:
            findings.append((f"🚨 Fake {brand} Site?", "Brand name copied - Typosquatting")); score += 35
            break

    if domain.count('.') > 3 or domain.count('-') > 4:
        findings.append(("⚠️ Weird Characters", "Too many dots/dashes")); score += 10

    hits = [k for k in PHISH_WORDS if k in full_path or k in domain]
    if hits:
        findings.append((f"⚠️ Suspicious Words: {', '.join(hits)}", "Phishing trick")); score += 10

    score = min(score, 100)
    
    if score >= 60:
        verdict, color = "DANGEROUS 🔴 DO NOT OPEN", "#ff4b4b"
    elif score >= 30:
        verdict, color = "SUSPICIOUS 🟠 BE CAREFUL", "#ffa500"
    else:
        verdict, color = "LIKELY SAFE 🟢", "#00cc66"
        
    return {"url": url, "domain": domain, "score": score, "verdict": verdict, "color": color, "findings": findings}

# --- UI ---
st.set_page_config(page_title="QR Fake Detection", page_icon="🛡️", layout="centered")

st.title("🛡️ QR Fake Detection")
st.markdown("**CRYPTATHON'26 | Team CyberFort | SRM TRP**")
st.divider()

st.subheader("1. Upload QR Code to Scan")
uploaded = st.file_uploader("Upload QR Image", type=["png","jpg","jpeg","webp"])
cam = st.camera_input("Or Scan with Camera")

image = None
if uploaded:
    image = Image.open(uploaded)
elif cam:
    image = Image.open(cam)

if image:
    st.image(image, use_container_width=True)
    with st.spinner("Scanning QR..."):
        decoded = decode_qr(image)
    
    if not decoded:
        st.error("❌ No QR found. Please upload clear QR image.")
    else:
        st.success(f"Found Link: {decoded}")
        report = analyze_url(decoded)
        
        st.markdown(f"""
        <div style="border-left:6px solid {report['color']}; padding:15px; background:#f8f9fa; border-radius:10px;">
            <h3 style="color:{report['color']}; margin:0;">{report['verdict']}</h3>
            <p style="margin:5px 0;">Risk Score: <b>{report['score']}/100</b> | Domain: {report['domain']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("### 🔍 Security Analysis:")
        for title, desc in report['findings']:
            st.write(f"**{title}** - {desc}")
        
        if not report['findings']:
            st.write("✅ No major risks found")

        st.divider()
        if report['score'] >= 30:
            st.warning("⚠️ This link looks risky! Are you sure?")
            if st.button("Proceed Anyway (At Your Risk)"):
                st.markdown(f"[Click to open link]({report['url']})")
        else:
            st.link_button("✅ Open Link - Safe", report['url'])

st.divider()
st.subheader("2. Check Any Link Without QR")
test_url = st.text_input("Paste any URL here to check", placeholder="https://example.com/login")
if test_url:
    r = analyze_url(test_url)
    st.metric(label=r['verdict'], value=f"{r['score']}/100 Risk", delta=r['domain'])
    for t,d in r['findings']:
        st.write(f"{t} - {d}")

st.caption("Built for CRYPTATHON'26 - 11 point fake detection engine")
