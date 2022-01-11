


$(document).ready(function(){

    $('.check' ).on('click', function(){

        id = $(this).attr('id');
        day = $("#filter_day").val();
        author = $("#author").val();
        action  = $(this).is(':checked');

        var data = [
            {"day": day},
            {"author": author},
            {"id_post": id},
            {"action": action}
        ];
        console.log(id, day, author, action);

        $.ajax({
          type: "POST",
          url: "/track",
          data: JSON.stringify(data),
          contentType: "application/json",
          dataType: 'json'
        });
    });

});
