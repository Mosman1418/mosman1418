$(function(){
    $("#wall").imagesLoaded( function(){
        $("#wall").isotope({
                itemSelector: '.cell',
                layoutMode: 'masonry'
            });
    });
});
