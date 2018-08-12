let app = angular.module('splitWiseAppView', []);

app.controller('SplitWiseAppView', ['$scope', '$http', '$window',
  function ($scope, $http, $window) {
    $scope.item = {};
    $scope.payments = [];
    $scope.debts = [];
    $scope.userOptions = [];

    let tokens = $window.location.pathname
        .split('?')[0]
        .split('/');
    $scope.pk = tokens[tokens.length - 2];

    // var csrftoken = Cookies.get('csrftoken');
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';

    function usernameToId(username) {
      for (i = 0; i < $scope.userOptions.length; i++)
        if ($scope.userOptions[i].username === username)
          return $scope.userOptions[i].pk;
    }

    function clearAllNewForm() {
      $scope.newPaymentUsername = '';
      $scope.newPaymentAmount = '';
      $scope.newDebtUsername = '';
      $scope.newDebtAmount = '';
    }

    function makeWritableBill(bill) {
      let copy = JSON.parse(JSON.stringify(bill));
      copy.creator__write = bill.creator.pk;

      return copy;
    }

    function makeWritablePayments(payments) {
      let result = [];
      for (i = 0; i < payments.length; i++) {
        result[i] = {
          pk: payments[i].pk,
          bill__write: $scope.pk,
          paid_by__write: payments[i].paid_by.pk,
          amount: payments[i].amount
        };
      }
      return result
    }

    function makeWritableDebts(debts) {
      let result = [];
      for (i = 0; i < debts.length; i++) {
        result[i] = {
          pk: debts[i].pk,
          bill__write: $scope.pk,
          owed_by__write: debts[i].owed_by.pk,
          amount: debts[i].amount
        };
      }
      return result
    }

    $scope.loadBill = function () {
      $http.get('/api/bills/' + $scope.pk + '/')
          .then(function (response) {
            if (response.status === 200) {
              $scope.item = response.data;
              $scope.payments = response.data.payments;
              $scope.debts = response.data.debts;

              clearAllNewForm();
            }
            else {
              console.log('could not retrieve the bill item');
            }
          })
    };

    $scope.loadUsers = function () {
      $http({
        method: 'GET',
        url: '/api/users/'
      })
          .then(function (response) {
            $scope.userOptions = response.data;
          })
    };

    $scope.onSubmitClicked = function () {
      let str_data = JSON.stringify(makeWritableBill($scope.item));
      $http({
        method: 'PUT',
        url: '/api/bills/' + $scope.pk + '/',
        data: str_data
      });
    };

    $scope.onNewPayerClick = function () {
      console.log('new payer click');

      let paid_by = usernameToId($scope.newPaymentUsername);
      if (paid_by <= 0) {
        console.log('invalid payment user');
        return;
      }

      if (parseFloat($scope.newPaymentAmount) <= 0) {
        console.log('invalid payment amount: ' + parseFloat($scope.newPaymentAmount));
        return;
      }

      let submit_data = {
        bill__write: parseInt($scope.pk),
        paid_by__write: paid_by,
        amount: parseFloat($scope.newPaymentAmount)
      };
      $http({
        method: 'POST',
        url: '/api/payments/',
        data: JSON.stringify(submit_data)
      })
          .then(function (response) {
            $scope.loadBill();
          });
    };

    $scope.onSavePaymentsClick = function () {
      console.log('save all payments');
      let writableData = makeWritablePayments($scope.payments);
      for (i = 0; i < writableData.length; i++) {
        let raw_data = JSON.stringify(writableData[i]);

        $http({
          method: 'PUT',
          url: '/api/payments/' + writableData[i].pk + '/',
          data: raw_data
        }).then(function (response) {
          $scope.loadBill();
        })
      }
    };

    $scope.onNewDebtClick = function () {
      console.log('new debt click');

      let owed_by = usernameToId($scope.newDebtUsername);
      if (owed_by <= 0) {
        console.log('invalid debt user');
        return;
      }

      if (parseFloat($scope.newDebtAmount) <= 0) {
        console.log('invalid debt amount: ' + parseFloat($scope.newDebtAmount));
        return;
      }

      let submit_data = {
        bill__write: parseInt($scope.pk),
        owed_by__write: owed_by,
        amount: parseFloat($scope.newDebtAmount)
      };
      $http({
        method: 'POST',
        url: '/api/debts/',
        data: JSON.stringify(submit_data)
      })
          .then(function (response) {
            $scope.loadBill();
          });

      clearAllNewForm();
    };

    $scope.onSaveDebtsClick = function () {
      console.log('save all debts');
      let writableData = makeWritableDebts($scope.debts);
      for (i = 0; i < writableData.length; i++) {
        let raw_data = JSON.stringify(writableData[i]);

        $http({
          method: 'PUT',
          url: '/api/debts/' + writableData[i].pk + '/',
          data: raw_data
        }).then(function (response) {
          $scope.loadBill();
        });
      }
    };

    $scope.loadUsers();
    $scope.loadBill();
  }]);