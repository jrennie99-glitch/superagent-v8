import os
import logging
import datetime
import uuid
from typing import List, Dict, Union, Optional

from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField, DateField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange, Optional as OptionalValidator
from wtforms import ValidationError

# Security imports (consider stronger options in a real production environment)
import secrets
from cryptography.fernet import Fernet  # For encrypting sensitive data (API keys, etc.)

# PDF Generation
from weasyprint import HTML

# Email/SMS sending libraries (implement properly with error handling in a real application)
# import smtplib
# from twilio.rest import Client

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///' + os.path.join(BASE_DIR, 'invoice.db'))
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))  # Generate a strong secret key
FERNET_KEY = os.environ.get('FERNET_KEY') # MUST be 32 url-safe base64-encoded bytes
if FERNET_KEY is None:
    FERNET_KEY = Fernet.generate_key().decode()
    os.environ["FERNET_KEY"] = FERNET_KEY  # Persist it securely (e.g. in environment variables)

# Twilio/Email credentials - store securely using environment variables and encrypt them in the DB
# TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
# EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
# EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Suppress warning
db = SQLAlchemy(app)

# Initialize Fernet for encryption
fernet = Fernet(FERNET_KEY.encode())


# -------------------------------------- Database Models --------------------------------------

class Invoice(db.Model):
    """
    Represents an invoice.
    """
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    company_address = db.Column(db.String(255))
    client_name = db.Column(db.String(100), nullable=False)
    client_address = db.Column(db.String(255))
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)
    status = db.Column(db.String(20), default='Pending')  # e.g., Pending, Paid, Overdue
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # Timestamp

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

class InvoiceItem(db.Model):
    """
    Represents an item within an invoice.
    """
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<InvoiceItem {self.description}>'


# -------------------------------------- Forms --------------------------------------

class InvoiceItemForm(FlaskForm):
    """
    Form for individual invoice items.
    """
    description = StringField('Description', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    unit_price = FloatField('Unit Price', validators=[DataRequired(), NumberRange(min=0.01)])


    def validate_unit_price(form, field):
        if field.data <= 0:
            raise ValidationError("Unit Price must be greater than 0")

    def validate_quantity(form, field):
        if field.data <= 0:
            raise ValidationError("Quantity must be greater than 0")

class InvoiceForm(FlaskForm):
    """
    Form for creating and editing invoices.
    """
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    company_address = StringField('Company Address')
    client_name = StringField('Client Name', validators=[DataRequired()])
    client_address = StringField('Client Address')
    items = FieldList(FormField(InvoiceItemForm), min_entries=1)
    notes = StringField('Notes', validators=[OptionalValidator()])
    submit = SubmitField('Create Invoice')


    def validate_invoice_number(form, field):
        """Check if an invoice with the same number already exists."""
        existing_invoice = Invoice.query.filter_by(invoice_number=field.data).first()
        if existing_invoice:
            raise ValidationError('Invoice number already exists.')


# -------------------------------------- Routes --------------------------------------

@app.route('/')
def index() -> str:
    """
    Renders the invoice listing page.
    """
    try:
        invoices = Invoice.query.order_by(Invoice.date.desc()).all()
        total_amount = sum(invoice.total_amount for invoice in invoices)  # Calculate total of all invoices
        return render_template('index.html', invoices=invoices, total_amount=total_amount)
    except Exception as e:
        logging.error(f"Error rendering index page: {e}")
        flash("An error occurred while retrieving invoices.", "error")  # Display error message
        return render_template('index.html', invoices=[], total_amount=0)  # Render with empty data

@app.route('/invoice/create', methods=['GET', 'POST'])
def create_invoice() -> Union[str, redirect]:
    """
    Handles invoice creation.
    """
    form = InvoiceForm()

    if form.validate_on_submit():
        try:
            # Calculate total amount based on item entries.
            total_amount = sum(item.data['quantity'] * item.data['unit_price'] for item in form.items)

            # Create new invoice object
            new_invoice = Invoice(
                invoice_number=form.invoice_number.data,
                date=form.date.data,
                company_name=form.company_name.data,
                company_address=form.company_address.data,
                client_name=form.client_name.data,
                client_address=form.client_address.data,
                total_amount=total_amount,
                notes = form.notes.data
            )

            # Create new InvoiceItem objects and link them to the invoice
            for item in form.items:
                new_item = InvoiceItem(
                    description=item.data['description'],
                    quantity=item.data['quantity'],
                    unit_price=item.data['unit_price'],
                    amount=item.data['quantity'] * item.data['unit_price'],
                    invoice=new_invoice
                )
                db.session.add(new_item)

            db.session.add(new_invoice)
            db.session.commit()
            logging.info(f"Invoice created successfully: {new_invoice.invoice_number}")
            flash('Invoice created successfully!', 'success')
            return redirect(url_for('index'))  # Redirect to index on success

        except Exception as e:
            db.session.rollback() # Rollback in case of errors
            logging.error(f"Error creating invoice: {e}")
            flash('An error occurred while creating the invoice.', 'error') #Display error on failure

    return render_template('create_invoice.html', form=form)

@app.route('/invoice/<int:invoice_id>/edit', methods=['GET', 'POST'])
def edit_invoice(invoice_id: int) -> Union[str, redirect]:
    """
    Handles invoice editing.
    """
    invoice = Invoice.query.get_or_404(invoice_id)
    form = InvoiceForm(obj=invoice)  # Initialize form with existing data
    # pre-populate items
    form.items.pop_entry()
    for item in invoice.items:
      form.items.append_entry(item)

    if form.validate_on_submit():
        try:
            # Update invoice fields
            invoice.invoice_number = form.invoice_number.data
            invoice.date = form.date.data
            invoice.company_name = form.company_name.data
            invoice.company_address = form.company_address.data
            invoice.client_name = form.client_name.data
            invoice.client_address = form.client_address.data
            invoice.notes = form.notes.data

            # Update total amount based on item entries.
            invoice.total_amount = sum(item.data['quantity'] * item.data['unit_price'] for item in form.items)

            # Synchronize invoice items (remove old ones, add new ones)
            # Delete old items
            InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
            # Add new items
            for item in form.items:
                new_item = InvoiceItem(
                    description=item.data['description'],
                    quantity=item.data['quantity'],
                    unit_price=item.data['unit_price'],
                    amount=item.data['quantity'] * item.data['unit_price'],
                    invoice=invoice
                )
                db.session.add(new_item)


            db.session.commit()
            logging.info(f"Invoice updated successfully: {invoice.invoice_number}")
            flash('Invoice updated successfully!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating invoice: {e}")
            flash('An error occurred while updating the invoice.', 'error')


    return render_template('edit_invoice.html', form=form, invoice=invoice)

@app.route('/invoice/<int:invoice_id>/delete', methods=['POST'])
def delete_invoice(invoice_id: int) -> redirect:
    """
    Handles invoice deletion.
    """
    invoice = Invoice.query.get_or_404(invoice_id)
    try:
        # Delete invoice items first (cascade delete should also handle this in the DB)
        InvoiceItem.query.filter_by(invoice_id=invoice.id).delete()
        db.session.delete(invoice)
        db.session.commit()
        logging.info(f"Invoice deleted successfully: {invoice.invoice_number}")
        flash('Invoice deleted successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting invoice: {e}")
        flash('An error occurred while deleting the invoice.', 'error')
    return redirect(url_for('index'))

@app.route('/invoice/<int:invoice_id>/pdf')
def download_invoice_pdf(invoice_id: int) -> send_file:
    """
    Generates and downloads a PDF version of the invoice.
    """
    invoice = Invoice.query.get_or_404(invoice_id)
    try:
        # Render the template with invoice data
        html = render_template('invoice_pdf.html', invoice=invoice)

        # Generate PDF from HTML
        pdf = HTML(string=html).write_pdf()

        # Return the PDF file
        return send_file(
            io.BytesIO(pdf),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'invoice_{invoice.invoice_number}.pdf'
        )

    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        flash('An error occurred while generating the PDF.', 'error')
        return redirect(url_for('index')) # Or render an error page

@app.route('/invoice/<int:invoice_id>/send', methods=['POST'])
def send_invoice(invoice_id: int) -> redirect:
  """
  Handles sending invoice via email/SMS (implementation incomplete)
  """
  invoice = Invoice.query.get_or_404(invoice_id)
  try:
        # TODO: Implement sending functionality here

        # --- Email Sending (requires configuration and error handling) ---
        # with smtplib.SMTP("your_smtp_server.com", 587) as server:
        #     server.starttls()
        #     server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        #     # Construct email message (subject, body, attachments etc.)
        #     message = ...
        #     server.sendmail(EMAIL_ADDRESS, "recipient@example.com", message.as_string())
        #     logging.info(f"Email sent for invoice {invoice.invoice_number}")


        # --- SMS Sending (requires configuration and error handling) ---
        # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # message = client.messages.create(
        #     to="+1234567890",  # Recipient phone number
        #     from_="+11234567890", # Your Twilio phone number
        #     body=f"Invoice {invoice.invoice_number} is due..."
        # )
        # logging.info(f"SMS sent for invoice {invoice.invoice_number}, SID: {message.sid}")

      flash("Sending functionality is not yet implemented.", "info") # Placeholder
      return redirect(url_for('index'))

  except Exception as e:
      logging.error(f"Error sending invoice: {e}")
      flash("An error occurred while sending the invoice", "error")
      return redirect(url_for("index"))



# -------------------------------------- Error Handling --------------------------------------
@app.errorhandler(404)
def page_not_found(e):
    """
    Handles 404 errors (page not found).
    """
    logging.warning(f"Page not found: {request.path}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    Handles 500 errors (internal server error).
    """
    db.session.rollback() # Attempt a rollback
    logging.exception("Internal server error") # Log the full exception traceback
    return render_template('500.html'), 500


# -------------------------------------- Application Setup --------------------------------------

def create_db():
    """
    Creates the database and tables if they don't exist.
    """
    with app.app_context():
        db.create_all()
        logging.info("Database created/updated.")

if __name__ == '__main__':
    create_db() # Ensure database is created before running the app
    app.run(debug=True)  #  Disable debug mode in production!