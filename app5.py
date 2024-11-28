import os
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine, Column, String, Date, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./certificates.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Certificate model
class Certificate(Base):
    __tablename__ = 'certificates'

    id = Column(Integer, primary_key=True, index=True)
    serial_no = Column(String, unique=False, index=True)
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

def generate_pdf(certificate, footer_text="Default Admin Text"):
    try:
        # Paths
        template_path = "https://github.com/your-username/certificate/image.pdf

        # Step 1: Create PDF overlay with student information
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=landscape(letter))

        # Set font and size
        can.setFont("Helvetica-Bold", 18)

        # Draw Certificate Information
        serial_no_x, serial_no_y = 200, 400
        name_x, name_y = 200, 360
        city_x, city_y = 200, 315
        country_x, country_y = 200, 275
        certificate_no_x, certificate_no_y = 250, 230
        date_x, date_y = 440, 190
        course_x, course_y = 200, 150

        can.drawString(serial_no_x, serial_no_y, certificate.serial_no or 'N/A')
        can.drawString(name_x, name_y, certificate.name or 'N/A')
        can.drawString(city_x, city_y, certificate.city or 'N/A')
        can.drawString(country_x, country_y, certificate.country or 'N/A')
        can.drawString(certificate_no_x, certificate_no_y, certificate.certificate_no or 'N/A')
        can.drawString(date_x, date_y, certificate.date_of_certificate.strftime('%Y-%m-%d') if certificate.date_of_certificate else 'N/A')
        can.drawString(course_x, course_y, certificate.course_name or 'N/A')

        # Include photo
        if certificate.photo and os.path.exists(certificate.photo):
            photo_x, photo_y = 650, 300
            photo_width, photo_height = 150, 150
            can.drawImage(certificate.photo, photo_x, photo_y, width=photo_width, height=photo_height)

        # Footer with custom admin text and website URL
        width, height = landscape(letter)
        can.setFont("Helvetica-Bold", 12)
        can.drawCentredString(width / 2, 70, footer_text)  # Custom text
        can.drawCentredString(width / 2, 50, certificate.website or "example.com")  # Website URL

        can.save()
        packet.seek(0)

        # Step 2: Merge overlay onto template
        with open(template_path, "rb") as f:
            template_pdf = PdfReader(BytesIO(f.read()))

        overlay_pdf = PdfReader(BytesIO(packet.getvalue()))
        output_pdf = PdfWriter()

        template_page = template_pdf.pages[0]
        overlay_page = overlay_pdf.pages[0]
        template_page.merge_page(overlay_page)
        output_pdf.add_page(template_page)

        output_buffer = BytesIO()
        output_pdf.write(output_buffer)
        output_buffer.seek(0)
        return output_buffer

    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None



def admin_page():
    """Display admin functions after login."""
    st.sidebar.subheader(f"Logged in as {ADMIN_USERNAME}")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out")
        return

    st.subheader("Admin Panel")

    # Admin actions: Add, Edit/Delete, Search Certificate, Import, Export
    action = st.radio("Select Action", ["Add", "Edit/Delete", "Search Certificate", "Import from CSV", "Export to CSV"])

    if action == "Add":
        add_certificate_form()
    elif action == "Edit/Delete":
        edit_delete_certificate()
    elif action == "Search Certificate":
        view_certificates()
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
        website = st.selectbox("Website", website_options, index=website_options.index(cer.website) if cer and cer.website in website_options else 0)
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
                    if photo:
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

def view_certificates():
    """Admin function to view and download certificates."""
    st.subheader("View Certificates")
    certificate_no = st.text_input("Enter Certificate No to Search")

    if st.button("Search Certificate"):
        session = SessionLocal()
        try:
            certificate = session.query(Certificate).filter_by(certificate_no=certificate_no).first()
            if certificate:
                st.write("### Certificate Details:")
                st.write(f"**Serial No:** {certificate.serial_no}")
                st.write(f"**Name:** {certificate.name}")
                st.write(f"**City:** {certificate.city}")
                st.write(f"**Country:** {certificate.country}")
                st.write(f"**Certificate Number:** {certificate.certificate_no}")
                st.write(f"**Date:** {certificate.date_of_certificate.strftime('%Y-%m-%d')}")
                st.write(f"**Course Name:** {certificate.course_name}")
                if certificate.photo and os.path.exists(certificate.photo):
                    st.image(certificate.photo, width=200)

                pdf_buffer = generate_pdf(certificate)

                if pdf_buffer:
                    st.download_button(
                        label="Download Certificate as PDF",
                        data=pdf_buffer,
                        file_name=f"{certificate_no}.pdf",
                        mime="application/pdf",
                    )
                else:
                    st.error("Failed to generate PDF.")
            else:
                st.error("Certificate not found!")
        except Exception as e:
            st.error(f"Error retrieving certificate: {e}")
        finally:
            session.close()

def edit_delete_certificate():
    """Admin function to edit or delete certificates."""
    st.subheader("Edit or Delete Certificates")
    session = SessionLocal()
    certificates = session.query(Certificate).all()
    for cer in certificates:
        st.write(f"**Serial No:** {cer.serial_no} | **Name:** {cer.name} | **Certificate No:** {cer.certificate_no}")
        if cer.photo and os.path.exists(cer.photo):
            st.image(cer.photo, width=100)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Edit", key=f"edit_{cer.id}"):
                add_certificate_form(editing=True, cer=cer)
                return  # Exit the function to prevent overlapping forms

        with col2:
            if st.button("Delete", key=f"delete_{cer.id}"):
                try:
                    session.delete(cer)
                    session.commit()
                    st.success(f"Certificate {cer.certificate_no} deleted!")
                    st.experimental_rerun()  # Refresh the widget state to reflect changes
                    return  # Exit after deletion
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
        "Date of Certificate": [cer.date_of_certificate.strftime('%Y-%m-%d') if cer.date_of_certificate else '' for cer in certificates],
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

    # Search field for certificate number
    certificate_no = st.text_input("Enter Certificate No to Search")

    session = SessionLocal()
    try:
        # Fetch certificate based on search
        if certificate_no:
            certificates = session.query(Certificate).filter_by(certificate_no=certificate_no).all()
        else:
            certificates = []

        # Show search results
        if certificates:
            st.write("### Certificate Information")
            table_data = []

            for cer in certificates:
                # Add data rows with "View" and "Verify" buttons
                table_data.append(
                    {
                        "Serial No": cer.serial_no,
                        "Name": cer.name,
                        "Course": cer.course_name,
                        "City": cer.city,
                        "Country": cer.country,
                        "Certificate No": cer.certificate_no,
                        "Verify": "✔️ Verified",  # Static verify option
                        "View": st.button("View", key=f"view_{cer.id}")
                    }
                )

            # Convert data to a DataFrame for better display
            df = pd.DataFrame(table_data)

            # Render the table with only the searched certificate
            st.dataframe(df)

            # Check which "View" button is clicked
            for cer in certificates:
                if st.session_state.get(f"view_{cer.id}"):
                    st.write(f"### Viewing Certificate for {cer.name}")
                    pdf_buffer = generate_pdf(cer)

                    if pdf_buffer:
                        # Convert PDF to Base64
                        pdf_base64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")

                        # Embed PDF in an iframe
                        pdf_html = f"""
                        <iframe
                            src="data:application/pdf;base64,{pdf_base64}"
                            width="100%"
                            height="600px"
                            style="border: none;">
                        </iframe>
                        """
                        st.markdown(pdf_html, unsafe_allow_html=True)
                    else:
                        st.error("Failed to generate the certificate view.")
                    break  # Only display one certificate at a time
        else:
            st.info("No certificate found with the given Certificate No. Please try again.")
    except Exception as e:
        st.error(f"Error retrieving certificates: {e}")
    finally:
        session.close()




# Main Routing Logic
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Get query parameters from the URL
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
