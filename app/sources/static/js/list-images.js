$(function(){
    $("#wall").imagesLoaded( function(){
        $("#wall").isotope({
                itemSelector: '.cell',
                layoutMode: 'masonry'
            });
    });
    $("#wall").infinitescroll({
        navSelector  : '.pager',    // selector for the paged navigation
        nextSelector : '.pager li a',  // selector for the NEXT link (to page 2)
        itemSelector : '.cell',     // selector for all items you'll retrieve
        loading: {
            finishedMsg: 'No more pages to load.',
            img: 'http://i.imgur.com/qkKy8.gif'
          }
        },
        // call Isotope as a callback
        function( newElements ) {
          $container.isotope('appended', $(newElements));
        }
    );
});
