let app = angular.module('splitWiseAppView', []);

app.controller('SplitWiseAppView', ['$scope', '$http', '$window',
  function ($scope, $http, $window) {
    $scope.item = {};
    $scope.payments = [];

    let tokens = $window.location.pathname
        .split('?')[0]
        .split('/');
    $scope.pk = tokens[tokens.length - 2];

    // var csrftoken = Cookies.get('csrftoken');
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';

    $scope.loadBill = function () {
      $http.get('/api/bills/' + $scope.pk + '/')
          .then(function (response) {
            if (response.status === 200) {
              $scope.item = response.data;
              $scope.payments = response.data.payments;
            }
            else {
              console.log('could not retrieve the bill item');
            }
          })
    };

    $scope.onSubmitClicked = function () {
      let str_data = JSON.stringify($scope.item);
      $http({
        method: 'PUT',
        url: '/api/bills/' + $scope.pk + '/',
        data: str_data
      });
    };

    $scope.loadBill();
  }]);