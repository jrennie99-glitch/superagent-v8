import unittest
import os
import tempfile
from typing import List, Dict, Union
from datetime import datetime

# Assuming the main application code is in a file named 'main.py'
from main import InvoiceSystem, Invoice

class TestInvoiceSystem(unittest.TestCase):

    def setUp(self) -> None:
        """Setup method to create an InvoiceSystem instance and a temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.invoice_system = InvoiceSystem(storage_directory=self.temp_dir)
        self.invoice_data = {
            "invoice_number": "INV-001",
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "billing_address": "123 Main St",
            "shipping_address": "456 Oak Ave",
            "items": [{"description": "Consulting", "quantity": 10, "unit_price": 100.0}],
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "customer_phone": "555-123-4567",
        }


    def tearDown(self) -> None:
        """Teardown method to clean up the temporary directory after each test."""
        # Remove all files in the temp directory
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        # Remove the directory itself.  Retry logic in case of permission issues on Windows
        import time
        for _ in range(5):
            try:
                os.rmdir(self.temp_dir)
                break
            except OSError as e:
                print(f"Failed to remove temporary directory: {e}. Retrying in 1 second...")
                time.sleep(1)
        else:
            print(f"Failed to remove temporary directory after multiple attempts.")

    def test_create_invoice(self) -> None:
        """Test creating a new invoice."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        self.assertIsInstance(invoice, Invoice)
        self.assertEqual(invoice.invoice_number, "INV-001")

    def test_store_invoice(self) -> None:
        """Test storing an invoice."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        invoice_path = self.invoice_system.store_invoice(invoice)
        self.assertTrue(os.path.exists(invoice_path))

    def test_get_invoice(self) -> None:
        """Test retrieving an invoice by its invoice number."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        self.invoice_system.store_invoice(invoice)
        retrieved_invoice = self.invoice_system.get_invoice("INV-001")
        self.assertIsInstance(retrieved_invoice, Invoice)
        self.assertEqual(retrieved_invoice.invoice_number, "INV-001")

        #Test Invoice Not Found
        with self.assertRaises(ValueError):
            self.invoice_system.get_invoice("INV-999")


    def test_get_all_invoices(self) -> None:
        """Test retrieving all invoices."""
        invoice1 = self.invoice_system.create_invoice(**self.invoice_data)
        self.invoice_system.store_invoice(invoice1)

        invoice_data2 = self.invoice_data.copy()
        invoice_data2["invoice_number"] = "INV-002"
        invoice2 = self.invoice_system.create_invoice(**invoice_data2)
        self.invoice_system.store_invoice(invoice2)

        all_invoices = self.invoice_system.get_all_invoices()
        self.assertIsInstance(all_invoices, list)
        self.assertEqual(len(all_invoices), 2)


    def test_calculate_total(self) -> None:
        """Test calculating the total amount of an invoice."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        total = invoice.calculate_total()
        self.assertEqual(total, 1000.0)

    def test_download_invoice_pdf(self) -> None:
        """Test downloading an invoice as a PDF."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        pdf_file_path = self.invoice_system.download_invoice_pdf(invoice)
        self.assertTrue(os.path.exists(pdf_file_path))
        self.assertTrue(pdf_file_path.endswith(".pdf"))

    def test_send_invoice_email(self) -> None:
        """Test sending an invoice via email. This test requires a properly configured email setup.
           For the purpose of this test, we only check if the method runs without errors."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        try:
            self.invoice_system.send_invoice_email(invoice)
            # Assert that the method ran without errors.
            self.assertTrue(True)  # If we reach here, the email function didn't throw error.
        except Exception as e:
            self.fail(f"send_invoice_email() raised an exception: {e}")

    def test_send_invoice_sms(self) -> None:
        """Test sending an invoice via SMS. This test requires a properly configured SMS setup.
           For the purpose of this test, we only check if the method runs without errors."""
        invoice = self.invoice_system.create_invoice(**self.invoice_data)
        try:
            self.invoice_system.send_invoice_sms(invoice)
            # Assert that the method ran without errors.
            self.assertTrue(True)  # If we reach here, the sms function didn't throw error.
        except Exception as e:
            self.fail(f"send_invoice_sms() raised an exception: {e}")

    def test_invoice_number_validation(self) -> None:
        """Test invoice number validation."""
        with self.assertRaises(ValueError):
            self.invoice_system.create_invoice(**{**self.invoice_data, "invoice_number": "INVALID NUMBER"})

    def test_negative_quantity(self) -> None:
        """Test negative invoice item quantity throws error"""
        invoice_data = self.invoice_data.copy()
        invoice_data["items"] = [{"description": "Consulting", "quantity": -1, "unit_price": 100.0}]

        with self.assertRaises(ValueError):
             self.invoice_system.create_invoice(**invoice_data)

    def test_zero_quantity(self) -> None:
        """Test zero invoice item quantity throws error"""
        invoice_data = self.invoice_data.copy()
        invoice_data["items"] = [{"description": "Consulting", "quantity": 0, "unit_price": 100.0}]

        with self.assertRaises(ValueError):
             self.invoice_system.create_invoice(**invoice_data)

    def test_calculate_total_invoices_for_year(self) -> None:
        """Test calculating the total value of invoices for a specific year."""
        now = datetime.now()
        current_year = now.year

        invoice1_data = self.invoice_data.copy()
        invoice1_data["issue_date"] = f"{current_year}-01-15"
        invoice1 = self.invoice_system.create_invoice(**invoice1_data)
        self.invoice_system.store_invoice(invoice1)

        invoice2_data = self.invoice_data.copy()
        invoice2_data["invoice_number"] = "INV-002"
        invoice2_data["issue_date"] = f"{current_year}-05-20"
        invoice2 = self.invoice_system.create_invoice(**invoice2_data)
        self.invoice_system.store_invoice(invoice2)

        invoice3_data = self.invoice_data.copy()
        invoice3_data["invoice_number"] = "INV-003"
        invoice3_data["issue_date"] = f"{current_year - 1}-12-10"  # Previous year
        invoice3 = self.invoice_system.create_invoice(**invoice3_data)
        self.invoice_system.store_invoice(invoice3)

        total_this_year = self.invoice_system.calculate_total_invoices_for_year(current_year)
        self.assertEqual(total_this_year, 2000.0)

if __name__ == '__main__':
    unittest.main()