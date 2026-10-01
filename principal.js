// ===== CARRITO =====
const CLAVE = "tecstore_carrito";
const tbody = document.querySelector("#lista-carrito tbody");
const contador = document.getElementById("contador-carrito");
const totalEl = document.getElementById("total-carrito");
const vacioEl = document.getElementById("carrito-vacio");
const btnVaciar = document.getElementById("vaciar-carrito");
const panel = document.getElementById("carrito");
const iconCarrito = document.getElementById("icon-carrito");

let carrito = [];
try { carrito = JSON.parse(localStorage.getItem(CLAVE)) || []; } catch (e) { carrito = []; }

const formatear = n => "$" + n.toLocaleString("es-CL");
const precioANumero = txt => parseInt(txt.replace(/\D/g, ""), 10) || 0;
const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(carrito)); } catch (e) {} };

function pintarCarrito() {
    tbody.innerHTML = "";
    carrito.forEach((p, i) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><img src="${p.imagen}" alt="" width="50"></td>
            <td>${p.nombre}</td>
            <td>${formatear(p.precio)}</td>
            <td>${p.cantidad}</td>
            <td><a href="#" class="borrar" data-index="${i}">X</a></td>`;
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
        const precio = precioANumero(item.querySelector(".price").textContent);
        const existente = carrito.find(p => p.nombre === nombre);
        if (existente) existente.cantidad++;
        else carrito.push({ nombre, imagen, precio, cantidad: 1 });
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
