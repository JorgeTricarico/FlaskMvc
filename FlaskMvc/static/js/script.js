// Obtén los elementos del formulario y el botón de envío
const uploadForm = document.getElementById('uploadForm');
const inputs = uploadForm.querySelectorAll('input');
const submitButton = uploadForm.querySelector('.enviar');
const labels = document.querySelectorAll('label');

inputs.forEach((input, index) => {
  input.addEventListener('input', () => {
    const inputValue = input.value.trim();
    
    if (inputValue !== '') {
      labels[index].classList.remove('vacio');
    } else {
      labels[index].classList.add('vacio');
    }
  });
});

// Agrega un evento 'input' a cada campo de entrada
inputs.forEach(input => {
  input.addEventListener('input', () => {
    // Verifica si todos los campos tienen contenido
    const allInputsFilled = Array.from(inputs).every(input => input.value.trim() !== '');
    
    // Si todos los campos están llenos, muestra el botón de envío
    if (allInputsFilled) {
      submitButton.classList.remove('oculto');
    } else {
      submitButton.classList.add('oculto');
    }
  });
});

document.getElementById("uploadForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    var form = event.target;
    var formData = new FormData(form);
    var cargando = document.getElementById('divCargando')
    var titulo1 = document.getElementById('titulo1')
    var titulo2 = document.getElementById('titulo2')
    var divFin = document.getElementById('fin')
    
    titulo1.style.display = 'none'
    titulo2.style.display = 'none'
    cargando.style.display = 'block'
    form.style.display = 'none'
    console.log("Formulario enviado");
    console.log("Datos del formulario:", Object.fromEntries(formData));
 
    try {
        const response = await fetch("http://127.0.0.1:3000/conversor", {
          method: "POST",
          body: formData,
          mode: "cors",
      });

        console.log("Respuesta del servidor:", response);

        const blob = await response.blob();
        cargando.style.display = 'none'
        console.log("Blob recibido:", blob);

        // Crear un enlace de descarga para el nuevo PDF
        var downloadLink = document.createElement("a");
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.download = form.elements.newPdfName.value + ".pdf";
        divFin.style.display = 'block'
        downloadLink.click();
    } catch (error) {
        console.error("Error:", error);
        cargando.style.display = 'none'
        document.getElementById('graveError').style.display = 'block'
    }

});