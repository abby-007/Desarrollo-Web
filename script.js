// ===============================
// PROYECTO INTEGRADOR - SEMANA 6
// Desarrollo de Aplicaciones Web
// ===============================

// Arreglo donde se almacenarán los registros
let registros = [];

// Elementos del formulario
const formulario = document.getElementById("formulario");
const nombre = document.getElementById("nombre");
const correo = document.getElementById("correo");
const categoria = document.getElementById("categoria");
const descripcion = document.getElementById("descripcion");

// Contenedores de error
const errorNombre = document.getElementById("errorNombre");
const errorCorreo = document.getElementById("errorCorreo");
const errorCategoria = document.getElementById("errorCategoria");
const errorDescripcion = document.getElementById("errorDescripcion");

const mensajeGeneral = document.getElementById("mensajeGeneral");
const listaRegistros = document.getElementById("listaRegistros");
const contador = document.getElementById("contador");

// ===============================
// VALIDAR NOMBRE
// ===============================
function validarNombre() {
    if (nombre.value.trim().length < 3) {
        nombre.classList.add("is-invalid");
        nombre.classList.remove("is-valid");
        errorNombre.textContent = "Debe ingresar al menos 3 caracteres.";
        return false;
    }
    nombre.classList.remove("is-invalid");
    nombre.classList.add("is-valid");
    errorNombre.textContent = "";
    return true;
}

// ===============================
// VALIDAR CORREO
// ===============================
function validarCorreo() {
    const expresion = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!expresion.test(correo.value.trim())) {
        correo.classList.add("is-invalid");
        correo.classList.remove("is-valid");
        errorCorreo.textContent = "Ingrese un correo válido.";
        return false;
    }
    correo.classList.remove("is-invalid");
    correo.classList.add("is-valid");
    errorCorreo.textContent = "";
    return true;
}

// ===============================
// VALIDAR CATEGORÍA
// ===============================
function validarCategoria() {
    if (categoria.value === "") {
        categoria.classList.add("is-invalid");
        categoria.classList.remove("is-valid");
        errorCategoria.textContent = "Seleccione una categoría.";
        return false;
    }
    categoria.classList.remove("is-invalid");
    categoria.classList.add("is-valid");
    errorCategoria.textContent = "";
    return true;
}

// ===============================
// VALIDAR DESCRIPCIÓN
// ===============================
function validarDescripcion() {
    if (descripcion.value.trim().length < 10) {
        descripcion.classList.add("is-invalid");
        descripcion.classList.remove("is-valid");
        errorDescripcion.textContent = "Ingrese una descripción de al menos 10 caracteres.";
        return false;
    }
    descripcion.classList.remove("is-invalid");
    descripcion.classList.add("is-valid");
    errorDescripcion.textContent = "";
    return true;
}

// ===============================
// EVENTOS EN TIEMPO REAL
// ===============================
nombre.addEventListener("input", validarNombre);
nombre.addEventListener("blur", validarNombre);

correo.addEventListener("input", validarCorreo);
correo.addEventListener("blur", validarCorreo);

categoria.addEventListener("change", validarCategoria);
categoria.addEventListener("blur", validarCategoria);

descripcion.addEventListener("input", validarDescripcion);
descripcion.addEventListener("blur", validarDescripcion);

// ===============================
// REGISTRAR
// ===============================
formulario.addEventListener("submit", function (e) {
    e.preventDefault();

    const nombreValido = validarNombre();
    const correoValido = validarCorreo();
    const categoriaValida = validarCategoria();
    const descripcionValida = validarDescripcion();

    if (nombreValido && correoValido && categoriaValida && descripcionValida) {
        const registro = {
            nombre: nombre.value.trim(),
            correo: correo.value.trim(),
            categoria: categoria.value,
            descripcion: descripcion.value.trim()
        };

        registros.push(registro);
        mostrarRegistros();

        mensajeGeneral.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                Registro realizado correctamente.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        formulario.reset();

        nombre.classList.remove("is-valid");
        correo.classList.remove("is-valid");
        categoria.classList.remove("is-valid");
        descripcion.classList.remove("is-valid");
    } else {
        mensajeGeneral.innerHTML = `
            <div class="alert alert-danger" role="alert">
                Existen campos incorrectos. Revise la información.
            </div>
        `;
    }
});

// ===============================
// MOSTRAR REGISTROS
// ===============================
function mostrarRegistros() {
    listaRegistros.innerHTML = "";

    registros.forEach(function (registro, indice) {
        listaRegistros.innerHTML += `
            <div class="col-md-6">
                <div class="registro">
                    <h5>${registro.nombre}</h5>
                    <p><strong>Correo:</strong> ${registro.correo}</p>
                    <p><strong>Categoría:</strong> ${registro.categoria}</p>
                    <p><strong>Descripción:</strong> ${registro.descripcion}</p>
                    <button class="btn btn-danger mt-2" onclick="eliminarRegistro(${indice})">
                        Eliminar
                    </button>
                </div>
            </div>
        `;
    });

    contador.textContent = registros.length;
}

// ===============================
// ELIMINAR REGISTRO (Globalización)
// ===============================
function eliminarRegistro(indice) {
    registros.splice(indice, 1);
    mostrarRegistros();
}

// Vinculamos la función al objeto window para solucionar el error de clic en producción
window.eliminarRegistro = eliminarRegistro;