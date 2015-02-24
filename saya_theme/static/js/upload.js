function VideoUploadController($scope) {
    "user strict";
    $scope.uploads = [];
    number = 0;

    applyDjangoResumable = function(form) {
        var dj = new DjangoResumable();
        dj.initField($("#" + form.elementId + " input[data-upload-url]")[0]);
        form["djangoResumable"] = dj;
    }

    $scope.addUpload = function() {
        var newForm = {
            id: number,
            elementId: "upload_form_" + number,
            djangoResumable: null
        };

        $scope.uploads.push(newForm);

        // horrible hack because angularjs is strange
        // it waits for this function to finish to update the dom
        // so I can't query to get the good dom element for DjangoResumable
        // I think that DjangoResumable should probably be rewritten for angularjs
        // but I don't have the time for that now
        setTimeout(function() { applyDjangoResumable(newForm)}, 100);

        number += 1;
    }
}
