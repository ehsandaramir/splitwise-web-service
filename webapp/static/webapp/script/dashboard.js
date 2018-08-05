var app = angular.module('splitwiseApp', []);

app.controller('SplitwiseApp', function ($scope, $http, $window) {

  $scope.splitBills = [];
  $scope.actionDisabled = false;
  $scope.selectedCount = 0;

  $scope.modalViewBillVisible = false;

  $http.defaults.xsrfCookieName = 'csrftoken';
  $http.defaults.xsrfHeaderName = 'X-CSRFToken';

  function loadBillTable() {
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
  }

  loadBillTable();


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
    $window.location.href = 'view/' + item.pk;
  };

  $scope.onEditBillClicked = function (item) {
    console.log('edit on ' + item.pk);
    $window.location.href = 'edit/' + item.pk;
  };

  $scope.onDeleteBillClicked = function (item) {
    console.log('delete on ' + item.pk);
    $http({
      method: 'DELETE',
      url: '/api/bills/' + item.pk + '/',
    })

    // $http.delete('/api/bills/' + item.pk + '/')
        .then(function (response) {
          loadBillTable();
        });
  };

});
