import os
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./certificates.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Certificate model
class Certificate(Base):
    __tablename__ = 'certificates'

    id = Column(Integer, primary_key=True, index=True)
    serial_no = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    course_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    certificate_no = Column(String, unique=True, nullable=False)
    date_of_certificate = Column(Date, nullable=False)
    photo = Column(String, nullable=True)
    access_by = Column(String, nullable=False)
    website = Column(String, nullable=False)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Ensure folders exist
if not os.path.exists("photos"):
    os.makedirs("photos")
if not os.path.exists("logos"):
    os.makedirs("logos")

# Admin credentials (for demonstration)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'  # Change this to a secure password

def login():
    """Admin login function."""
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Logged in as admin!")
        else:
            st.error("Invalid username or password")

def generate_pdf(certificate):
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=landscape(letter))

        # Dimensions
        width, height = landscape(letter)

        # Set background color to light gray and fill page
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(0, 0, width, height, fill=1)

        # Reset fill color to black for text
        c.setFillColorRGB(0, 0, 0)

        # Add Institute Logo at top left corner if available
        logo_path = "logos/institute_logo.png"
        if os.path.exists(logo_path):
            try:
                logo_image = ImageReader(logo_path)
                logo_width, logo_height = logo_image.getSize()
                aspect = logo_height / float(logo_width)
                logo_display_width = 100  # Width in the PDF
                logo_display_height = logo_display_width * aspect
                c.drawImage(logo_image, 30, height - logo_display_height - 30, width=logo_display_width, height=logo_display_height, mask='auto')
            except Exception as e:
                st.error(f"Error displaying logo: {e}")

        # Draw Title
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(width / 2, height - 100, "Certificate of Completion")

        # Adjust position for certificate details
        c.setFont("Helvetica", 18)
        text_y_position = height - 170  # Starting Y position
        line_spacing = 30  # Space between lines

        c.drawString(50, text_y_position, f"Serial No: {certificate.serial_no or 'N/A'}")
        text_y_position -= line_spacing
        c.drawString(50, text_y_position, f"Name: {certificate.name or 'N/A'}")
        text_y_position -= line_spacing
        c.drawString(50, text_y_position, f"City: {certificate.city or 'N/A'}, Country: {certificate.country or 'N/A'}")
        text_y_position -= line_spacing
        c.drawString(50, text_y_position, f"Certificate No: {certificate.certificate_no or 'N/A'}")
        text_y_position -= line_spacing

        # Handle date formatting safely
        if certificate.date_of_certificate:
            date_str = certificate.date_of_certificate.strftime('%Y-%m-%d')
        else:
            date_str = 'N/A'
        c.drawString(50, text_y_position, f"Date: {date_str}")
        text_y_position -= line_spacing

        c.drawString(50, text_y_position, f"Course: {certificate.course_name or 'N/A'}")

        # Add Student Photo at the right side
        if certificate.photo and os.path.exists(certificate.photo):
            try:
                c.drawImage(certificate.photo, width - 200, height - 400, width=150, height=200, mask='auto')
            except Exception as e:
                st.error(f"Error displaying photo: {e}")
        else:
            text_y_position -= line_spacing
            c.drawString(50, text_y_position, "Photo: Not Available")

        # Footer with Access By and Website
        footer_text = f"Access By: {certificate.access_by or 'N/A'}    Website: {certificate.website or 'N/A'}"
        c.setFont("Helvetica", 14)
        c.drawCentredString(width / 2, 50, footer_text)

        c.save()
        buffer.seek(0)
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

    return buffer

def admin_page():
    """Display admin functions after login."""
    st.sidebar.subheader(f"Logged in as {ADMIN_USERNAME}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out")
        return

    st.subheader("Admin Panel")
    
    # Admin actions: Add, Edit/Delete, Import, Export
    action = st.radio("Select Action", ["Add", "Edit/Delete", "Import from CSV", "Export to CSV"])

    if action == "Add":
        add_certificate_form()
    elif action == "Edit/Delete":
        edit_delete_certificate()
    elif action == "Import from CSV":
        import_certificates_from_csv()
    elif action == "Export to CSV":
        export_certificates_to_csv()

def add_certificate_form(editing=False, cer=None):
    """Admin function to add or edit certificates."""
    if editing:
        st.subheader("Edit Certificate")
    else:
        st.subheader("Add Certificate")
    
    with st.form("certificate_form"):
        serial_no = st.text_input("Serial No", cer.serial_no if cer else "")
        name = st.text_input("Name", cer.name if cer else "")
        course_name = st.text_input("Course Name", cer.course_name if cer else "")
        city = st.text_input("City", cer.city if cer else "")
        country = st.text_input("Country", cer.country if cer else "")
        certificate_no = st.text_input("Certificate No", cer.certificate_no if cer else "")
        date_of_certificate = st.date_input("Date of Certificate", cer.date_of_certificate if cer else datetime.today())
        
        access_by = "Admin"

        website_options = ["example.com", "mysite.org", "Other"]
        website = st.selectbox("Website", website_options, index=website_options.index(cer.website) if cer else 0)
        if website == "Other":
            custom_website = st.text_input("Enter Website", cer.website if cer and cer.website not in website_options else "")
            if custom_website.strip():
                website = custom_website

        photo = st.file_uploader("Upload Student Photo", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Submit")
        if submitted:
            if not all([serial_no, name, course_name, city, country, certificate_no]):
                st.error("Please fill in all required fields!")
            elif not date_of_certificate:
                st.error("Please select a valid date!")
            else:
                session = SessionLocal()
                try:
                    if not editing and photo:
                        photo_path = f"photos/{serial_no}_{photo.name}"
                        with open(photo_path, "wb") as f:
                            f.write(photo.getbuffer())
                    else:
                        photo_path = cer.photo if cer else None

                    if editing:
                        cer.serial_no = serial_no
                        cer.name = name
                        cer.course_name = course_name
                        cer.city = city
                        cer.country = country
                        cer.certificate_no = certificate_no
                        cer.date_of_certificate = date_of_certificate
                        cer.access_by = access_by
                        cer.website = website
                        if photo:
                            cer.photo = photo_path
                        session.commit()
                        st.success("Certificate updated successfully!")
                    else:
                        new_certificate = Certificate(
                            serial_no=serial_no,
                            name=name,
                            course_name=course_name,
                            city=city,
                            country=country,
                            certificate_no=certificate_no,
                            date_of_certificate=date_of_certificate,
                            photo=photo_path,
                            access_by=access_by,
                            website=website
                        )
                        session.add(new_certificate)
                        session.commit()
                        st.success("Certificate added successfully!")
                except Exception as e:
                    session.rollback()
                    st.error(f"Error saving certificate: {e}")
                finally:
                    session.close()

def edit_delete_certificate():
    """Admin function to edit or delete certificates."""
    st.subheader("Edit or Delete Certificates")
    session = SessionLocal()
    certificates = session.query(Certificate).all()
    for cer in certificates:
        st.write(f"**Name:** {cer.name} | **Certificate No:** {cer.certificate_no}")
        if os.path.exists(cer.photo):
            st.image(cer.photo, width=100)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Edit", key=f"edit_{cer.id}"):
                add_certificate_form(editing=True, cer=cer)

        with col2:
            if st.button("Delete", key=f"delete_{cer.id}"):
                try:
                    session.delete(cer)
                    session.commit()
                    st.success(f"Certificate {cer.certificate_no} deleted!")
                    st.experimental_rerun()  # Refresh the widget state to reflect changes
                except Exception as e:
                    session.rollback()
                    st.error(f"Error deleting certificate: {e}")
                finally:
                    session.close()

def import_certificates_from_csv():
    """Import certificates from a CSV file."""
    st.subheader("Import Certificates from CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file:
        session = SessionLocal()
        try:
            data = pd.read_csv(uploaded_file)
            for _, row in data.iterrows():
                new_certificate = Certificate(
                    serial_no=row["serial_no"],
                    name=row["name"],
                    course_name=row["course_name"],
                    city=row["city"],
                    country=row["country"],
                    certificate_no=row["certificate_no"],
                    date_of_certificate=pd.to_datetime(row["date_of_certificate"]),
                    photo=row["photo"],  # Assuming photos are pre-uploaded and paths are included
                    access_by="Admin",   # Defaulting to admin
                    website=row["website"]
                )
                session.add(new_certificate)
            session.commit()
            st.success("Certificates imported successfully!")
        except Exception as e:
            session.rollback()
            st.error(f"Error importing certificates: {e}")
        finally:
            session.close()

def export_certificates_to_csv():
    """Export all certificates to a CSV file."""
    st.subheader("Export Certificates to CSV")
    session = SessionLocal()
    
    certificates = session.query(Certificate).all()

    data = {
        "Serial No": [cer.serial_no for cer in certificates],
        "Name": [cer.name for cer in certificates],
        "Course Name": [cer.course_name for cer in certificates],
        "City": [cer.city for cer in certificates],
        "Country": [cer.country for cer in certificates],
        "Certificate No": [cer.certificate_no for cer in certificates],
        "Date of Certificate": [cer.date_of_certificate for cer in certificates],
        "Photo": [cer.photo for cer in certificates],
        "Access By": [cer.access_by for cer in certificates],
        "Website": [cer.website for cer in certificates],
    }

    df = pd.DataFrame(data)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='certificates.csv',
        mime='text/csv',
    )
    session.close()

def public_verification():
    """Public function to verify certificates."""
    st.subheader("Verify Certificate")
    certificate_no = st.text_input("Enter Certificate No to Verify")

    if st.button("Verify"):
        session = SessionLocal()
        try:
            certificate = session.query(Certificate).filter_by(certificate_no=certificate_no).first()
            if certificate:
                st.success(f"Certificate {certificate_no} is verified!")
                st.write("### Certificate Details:")

                # Prepare data for tabular display, including HTML for the image
                photo_html = ""
                if os.path.exists(certificate.photo):
                    # Create an img tag with base64 encoding of the image
                    with open(certificate.photo, "rb") as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode("utf-8")
                        photo_html = f'<img src="data:image/jpeg;base64,{img_base64}" width="100" />'

                data = {
                    "Name": [certificate.name],
                    "Course Name": [certificate.course_name],
                    "City": [certificate.city],
                    "Country": [certificate.country],
                    "Date": [certificate.date_of_certificate.strftime('%Y-%m-%d')],
                    "Certificate Number": [certificate.certificate_no],
                    "Photo": [photo_html],
                    "Status": ["Verified"]
                }

                # Convert to a Pandas DataFrame
                df = pd.DataFrame(data)

                # Use st.markdown with unsafe_allow_html=True to render the table with HTML content
                st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.error("Certificate not found!")
        except Exception as e:
            st.error(f"Error verifying certificate: {e}")
        finally:
            session.close()

# Main Routing Logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

query_params = st.query_params  # Updated from experimental_get_query_params
if 'admin' in query_params:
    if st.session_state.logged_in:
        admin_page()
    else:
        login()
elif 'verify' in query_params:
    public_verification()
else:
    st.info("Welcome to the Certificate Management System. Use the query parameters to navigate.")
    st.write("For Public Verification: Add `?verify` to the URL in your browser.")
    st.write("For Admin Login: Add `?admin` to the URL in your browser.")
