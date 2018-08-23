let app = angular.module('splitWiseAppView', []);

app.controller('SplitWiseAppView', ['$scope', '$http', '$window',
  function ($scope, $http, $window) {
    $scope.item = {};
    $scope.payments = [];
    $scope.debts = [];
    $scope.userOptions = [];
    $scope.userOptionUsernames = [];

    $scope.tmpPaidBy = '';

    let tokens = $window.location.pathname
        .split('?')[0]
        .split('/');
    $scope.pk = tokens[tokens.length - 2];

    // var csrftoken = Cookies.get('csrftoken');
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';


    function calculateBalances(bill) {
      let paid_sum = 0;
      bill.payments.forEach(pay => paid_sum += pay.amount);
      bill.paid_sum = paid_sum;

      let owed_sum = 0;
      bill.debts.forEach(debt => owed_sum += debt.amount);
      bill.owed_sum = owed_sum;
    }


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
              calculateBalances(response.data);
              $scope.item = response.data;
              $scope.payments = response.data.payments;
              $scope.debts = response.data.debts;

              $scope.payments.forEach(element => element.paid_by = element.paid_by.username);
              $scope.debts.forEach(element => element.owed_by = element.owed_by.username);

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
            $scope.userOptionUsernames = [];
            $scope.userOptions.forEach(element => $scope.userOptionUsernames.push(element.username));
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


    $scope.saveChangedPayment = function (payment) {
      console.log('on payment user change');
      payment.paid_by__write = usernameToId(payment.paid_by);
      payment.bill__write = $scope.pk;

      $http({
        method: 'PUT',
        url: '/api/payments/' + payment.pk + '/',
        data: JSON.stringify(payment)
      }).then(function (response) {
        $scope.loadBill();
      });
    };


    $scope.deletePayment = function (payment) {
      $http({
        method: 'DELETE',
        url: '/api/payments/' + payment.pk + '/'
      }).then(function (response) {
        $scope.loadBill();
      })
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


    $scope.saveChangedDebt = function (debt) {
      console.log('on debt user change');
      debt.owed_by__write = usernameToId(debt.owed_by);
      debt.bill__write = $scope.pk;

      $http({
        method: 'PUT',
        url: '/api/debts/' + debt.pk + '/',
        data: JSON.stringify(debt)
      }).then(function (response) {
        $scope.loadBill();
      });
    };


      $scope.deleteDebt = function (debt) {
          $http({
              method: 'DELETE',
              url: '/api/debts/' + debt.pk + '/'
          }).then(function (response) {
              $scope.loadBill();
          })
      };


    $scope.loadUsers();
    $scope.loadBill();
  }]);