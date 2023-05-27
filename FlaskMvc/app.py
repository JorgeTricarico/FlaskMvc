from flask import Flask, render_template, request, make_response, send_file
from werkzeug.wrappers import Response
import fitz as f
import re
import pandas as pd
import math
import io

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/conversor", methods=["POST"])
def conversor():
    print("Solicitud recibida en /convert")
    
    # Verificar que la solicitud tenga los campos requeridos
    if "excelFile" not in request.files or "pdfFile" not in request.files:
        return "Error: Campos de archivo faltantes", 400

    excel_file = request.files["excelFile"]
    pdf_file = request.files["pdfFile"]
    ganancia = float(request.form["ganancia"])
    new_pdf_name = request.form["newPdfName"]
    
    print(f"Archivo de Excel recibido: {excel_file.filename}")
    print(f"Archivo PDF recibido: {pdf_file.filename}")
    print(f"Ganancia recibida: {ganancia}")
    print(f"Nuevo nombre del archivo PDF: {new_pdf_name}")
    
    df_precios = pd.read_excel(excel_file)
    df_precios = df_precios.rename(columns={'Unnamed: 0': 'Código', 'LOS PRECIOS NO INCLUYEN IVA, PRECIOS SUJETOS A MODIFICACIONES SIN PREVIO AVISO.': 'Precios'})
    df_codigo = df_precios[['Código', 'Precios']]
    
    df_codigo = df_codigo.dropna(subset=['Código', 'Precios'])
    df_codigo = df_codigo[df_codigo['Código'].str.contains('\d')]
    df_codigo['Precios con ganancia'] = df_codigo['Precios'].apply(lambda x: math.ceil(x * (1 + ganancia/100) / 50) * 50)
    
    pdf_data = pdf_file.read()
    pdf_buffer = io.BytesIO(pdf_data)
    documento = f.open("pdf", pdf_buffer)

    regex = r"\d{2,}/\d{2,}|/\d{2,}\b|\d{2,}/\b"
    for numeroDePagina in range(len(documento)):
        pagina = documento.load_page(numeroDePagina)
        text = pagina.get_text("text")
        codigos = re.findall(regex, text)
        for codigo in codigos:
            precio_serie = df_codigo.loc[df_codigo['Código'] == codigo, 'Precios con ganancia']
            if not precio_serie.empty:
                precio = precio_serie.iloc[0]
                text_instances = pagina.search_for(codigo)
                for inst in text_instances:
                    bbox = inst.irect
                    new_y = bbox.y0 - 70
                    new_x = bbox.x0
                    pagina.insert_text((new_x, new_y), str(precio), fontsize=20, fill=(1, 0.3, 0), render_mode=2)
    
    new_pdf_buffer = io.BytesIO()
    documento.save(new_pdf_buffer)
    new_pdf_buffer.seek(0)

    print("Generando archivo PDF nuevo...")

    response = make_response(new_pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={new_pdf_name}.pdf'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'

    return response

app.run(host= "0.0.0.0", port= 3000, debug= True) #(host= "0.0.0.0", port= 3000, debug= True)