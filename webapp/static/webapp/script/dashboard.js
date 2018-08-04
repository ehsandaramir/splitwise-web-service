var app = angular.module('splitwiseApp', []);

app.controller('SplitwiseApp', function ($scope, $http) {

  $scope.splitBills = [];
  $scope.actionDisabled = false;
  $scope.selectedCount = 0;

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

  $scope.onCheckClick = function (x) {
    if (x.selected)
      $scope.selectedCount--;
    else
      $scope.selectedCount++;

    $scope.actionDisabled = $scope.selectedCount !== 1;
    console.log('selectedCount: ' + $scope.selectedCount);
  };

  $scope.onViewBillClicked = function () {
    let selectedCount = 0;
    let selectedBill;
    $scope.splitBills.forEach(element => {
      if (element.selected) {
        selectedCount++;
        selectedBill = element;
      }
    });

    if (selectedCount === 1) {
      console.log(selectedBill);
    }
    else {
      alert('please select exactly one bill');
    }
  }
});
