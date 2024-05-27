document.addEventListener('DOMContentLoaded', (event) => {
    const openModalBtn = document.querySelector('.openModalBtn');
    const modal = document.querySelector('.modal');
    const closeModalBtn = document.querySelector('.modal__close');
  
    openModalBtn.addEventListener('click', () => {
      modal.classList.add('modal--show');
    });
  
    closeModalBtn.addEventListener('click', () => {
      modal.classList.remove('modal--show');
    });
  
    window.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('modal--show');
      }
    });
  });
  