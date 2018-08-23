const app = angular.module('ProfileApp', []);

app.controller('profileApp', function ($scope, $http, $window) {

    $scope.user = {
        profile: {}
    };

    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';


    $scope.loadUser = function () {
        $http({
            method: 'GET',
            url: '/users/'
        })
    };


    $scope.saveChanges = function () {
        console.log('saving profile');
    }

});
