function VideoUploadController($scope) {
    "user strict";
    $scope.uploads = [];
    number = 0;

    applyDjangoResumable = function(form) {
        var dj = new DjangoResumable();
        dj.initField($("#" + form.elementId + " input[data-upload-url]")[0]);
    }

    $scope.addUpload = function() {
        var newForm = {
            id: number,
            elementId: "upload_form_" + number,
            djangoResumable: null
        };

        $scope.uploads.push(newForm);

        // horrible hack because angularjs is strange
        setTimeout(function() { applyDjangoResumable(newForm)}, 100);

        number += 1;
    }
}
