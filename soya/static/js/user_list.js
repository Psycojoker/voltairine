$(function() {
    $('[data-toggle="tooltip"]').tooltip();

    $(".delete-all-checkbox").click(function(event) {
        checked = event.currentTarget.checked;
        $(".delete-checkbox").each(function(index, checkbox) {  checkbox.checked = checked })
        $(".delete-all-checkbox").each(function(index, checkbox) {  checkbox.checked = checked })
        $("#delete-users-button").attr("disabled", checked ? false : "disabled");
    });

    $(".delete-checkbox").click(function() {
        var checked_values = $.map($.makeArray($(".delete-checkbox")), function(checkbox) { return checkbox.checked });

        // if one checkbox is not checked
        if (checked_values.indexOf(false) != -1) {
            $(".delete-all-checkbox").each(function(index, checkbox) {  checkbox.checked = false })
        } else {
            $(".delete-all-checkbox").each(function(index, checkbox) {  checkbox.checked = true })
        }

        // if one checkbox IS checked
        if (checked_values.indexOf(true) != -1) {
            $("#delete-users-button").attr("disabled", null);
        } else {
            $("#delete-users-button").attr("disabled", "disabled");
        }
    })

    $("#delete-users").submit(function(event) {
        if (confirm("Voulez vous vraiment Supprimer ces utilisateurs ?")) {
            // do nothing
        } else {
            event.preventDefault();
        }
    })
});
