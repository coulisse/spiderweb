document.addEventListener('DOMContentLoaded', function() {
    // Select all forms with the class 'delete-user-form'
    const deleteForms = document.querySelectorAll('.delete-user-form');

    deleteForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            const username = this.action.split('/').pop(); // Extracts username from the form's action URL
            const confirmation = confirm(`Are you sure you want to delete ${username}?`);

            if (!confirmation) {
                event.preventDefault(); // Prevent the form from submitting if the user clicks "Cancel"
            }
        });
    });
});
