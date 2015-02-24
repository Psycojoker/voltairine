function VideoUploadController($scope) {
    "user strict";
    $scope.uploads = [];
    number = 0;

    applyDjangoResumable = function(elementId) {
        var dj = new DjangoResumable();
        dj.initField($("#" + elementId + " input[data-upload-url]")[0]);
    }

    $scope.addUpload = function() {
        var new_form = {
            id: number
        };

        $scope.uploads.push(new_form);

        // horrible hack because angularjs is strange
        setTimeout(function() { applyDjangoResumable("upload_form_" + new_form.id)}, 100);

        number += 1;
    }
}
