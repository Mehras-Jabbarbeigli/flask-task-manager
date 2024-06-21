document.querySelectorAll('.mark-complete-btn').forEach(item => {
    item.addEventListener('click', event => {
        event.preventDefault();

        const btn = event.target;
        const todoSno = btn.getAttribute('data-todo-sno');

        fetch(`/complete/${todoSno}`, {
            method: 'POST',
        }).then(response => {
            console.log(response);
            if (response.ok) {
                location.reload();
            }
        }).catch(error => {
            console.error('Error:', error);
        });
    });
});
