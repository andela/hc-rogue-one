$(function() {

    $(".member-remove").click(function() {
        var $this = $(this);

        $("#rtm-email").text($this.data("email"));
        $("#remove-team-member-email").val($this.data("email"));
        console.log($this.data("email"))
        $('#remove-team-member-modal').modal("show");

        return false;
    });

    $(".member-email").click(function(){
        $("#priority-team-member-email").text($(this).data("priority-email"));
        $("#email_input").val($(this).data("priority-email"));


        // return false;
    });

});