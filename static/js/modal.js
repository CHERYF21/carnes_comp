const openModal = document.querySelector('.openModalBtn');
const modal = document.querySelector('.modal');
const closeModal = document.querySelector('.modal__close');

openModal.addEventListener('click', (e)=>{
    e.preventDefault();
    modal.classList.add('modal--show');
});

closeModal.addEventListener('click', (e)=>{
    e.preventDefault();
    modal.classList.remove('modal--show');
});

// document.getElementById('registrationForm').addEventListener('submit', function(event){
//     event.preventDefault();

//     fetch('{{url_for("registro")}}', {
//         method: 'POST',
//         body: formData
//     })
//     .then(response => response.json())
//     .then(data => {
//         if(data.success){
//             document.getElementById('msg').textContent = data.msg;
//         }else{
//             document.getElementById('msg').textContent = data.msg;
//         }

//         if(data.success){
//             modal.classList.remove('modal--show');
//         }
//     })
//     .catch(error => console.error('Error', error));
// });