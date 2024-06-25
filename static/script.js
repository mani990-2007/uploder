$(function() {
    // Animation for fade-in effect on page load
    $('.login-container, .register-container, .dashboard-container, .account-container, .upload-container').fadeIn(1000);

    // Form validation for login form
    $('#login-form').submit(function(event) {
        var username = $('#username').val();
        var password = $('#password').val();
        if (!username || !password) {
            $('#login-error').text('Please fill in all fields.');
            event.preventDefault();
        }
    });

    // Form validation for register form
    $('#register-form').submit(function(event) {
        var username = $('#username').val();
        var password = $('#password').val();
        if (!username || !password) {
            $('#register-error').text('Please fill in all fields.');
            event.preventDefault();
        }
    });

    // Form validation for account form
    $('#account-form').submit(function(event) {
        var old_password = $('#old_password').val();
        var new_username = $('#new_username').val();
        var new_password = $('#new_password').val();
        if (!old_password) {
            $('#account-error').text('Current password is required.');
            event.preventDefault();
        }
        if (!new_username && !new_password) {
            $('#account-error').text('Please fill in at least one field.');
            event.preventDefault();
        }
    });

    // Clear validation message on input focus
    $('input').focus(function() {
        $(this).css('border-color', '#ccc');
        $('#login-error, #register-error, #account-error').text('');
    });

    // JavaScript for handling edit modal

    // Get the modal
    var modal = document.getElementById('editModal');

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on edit button, open the modal
    $('.edit-btn').click(function() {
        var tr = $(this).closest('tr');
        var filename = tr.data('filename');
        var editContent = tr.find('td:first').text().trim(); // Assuming file content is in the first cell

        $('#edit-filename').val(filename);
        $('#edit-content').val(editContent);

        modal.style.display = "block";
    });

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    };

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Form validation for edit form
    $('#edit-form').submit(function(event) {
        var content = $('#edit-content').val().trim();
        if (!content) {
            $('#edit-error').text('Please fill in the content.');
            event.preventDefault();
        }
    });
});
