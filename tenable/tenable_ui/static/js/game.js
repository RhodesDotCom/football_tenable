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
        
        headings = Object.keys(data[0])

        var seasonIndex = headings.indexOf('season');
        if (seasonIndex > -1) {
            headings.splice(seasonIndex, 1);
            headings.unshift('season');
        }

        var $tr = $('<tr></tr>');
        $.each(headings, function(index, heading) {
            var $th = $('<th></th').text(heading);
            $tr.append($th)
        });
        $table.append($tr)

        $.each(data, function(index, row) {
            var $tr = $('<tr></tr>');
            $.each(headings, function(index, heading) {
                var $td = $('<td></td>').text(row[heading]);
                $tr.append($td);
            });
            $table.append($tr);
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