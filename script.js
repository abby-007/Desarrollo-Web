// ===============================
// PROYECTO INTEGRADOR - SEMANA 7
// Desarrollo de Aplicaciones Web
// ===============================

// --- NUEVO: Datos iniciales de Servicios para renderizado dinámico ---
const servicios = [
    {
        titulo: "Diseño Web",
        descripcion: "Interfaces modernas, atractivas y adaptables a cualquier dispositivo móvil o tablet.",
        icono: "🎨"
    },
    {
        titulo: "Aplicaciones Web",
        descripcion: "Sistemas robustos desarrollados a medida, listos para integrarse con Flask en el backend.",
        icono: "💻"
    },
    {
        titulo: "Soporte Técnico",
        descripcion: "Optimización de plataformas, configuraciones de red y mantenimiento continuo de tu software.",
        icono: "🛠️"
    }
];

// Arreglo donde se almacenarán los registros del formulario
let registros = [];

// Elementos del formulario y contenedores
const formulario = document.getElementById("formulario");
const nombre = document.getElementById("nombre");
const correo = document.getElementById("correo");
const categoria = document.getElementById("categoria");
const descripcion = document.getElementById("descripcion");

const errorNombre = document.getElementById("errorNombre");
const errorCorreo = document.getElementById("errorCorreo");
const errorCategoria = document.getElementById("errorCategoria");
const errorDescripcion = document.getElementById("errorDescripcion");

const mensajeGeneral = document.getElementById("mensajeGeneral");
const listaRegistros = document.getElementById("listaRegistros");
const listaServicios = document.getElementById("listaServicios"); // NUEVO
const contador = document.getElementById("contador");

// ===============================
// NUEVO: RENDERIZAR SERVICIOS DINÁMICAMENTE (Estructura Repetitiva)
// ===============================
function cargarServicios() {
    listaServicios.innerHTML = "";
    servicios.forEach(function (servicio) {
        listaServicios.innerHTML += `
            <div class="col-md-4">
                <div class="card h-100 text-center p-4">
                    <div class="fs-1 mb-3">${servicio.icono}</div>
                    <div class="card-body">
                        <h5 class="card-title text-primary">${servicio.titulo}</h5>
                        <p class="card-text text-muted">${servicio.descripcion}</p>
                    </div>
                </div>
            </div>
        `;
    });
}

// ===============================
// VALIDACIONES (SEMANA 6) - Se conservan intactas
// ===============================
function validarNombre() {
    if (nombre.value.trim().length < 3) {
        nombre.classList.add("is-invalid");
        nombre.classList.remove("is-valid");
        errorNombre.textContent = "Debe ingresar al menos 3 caracteres.";
        return false;
    }
    nombre.classList.remove("is-invalid");
    nombre.classList.add("is-valid");S
    errorNombre.textContent = "";
    return true;
}

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

// Escuchadores de eventos
nombre.addEventListener("input", validarNombre);
nombre.addEventListener("blur", validarNombre);
correo.addEventListener("input", validarCorreo);
correo.addEventListener("blur", validarCorreo);
categoria.addEventListener("change", validarCategoria);
categoria.addEventListener("blur", validarCategoria);
descripcion.addEventListener("input", validarDescripcion);
descripcion.addEventListener("blur", validarDescripcion);

// ===============================
// REGISTRAR NUEVOS DATOS
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
// MOSTRAR REGISTROS (Con Condicionales requeridos)
// ===============================
function mostrarRegistros() {
    listaRegistros.innerHTML = "";

    // IMPLEMENTACIÓN DE CONDICIONAL SEGÚN EL ESTADO DE LOS DATOS
    if (registros.length === 0) {
        listaRegistros.innerHTML = `
            <div class="col-12 text-center">
                <div class="alert alert-info py-4" role="alert">
                    <p class="mb-0 fw-bold">No existen registros actuales en el sistema.</p>
                    <small class="text-muted">Utilice el formulario de la izquierda para agregar nueva información.</small>
                </div>
            </div>
        `;
    } else {
        // Estructura repetitiva para mostrar registros existentes
        registros.forEach(function (registro, indice) {
            listaRegistros.innerHTML += `
                <div class="col-md-6">
                    <div class="registro">
                        <h5>${registro.nombre}</h5>
                        <p><strong>Correo:</strong> ${registro.correo}</p>
                        <p><strong>Categoría:</strong> ${registro.categoria}</p>
                        <p><strong>Descripción:</strong> ${registro.descripcion}</p>
                        <button class="btn btn-danger btn-sm mt-2" onclick="eliminarRegistro(${indice})">
                            Eliminar
                        </button>
                    </div>
                </div>
            `;
        });
    }

    contador.textContent = registros.length;
}

// ===============================
// ELIMINAR REGISTRO
// ===============================
function eliminarRegistro(indice) {
    registros.splice(indice, 1);
    mostrarRegistros();
}

window.eliminarRegistro = eliminarRegistro;

// --- Inicialización al cargar la página ---
document.addEventListener("DOMContentLoaded", function() {
    cargarServicios();   // Carga las tarjetas dinámicas de servicios
    mostrarRegistros();  // Muestra el mensaje condicional de "vacío" de inicio
});