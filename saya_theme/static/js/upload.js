function VideoUploadController($scope) {
    "user strict";
    $scope.uploads = [];
    number = 0;

    applyDjangoResumable = function(form) {
        var dj = new DjangoResumable({
            onFileAdded: onFileAdded,
            onFileError: onFileError,
            onFileSuccess: onFileSuccess,
            angularReference: form
        });
        dj.initField($("#" + form.elementId + " input[data-upload-url]")[0]);
        form["djangoResumable"] = dj;
    }

    $scope.addUpload = function() {
        var newForm = {
            id: number,
            elementId: "upload_form_" + number,
            djangoResumable: null,
            state: "empty",
            fileName: ""
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

    noneIsRunning = function() {
        result = true;

        $scope.uploads.forEach(function(i) {
            if (i.state == "running") {
                result = false;
            }
        });

        return result;
    }

    startNextUpload = function() {
        for (var i = 0; i < $scope.uploads.length; ++i) {
            if ($scope.uploads[i].state == "waiting") {
                // spaguetti!
                $scope.uploads[i].djangoResumable.startUpload($scope.uploads[i].r, $scope.uploads[i].progress);
                return;
            }
        }
    }

    onFileError = function (r, file, message, el) {
        "use strict";
        console.log(message);
        var errorList = this.getErrorList(el, true),
            error = document.createElement('li');
        error.innerHTML = message;
        if (errorList) {
            errorList.appendChild(error);
        }
        this.options.angularReference.state = "done";
        startNextUpload();
    };

    onFileAdded = function (r, file, event, el, progress, filePath, fileName) {
        "use strict";
        var errorList = this.getErrorList(el);
        if (errorList) {
            errorList.parentNode.removeChild(errorList);
        }
        if (noneIsRunning()) {
            this.startUpload(r, progress);
        }

        this.options.angularReference.r = r;
        this.options.angularReference.progress = progress;

        if (this.options.angularReference.fileName.length == 0) {
            var fileName = file.fileName.replace(/\.[^/.]+$/, "").replace(/_/g, " ");
            this.options.angularReference.fileName = fileName;
            // stupid angular, I need to do that because I can't find a way to
            // update this from here (modifying the ng-model doesn't work, like
            // all my other more advanced attemps
            $("#" + this.options.angularReference.elementId + " #id_title").val(fileName);
        }
    };

    onFileSuccess = function (r, file, message, el, progress, filePath, fileName) {
        "use strict";
        filePath.setAttribute('value', file.size + '_' + file.fileName);
        fileName.innerHTML = file.fileName;
        progress.firstChild.className += ' progress-bar-success';
        progress.firstChild.innerHTML = 'Upload terminé'
        this.options.angularReference.state = "done";
        startNextUpload();
    };
}
