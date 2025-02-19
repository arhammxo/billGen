import os
import random
import datetime
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

def generate_bill_number():
    """Generate a unique bill number based on timestamp and random number."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_number = random.randint(1000, 9999)  # Random number for added uniqueness
    return f"Bill-{timestamp}-{random_number}"

def generate_pdf(bill_data, filename):
    """Generate a PDF file with bill details."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Adding title and hotel info
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 50, "Hotel Name")
    c.drawString(100, height - 70, "Hotel Address: XYZ Street, City, Country")
    c.drawString(100, height - 100, f"Bill Number: {bill_data['bill_number']}")
    c.drawString(100, height - 120, f"Customer Name: {bill_data['customer_name']}")
    c.drawString(100, height - 140, f"Room Type: {bill_data['room_type']}")
    c.drawString(100, height - 160, f"Bill Amount: ₹{bill_data['bill_amount']}")
    c.drawString(100, height - 180, f"GST (6%): ₹{bill_data['gst']}")
    c.drawString(100, height - 200, f"Tax (6%): ₹{bill_data['tax']}")
    c.drawString(100, height - 220, f"Total Amount: ₹{bill_data['total_amount']}")

    # Save PDF
    c.save()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve the data from the form
        customer_name = request.form["customer_name"]
        room_type = request.form["room_type"]
        bill_amount = float(request.form["bill_amount"])

        # Generate unique bill number
        bill_number = generate_bill_number()

        # Perform GST and Tax Calculation
        gst = bill_amount * 0.06
        tax = bill_amount * 0.06
        total_amount = bill_amount + gst + tax

        # Data to be passed to the PDF generation function
        bill_data = {
            "bill_number": bill_number,
            "customer_name": customer_name,
            "room_type": room_type,
            "bill_amount": bill_amount,
            "gst": gst,
            "tax": tax,
            "total_amount": total_amount
        }

        # Generate PDF file
        pdf_filename = f"static/bills/{bill_number}.pdf"
        generate_pdf(bill_data, pdf_filename)

        # Render the result on the page and send the link to the PDF
        return render_template("index.html", 
                               customer_name=customer_name,
                               room_type=room_type,
                               bill_amount=bill_amount,
                               gst=gst,
                               tax=tax,
                               total_amount=total_amount,
                               bill_number=bill_number,
                               pdf_filename=pdf_filename)

    return render_template("index.html", customer_name=None)

if __name__ == "__main__":
    # Ensure the 'bills' directory exists
    if not os.path.exists('static/bills'):
        os.makedirs('static/bills')
    app.run(debug=True)
