The Certificate Management System is a web application built with Streamlit to manage, verify, and generate certificates. The application allows administrative users to add, edit, delete, import, and export certificate details, as well as verify certificates via a public interface.

## Features

- **Admin Panel**:
  - Add new certificate details.
  - Edit existing certificate information.
  - Delete certificates.
  - Import certificate data from a CSV file.
  - Export certificate data to a CSV file.

- **Public Interface**:
  - Verify certificate details by certificate number.

- **PDF Generation**:
  - Generate and download certificates as PDF files.

## Prerequisites

- Python 3.7 or later
- Virtual environment (recommended)

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/certificate-management.git
    cd certificate-management
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    The `requirements.txt` file should contain:
    ```
    streamlit
    SQLAlchemy
    pandas
    reportlab
    ```

4. **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## Usage

### Admin Panel

- **Access**: Add `?admin` to the URL to access the admin panel. [Example URL](http://localhost:8501/?admin)
- **Login**: Use the default credentials (admin/password123) to log in as an admin.
- **Admin Actions**:
  - Navigate the actions using the radio buttons to Add, Edit/Delete, Import, or Export certificates.
  - Import and export options support CSV format for batch operations.

### Public Verification

- **Access**: Add `?verify` to the URL to access the public verification interface. [Example URL](http://localhost:8501/?verify)
- **Verification**: Enter the certificate number to verify the certificate's authenticity and view its details.

## File Structure

- `app.py`: Main application file.
- `certificates.db`: SQLite database for storing certificate details.
- `photos/`: Directory for storing student photos.
- `logos/`: Directory for storing institute logos.

## License

Customize this section with the appropriate license for your project.

---

Feel free to adjust the content, links, and instructions in the `README.md` file to better suit your specific application details and repository setup.
