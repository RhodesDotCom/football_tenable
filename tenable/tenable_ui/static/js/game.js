function display_info(player, data) {
    if (data.length > 0) {
        $('#info').remove();

        if (typeof data === 'string') {
            try {
                data = JSON.parse(data);
            } catch (e) {
                console.error("Error parsing JSON:", e);
                return;
            }
        }

        var $infoDiv = $('<div id="info" class="curved-border"></div>');
        $infoDiv.append('<h2 class="center-align">' + player + '</h2>');

        var $table = $('<table class="full-width" id="info-table"></table>');
        $table.append('<tr><th>Season</th><th>Goals</th></tr>');

        $.each(data, function(index, row) {
            $table.append('<tr><td>' + row['season'] + '</td><td>' + row['goals'] + '</td></tr>');
        });
        $infoDiv.append($table);
        
        $('#left-side').append($infoDiv);
    }
}

$('#guess-form').submit(function(event) {
    let input = $('#guess');
    if (input.val().trim() === '') {
        event.preventDefault();
    }
})

$("#game-over").click(function() {
    e.preventDefault()
    $
})

$(".answer").click(function() {
    let answer = $(this).text().trim();

    $.ajax({
        url: '/game/get_info/' + answer ,
        type: 'GET',
        success: function(response) {

            display_info(answer, response);
        },
        error: function(xhr, status, error) {
            console.error(error)
        }
    })
})

$(function() {
    $('#guess').autocomplete({
        source: function(request, response) {

            let category = $('#guess').data('category');

            $.ajax({
                url: "/game/autocomplete",
                dataType: 'json',
                data: {
                    query: request.term,
                    category: category
                },
                success: function(data) {
                    response(data);
                }
            });
        },
        minLength: 3,
    })
})