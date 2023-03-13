function show_error(msg, action_status) {
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
    }, 3000)
}
function change_number_answers(url, data) {
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data, status) {
            if (status == 'success'){
                action_status = data['action_status'];
                msg = data['msg'];
            } else {
                action_status = 'danger'
                msg = 'Что-то пошло не так, повторите попытку'
            };
            show_error(msg, action_status);
        },

        error: function (request, status, error) {
            action_status = 'danger';
            msg = error;
            show_error(msg, action_status);
        },
    });
};

function change_status(url, data) {
    $.ajax({
        url: url,
        type: "POST",
        data: data,
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
            msg = error;
            show_error(msg, action_status);
        }
    });
};


$(document).ready(function() {
    $('#change_status').on('submit', function(event){
        event.preventDefault();
        var url = '/dictionary/change_status/';
        var dictionary_pk = $('#id_dictionary_pk').val();
        var data = {
            'dictionary_pk': dictionary_pk,
        };
        change_status(url, data);
    });

    $('#id_required_answers')
    .on('change', function (event) {
        var url = '/lesson/change_number_answers/';
        var lesson_pk = $('#id_lesson_pk').val();
        var required_answers = this.value;
        var data = {
                'required_answers': required_answers,
                'lesson_pk': lesson_pk,
        };
        change_number_answers(url, data)
    });
});






