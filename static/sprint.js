$(document).ready(function(){

    $(".success_new_post").hide();
    $(".error_new_post").hide();

    $('.check' ).on('click', function(){

        progress()
        id = $(this).attr('id');
        day = $("#day_sel").val();
        action  = $(this).is(':checked');

        var data = [
            {"day": day},
            {"id_post": id},
            {"action": action}
        ];
        console.log(id, day, action);

        $.ajax({
          type: "POST",
          url: "/save_check",
          data: JSON.stringify(data),
          contentType: "application/json",
          dataType: 'json'
        });
    });

    function progress(){
        var checked = $("input:checkbox:checked").length
        var total = $("input:checkbox").length
        $("#progress").html('Progress:<br><br>' + checked + '/' + total)
    }

    progress();



    $('#newPost').click(function(){
        var userid = $(this).data('id');
        $('#empModal').modal('show');
    });

    $('#save_post').click(function(){
        var userid = $(this).data('id');
        $('#empModal').modal('show');
        new_day = $('#new_day').val();
        new_sprinter = $('#new_sprinter').val();
        new_link = $('#new_link').val();

        var data = {
            "new_day": new_day,
            "new_sprinter": new_sprinter,
            "new_link": new_link
        }
        ;

        //var data = JSON.stringify(
        //    {"new_day": new_day},
        //    {"new_sprinter": new_sprinter},
        //    {"new_link": new_link}
        //);

        $.ajax({
            type: "POST",
            url: "/new_post",
            data: JSON.stringify(data),
            contentType: "application/json",
            dataType: 'json',
        })
        .always(function(){
            $('#empModal').modal('hide');
        })
        .done(function(){
            console.log('ok');
            $(".success_new_post").show();
            setTimeout(function(){
                $(".success_new_post").hide();
            }, 3000);
        })
        .fail(function(){
            console.log('error');
            $(".error_new_post").show();
            setTimeout(function(){
                $(".error_new_post").hide();
            }, 3000);
        });
    });
});
