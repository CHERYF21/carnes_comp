document.addEventListener('DOMContentLoaded', () => {
    const abrirModalElements = document.querySelectorAll('.activate');
    const modalupdate = document.querySelector('.modal-update');
    const modalclose = document.querySelector('.modalclose');
  
    abrirModalElements.forEach(abrirModal => {
      abrirModal.addEventListener('click', (e) => {
        e.preventDefault();
        modalupdate.classList.add('modalview');
        // Aquí puedes agregar lógica para cargar datos específicos en el modal si es necesario.
      });
    });
  
    modalclose.addEventListener('click', (e) => {
      e.preventDefault();
      modalupdate.classList.remove('modalview');
    });
  });
  