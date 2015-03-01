function editVideoDetailsController($scope) {
    $scope.inEditMode = false;

    $scope.toggleEditMode = function() {
        $scope.inEditMode = !$scope.inEditMode;
        if ($scope.inEditMode == false) {
            $scope.title = $("#id_title").val();
            $scope.film_name = $("#id_film_name").val();
            $scope.realisation = $("#id_realisation").val();
            $scope.production = $("#id_production").val();
            $scope.photo_direction = $("#id_photo_direction").val();
            $scope.observations = $("#id_observations").val();
        }
    }
}
