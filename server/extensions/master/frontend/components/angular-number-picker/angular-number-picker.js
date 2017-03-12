/**
 *
 *  Defines `hNumberPicker` directive which can only be used as element.
 *
 *  It allows end-user to choose number, instead of typing
 *
 *  usage:
 *
 *       <h-number value="input.num" min="1" max="10" step="1" change="onChange()"></h-number>
 *
 *  @author  Howard.Zuo
 *  @date    Feb 6th, 2016
 *
 */
(function(global) {
    'use strict';

    var definition = function(angular) {

        var defaults = {
            min: 0,
            max: 100,
            step: 1,
            timeout: 600
        };

        var assign = function(dest, src) {
            for (var key in src) {
                if (!dest[key]) {
                    dest[key] = src[key];
                }
            }
            return dest;
        };

        var isNumber = function(value) {
            var val = Number(value);
            return !isNaN(val) && val == value;
        };

        var toNumber = function(value) {
            return Number(value);
        };

        var checkNumber = function(value) {
            if (!isNumber(value)) {
                throw new Error('value [' + value + '] is not a valid number');
            }
        };

        var getTarget = function(e) {
            if (e.touches && e.touches.length > 0) {
                return angular.element(e.touches[0].target);
            }
            return angular.element(e.target);
        };

        var getType = function(e) {
            return getTarget(e).attr('type');
        };

        var transform = function(opts) {
            for (var key in opts) {
                var value = opts[key];
                opts[key] = toNumber(value);
            }
        };

        var directive = function($timeout, $interval) {

            return {
                restrict: 'E',
                scope: {
                    'value': '=',
                    'singular': '@',
                    'plural': '@',
                    'min': '@',
                    'max': '@',
                    'step': '@',
                    'change': '&'
                },
                link: function($scope, element) {

                    var opts = assign({
                        min: $scope.min,
                        max: $scope.max,
                        step: $scope.step
                    }, defaults);

                    checkNumber(opts.min);
                    checkNumber(opts.max);
                    checkNumber(opts.step);

                    transform(opts);

                    if (opts.min > $scope.value) {
                        $scope.value = opts.min;
                    }

                    $scope.$watch('value', function(newValue, oldValue) {
                        $scope.canDown = newValue > opts.min;
                        $scope.canUp = newValue < opts.max;

                        if (newValue !== oldValue) {
                            $scope.change();
                        }
                    });

                    var changeNumber = function($event) {
                        var type = getType($event);
                        if ('up' === type) {
                            if ($scope.value >= opts.max) {
                                return;
                            }
                            $scope.value += opts.step;
                            if ($scope.value > opts.max) {
                                $scope.value = opts.max;
                            }
                        } else if ('down' === type) {
                            if ($scope.value <= opts.min) {
                                return;
                            }
                            $scope.value -= opts.step;
                            if ($scope.value < opts.min) {
                                $scope.value = opts.min;
                            }
                        }
                    };

                    var isPressing;
                    var timeoutPro;
                    var intervalPro;
                    var start;
                    var end;
                    var addon = element.find('span');

                    addon.on('click', function(e) {
                        changeNumber(e);
                        $scope.$apply();
                        e.stopPropagation();
                    });

                    addon.on('touchstart', function(e) {
                        if (isPressing) {
                            return;
                        }
                        isPressing = true;
                        getTarget(e).addClass('active');
                        start = new Date().getTime();
                        timeoutPro = $timeout(function() {
                            intervalPro = $interval(function() {
                                changeNumber(e);
                            }, 200);
                        }, opts.timeout);
                        e.preventDefault();
                    });

                    addon.on('touchend', function(e) {
                        end = new Date().getTime();
                        if (intervalPro) {
                            $interval.cancel(intervalPro);
                            intervalPro = undefined;
                        }
                        if (timeoutPro) {
                            $timeout.cancel(timeoutPro);
                            timeoutPro = undefined;
                        }
                        if ((end - start) < opts.timeout) {
                            changeNumber(e);
                            $scope.$apply();
                        }
                        getTarget(e).removeClass('active');
                        e.stopPropagation();
                        isPressing = false;
                    });

                    $scope.$on('$destroy', function() {
                        addon.off('touchstart touchend click');
                    });

                },
                template: '<div class="input-group"><span class="input-group-addon" type="down" ng-disabled="!canDown">&nbsp;&nbsp;-&nbsp;&nbsp;</span><label class="form-control">{{ value }} {{value === 1 ? singular : plural}}</label><span class="input-group-addon" type="up" ng-disabled="!canUp">&nbsp;&nbsp;+&nbsp;&nbsp;</span></div>'
            };
        };

        var name = 'angularNumberPicker';
        angular.module(name, [])
            .directive('hNumber', ['$timeout', '$interval', directive]);
        return name;
    };

    if (typeof exports === 'object') {
        module.exports = definition(require('angular'));
    } else if (typeof define === 'function' && define.amd) {
        define(['angular'], definition);
    } else {
        definition(global.angular);
    }

}(window));
