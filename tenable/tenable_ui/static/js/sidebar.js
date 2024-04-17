$(".open-sidepanel").click(function() {
    let sidepanel = $(".sidepanel")
    let main = $(".main")

    let size = "250px"
    
    sidepanel.width(size)
    main.css('margin-left', size)
})
$(".closebtn").click(function() {
    let sidepanel = $(".sidepanel")
    let main = $(".main")
    sidepanel.width("0")
    main.css('margin-left', 0)
})
