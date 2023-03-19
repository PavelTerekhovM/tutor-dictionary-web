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
    }, 10000)
}

function check_card(url, data) {
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data, status) {
            console.log(data);
            if (status == 'success'){
                action_status = data['action_status'];
                msg = data['msg'];
            } else {
                action_status = 'error'
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
    $('#check_card').on('submit', function(event){
        event.preventDefault();
        $('#check_card')[0].reset();
        var url = '/lesson/learn/0/13/';
        var card_pk = $('#id_card_pk').val();
        var translations = $('#id_translations').val();
        var body = $('#id_body').val();
        var data = {
            'card_pk': card_pk,
            'translations': translations,
            'body': body,
        };
        check_card(url, data);
    });
});






