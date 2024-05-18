$(".dropdown").click(function() {

    console.log('dropdown clicked')

    let games = $(this).closest('.category').find('.games')
    games.slideToggle("500");

})

$(".game").click(function() {
    let title = $(this).text()
    window.location.href = "/game/game/" + title
})