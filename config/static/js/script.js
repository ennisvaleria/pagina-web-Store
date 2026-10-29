const container = document.querySelector(".container");
const btnSignIn = document.getElementById("btn-sign-in");
const btnSignUp = document.getElementById("btn-sign-up");

btnSignIn.addEventListener("click",()=>{
    container.classList.remove("toggle");
});

btnSignUp.addEventListener("click",()=>{
    container.classList.add("toggle");
});

function guardarDato(nombre, valor) {
    document.cookie = nombre + "=" + escape(valor) + ";path=/;max-age=" + (60 * 60 * 24 * 30);
}

function leerDato(nombre) {
    var search = nombre + "=";
    if (document.cookie.length > 0) {
        var i = document.cookie.indexOf(search);
        if (i != -1) {
            i += search.length;
            var j = document.cookie.indexOf(";", i);
            if (j == -1) j = document.cookie.length;
            return unescape(document.cookie.substring(i, j));
        }
    }
    return null;
}

function registrarUsuario() {
    var nombre = document.getElementById('nombre').value.trim();
    var apellido = document.getElementById('apellido').value.trim();
    var direccion = document.getElementById('direccion').value.trim();
    var correo = document.getElementById('correo').value.trim().toLowerCase();
    var contrasena = document.getElementById('contraseña').value;

    if (nombre == "") {
        alert("Ingresa tu nombre.");
        document.getElementById('nombre').focus();
        return;
    }
    if (apellido == "") {
        alert("Ingresa tu apellido.");
        document.getElementById('apellido').focus();
        return;
    }
    if (direccion == "") {
        alert("Ingresa tu dirección.");
        document.getElementById('direccion').focus();
        return;
    }
    if (correo == "") {
        alert("Ingresa tu correo.");
        document.getElementById('correo').focus();
        return;
    }

    var patronCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!patronCorreo.test(correo)) {
        alert("Ingresa un correo válido");
        document.getElementById('correo').focus();
        return;
    }

    if (contrasena == "") {
        alert("Ingresa tu contraseña.");
        document.getElementById('contraseña').focus();
        return;
    }

    var usuariosExistentes = leerDato("listaCorreos");

    if (usuariosExistentes != null) {
        if (usuariosExistentes.split(",").indexOf(correo) != -1) {
            alert("El correo ya está registrado.");
            document.getElementById('correo').focus();
            return;
        }
        usuariosExistentes += "," + correo;
    } else {
        usuariosExistentes = correo;
    }

    guardarDato("listaCorreos", usuariosExistentes);
    guardarDato("pass_" + correo, contrasena);
    guardarDato("nombre_" + correo, nombre);
    guardarDato("apellido_" + correo, apellido);
    guardarDato("direccion_" + correo, direccion);

    alert("Cuenta creada exitosamente.");
    container.classList.remove("toggle");
}

function iniciarSesion() {
    var correo = document.getElementById('correo-inicio').value.trim().toLowerCase();
    var contrasena = document.getElementById('contraseña-login').value;

    if (correo == "") {
        alert("Ingresa tu correo.");
        document.getElementById('correo-inicio').focus();
        return;
    }
    if (contrasena == "") {
        alert("Ingresa tu contraseña.");
        document.getElementById('contraseña-login').focus();
        return;
    }

    var passGuardada = leerDato("pass_" + correo);

    if (passGuardada == null || passGuardada != contrasena) {
        alert("Correo o contraseña incorrectos.");
        return;
    }

    guardarDato("usuarioSesion", correo);
    alert("Bienvenido al sistema.");
    window.location.href = "principal.html";
}