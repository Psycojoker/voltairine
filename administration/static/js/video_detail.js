function editVideoDetailsController($scope) {
    $scope.inEditMode = false;

    $scope.toggleEditMode = function() {
        if ($scope.inEditMode == true) {
            $scope.title = $("#id_title").val();
            $scope.film_name = $("#id_film_name").val();
            $scope.realisation = $("#id_realisation").val();
            $scope.production = $("#id_production").val();
            $scope.photo_direction = $("#id_photo_direction").val();
            $scope.observations = $("#id_observations").val();
            $scope.section_id = $("#id_section").val();

            $.post("", {
                title: $scope.title,
                film_name: $scope.film_name,
                realisation: $scope.realisation,
                production: $scope.production,
                photo_direction: $scope.photo_direction,
                observations: $scope.observations,
                section: $("#id_section").val(),
                "csrfmiddlewaretoken": $('input[name="csrfmiddlewaretoken"]').val()
            }).done(function(section) {
                $scope.inEditMode = false;
                $scope.section = section;
                $scope.$digest();
            })
        } else {
            $scope.inEditMode = true;
        }
    }
}
