from fpdf import FPDF
from datetime import datetime, timedelta
import os


def generar_pdf(data, filename):
    pdf = FPDF()
    pdf.add_page()

    # Fuente Unicode (DejaVu)
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 11)

    # === ENCABEZADO AZUL ===
    pdf.set_fill_color(70, 130, 180)  # azul acero
    pdf.rect(0, 0, 210, 30, 'F')

    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 8)
    pdf.set_font("DejaVu", 'B', 20)
    pdf.cell(210, 10, "Primer Crédito", align='C', ln=True)

    # Nombre completo en la esquina superior izquierda
    nombre_completo = f"{data['name']} {data['surname']} {data['patronymic']}"
    pdf.set_xy(10, 20)
    pdf.set_font("DejaVu", '', 11)
    pdf.cell(0, 8, f"Nombre completo: {nombre_completo}")

    # Volver a color de texto negro
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(40)

    # === TÍTULO ===
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(0, 10, "CONTRATO DE CRÉDITO", ln=True)

    pdf.set_font("DejaVu", size=11)
    pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True)

    # === SECCIÓN 1 ===
    pdf.set_font("DejaVu", 'B', 12)
    pdf.cell(0, 10, "1. OBJETO DEL CONTRATO", ln=True)

    pdf.set_font("DejaVu", size=11)
    texto1 = (
        f"1.1. La empresa 'KREDIT PERVIY' proporciona servicios de otorgamiento de crédito al solicitante: "
        f"un préstamo de {data['loan_amount']} {data['currency']} con una comisión anual del {data['commission']}%."
    )
    pdf.multi_cell(0, 7, texto1)

    # === SECCIÓN 2 ===
    pdf.set_font("DejaVu", 'B', 12)
    pdf.cell(0, 10, "2. CONDICIONES DE CÁLCULO", ln=True)

    pdf.set_font("DejaVu", size=11)
    texto2 = (
        "2.1. El prestatario se compromete a devolver el préstamo en tiempo y forma según los términos del contrato.\n"
        "2.2. Un pago único de 0 UZS por servicios y tramitación debe realizarse antes de recibir el desembolso."
    )
    pdf.multi_cell(0, 7, texto2)

    # === GARANTÍA ===
    pdf.set_font("DejaVu", size=13)
    garantia_text = (
        "Garantía de pago de la entidad crediticia\n\n"
        "- El pago por los servicios de tramitación y garantía de recepción corre a cargo del destinatario. "
        "Es necesario realizar una transferencia de 55.000 $ARS para recibir el desembolso del crédito.\n\n"
        "- Esta cantidad corresponde al trabajo del gestor e incluye: tramitación de documentos, verificación de datos, "
        "cálculo de la cuota mensual, registro oficial en la base de datos, elaboración del contrato y transferencia "
        "del crédito a su tarjeta. Su pago garantiza el 100% de la recepción de los fondos. ¡PAGO ÚNICO!"
    )
    pdf.multi_cell(0, 8, garantia_text)

    # === FIRMAS Y SELLOS ===
    y_stamps = pdf.get_y() + 10
    if os.path.exists("stamps/banco.png"):
        pdf.image("stamps/banco.png", x=20, y=y_stamps, w=40)
    if os.path.exists("stamps/aprobado.png"):
        pdf.image("stamps/aprobado.png", x=150, y=y_stamps, w=40)

    # === SEGUNDA PÁGINA CON TABLA ===
    pdf.add_page()
    pdf.set_font("DejaVu", size=12)
    pdf.set_fill_color(200, 200, 200)

    headers = ["Fecha", "Saldo", "Interés", "Capital", "Cuota"]
    for header in headers:
        pdf.cell(38, 10, header, 1, 0, 'C', 1)
    pdf.ln()

    saldo = float(data['loan_amount'])
    interes = float(data['commission']) / 100 / 12
    meses = int(data['loan_term'])
    cuota = saldo * (interes * (1 + interes) ** meses) / ((1 + interes) ** meses - 1)
    cuota = round(cuota, 2)

    fecha_inicio = datetime.now().replace(day=int(data['first_payment_day']))
    if fecha_inicio < datetime.now():
        if fecha_inicio.month == 12:
            fecha_inicio = fecha_inicio.replace(month=1, year=fecha_inicio.year + 1)
        else:
            fecha_inicio = fecha_inicio.replace(month=fecha_inicio.month + 1)

    for i in range(meses):
        interes_mensual = round(saldo * interes, 2)
        principal = round(cuota - interes_mensual, 2)
        saldo -= principal
        fecha = fecha_inicio + timedelta(days=30 * i)
        pdf.cell(38, 10, fecha.strftime("%d.%m.%Y"), 1)
        pdf.cell(38, 10, f"{round(saldo + principal, 2)}", 1)
        pdf.cell(38, 10, f"{interes_mensual}", 1)
        pdf.cell(38, 10, f"{principal}", 1)
        pdf.cell(38, 10, f"{cuota}", 1)
        pdf.ln()

    # === FIRMAS DEBAJO DE LA TABLA ===
    y_position = pdf.get_y() + 10
    if os.path.exists("stamps/aprobado.png"):
        pdf.image("stamps/aprobado.png", x=30, y=y_position, w=50)
    if os.path.exists("stamps/banco.png"):
        pdf.image("stamps/banco.png", x=130, y=y_position, w=50)

    os.makedirs("pdfs", exist_ok=True)
    output_path = f"pdfs/{filename}"
    pdf.output(output_path)
    return output_path
