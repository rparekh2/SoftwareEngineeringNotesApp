$(document).ready(function() {
    $(".default").on('click', function(){
        if ( $(this).hasClass('button') ) {
            $(this).removeClass('button');
            $(this).addClass('like')
            $(this).html('Liked!')
        } else {
            $(this).removeClass('like');
            $(this).addClass('button');
            $(this).html('Like?')
        }

    })
});
