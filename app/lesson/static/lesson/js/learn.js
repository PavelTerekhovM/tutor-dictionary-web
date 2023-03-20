function show_msg(msg, action_status) {
    const div_alert = document.querySelector('.alert');
    div_alert.innerHTML = ''
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

function check_card(url, data) {
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        success: function(data, status) {
            if (status == 'success'){
                var action_status = data['status'];
                var msg = data['msg'];
                var next_card = data['next_card'];
                var card = JSON.parse(data['card']);
                $('#card-header').html(
                    card[0].fields.translations + ' - ' + card[0].fields.body
                );
                $('#example').html(
                            'Пример: ' + card[0].fields.example
                        );
                $('#id_body').hide();
                $('#check_card_btn').hide();
                if (next_card == true){
                    $('#next_card_btn').show();
                };
            } else {
                action_status = 'danger'
                msg = 'Что-то пошло не так, повторите попытку'
            };
            if (msg) {
                show_msg(msg, action_status);
            };
        },
        error: function (request, status, error) {
            console.log(error)
            action_status = 'danger';
            msg = error;
            show_msg(msg, action_status);
        }
    });
};

function get_next_card(url) {
    $.ajax({
        url: url,
        success: function(data, status) {
            if (status == 'success'){
                var action_status = data['status'];
                var msg = data['msg'];
                var next_card = data['next_card'];
                var card_pk = data['card_pk'];
                var reverse = data['reverse'];
                var card = JSON.parse(data['card']);
                $('#next_card_btn').hide();
                $('#check_card_btn').show();
                if (reverse == 'reverse') {
                    $('#card-header').html(
                            card[0].fields.body
                        );
                    $('#example').html(
                            'Пример: ' + card[0].fields.example.split('—')[0]
                        );
                } else {
                    $('#card-header').html(
                            card[0].fields.translations
                        );
                    $('#example').html(
                            'Пример: ' + card[0].fields.example.split('—')[1]
                        );
                };

                $('#id_card_pk').val(card_pk);
                $('#id_body').show();
            } else {
                action_status = 'danger'
                msg = 'Что-то пошло не так, повторите попытку'
            };
            if (msg) {
                show_msg(msg, action_status);
            };
        },
        error: function (request, status, error) {
            action_status = 'danger';
            msg = error;
            show_msg(msg, action_status);
        }
    });
};


$(document).ready(function() {
    var url = $("#url").attr("data-url");
    $('#check_card').on('submit', function(event){
        event.preventDefault();
        var card_pk = $('#id_card_pk').val();
        var translations = $('#id_translations').val();
        var body = $('#id_body').val();
        var data = {
            'card_pk': card_pk,
            'translations': translations,
            'body': body,
        };
        $('#check_card')[0].reset();
        check_card(url, data);
    });
    $('#next_card_btn').on('click', function(event){
        event.preventDefault();
        get_next_card(url);
    });
});






