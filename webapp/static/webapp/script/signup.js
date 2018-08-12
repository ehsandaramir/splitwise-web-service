var app = angular.module('SignupApp', []);

app.controller('signupApp', function ($scope, $http, $window) {
  $scope.toWrite = {
    profile: {}
  };
  $scope.results = {};


  $http.defaults.xsrfCookieName = 'csrftoken';
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';


  function verifyWrite(raw_data) {
    return raw_data;
  }


  $scope.onSignupClick = function () {
    $scope.results = {};
    $http({
      method: 'POST',
      url: '/api/users/',
      data: JSON.stringify(verifyWrite($scope.toWrite))
    })
        .then(function (response) {
          if (response.status === 201) {
            console.log('created successfully');
            $window.location = '/accounts/login/';
          }
          else {
            console.log('create user failed');
            $scope.results.errors = response.data;
          }
        }, function (response) {
          console.log('create user failed');
          $scope.results.errors = response.data;
        });
  }
});