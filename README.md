# Card Scan AI

Card Scan AI is an OCR-based business card scanning application that automatically extracts and organizes contact information from business card images.

The application uses image preprocessing and Tesseract OCR to identify important details such as name, phone number, email, role, company, website, and address.

---

## Overview

Manually entering contact information from business cards can be time-consuming and error-prone.

Card Scan AI simplifies this process by allowing users to upload a business card image. The system processes the image, extracts the text using OCR, identifies relevant information, and presents the results in a structured format.

---

## Key Features

- Business card image upload
- OCR-based text extraction
- Image preprocessing for improved recognition
- Name detection
- Phone number detection
- Email address extraction
- Website detection
- Role identification
- Company identification
- Address extraction
- Indian phone number format support
- Clean Streamlit-based interface
- Multiple OCR processing methods for better accuracy

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| OpenCV | Image preprocessing |
| Tesseract OCR | Optical Character Recognition |
| Pytesseract | Python-Tesseract integration |
| NumPy | Image processing |
| Pillow | Image handling |
| Regular Expressions | Information extraction |

---

## System Workflow

```text
Business Card Image
        |
        v
Image Upload
        |
        v
Image Preprocessing
        |
        +-------------------+
        |                   |
        v                   v
   Grayscale          Image Resizing
        |                   |
        +---------+---------+
                  |
                  v
            Thresholding
                  |
                  v
              OCR Engine
                  |
                  v
           Text Extraction
                  |
                  v
       Information Detection
                  |
        +---------+----------+
        |         |          |
        v         v          v
      Name      Phone      Email
        |         |          |
        +---------+----------+
                  |
        +---------+----------+
        |         |          |
        v         v          v
     Company   Website    Address
                  |
                  v
          Structured Output
                  |
                  v
          Streamlit Interface
