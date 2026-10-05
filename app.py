import streamlit as st
import cv2
import pytesseract
import numpy as np
from PIL import Image
import re


# =========================================================
# TESSERACT PATH
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Card Scan AI",
    page_icon="🪪",
    layout="centered"
)


# =========================================================
# TITLE
# =========================================================

st.title("🪪 Card Scan AI")
st.write("Upload your business card image to scan the details.")


# =========================================================
# UPLOAD CARD
# =========================================================

uploaded_file = st.file_uploader(
    "📤 Upload Business Card",
    type=["jpg", "jpeg", "png"]
)


# =========================================================
# FUNCTIONS
# =========================================================

def clean_line(line):
    """
    Clean OCR line.
    """
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def normalize_phone(phone_number):
    """
    Convert different phone formats into:
    +91 98765 43210
    """

    # Remove everything except digits
    digits = re.sub(r"\D", "", phone_number)

    # Indian number with country code
    if digits.startswith("91") and len(digits) >= 12:
        digits = digits[-10:]

    # Normal 10 digit number
    if len(digits) == 10 and digits[0] in "6789":
        return "+91 " + digits[:5] + " " + digits[5:]

    return None


def detect_phone(text):
    """
    Detect Indian phone numbers from OCR text.
    """

    # -----------------------------------------------------
    # Pattern 1
    # +91 98765 43210
    # +91-98765-43210
    # +91 9876543210
    # -----------------------------------------------------

    patterns = [

        r"\+?\s*91[\s\-\.]*"
        r"[6-9]\d{4}[\s\-\.]?\d{5}",

        # 10 digit number with optional spaces
        r"\b[6-9]\d{4}[\s\-\.]?\d{5}\b",

        # Digits separated by spaces
        r"\b[6-9]\d[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b"
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            phone = normalize_phone(match)

            if phone:
                return phone

    # -----------------------------------------------------
    # FALLBACK
    # Remove spaces and search 10 digit number
    # -----------------------------------------------------

    digits_only = re.sub(r"\D", "", text)

    # Search for Indian 10 digit number
    matches = re.findall(
        r"[6-9]\d{9}",
        digits_only
    )

    for match in matches:

        phone = normalize_phone(match)

        if phone:
            return phone

    return None


def detect_email(text):
    """
    Detect email addresses.
    """

    pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}"
    )

    matches = re.findall(
        pattern,
        text
    )

    result = []

    for email in matches:

        email = email.strip()

        if email not in result:
            result.append(email)

    return result


def detect_website(text):
    """
    Detect websites.
    """

    pattern = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"[A-Za-z0-9-]+\."
        r"[A-Za-z]{2,}"
        r"(?:/[^\s]*)?"
    )

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    websites = []

    for website in matches:

        website = website.rstrip(
            ".,;:)]}"
        )

        # Don't treat email domains as websites
        if "@" in website:
            continue

        if website not in websites:
            websites.append(website)

    return websites


def is_phone_line(line):
    """
    Check whether OCR line contains a phone number.
    """

    digits = re.sub(
        r"\D",
        "",
        line
    )

    if len(digits) >= 10:
        return True

    return False


def is_contact_line(line):
    """
    Check whether line contains email, website or phone.
    """

    lower_line = line.lower()

    if "@" in line:
        return True

    if "www." in lower_line:
        return True

    if "http://" in lower_line:
        return True

    if "https://" in lower_line:
        return True

    if is_phone_line(line):
        return True

    return False


# =========================================================
# WHEN IMAGE IS UPLOADED
# =========================================================

if uploaded_file is not None:

    # =====================================================
    # READ IMAGE
    # =====================================================

    image = Image.open(uploaded_file).convert("RGB")

    img = np.array(image)


    # =====================================================
    # DISPLAY IMAGE
    # =====================================================

    st.image(
        image,
        caption="Uploaded Business Card",
        use_container_width=True
    )


    # =====================================================
    # CONVERT TO GRAYSCALE
    # =====================================================

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_RGB2GRAY
    )


    # =====================================================
    # RESIZE IMAGE
    # =====================================================

    gray = cv2.resize(
        gray,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )


    # =====================================================
    # IMAGE PREPROCESSING
    # =====================================================

    # Remove noise
    blurred = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )


    # OTSU threshold
    processed_otsu = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]


    # Adaptive threshold
    processed_adaptive = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )


    # =====================================================
    # GENERAL OCR
    # =====================================================

    text1 = pytesseract.image_to_string(
        processed_otsu,
        config="--oem 3 --psm 6"
    )

    text2 = pytesseract.image_to_string(
        processed_otsu,
        config="--oem 3 --psm 11"
    )

    text3 = pytesseract.image_to_string(
        processed_adaptive,
        config="--oem 3 --psm 11"
    )

    # Also OCR original resized grayscale
    text4 = pytesseract.image_to_string(
        gray,
        config="--oem 3 --psm 6"
    )


    # =====================================================
    # COMBINE OCR RESULTS
    # =====================================================

    text = (
        text1
        + "\n"
        + text2
        + "\n"
        + text3
        + "\n"
        + text4
    )


    # =====================================================
    # CLEAN OCR LINES
    # =====================================================

    lines = []

    for line in text.split("\n"):

        line = clean_line(line)

        if line:

            if line not in lines:
                lines.append(line)


    # =====================================================
    # PHONE-SPECIFIC OCR
    # =====================================================

    # This is the important fix.
    # Tesseract is instructed to look mainly for numbers.

    phone_config = (
        "--oem 3 --psm 11 "
        "-c tessedit_char_whitelist=0123456789+()- "
    )

    phone_text1 = pytesseract.image_to_string(
        gray,
        config=phone_config
    )

    phone_text2 = pytesseract.image_to_string(
        processed_otsu,
        config=phone_config
    )

    phone_text3 = pytesseract.image_to_string(
        processed_adaptive,
        config=phone_config
    )


    phone_ocr_text = (
        phone_text1
        + "\n"
        + phone_text2
        + "\n"
        + phone_text3
    )


    # =====================================================
    # PHONE DETECTION
    # =====================================================

    phone = detect_phone(phone_ocr_text)

    # If phone OCR fails, try complete OCR text
    if not phone:

        phone = detect_phone(text)


    # =====================================================
    # EMAIL DETECTION
    # =====================================================

    email = detect_email(text)


    # =====================================================
    # WEBSITE DETECTION
    # =====================================================

    website = detect_website(text)


    # =====================================================
    # REMOVE CONTACT INFORMATION
    # =====================================================

    remaining = []

    for line in lines:

        if is_contact_line(line):
            continue

        remaining.append(line)


    # =====================================================
    # REMOVE VERY SHORT OCR NOISE
    # =====================================================

    cleaned_remaining = []

    for line in remaining:

        # Ignore single-character noise
        if len(line.strip()) <= 1:
            continue

        cleaned_remaining.append(line)

    remaining = cleaned_remaining


    # =====================================================
    # NAME
    # =====================================================

    name = ""

    if len(remaining) >= 1:
        name = remaining[0]


    # =====================================================
    # ROLE
    # =====================================================

    role = ""

    role_keywords = [
        "developer",
        "designer",
        "engineer",
        "manager",
        "director",
        "founder",
        "developer",
        "consultant",
        "analyst",
        "architect",
        "student",
        "officer",
        "executive",
        "specialist",
        "lead",
        "intern",
        "ceo",
        "cto",
        "coo"
    ]


    for line in remaining:

        lower_line = line.lower()

        for keyword in role_keywords:

            if keyword in lower_line:

                role = line
                break

        if role:
            break


    # =====================================================
    # COMPANY
    # =====================================================

    company = ""

    company_keywords = [
        "solutions",
        "solution",
        "technologies",
        "technology",
        "tech",
        "systems",
        "software",
        "company",
        "labs",
        "laboratories",
        "consulting",
        "services",
        "industries",
        "group",
        "corp",
        "corporation",
        "pvt",
        "ltd",
        "limited"
    ]


    for line in remaining:

        lower_line = line.lower()

        for keyword in company_keywords:

            if keyword in lower_line:

                # Don't use role as company
                if line != role:

                    company = line

                break

        if company:
            break


    # =====================================================
    # COMPANY FALLBACK
    # =====================================================

    # If company wasn't detected through keywords,
    # look for a line after the role.

    if not company:

        try:

            role_index = remaining.index(role)

            if role_index + 1 < len(remaining):

                candidate = remaining[role_index + 1]

                # Don't use address as company
                candidate_lower = candidate.lower()

                address_words = [
                    "road",
                    "street",
                    "nagar",
                    "chennai",
                    "tamil",
                    "no."
                ]

                if not any(
                    word in candidate_lower
                    for word in address_words
                ):

                    company = candidate

        except ValueError:

            pass


    # =====================================================
    # ADDRESS
    # =====================================================

    address_lines = []

    address_keywords = [
        "no.",
        "street",
        "road",
        "nagar",
        "chennai",
        "tamil nadu",
        "india",
        "avenue",
        "salai",
        "main road"
    ]


    for line in remaining:

        lower_line = line.lower()

        # Check address keywords
        has_address_keyword = any(
            keyword in lower_line
            for keyword in address_keywords
        )

        # Check PIN code
        has_pincode = re.search(
            r"\b\d{6}\b",
            line
        )

        if has_address_keyword or has_pincode:

            if line not in address_lines:

                address_lines.append(line)


    address = " ".join(address_lines)


    # =====================================================
    # CLEAN NAME
    # =====================================================

    if name == role:
        role = ""

    if name == company:
        company = ""


    # =====================================================
    # CLEAN COMPANY
    # =====================================================

    if company == role:
        company = ""


    # =====================================================
    # SHOW SUCCESS
    # =====================================================

    st.success("✅ Card scanned successfully!")


    # =====================================================
    # CARD DETAILS
    # =====================================================

    st.subheader("📋 Card Details")


    # =====================================================
    # NAME
    # =====================================================

    st.markdown("### 👤 Name")

    st.info(
        name if name else "Not detected"
    )


    # =====================================================
    # PHONE
    # =====================================================

    st.markdown("### 📱 Phone")

    st.info(
        phone if phone else "Not detected"
    )


    # =====================================================
    # ROLE
    # =====================================================

    st.markdown("### 💼 Role")

    st.info(
        role if role else "Not detected"
    )


    # =====================================================
    # EMAIL
    # =====================================================

    st.markdown("### 📧 Email")

    st.info(
        email[0] if email else "Not detected"
    )


    # =====================================================
    # COMPANY
    # =====================================================

    st.markdown("### 🏢 Company")

    st.info(
        company if company else "Not detected"
    )


    # =====================================================
    # WEBSITE
    # =====================================================

    st.markdown("### 🌐 Website")

    st.info(
        website[0] if website else "Not detected"
    )


    # =====================================================
    # ADDRESS
    # =====================================================

    st.markdown("### 📍 Address")

    st.info(
        address if address else "Not detected"
    )


    # =====================================================
    # OPTIONAL: DEBUG OCR
    # =====================================================

    with st.expander("🔍 View OCR Text"):

        st.text(text)

    with st.expander("📱 View Phone OCR"):

        st.text(phone_ocr_text)