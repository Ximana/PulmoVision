function initializeDeleteConfirmation() {
    document.addEventListener('DOMContentLoaded', function() {
        var confirmDeleteModal = document.getElementById('confirmDeleteModal');
        confirmDeleteModal.addEventListener('show.bs.modal', function(event) {
            var button = event.relatedTarget;
            var usuarioId = button.getAttribute('data-id');
            var usuarioNome = button.getAttribute('data-nome');

            var modalBody = confirmDeleteModal.querySelector('.modal-body #usuarioNome');
            var deleteForm = confirmDeleteModal.querySelector('#deleteForm');

            modalBody.textContent = usuarioNome;
            deleteForm.action = '/usuarios/excluir/' + usuarioId;
        });
    });
}

// Chama a função para inicializar a confirmação de exclusão
initializeDeleteConfirmation();
