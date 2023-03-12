$(document).ready(function() {
    $('#change_status').on('submit', function(event){
       event.preventDefault();
       change_status();
    });

    function show_error() {
        const div_alert = document.querySelector('.alert');
        const error_div = document.createElement("div");
        error_div.classList.add(`alert-${action_status}`, 'my-3', 'alert');
        error_div.setAttribute('role', 'alert');
        const error_msg = document.createElement("p");
        error_msg.textContent = msg;
        error_div.appendChild(error_msg);
        div_alert.appendChild(error_div);
        setTimeout(() => {
            error_div.remove()
        }, 2000)
    }

    function change_status() {
        $.ajax({
            url: '/dictionary/change_status/',  // '{% url "dictionary:change_status" %}'  -- can't work
            type: "POST",
            data: {
                dictionary_pk: $('#id_dictionary_pk').val(),
            },
            success: function(data, status) {
                if (status == 'success'){
                    action_status = data['action_status'];
                    msg = data['msg'];
                    dictionary_status = data['dictionary_status'];
                    if (action_status == 'success') {
                        if (dictionary_status == 'private') {
                            button = 'Сделать публичным';
                        } else {
                            button = 'Сделать приватным';
                        };
                        $('.change_status_bg').html(
                            dictionary_status.charAt(0).toUpperCase() + dictionary_status.slice(1)
                        );
                        $('.change_status_btn').html(button);
                    };
                } else {
                    action_status = 'danger'
                    msg = 'Что-то пошло не так, повторите попытку'
                };
                show_error(msg, action_status);
            },
            error: function (request, status, error) {
                action_status = 'danger';
                msg = 'Что-то пошло не так, повторите попытку';
                show_error();
            }
        });
    };
});
