'use strict';

/**
 * @ngdoc function
 * @name sespaApp.controller:StudentDetailCtrl
 * @description
 * # StudentDetailCtrl
 * Controller of the sespaApp
 */
angular.module('sespaApp')
  .controller('StudentDetailCtrl', function(advisingData, advisingUtilities, $scope, $routeParams) {
  	$scope.student = null;
    $scope.advisors = null;
    $scope.mentors = null;
    $scope.classSites = null;
    $scope.sortTypeAdvisor = 'advisor.last_name';
    $scope.sortTypeMentor = 'mentor.last_name';
  	$scope.sortType = 'class_site.description';
    $scope.sortReverseAdvisor = false;
    $scope.sortReverseMentor = false;
    $scope.sortReverse = false;

  	advisingData.studentDetails($routeParams.student).then(function(student) {
      $scope.student = student;
    }, function(reason) {
        advisingUtilities.httpErrorHandler(reason, $scope);
    });
    
    advisingData.studentAdvisors($routeParams.student).then(function(advisors) {
      $scope.advisors = advisors;
    }, function(reason) {
        advisingUtilities.httpErrorHandler(reason, $scope);
    });
    
    advisingData.studentClassSites($routeParams.student).then(function(class_sites) {
      $scope.classSites = class_sites;
    }, function(reason) {
        advisingUtilities.httpErrorHandler(reason, $scope);
    });

  });
