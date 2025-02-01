// Fromatacao da tabela e da tabela interna
document.addEventListener('DOMContentLoaded', function() {
  const expandButtons = document.querySelectorAll('.expand-button i');
  
  expandButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Encontra a próxima linha que contém a tabela interna
      const parentRow = this.closest('tr');
      const innerTableRow = parentRow.nextElementSibling;
      const innerTable = innerTableRow.querySelector('.inner-table');
      
      // Toggle da classe para rotacionar o ícone
      this.classList.toggle('rotate-icon');
      
      // Toggle da visibilidade da tabela interna
      if (innerTable.style.display === 'none' || !innerTable.style.display) {
        innerTable.style.display = 'block';
      } else {
        innerTable.style.display = 'none';
      }
    });
  });
});
