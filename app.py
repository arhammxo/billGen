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
    
    # New header section
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0, 0, 0)
    # Left-aligned GSTIN
    c.drawString(50, height-40, f"GSTIN: 09AALP15013J1ZO")
    # Centered "TAX INVOICE" with highlight
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.8, 0, 0)  # Red color for highlight
    c.drawCentredString(width/2, height-40, "TAX INVOICE")
    # Right-aligned bill number
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawRightString(width-50, height-40, f"Bill No: {bill_data['bill_number'][-4:]}")

    # Centered Logo at the top (moved down slightly)
    logo_path = "static/images/logo.png"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width = 80
        logo_height = 80
        # Adjust logo position down by 40 pixels
        c.drawImage(logo, (width-logo_width)/2, height-120, 
                   width=logo_width, height=logo_height, 
                   preserveAspectRatio=True, mask='auto')

    # Header Section below logo
    c.setFont("Helvetica-Bold", 16)
    c.setFillColorRGB(0, 0.2, 0.5)
    c.drawCentredString(width/2, height-130, "HOTEL RIZ VARANASI")  # Moved down
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(width/2, height-150, "S-19/32, Nadesar, Chaukaghat, Varanasi, Uttar Pradesh 221002  MOBILE: 9794907109")  # Moved down
    
    # Bill Information Section (starting lower)
    y_position = height - 170  # Adjusted starting position
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    
    # Updated bill details
    # Group 1: Guest information
    group1_details = [
        ("Guest Name:", bill_data['guest_name']),
        ("Address:", bill_data['address']),
        ("Mobile:", bill_data['mobile']),
        ("Number of Guests:", bill_data['number_of_guests']),
        ("Room Number:", bill_data['room_number']),
        ("Room Type:", bill_data['room_type']),
        ("Bill Number:", bill_data['bill_number'])
    ]
    
    # Group 2: Stay and payment details with formatted dates
    group2_details = [
        ("Issue Date:", datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")),
        ("Arrival Date and Time:", bill_data['arrival']),
        ("Departure Date and Time:", bill_data['departure']),
        ("Room Tariff:", f"Rs. {bill_data['room_tariff']:.2f}/-"),
        ("Total Days:", str((datetime.datetime.strptime(bill_data['departure'], '%d %b %Y, %I:%M %p') - 
                           datetime.datetime.strptime(bill_data['arrival'], '%d %b %Y, %I:%M %p')).days + 1)),
        ("Total Amount:", f"Rs. {bill_data['total_amount']:.2f}/-"),
        ("CGST (6%):", f"Rs. {bill_data['cgst']:.2f}/-"),
        ("SGST (6%):", f"Rs. {bill_data['sgst']:.2f}/-"),
        ("Service Tax (5%):", f"Rs. {bill_data['service_tax']:.2f}/-"),
        ("Amount Including Tax:", f"Rs. {bill_data['amount_including_tax']:.2f}/-"),
        ("Advance:", f"Rs. {bill_data['advance_paid']:.2f}/-"),
        ("Net Balance:", f"Rs. {bill_data['net_amount']:.2f}/-"),
        ("Cash Received:", "")  # Blank field
    ]
    
    # Draw group 1
    for label, value in group1_details:
        y_position -= 20
        c.drawString(50, y_position, label)
        c.drawString(200, y_position, value)

    # Updated amount breakdown
    y_position -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Amount Details:")
    c.line(50, y_position-2, 350, y_position-2)
    
    # Draw group 2
    for label, value in group2_details:
        y_position -= 20
        c.drawString(50, y_position, label)
        c.drawString(200, y_position, value)
    
    # Add space between groups
    y_position -= 20
    
    # Total Amount
    y_position -= 20
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0.8, 0, 0)  # Red color
    c.drawString(50, y_position, "Total Amount Payable:")
    c.drawString(250, y_position, f"Rs. {bill_data['net_amount']:.2f}/-")
    c.line(50, y_position-2, 350, y_position-2)
    
    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    
    # Left-aligned E. & O.E. (moved up 10 points)
    c.drawString(50, 120, "E. & O.E.")
    
    # Right-aligned hotel name (moved up 10 points)
    c.drawRightString(width-50, 120, "For: HOTEL RIZ")
    
    # Bottom left customer signature (moved down 5 points)
    c.drawString(50, 25, "Customer's Sign")
    
    # Bottom right authorized signature (moved down 5 points)
    c.drawRightString(width-50, 25, "Auth. Signature")
    
    # Save PDF
    c.save()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Retrieve the data from the form
        guest_name = request.form["guest_name"]
        address = request.form["address"]
        mobile = request.form["mobile"]
        number_of_guests = request.form["number_of_guests"]
        room_number = request.form["room_number"]
        arrival = request.form["arrival"]
        departure = request.form["departure"]
        room_type = request.form["room_type"]
        room_tariff = float(request.form["room_tariff"])
        total_amount = float(request.form["total_amount"])
        advance_paid = float(request.form["advance_paid"])

        # Date validation
        try:
            arrival_date = datetime.datetime.strptime(arrival, '%Y-%m-%dT%H:%M')
            departure_date = datetime.datetime.strptime(departure, '%Y-%m-%dT%H:%M')
            today = datetime.datetime.now()
            
            if arrival_date > today or departure_date > today:
                raise ValueError("Dates cannot be in the future")
            if departure_date <= arrival_date:
                raise ValueError("Departure date must be after arrival date")
                
        except ValueError as e:
            return render_template("index.html",
                                error=str(e),
                                guest_name=request.form["guest_name"],
                                address=request.form["address"],
                                mobile=request.form["mobile"],
                                number_of_guests=request.form["number_of_guests"],
                                room_number=request.form["room_number"],
                                arrival=arrival,
                                departure=departure,
                                room_type=request.form["room_type"],
                                room_tariff=request.form["room_tariff"],
                                total_amount=request.form["total_amount"],
                                advance_paid=request.form["advance_paid"],
                                pdf_filename=None)

        # Generate unique bill number
        bill_number = generate_bill_number(guest_name)

        # Calculate taxes
        cgst = total_amount * 0.06  # 6% CGST
        sgst = total_amount * 0.06  # 6% SGST
        service_tax = total_amount * 0.05  # 5% Service Tax
        amount_including_tax = total_amount + cgst + sgst + service_tax
        net_amount = amount_including_tax - advance_paid

        # Data for PDF generation with formatted dates
        bill_data = {
            "bill_number": bill_number,
            "guest_name": guest_name,
            "address": address,
            "mobile": mobile,
            "room_number": room_number,
            "number_of_guests": number_of_guests,
            "arrival": arrival_date.strftime('%d %b %Y, %I:%M %p'),
            "departure": departure_date.strftime('%d %b %Y, %I:%M %p'),
            "room_type": room_type,
            "room_tariff": room_tariff,
            "total_amount": total_amount,
            "cgst": cgst,
            "sgst": sgst,
            "service_tax": service_tax,
            "amount_including_tax": amount_including_tax,
            "advance_paid": advance_paid,
            "net_amount": net_amount
        }

        # Generate PDF file
        pdf_filename = f"static/bills/{bill_number}.pdf"
        generate_pdf(bill_data, pdf_filename)

        # CSV logging updates
        csv_file = 'bills.csv'
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, 'a', newline='') as f:
            fieldnames = [
                'BillNumber', 'GuestName', 'Mobile', 'Address',
                'RoomNumber', 'NumberOfGuests', 'Arrival', 'Departure',
                'RoomType', 'RoomTariff', 'TotalAmount', 'CGST', 
                'SGST', 'ServiceTax', 'AmountIncludingTax', 'AdvancePaid', 'NetAmount', 'Timestamp'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'BillNumber': bill_number,
                'GuestName': guest_name,
                'Mobile': mobile,
                'Address': address,
                'RoomNumber': room_number,
                'NumberOfGuests': number_of_guests,
                'Arrival': arrival,
                'Departure': departure,
                'RoomType': room_type,
                'RoomTariff': room_tariff,
                'TotalAmount': total_amount,
                'CGST': cgst,
                'SGST': sgst,
                'ServiceTax': service_tax,
                'AmountIncludingTax': amount_including_tax,
                'AdvancePaid': advance_paid,
                'NetAmount': net_amount,
                'Timestamp': datetime.datetime.now().isoformat()
            })

        return render_template("index.html", 
                               guest_name=guest_name,
                               address=address,
                               mobile=mobile,
                               number_of_guests=number_of_guests,
                               room_number=room_number,
                               arrival=bill_data['arrival'],
                               departure=bill_data['departure'],
                               room_type=room_type,
                               room_tariff=room_tariff,
                               total_amount=total_amount,
                               advance_paid=advance_paid,
                               cgst=cgst,
                               sgst=sgst,
                               service_tax=service_tax,
                               amount_including_tax=amount_including_tax,
                               net_amount=net_amount,
                               bill_number=bill_number,
                               pdf_filename=pdf_filename)

    return render_template("index.html")

if __name__ == "__main__":
    # Ensure the 'bills' directory exists
    if not os.path.exists('static/bills'):
        os.makedirs('static/bills')
    app.run(host='0.0.0.0', debug=False)
