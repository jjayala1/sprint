


$(document).ready(function(){

    $('.check' ).on('click', function(){

        progress()
        id = $(this).attr('id');
        day = $("#filter_day").val();
        action  = $(this).is(':checked');

        var data = [
            {"day": day},
            {"id_post": id},
            {"action": action}
        ];
        console.log(id, day, action);

        $.ajax({
          type: "POST",
          url: "/track",
          data: JSON.stringify(data),
          contentType: "application/json",
          dataType: 'json'
        });
    });

    function progress(){
        var checked = $("input:checkbox:checked").length
        var total = $("input:checkbox").length
        $("#progress").html(checked + '/' + total)
    }

    progress();
});
