// modify version of django resumable bundled script to allow to work wit
// a dynamic uploading interface

var DjangoResumable = function (options) {
    "use strict";
    var defaults, els;
    options = options || {};
    defaults = {
        csrfInputName: 'csrfmiddlewaretoken',
        urlAttribute: 'data-upload-url',
        progressDisplay: '',
        errorListClass: 'errorlist',
        onFileError: this.onFileError,
        onFileAdded: this.onFileAdded,
        onFileSuccess: this.onFileSuccess,
        onProgress: this.onProgress,
        angularReference: {},
        resumableOptions: {}
    };
    this.startTime = -1;
    this.lastTimerUpdateTime = -1;
    this.previousProgressNumber = 0;
    this.options = this.extend(defaults, options);
    this.csrfToken = document.querySelector('input[name=' + this.options.csrfInputName + ']').value;
};


DjangoResumable.prototype.each = function (elements, fn) {
    "use strict";
    var i, l;
    for (i = 0, l = elements.length; i < l; i += 1) {
        fn.apply(this, [elements[i]]);
    }
};


DjangoResumable.prototype.extend = function (target, source) {
    "use strict";
    var property;
    for (property in source) {
        if (source.hasOwnProperty(property)) {
            target[property] = source[property];
        }
    }
    return target;
};


DjangoResumable.prototype.getErrorList = function (el, create) {
    "use strict";
    var errorList = el.parentNode.previousSibling;
    while (errorList && errorList.tagName === undefined) {
        errorList = errorList.previousSibling;
    }
    if (errorList && !errorList.classList.contains(this.options.errorListClass)) {
        if (create === true) {
            errorList = document.createElement('ul');
            errorList.classList.add(this.options.errorListClass);
            el.parentNode.parentNode.insertBefore(errorList, el.parentNode);
        } else {
            errorList = null;
        }
    }
    return errorList;
};


DjangoResumable.prototype.getForm = function (el) {
    "use strict";
    var parent = el;
    while (parent.tagName !== 'FORM') {
        parent = parent.parentNode;
    }
    return parent;
};


DjangoResumable.prototype.initField = function (el) {
    "use strict";
    var progress, fileName, filePath, filePathName, timer;

    progress = this.initProgressBar();
    timer = this.initTimer();
    progress.timer = timer;
    el.parentNode.parentNode.insertBefore(timer, el.parentNode.nextSibling);
    el.parentNode.parentNode.insertBefore(progress, el.parentNode.nextSibling);

    filePathName = el.getAttribute('name') + '-path';
    filePath = el.parentNode.querySelector('[name=' + filePathName + ']');

    this.initResumable(el, progress, filePath, fileName);

    this.el = el;
};


DjangoResumable.prototype.initProgressBar = function () {
    "use strict";
    var progress = document.createElement('div');
    progress.className = "progress";
    progress.innerHTML = '<div class="progress-bar progress-bar-striped" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">0%</div>';
    progress.style.display = 'none';
    return progress;
};

DjangoResumable.prototype.initTimer = function() {
    "use strict";
    var timer = document.createElement('p');
    timer.style.display = 'none';
    return timer;
};


DjangoResumable.prototype.initResumable = function (el, progress, filePath, fileName) {
    "use strict";
    var elements = Array.prototype.slice.call(arguments),
        self = this,
        opts = {
            target: el.getAttribute(this.options.urlAttribute),
            query: {
                'csrfmiddlewaretoken': this.csrfToken
            }
        };

    opts = this.extend(this.options.resumableOptions, opts);
    var r = new Resumable(opts);
    r.assignBrowse(el);
    this.each(['fileAdded', 'progress', 'fileSuccess', 'fileError'], function (eventType) {
        var callback = this.options['on' + eventType.substring(0, 1).toUpperCase() + eventType.substring(1)];
        r.on(eventType, function () {
            var args = arguments.length > 0 ? Array.prototype.slice.call(arguments) : [];
            callback.apply(self, [r].concat(args).concat(elements));
        });
    });
    return r;
};


DjangoResumable.prototype.onFileError = function (r, file, message, el) {
    "use strict";
    console.log(message);
    var errorList = this.getErrorList(el, true),
        error = document.createElement('li');
    error.innerHTML = message;
    if (errorList) {
        errorList.appendChild(error);
    }
};


DjangoResumable.prototype.onFileAdded = function (r, file, event, el, progress, filePath, fileName) {
    "use strict";
    var errorList = this.getErrorList(el);
    if (errorList) {
        errorList.parentNode.removeChild(errorList);
    }
    r.upload();
    progress.style.display = this.options.progressDisplay;
    progress.timer.style.display = this.options.progressDisplay;
};


DjangoResumable.prototype.onFileSuccess = function (r, file, message, el, progress, filePath, fileName) {
    "use strict";
    filePath.setAttribute('value', file.size + '_' + file.fileName);
    progress.firstChild.className += ' progress-bar-success';
    progress.firstChild.innerHTML = 'Upload terminé';
};


DjangoResumable.prototype.onProgress = function (r, el, progress, filePath, fileName) {
    "use strict";
    var number = Math.floor(r.progress() * 100);
    var timeRemaning = this.calculateRemainigUploadTime(r);
    if (number == this.previousProgressNumber) {
        return;
    }
    this.previousProgressNumber = number;
    progress.firstChild.style.width = number + "%";
    progress.firstChild.setAttribute("aria-valuenow", number);
    console.log(timeRemaning);
    if (timeRemaning !== null) {
        progress.firstChild.innerHTML = timeRemaning;
    }
    // progress.firstChild.innerHTML = number + "%";
};

DjangoResumable.prototype.startUpload = function (r, progress) {
    r.upload();
    this.startTime = Date.now();
    this.lastTimerUpdateTime = Date.now();
    progress.style.display = this.options.progressDisplay;
    progress.timer.style.display = this.options.progressDisplay;
    this.options.angularReference.state = "running";
    this.el.style.display = "none";
};

DjangoResumable.prototype.calculateRemainigUploadTime = function(r) {
    // update the display only once per second at max
    if (((Date.now() - this.lastTimerUpdateTime) / 1000) < 1) {
        return null;
    }

    var progress = r.progress();
    var remainingProgress = 1.0 - progress;

    var estimatedCompletionTime = Math.round((remainingProgress / progress) * ((Date.now() - this.startTime) / 1000));

    var estimatedHours, estimatedMinutes, estimatedSeconds, displayHours, displayMinutes, displaySeconds;

    // If progress is complete then quit
    if (progress >= 1.0) {
        return null;
    }

    this.lastTimerUpdateTime = Date.now();

    // If the estimated time is valid then calculate the time values.
    // NOTE: It might take 1 or 2 iterations to get a valid estimate.
    if (isFinite(estimatedCompletionTime)) {
        estimatedHours = Math.floor(estimatedCompletionTime / 3600);
        estimatedMinutes = Math.floor((estimatedCompletionTime / 60) % 60);
        estimatedSeconds = estimatedCompletionTime % 60;

        if (estimatedHours > 0) {
            return estimatedHours + "h " + estimatedMinutes + "min " + estimatedSeconds + "s";
        } else if (estimatedMinutes > 0) {
            return estimatedMinutes + "min " + estimatedSeconds + "s";
        } else {
            return estimatedSeconds + "s";
        }

    }
};
