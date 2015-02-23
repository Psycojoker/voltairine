function VideoUploadController($scope) {
    "user strict";
    $scope.uploads = [];

    $scope.addUpload = function() {
        $scope.uploads.push({});
    }
}
