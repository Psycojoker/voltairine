var app = angular.module('voltairine', ['ngCookies', 'ngSanitize'])
    .config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{&');
        $interpolateProvider.endSymbol('&}');
    })
    .run(function($http, $cookies){
        $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    })
