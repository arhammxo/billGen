import os
import random
import datetime
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import csv  # Add this import at the top

app = Flask(__name__)

def generate_bill_number(name):
    """Generate a unique bill number based on timestamp and random number."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_number = random.randint(1000, 9999)  # Random number for added uniqueness
    return f"{name}-{timestamp}-{random_number}"

def generate_pdf(bill_data, filename):
    """Generate a PDF file with bill details."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Centered Logo at the top
    logo_path = "static/images/logo.png"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width = 80
        logo_height = 80
        # Center horizontally: (page width - logo width) / 2
        c.drawImage(logo, (width-logo_width)/2, height-100, 
                   width=logo_width, height=logo_height, 
                   preserveAspectRatio=True, mask='auto')

    # Header Section below logo
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0, 0.2, 0.5)
    c.drawCentredString(width/2, height-110, "HOTEL RIZ VARANASI")  # Moved down
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(width/2, height-130, "S-19/32, Nadesar, Chaukaghat, Varanasi, Uttar Pradesh 221002")  # Moved down
    
    # Bill Information Section (starting lower)
    y_position = height - 170  # Adjusted starting position
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, y_position, "TAX INVOICE:")
    c.line(50, y_position-2, 350, y_position-2)
    
    # Bill Details Table
    details = [
        ("Bill Number:", bill_data['bill_number']),
        ("Issue Date:", datetime.datetime.now().strftime("%d-%b-%Y")),
        ("Customer Name:", bill_data['customer_name']),
        ("Room Type:", bill_data['room_type']),
        ("Number of Rooms:", bill_data['number_of_rooms']),
        ("Check-In Date:", bill_data['check_in']),
        ("Check-Out Date:", bill_data['check_out']),
    ]
    
    for label, value in details:
        y_position -= 20
        c.drawString(50, y_position, label)
        c.drawString(200, y_position, value)
    
    # Amount Breakdown
    y_position -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Amount Details:")
    c.line(50, y_position-2, 350, y_position-2)
    
    y_position -= 30
    c.setFont("Helvetica", 10)
    details = [
        ("Base Amount", f"Rs. {bill_data['bill_amount']:.2f}/-"),
        ("GST (6%)", f"Rs. {bill_data['gst']:.2f} /-"),
        ("Service Tax (6%)", f"Rs. {bill_data['tax']:.2f}/-"),
    ]
    
    for label, value in details:
        c.drawString(50, y_position, label)
        c.drawString(250, y_position, value)
        y_position -= 20
    
    # Total Amount
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.8, 0, 0)  # Red color
    c.drawString(50, y_position, "Total Amount Payable:")
    c.drawString(250, y_position, f"Rs. {bill_data['total_amount']:.2f}/-")
    c.line(50, y_position-2, 350, y_position-2)
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawCentredString(width/2, 50, "Thank you for choosing Hotel Riz! | For queries: contact@hotelriz.com")
    
    # Save PDF
    c.save()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve the data from the form
        customer_name = request.form["customer_name"]
        room_type = request.form["room_type"]
        number_of_rooms = request.form["number_of_rooms"]
        bill_amount = float(request.form["bill_amount"])
        check_in = request.form["check_in"]
        check_out = request.form["check_out"]
        corporate_gst_number = request.form["corporate_gst"]

        # Add date validation
        try:
            check_in_date = datetime.datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.datetime.strptime(check_out, '%Y-%m-%d').date()
            today = datetime.date.today()
            
            if check_in_date > today or check_out_date > today:
                raise ValueError("Dates cannot be in the future")
            if check_out_date <= check_in_date:
                raise ValueError("Check-out date must be after check-in date")
                
        except ValueError as e:
            return render_template("index.html",
                                error=str(e),
                                customer_name=request.form["customer_name"],
                                room_type=request.form["room_type"],
                                number_of_rooms=request.form["number_of_rooms"],
                                bill_amount=request.form["bill_amount"],
                                check_in=check_in,
                                check_out=check_out,
                                corporate_gst=request.form["corporate_gst"],
                                pdf_filename=None,
                                today=today.isoformat())

        # Generate unique bill number
        bill_number = generate_bill_number(customer_name)

        # Perform GST and Tax Calculation
        gst = bill_amount * 0.06
        tax = bill_amount * 0.06
        total_amount = bill_amount + gst + tax

        # Data to be passed to the PDF generation function
        bill_data = {
            "bill_number": bill_number,
            "customer_name": customer_name,
            "room_type": room_type,
            "number_of_rooms": number_of_rooms,
            "check_in": check_in,
            "check_out": check_out,
            "bill_amount": bill_amount,
            "gst": gst,
            "tax": tax,
            "corporate_gst": corporate_gst_number,
            "total_amount": total_amount
        }

        # Generate PDF file
        pdf_filename = f"static/bills/{bill_number}.pdf"
        generate_pdf(bill_data, pdf_filename)

        # Add to CSV log
        csv_file = 'bills.csv'
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, 'a', newline='') as f:
            fieldnames = [
                'BillNumber', 'CustomerName', 'RoomType', 'NumberOfRooms',
                'CheckInDate', 'CheckOutDate', 'BaseAmount', 'GST',
                'ServiceTax', 'TotalAmount', 'CorporateGST', 'Timestamp'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'BillNumber': bill_number,
                'CustomerName': customer_name,
                'RoomType': room_type,
                'NumberOfRooms': number_of_rooms,
                'CheckInDate': check_in,
                'CheckOutDate': check_out,
                'BaseAmount': bill_amount,
                'GST': gst,
                'ServiceTax': tax,
                'TotalAmount': total_amount,
                'CorporateGST': corporate_gst_number,
                'Timestamp': datetime.datetime.now().isoformat()
            })

        # Render the result on the page and send the link to the PDF
        return render_template("index.html", 
                               customer_name=customer_name,
                               room_type=room_type,
                               number_of_rooms=number_of_rooms,
                               bill_amount=bill_amount,
                               gst=gst,
                               tax=tax,
                               total_amount=total_amount,
                               check_in=check_in,
                               check_out=check_out,
                               bill_number=bill_number,
                               pdf_filename=pdf_filename,
                               today=today.isoformat())

    return render_template("index.html", customer_name=None, today=datetime.date.today().isoformat())

if __name__ == "__main__":
    # Ensure the 'bills' directory exists
    if not os.path.exists('static/bills'):
        os.makedirs('static/bills')
    app.run(debug=True)
