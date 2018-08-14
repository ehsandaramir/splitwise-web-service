var app = angular.module('splitwiseApp', []);

app.controller('SplitwiseApp', function ($scope, $http, $window) {

  $scope.splitBills = [];
  $scope.newBill = {};
  $scope.addNewBillError = {};
  $scope.actionDisabled = false;
  $scope.selectedCount = 0;

  $scope.modalViewBillVisible = false;

  $http.defaults.xsrfCookieName = 'csrftoken';
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';

  $scope.loadBillTable = function () {
    $scope.splitBills = {};
    $http.get('/api/bills/')
      .then(function (response) {
        if (response.status === 200) {
          console.log('split bills retrieved successfully');

          var data = response.data;
          data.forEach(element => element.selected = false);

          $scope.actionDisabled = true;
          $scope.selectedCount = 0;
          $scope.splitBills = data;
        }
        else {
          console.log('error on getting split bill: ' + response.status);
          $scope.splitBills = [];
        }
      });
  };


  $scope.onCheckClick = function (x) {
    if (x.selected)
      $scope.selectedCount--;
    else
      $scope.selectedCount++;

    $scope.actionDisabled = $scope.selectedCount !== 1;
    console.log('selectedCount: ' + $scope.selectedCount);
  };

  $scope.onViewBillClicked = function (item) {
    console.log('view on ' + item.pk);
    $window.location = 'view/' + item.pk;
  };

  $scope.onEditBillClicked = function (item) {
    console.log('edit on ' + item.pk);
    $window.location = 'edit/' + item.pk;
  };

  $scope.onDeleteBillClicked = function (item) {
    console.log('delete on ' + item.pk);
    $http({
      method: 'DELETE',
      url: '/api/bills/' + item.pk + '/',
    })
        .then(function (response) {
          $scope.loadBillTable();
        });
  };

  $scope.onAddBillClick = function () {
    $http({
      method: 'POST',
      url: '/api/bills/',
      data: JSON.stringify($scope.newBill)
    }).then(function (response) {
      console.log('post bill successful');
      $scope.loadBillTable();

      $scope.addNewBillError = {};
      $scope.newBill = {};
      angular.element('#modalAddBill').modal('hide');

    }, function (response) {
      console.log('post bill failed');
      $scope.loadBillTable();
      $scope.addNewBillError.error = 'insertion failed';
    });
  };

  $scope.onAddBillCloseClick = function () {
    $scope.newBill = {};
    $scope.addNewBillError = {};
    $scope.loadBillTable();
    angular.element('#modalAddBill').modal('hide');
  };

  $scope.loadBillTable();

});
