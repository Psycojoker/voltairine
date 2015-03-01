function editVideoDetailsController($scope) {
    $scope.inEditMode = false;

    $scope.switchToEditMode = function() {
        $scope.inEditMode = true;
    }
}
