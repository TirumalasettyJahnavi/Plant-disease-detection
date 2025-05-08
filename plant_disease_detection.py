import cv2
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from skimage.metrics import structural_similarity as ssim

# Function to send email notifications
def send_email_notification(recipient_email, subject, body):
    """Send an email notification using Gmail SMTP."""
    sender_email = # Replace with your Gmail
    sender_password =  # Use App Password

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("✅ Email sent successfully.")

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check your App Password and security settings.")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Function to load images from CSV
def load_images_from_csv(csv_file, images_folder):
    """Load images and labels from CSV file."""
    images_data = []
    try:
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")

        df = pd.read_csv(csv_file)

        if "image_id" not in df.columns or "label" not in df.columns:
            raise ValueError("CSV must contain 'image_id' and 'label' columns.")

        available_files = [f.lower() for f in os.listdir(images_folder)]

        for _, row in df.iterrows():
            image_id_base = os.path.splitext(row["image_id"])[0].lower()
            label = row["label"]
            fertilizer = row.get("fertilizer", "N/A")  # Default to "N/A" if missing

            for ext in [".jpg", ".jpeg", ".png"]:
                file_name = f"{image_id_base}{ext}"
                if file_name in available_files:
                    image_path = os.path.join(images_folder, file_name)
                    image = cv2.imread(image_path)
                    if image is not None:
                        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        images_data.append((gray_image, label, fertilizer))
                    break

    except Exception as e:
        print(f"❌ Error loading images: {e}")
    return images_data

# Function to compare images using SSIM
def compare_images(image1, image2, threshold=0.8):
    """Compare two images using SSIM."""
    try:
        resized_image = cv2.resize(image1, (image2.shape[1], image2.shape[0]))
        score, _ = ssim(resized_image, image2, full=True)
        return score >= threshold, score
    except Exception as e:
        print(f"❌ Error comparing images: {e}")
        return False, 0.0

# Streamlit App
def main():
    st.title("🔬 Disease Detection System")

    use_webcam = st.checkbox("📷 Capture Image Using Webcam")
    captured_image = None

    if use_webcam:
        st.write("Click the button below to capture an image.")
        camera_image = st.camera_input("Capture Image")
        if camera_image is not None:
            image_pil = Image.open(camera_image)
            captured_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    else:
        uploaded_image = st.file_uploader("📁 Upload an Image", type=["jpg", "png", "jpeg"])
        if uploaded_image is not None:
            image_pil = Image.open(uploaded_image)
            captured_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    if captured_image is not None:
        try:
            captured_gray = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            st.error(f"❌ Error processing image: {e}")
            return

        # Corrected Paths
        csv_file = # Fixed path
        images_folder = # Fixed path

        if not os.path.exists(csv_file):
            st.error(f"❌ CSV file not found: {csv_file}")
            return

        images_data = load_images_from_csv(csv_file, images_folder)

        if not images_data:
            st.error("❌ No valid images found in the CSV file.")
            return

        disease_detected = False
        threshold = 0.7  

        for i, (provided_image, label, fertilizer) in enumerate(images_data):
            match_found, score = compare_images(provided_image, captured_gray, threshold)

            st.write(f"🔍 SSIM Score for Image {i+1}: {score:.2f}")

            if match_found:
                st.success(f"✅ Disease Detected: *{label}* - Recommended Fertilizer: *{fertilizer}* (Score = {score:.2f})")
                disease_detected = True

                recipient_email = #enter mail
                subject = f"Disease Detection Alert: {label} - Recommended Fertilizer: {fertilizer}"
                body = f"Disease detected in the captured image: {label}. Recommended Fertilizer: {fertilizer}."
                send_email_notification(recipient_email, subject, body)
                break

        if not disease_detected:
            st.warning("❌ No Disease Detected.")
            recipient_email = #enter mail
            subject = "Disease Detection Result"
            body = "No disease was detected in the captured image."
            send_email_notification(recipient_email, subject, body)

# Run Streamlit App
if __name__ == "__main__":
    main()
