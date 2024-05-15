$(".dropdown").click(function() {

    console.log('dropdown clicked')

    let games = $(this).closest('.categories').find('.games')
    games.slideToggle("500");

})