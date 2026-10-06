// Comportamentos gerais do sistema, carregados em todas as páginas.

document.addEventListener('DOMContentLoaded', function () {
    // Abre e fecha o menu em telas pequenas.
    var botaoMenu = document.getElementById('botao-menu');
    var menu = document.getElementById('menu-principal');

    if (botaoMenu && menu) {
        botaoMenu.addEventListener('click', function () {
            var fechado = menu.classList.toggle('hidden');
            menu.classList.toggle('flex', !fechado);
            botaoMenu.setAttribute('aria-expanded', String(!fechado));
        });
    }

    // Pede confirmação antes de enviar formulários marcados com data-confirmar.
    // Exemplo: <form data-confirmar="Deseja remover este cliente?">
    document.querySelectorAll('form[data-confirmar]').forEach(function (formulario) {
        formulario.addEventListener('submit', function (evento) {
            if (!window.confirm(formulario.dataset.confirmar)) {
                evento.preventDefault();
            }
        });
    });
});
