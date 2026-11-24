
const CLAVE = "tecstore_carrito_v2";
const tbody = document.querySelector("#lista-carrito tbody");
const contador = document.getElementById("contador-carrito");
const totalEl = document.getElementById("total-carrito");
const vacioEl = document.getElementById("carrito-vacio");
const btnVaciar = document.getElementById("vaciar-carrito");
const btnFinalizar = document.getElementById("finalizar-compra");
const panel = document.getElementById("carrito");
const iconCarrito = document.getElementById("icon-carrito");

let carrito = [];
try { carrito = JSON.parse(localStorage.getItem(CLAVE)) || []; } catch (e) { carrito = []; }

const formatear = n => "$" + n.toLocaleString("es-CL");
const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(carrito)); } catch (e) {} };

function pintarCarrito() {
    tbody.innerHTML = "";
    carrito.forEach((p, i) => {
        const tr = document.createElement("tr");
        const imagenTd = document.createElement("td");
        const imagen = document.createElement("img");
        imagen.src = p.imagen;
        imagen.alt = "";
        imagen.width = 50;
        imagenTd.appendChild(imagen);
        const nombreTd = document.createElement("td");
        nombreTd.textContent = p.nombre;
        const precioTd = document.createElement("td");
        precioTd.textContent = formatear(p.precio);
        const cantidadTd = document.createElement("td");
        cantidadTd.textContent = p.cantidad;
        const accionesTd = document.createElement("td");
        const borrar = document.createElement("a");
        borrar.href = "#";
        borrar.className = "borrar";
        borrar.dataset.index = i;
        borrar.textContent = "X";
        accionesTd.appendChild(borrar);
        tr.append(imagenTd, nombreTd, precioTd, cantidadTd, accionesTd);
        tbody.appendChild(tr);
    });
    const unidades = carrito.reduce((a, p) => a + p.cantidad, 0);
    const total = carrito.reduce((a, p) => a + p.precio * p.cantidad, 0);
    contador.textContent = unidades;
    contador.style.display = unidades ? "flex" : "none";
    totalEl.textContent = formatear(total);
    vacioEl.style.display = unidades ? "none" : "block";
    guardar();
}

// Añadir al carrito (botones del catálogo)
document.querySelectorAll(".item .info-item button").forEach(btn => {
    btn.addEventListener("click", () => {
        const item = btn.closest(".item");
        const nombre = item.querySelector("h3").textContent.trim();
        const imagen = item.querySelector("img").getAttribute("src");
        const productoId = Number(btn.dataset.productId);
        const precio = Number(btn.dataset.price);
        const existente = carrito.find(p => p.id === productoId);
        if (existente) existente.cantidad++;
        else carrito.push({ id: productoId, nombre, imagen, precio, cantidad: 1 });
        pintarCarrito();
        btn.textContent = "¡Añadido!";
        setTimeout(() => (btn.textContent = "Añadir al carrito"), 900);
    });
});

// Eliminar un producto (resta 1 unidad)
tbody.addEventListener("click", e => {
    const borrar = e.target.closest(".borrar");
    if (!borrar) return;
    e.preventDefault();
    const i = +borrar.dataset.index;
    if (carrito[i].cantidad > 1) carrito[i].cantidad--;
    else carrito.splice(i, 1);
    pintarCarrito();
});

btnVaciar.addEventListener("click", () => { carrito = []; pintarCarrito(); });

function obtenerCookie(nombre) {
    const cookie = document.cookie.split("; ").find(par => par.startsWith(`${nombre}=`));
    return cookie ? decodeURIComponent(cookie.split("=").slice(1).join("=")) : "";
}

btnFinalizar.addEventListener("click", async () => {
    if (!carrito.length) {
        alert("Agrega productos al carrito antes de finalizar la compra.");
        return;
    }

    btnFinalizar.disabled = true;
    try {
        const respuesta = await fetch("/checkout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCookie("csrftoken"),
            },
            body: JSON.stringify({
                items: carrito.map(({ id, cantidad }) => ({ id, cantidad })),
            }),
        });
        const resultado = await respuesta.json();
        if (!respuesta.ok) {
            if (respuesta.status === 401) {
                window.location.href = "/";
                return;
            }
            throw new Error(resultado.error || "No se pudo completar la compra.");
        }

        carrito = [];
        pintarCarrito();
        alert(`Compra realizada. Tu pedido es el #${resultado.pedido_id}.`);
        window.location.href = "/mis-pedidos";
    } catch (error) {
        alert(error.message || "No se pudo completar la compra. Intenta de nuevo.");
    } finally {
        btnFinalizar.disabled = false;
    }
});

// En celular (sin hover) el icono abre/cierra el carrito
iconCarrito.addEventListener("click", () => panel.classList.toggle("abierto"));

pintarCarrito();

// ===== BUSCADOR =====
const buscador = document.getElementById("buscador");
const sinResultados = document.getElementById("sin-resultados");
const normalizar = t => t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

buscador.addEventListener("input", () => {
    const q = normalizar(buscador.value.trim());
    let visibles = 0;
    document.querySelectorAll(".container-items .item").forEach(item => {
        const texto = normalizar(item.textContent);
        const ok = texto.includes(q);
        item.style.display = ok ? "" : "none";
        if (ok) visibles++;
    });
    sinResultados.style.display = visibles ? "none" : "block";
});

document.addEventListener("DOMContentLoaded", () => {
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            window.location.href = btnLogout.dataset.url;
        });
    }
});