function VideoUploadController($scope) {
    "user strict";
    $scope.uploads = [];
    $scope.number = 0;

    applyDjangoResumable = function(form) {
        var dj = new DjangoResumable({
            onFileAdded: onFileAdded,
            onFileError: onFileError,
            onFileSuccess: onFileSuccess,
            angularReference: form
        });
        dj.initField($("#" + form.elementId + " input[data-upload-url]")[0]);
        form["djangoResumable"] = dj;
        $('[data-toggle="tooltip"]').tooltip();
    }

    $scope.addUpload = function() {
        var newForm = {
            id: $scope.number,
            elementId: "upload_form_" + $scope.number,
            djangoResumable: null,
            state: "empty",
            isSubmited: false,
            title: ""
        };

        $scope.uploads.push(newForm);
        console.log("id: " + newForm.id);

        // horrible hack because angularjs is strange
        // it waits for this function to finish to update the dom
        // so I can't query to get the good dom element for DjangoResumable
        // I think that DjangoResumable should probably be rewritten for angularjs
        // but I don't have the time for that now
        setTimeout(function() { applyDjangoResumable(newForm)}, 100);

        $scope.number += 1;
    }

    $scope.addUpload();

    $scope.saveVideo = function(id) {
        var video = $scope.uploads[id];
        var data = $("#" + video.elementId).serialize();

        video.isSubmited = true;

        if (video.state == "done") {
            $.post("", data).done(function(response) {
                console.log("success!");
                console.log(response);
                $scope.$digest();
            }).fail(function(response) {
                console.log("fail!");
                console.log(response);
            })
        }
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
                console.log(i + " '" + $scope.uploads[i].title + "' is waiting, starts it");
                // spaguetti!
                $scope.uploads[i].djangoResumable.startUpload($scope.uploads[i].r, $scope.uploads[i].progress);
                return;
            }
            console.log(i + " '" + $scope.uploads[i].title + "' is in state '" + $scope.uploads[i].state + "', skipping");
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
        $scope.$digest();
    };

    onFileAdded = function (r, file, event, el, progress, filePath, fileName) {
        "use strict";
        var errorList = this.getErrorList(el);
        if (errorList) {
            errorList.parentNode.removeChild(errorList);
        }
        if (noneIsRunning()) {
            this.startUpload(r, progress);
        } else {
            this.options.angularReference.state = "waiting";
        }

        this.options.angularReference.r = r;
        this.options.angularReference.progress = progress;

        if (this.options.angularReference.title.length == 0) {
            this.options.angularReference.title = file.fileName.replace(/\.[^/.]+$/, "").replace(/_/g, " ");
        }
        $scope.$digest();
    };

    onFileSuccess = function (r, file, message, el, progress, filePath, fileName) {
        "use strict";
        filePath.setAttribute('value', file.size + '_' + file.fileName);
        progress.firstChild.className += ' progress-bar-success';
        progress.firstChild.innerHTML = 'Upload terminé'
        this.options.angularReference.state = "done";

        if (this.options.angularReference.isSubmited) {
            $scope.saveVideo(this.options.angularReference.id);
        }

        startNextUpload();
        $scope.$digest();
    };
}
