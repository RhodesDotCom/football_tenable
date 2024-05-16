$(".dropdown").click(function() {

    console.log('dropdown clicked')

    let games = $(this).closest('.category').find('.games')
    games.slideToggle("500");

})