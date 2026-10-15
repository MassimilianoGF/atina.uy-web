// Envía el formulario de contacto sin salir de atina.uy y lleva a /gracias/.
// Si algo falla, muestra un aviso; sin JavaScript el formulario se envía igual.
(function () {
  var form = document.getElementById("contacto");
  if (!form || !window.fetch) return;
  var error = document.getElementById("form-error");
  var button = form.querySelector("button[type=submit]");

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    error.hidden = true;
    button.disabled = true;
    button.textContent = "Enviando…";
    fetch(form.dataset.ajax, {
      method: "POST",
      headers: { Accept: "application/json" },
      body: new FormData(form)
    })
      .then(function (r) { return r.json().then(function (d) { return r.ok && String(d.success) === "true"; }); })
      .then(function (ok) {
        if (!ok) throw new Error("envío rechazado");
        window.location.href = "/gracias/";
      })
      .catch(function () {
        error.hidden = false;
        button.disabled = false;
        button.textContent = "Enviar consulta";
      });
  });
})();
