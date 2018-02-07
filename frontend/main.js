function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

//var config = require('./config');
var config = function () {
    var jsonTemp = null;
    $.ajax({
        'async': false,
        'url': "config.json",
        'success': function (data) {
            jsonTemp = data;
        }
    });
    return jQuery.parseJSON(jsonTemp);
}();

var access_token = getCookie('portal_cookie');
//var id_token = $window.sessionStorage.accessToken;
//console.log(id_token);
var app_url = config.url;
var auth_url = config.auth_url;
endpoint = "https://" + app_url + "/api";
console.log(endpoint);

app = angular.module("app", ["ngRoute", "ui.bootstrap"]);

app.factory('AwsAuthInterceptor', function () {
    return {
        request: function (config) {
            config.headers = config.headers || {};
            config.headers.Authorization = access_token;
            config.timeout = 90000;
            //console.log(config.headers);
            return config;
        },
        response: function (response) {
            if (response.status === 401) {
                windows.location = auth_url;
            }
            return response;
        }
    };
});

app.config(function ($httpProvider) {
    $httpProvider.interceptors.push('AwsAuthInterceptor');
});


app.config(["$locationProvider", function ($locationProvider) {
    $locationProvider.hashPrefix("!");
}]);

app.config(["$routeProvider", "$sceDelegateProvider",
        function ($routeProvider, $sceDelegateProvider) {
            "use strict";
            $routeProvider
                .when("/", {
                    templateUrl: "partials/summary.html",
                    controller: "DashboardController"
                })
                .when("/admin", {
                    templateUrl: "partials/admin.html",
                    controller: "AdminController"
                })
                .when("/about", {
                    templateUrl: "partials/about.html"
                })
                .when("/summary", {
                    templateUrl: "partials/summary.html",
                    controller: "DashboardController"
                })
                .when("/compliance", {
                    templateUrl: "partials/compliance-list.html",
                    controller: "ComplianceListController"
                })
                .when("/compliance/:accountNum", {
                    templateUrl: "partials/compliance.html",
                    controller: "ComplianceController"
                })
                .when("/alerts", {
                    templateUrl: "partials/alerts-list.html",
                    controller: "AlertListController"
                })
                .when("/alerts/:accountNum", {
                    templateUrl: "partials/alerts.html",
                    controller: "AlertsController"
                })
                .when("/accounts", {
                    templateUrl: "partials/accounts-list.html",
                    controller: "AccountListController"
                })
                .when("/accounts/:accountNum", {
                    templateUrl: "partials/account.html",
                    controller: "AccountController"
                })
                .when("/accounts/:accountNum/:instanceId", {
                    templateUrl: "partials/instance.html",
                    controller: "InstanceController"
                })
                .when("/instances", {
                    templateUrl: "partials/instances-list.html",
                    controller: "InstanceListController"
                })
                .when("/publicips", {
                    templateUrl: "partials/publicip-list.html",
                    controller: "PublicIpListController"
                })
                .when("/instances/:accountNum/:instanceId", {
                    templateUrl: "partials/instance.html",
                    controller: "InstanceController"
                })
                .when("/instances/:accountNum/:region/:instanceId", {
                    templateUrl: "partials/instance.html",
                    controller: "InstanceController"
                })
                .when("/users", {
                    templateUrl: "partials/users-list.html",
                    controller: "UserListController"
                })
                .when("/users/:accountNum/:user", {
                    templateUrl: "partials/user.html",
                    controller: "UserController"
                })
                .when("/roles", {
                    templateUrl: "partials/role-list.html",
                    controller: "RoleListController"
                })
                .when("/databases", {
                    templateUrl: "partials/database-list.html",
                    controller: "DatabaseListController"
                })
                .when("/dynamotables", {
                    templateUrl: "partials/dynamo-list.html",
                    controller: "DynamoListController"
                })
                .when("/redshift", {
                    templateUrl: "partials/redshift-list.html",
                    controller: "RedshiftListController"
                })
                .when("/securitygroups", {
                    templateUrl: "partials/sg-list.html",
                    controller: "SGListController"
                })
                .when("/securitygroups/:accountNum/:region/:sgId", {
                    templateUrl: "partials/sg.html",
                    controller: "SGController"
                })
                .when("/loadbalancers", {
                    templateUrl: "partials/elb-list.html",
                    controller: "ELBListController"
                })
                .when("/loadbalancers/:accountNum/:elbId", {
                    templateUrl: "partials/elb.html",
                    controller: "ELBController"
                })
                .when("/loadbalancers/:accountNum/:region/:elbId", {
                    templateUrl: "partials/elb.html",
                    controller: "ELBController"
                })
                .when("/buckets", {
                    templateUrl: "partials/bucket-list.html",
                    controller: "S3ListController"
                })
                .when("/buckets/:accountNum/:bucket", {
                    templateUrl: "partials/bucket.html",
                    controller: "S3Controller"
                })
                .when("/totp", {
                    templateUrl: "partials/totp.html",
                    controller: "TOTPController"
                })
                .otherwise({
                    redirectTo: "/"
                });
        }
    ])


    .controller("MainController", ["$scope", "$location", "$http",
        function ($scope, $location, $http) {
            "use strict";
            $scope.routeActive = function (loc) {
                return loc === $location.path();
            };

            $scope.loading = false;
            $scope.userLoading = false;
            $scope.instanceLoading = false;
            $scope.accountLoading = false;
            $scope.elbs = [];
            $scope.instances = [];
            $scope.securitygroups = [];
            $scope.s3buckets = [];
            $scope.regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"];

            $scope.getDate = function (inDate) {
                const date = new Date(inDate * 1000);
                const formatted = date.toLocaleDateString("de-DE", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit"
                }).replace(/\./g, "/");

                return formatted;
            };

            $scope.ready = function () {
                $scope.loading = false;
            };

            $scope.regionsREST = function (data) {
                return apigClient.apiGetregionsGet({}, {}, {}, data);
            };

            //noinspection JSLint
            $scope.latestComplianceReportREST = function (params, body, additionalParams, data) {
                $scope.loading = true;
                return apigClient.lastestComplianceReportGet(params, body, additionalParams, data);
            };

        }
    ])

    .controller("DashboardController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;
        $scope.visitInstances = () => $location.path("/instances");
        $scope.visitUsers = () => $location.path("/users");
        $scope.visitAccounts = () => $location.path("/accounts");
        $scope.instanceCount = 0;
        $scope.getInstanceTotalCount = function () {
            let total = 0;
            for (let i of $scope.instanceCount) {
                total += i.InstanceCount;
            }
            return total;
        };

        $scope.getInstanceAccountMax = function () {
            let max = 0;
            let account = {
                "Account": "000000000"
            };
            for (let i = 0; i < $scope.instanceCount.length; i++) {
                const instances = $scope.instanceCount[i];
                if (instances.InstanceCount > max) {
                    max = instances.InstanceCount;
                    account = instances;
                }
            }
            return account;
        };

        $scope.getUserTotalCount = function () {
            let total = 0;
            for (let i of $scope.userCount) {
                total += i.UserCount;
            }
            return total;
        };

        $scope.getUserAccountMax = function () {
            let max = 0;
            let account = {
                "Account": "000000000"
            };
            for (let i = 0; i < $scope.userCount.length; i++) {
                const users = $scope.userCount[i];
                if (users.UserCount > max) {
                    max = users.UserCount;
                    account = users;
                }
            }
            return account;
        };

        $scope.collapseInstances = function () {
            $scope.instanceCountCollapsed = $scope.instanceCountCollapsed === false;
            $scope.$apply();
        };
        $scope.collapseUsers = function () {
            $scope.userCountCollapsed = $scope.userCountCollapsed === false;
            $scope.$apply();
        };

        $scope.userCountCollapsed = true;
        $scope.instanceCountCollapsed = true;
        const params = {};
        const body = {};
        const additionalParams = {};

        $scope.userLoading = true;
        $scope.accountLoading = true;
        $scope.instanceLoading = true;
        $scope.loading = true;
        $http({
                method: "GET",
                url: endpoint + "/summary/instancecount"

            })
            .then(function (response) {
                $scope.instanceCount = response.data.Summary;
                $scope.instanceLoading = false;
                $scope.loading = false;
            }, function (reason) {
                $scope.instanceCount = -1;
                $scope.instanceLoading = false;
                $scope.loading = false;
            });

        $http({
                method: "GET",
                url: endpoint + "/summary/usercount"

            })
            .then(function (response) {
                $scope.userCount = response.data.Summary;
                $scope.userLoading = false;
                $scope.loading = false;
            }, function (reason) {
                $scope.userCount = -1;
                $scope.userLoading = false;
                $scope.loading = false;
            });

        $http({
                method: "GET",
                url: endpoint + "/summary/accountcount"

            })
            .then(function (response) {
                $scope.accountCount = response.data.Summary;
                $scope.accountLoading = false;
                $scope.loading = false;
            }, function (reason) {
                $scope.accountCount = -1;
                $scope.accountLoading = false;
                $scope.loading = false;
            });
    }])

    .controller("PublicIpListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.addresses = [];

        $scope.loading = true;
        for (let i = 0; i < $scope.regions.length; i++) {
            const params = {
                region: $scope.regions[i]
            };

            $http({
                    method: "GET",
                    url: endpoint + "/publicips",
                    params: params
                })
                .then(function (response) {
                    for (let j = 0; j < response.data.Addresses.length; j++) {
                        $scope.addresses.push(response.data.Addresses[j]);
                    };
                    //$scope.addresses = response.data.Addresses;
                    $scope.loading = false;
                }, function (reason) {
                    $scope.loading = false;
                });
        };

    }])

    .controller("ComplianceListController", ["$scope", "$window", "$timeout", "$location", "$http", "$uibModal", function ($scope, $window, $timeout, $location, $http, $uibModal) {
        "use strict";
        $scope.loading = true;

        $scope.visit = function (id) {
            let uri = "compliance/" + id; //+ "?reportUri=" + $scope.selectedReport.Uri;
            console.log($scope.selectedReport);
            $location.path(uri).search({
                "reportUri": $scope.selectedReport.Report
            });
        };

        $scope.reloadPage = function () {
            $window.location.reload();
        };

        $scope.runReport = function () {
            //$scope.complianceRUN({}, {}, {});
            //return apigClient.portalComplianceRun(params, body, additionalParams, data);

            $scope.buttonClicked = true;

            $timeout(function () {
                $scope.reloadPage();
            }, 30000);

            $http({
                method: "GET",
                url: endpoint + "/reports/run"
            }).then(function (response) {
                console.log("worked");
            }, function (reason) {
                console.log("failed");
            });


        };

        $scope.oneAtATime = true;
        $scope.status = {
            isFirstOpen: true,
            isFirstDisabled: false
        };
        $scope.animationsEnabled = true;

        //Start of main
        const params = {};

        $scope.selectionUpdate = function () {
            console.log($scope.selectedReport);
            const params = {
                report: $scope.selectedReport.Report
            }
            $http({
                method: "GET",
                url: endpoint + "/reports",
                params: params,
                cache: false
            }).then(function (response) {
                $scope.complianceAlerts = response.data;
                console.log($scope.complianceAlerts);
                $scope.loading = false;
            }, function (reason) {
                $scope.complianceAlerts = [];
                console.log("failed");
            });
        };


        $http({
            method: "GET",
            url: endpoint + "/reports",

        }).then(function (response) {
            $scope.reportsList = response.data;
            if (!$scope.selectedReport) {
                $scope.selectedReport = $scope.reportsList[$scope.reportsList.length - 1];
                $scope.selectionUpdate();
                $scope.loading = false;
            }
        }, function (reason) {
            console.log(reason);
        });

        $http({
            method: "GET",
            url: endpoint + "/rules",

        }).then(function (response) {
            $scope.rules = response.data;
            console.log($scope.rules);
        }, function (reason) {
            console.log(reason);
        });

    }])

    .controller("ComplianceController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        $scope.loading = true;
        const account = $routeParams.accountNum;
        const reportUri = $routeParams.reportUri;
        console.log(reportUri);
        const params = {
            report: reportUri
        }
        $http({
            method: "GET",
            url: endpoint + "/reports",
            params: params,
            cache: true
        }).then(function (response) {
            $scope.alerts = response.data.accountReports.find((obj) => obj.accountNum === account);
            $scope.loading = false;
        }, function (reason) {
            $scope.alerts = [];
            console.log("failed");
        });
    }])

    .controller("AdminController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        $scope.ok = function (account, alias, email, owner) {
            const params = {
                account: account,
                alias: alias,
                email: email,
                owner: owner
            };

            $http({
                    method: "POST",
                    url: endpoint + "/accounts",
                    params: params

                })
                .then(function (response) {
                    $scope.accounts = response.data;
                    //$scope.$apply();
                }, function (reason) {
                    $scope.loading = false;
                });
        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss("cancel");
        };
    }])

    .controller("AccountListController", ["$scope", "$location", "$window", "$http", '$uibModal', function ($scope, $location, $window, $http, $uibModal) {
        "use strict";
        $scope.visit = function (id) {
            $location.path("accounts/" + id);
        };

        $scope.reloadPage = function () {
            $window.location.reload();
        };

        $scope.addAccount = function () {
            $scope.animationsEnabled = true;
            var modalInstance = $uibModal.open({
                animation: $scope.animationsEnabled,
                ariaLabelledBy: 'modal-title',
                ariaDescribedBy: 'modal-body',
                templateUrl: 'partials/addAccountModal.html',
                controller: 'AddAccountModalController',
                controllerAs: '$ctrl',
                resolve: {}
            });

            modalInstance.result.then(function () {
                $scope.reloadPage();
                console.log("modalclose");
            }, function () {
                console.log('Modal dismissed at: ' + new Date());
            });
        };

        $http({
                method: "GET",
                url: endpoint + "/accounts"

            })
            .then(function (response) {
                $scope.accounts = response.data;
                $scope.loading = false;
                //$scope.$apply();
            }, function (reason) {
                $scope.loading = false;
            });
    }])


    .controller("RedshiftListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;

        const params = {};
        $http({
                method: "GET",
                url: endpoint + "/redshiftclusters",
                params: params
            })
            .then(function (response) {
                $scope.clusters = response.data.Clusters;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("DynamoListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;
        $scope.visitDynamo = function (accountNum, region, table) {
            $location.path("dynamotables/" + accountNum + "/" + region + "/" + table);
        };

        $http({
                method: "GET",
                url: endpoint + "/dynamotables"

            })
            .then(function (response) {
                $scope.tables = response.data.Tables;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("DatabaseListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitDatabase = function (accountNum, region, id) {
            $location.path("databases/" + accountNum + "/" + region + "/" + id);
        };

        $http({
                method: "GET",
                url: endpoint + "/databases"

            })
            .then(function (response) {
                $scope.databases = response.data.Databases;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("RoleListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;

        $http({
                method: "GET",
                url: endpoint + "/roles"

            })
            .then(function (response) {
                $scope.roles = response.data.Roles;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("UserListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitUser = function (accountNum, name) {
            $location.path("users/" + accountNum + "/" + name);
        };

        $http({
                method: "GET",
                url: endpoint + "/users"

            })
            .then(function (response) {
                $scope.users = response.data.Users;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });
    }])

    .controller("SGListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitSecurityGroup = function (accountNum, region, id) {
            $location.path("securitygroups/" + accountNum + "/" + region + "/" + id);
        };
        $scope.securitygroups = [];
        for (let i = 0; i < $scope.regions.length; i++) {
            const params = {
                region: $scope.regions[i]
            };
            //}

            //$scope.securitygroupsREST(params, body, additionalParams)
            $http({
                    method: "GET",
                    url: endpoint + "/securitygroups",
                    params: params

                })
                .then(function (response) {
                    for (let j = 0; j < response.data.SecurityGroups.length; j++) {
                        $scope.securitygroups.push(response.data.SecurityGroups[j]);
                    }
                    $scope.loading = false;
                }, function (reason) {
                    $scope.loading = false;
                });
        }
    }])

    .controller("InstanceListController", ["$scope", "$location", "$http", function ($scope, $location, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitInstanceFromInstances = function (accountNum, region, id) {
            $location.path("instances/" + accountNum + "/" + region + "/" + id);
        };
        $scope.visitInstance = function (accountNum, region, id) {
            $location.path("instances/" + accountNum + "/" + region + "/" + id);
        };

        $scope.avgAge = function (instances) {
            let age = 0;
            const _MS_PER_DAY = 1000 * 60 * 60 * 24;
            for (let i = 0; i < instances.length; i++) {
                const date = new Date(instances[i].CreateDate * 1000);
                const now = new Date();
                const diff = now.getTime() - date.getTime();
                age += Math.round(diff / _MS_PER_DAY);
            }
            const avg = Math.round(age / instances.length);
            return avg;
        };

        $scope.riskscore = function (runtime, imageAge) {
            let runtimeScore = 3;
            let ageScore = 3;

            if (runtime < 3) {
                runtimeScore = 1;
            } else if (runtime <= 6) {
                runtimeScore = 2;
            } else {
                runtimeScore = 3;
            }

            if (imageAge < 6) {
                ageScore = 1;
            } else if (imageAge <= 12) {
                ageScore = 2;
            } else {
                ageScore = 3;
            }

            let score = 0.7 * ageScore + 0.3 * runtimeScore;
            if (score <= 1) {
                return "low";
            } else if (score <= 2) {
                return "medium";
            }

            return "high";

        }

        $scope.instances = [];
        //var handleInstancesREST = function (response) {
        //    for (let j = 0; j < response.data.Instances.length; j++) {
        //        $scope.instances.push(response.data.Instances[j]);
        //    }
        //    $scope.loading = false;
        //    $scope.$apply();
        //};

        for (let i = 0; i < $scope.regions.length; i++) {
            const params = {
                region: $scope.regions[i]
            };

            $http({
                    method: "GET",
                    url: endpoint + "/instances",
                    params: params
                })
                .then(function (response) {
                    for (let j = 0; j < response.data.Instances.length; j++) {
                        $scope.instances.push(response.data.Instances[j]);
                    }
                    $scope.loading = false;
                }, function (reason) {
                    console.log(reason)
                    $scope.loading = false;
                });
            //$scope.loading = false;
        }


    }])

    .controller("S3Controller", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        const name = $routeParams.bucket;
        const accountNum = $routeParams.accountNum;
        const params = {
            account: accountNum,
            bucket: name
        };

        $http({
                method: "GET",
                url: endpoint + "/bucket",
                params: params
            })
            .then(function (response) {
                $scope.bucket = response.data.Bucket;
                console.log($scope.bucket);
                $scope.objects = response.data.Objects;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("S3ListController", ["$scope", "$location", "$http", "$timeout", function ($scope, $location, $http, $timeout) {
        "use strict";
        $scope.loading = true;

        $scope.visitS3 = function (accountNum, s3) {
            $location.path("buckets/" + accountNum + "/" + s3);
        };

        const params = {};

        $http({
                method: "GET",
                url: endpoint + "/s3",
                params: params
            })
            .then(function (response) {
                $scope.s3buckets = response.data.Buckets;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("ELBListController", ["$scope", "$location", "$http", "$timeout", function ($scope, $location, $http, $timeout) {
        "use strict";
        $scope.loading = true;

        $scope.visitELB = function (accountNum, id) {
            $location.path("loadbalancers/" + accountNum + "/" + id);
        };
        for (let i = 0; i < $scope.regions.length; i++) {
            const params = {
                region: $scope.regions[i]
            };


            $http({
                    method: "GET",
                    url: endpoint + "/elbs",
                    params: params
                })
                .then(function (response) {
                    for (let j = 0; j < response.data.LoadBalancers.length; j++) {
                        $scope.elbs.push(response.data.LoadBalancers[j]);
                    }
                    $scope.loading = false;
                }, function (reason) {
                    $scope.loading = false;
                });
        }
    }])

    .controller("AccountController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitInstance = function (accountNum, region, id) {
            $location.path("instances/" + accountNum + "/" + region + "/" + id);
        };

        $scope.visitAccount = function (accountNum) {
            $location.path("accounts/" + accountNum);
        };

        $scope.visitUser = function (accountNum, user) {
            $location.path("users/" + accountNum + "/" + user);
        };

        $scope.instancesCollapsed = true;
        $scope.usersCollapsed = true;
        $scope.elbsCollapsed = true;
        $scope.instances = [];
        $scope.databases = [];
        $scope.tables = [];

        const alias = $routeParams.accountNum;
        const params = {
            account: alias,
            region: "us-east-1"
        };

        $http({
                method: "GET",
                url: endpoint + "/account",
                params: params
            })
            .then(function (response) {
                $scope.account = response.data.Account;
                //$scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

        for (let i = 0; i < $scope.regions.length; i++) {
            const params = {
                account: alias,
                region: $scope.regions[i]
            };

            //}

            $http({
                    method: "GET",
                    url: endpoint + "/instances",
                    params: params
                })
                .then(function (response) {
                    for (let j = 0; j < response.data.Instances.length; j++) {
                        $scope.instances.push(response.data.Instances[j]);
                    }

                }, function (reason) {
                    $scope.loading = false;
                });

            $http({
                    method: "GET",
                    url: endpoint + "/databases",
                    params: params
                })
                .then(function (response) {
                    for (let j = 0; j < response.data.Databases.length; j++) {
                        $scope.databases.push(response.data.Databases[j]);
                    }
                }, function (reason) {
                    $scope.loading = false;
                });

            $http({
                    method: "GET",
                    url: endpoint + "/dynamotables",
                    params: params
                })
                .then(function (response) {
                    for (let j = 0; j < response.data.Tables.length; j++) {
                        $scope.tables.push(response.data.Tables[j]);
                    }
                }, function (reason) {
                    $scope.loading = false;
                });

            $http({
                    method: "GET",
                    url: endpoint + "/users",
                    params: params
                })
                .then(function (response) {
                    $scope.users = response.data.Users;
                    $scope.loading = false;
                }, function (reason) {
                    $scope.loading = false;
                });

            $http({
                    method: "GET",
                    url: endpoint + "/s3",
                    params: params
                })
                .then(function (response) {
                    $scope.s3buckets = response.data.Buckets;
                    $scope.loading = false;
                }, function (reason) {
                    $scope.loading = false;
                });
        }

        $scope.instanceSubmit = function () {
            if ($scope.instanceId) {
                $scope.visitInstance($scope.account.accountNum, $scope.instanceId);
            }
        };
    }])

    .controller("ELBController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitELB = function (accountNum, region, elbId) {
            $location.path("loadbalancers/" + accountNum + "/" + region + "/" + elbId);
        };

        $scope.visitSecurityGroup = function (accountNum, region, sgId) {
            $location.path("securitygroups/" + accountNum + "/" + region + "/" + sgId);
        };

        $scope.visitInstance = function (accountNum, region, id) {
            $location.path("instances/" + accountNum + "/" + region + "/" + id);
        };

        const elbId = $routeParams.elbId;
        const accountNum = $routeParams.accountNum;
        const params = {
            account: accountNum,
            elb: elbId
        };

        $http({
                method: "GET",
                url: endpoint + "/elb",
                params: params
            })
            .then(function (response) {
                $scope.elb = response.data.LoadBalancer;
                $scope.account = response.data.Account;
                $scope.instances = response.data.Instances;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("SGController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitSecurityGroup = function (accountNum, region, sgId) {
            $location.path("securitygroups/" + accountNum + "/" + region + "/" + sgId);
        };

        $scope.visitELB = function (accountNum, region, id) {
            $location.path("loadbalancers/" + accountNum + "/" + region + "/" + id);
        };

        $scope.visitInstance = function (accountNum, region, id) {
            $location.path("instances/" + accountNum + "/" + region + "/" + id);
        };

        $scope.formatInboundSGData = function (sg) {
            let rules = [];

            try {
                if (sg.InboundRules.length === 0) {
                    rules.push({
                        "Source": "all",
                        "Ports": "all",
                        "Protocol": "all"
                    });
                } else {
                    for (let i = 0; i < sg.InboundRules.length; i++) {
                        let ports;
                        let protocol;
                        switch (sg.InboundRules[i].IpProtocol) {
                            case "-1":
                                protocol = "all";
                                break;
                            case "tcp":
                                protocol = "tcp";
                                break;
                            case "udp":
                                protocol = "udp";
                                break;
                            default:
                                protocol = "?";
                                break;
                        }
                        if (sg.InboundRules[i].FromPort) {
                            ports = sg.InboundRules[i].FromPort + "-";
                            ports += sg.InboundRules[i].ToPort;
                        } else {
                            ports = "all";
                        }
                        for (let j = 0; j < sg.InboundRules[i].IpRanges.length; j++) {
                            rules.push({
                                "Source": sg.InboundRules[i].IpRanges[j].CidrIp,
                                "Ports": ports,
                                "Protocol": protocol
                            });
                        }

                        for (let j = 0; j < sg.InboundRules[i].UserIdGroupPairs.length; j++) {
                            rules.push({
                                "Source": sg.InboundRules[i].UserIdGroupPairs[j].GroupId,
                                "Ports": ports,
                                "Protocol": protocol
                            });
                        }
                        for (let j = 0; j < sg.InboundRules[i].PrefixListIds.length; j++) {
                            rules.push({
                                "Source": sg.InboundRules[i].PrefixListIds[j].GroupId,
                                "Ports": ports,
                                "Protocol": protocol
                            });
                        }
                    }
                }
            } finally {}
            return rules;
        };

        $scope.formatOutboundSGData = function (sg) {
            let rules = [];
            try {
                if (sg.OutboundRules.length === 0) {
                    rules.push({
                        "Source": "all",
                        "Ports": "all",
                        "Protocol": "all"
                    });
                }
                for (let i = 0; i < sg.OutboundRules.length; i++) {
                    let ports;
                    let protocol;
                    switch (sg.OutboundRules[i].IpProtocol) {
                        case "-1":
                            protocol = "all";
                            break;
                        case "tcp":
                            protocol = "tcp";
                            break;
                        case "udp":
                            protocol = "udp";
                            break;
                        default:
                            protocol = "?";
                            break;
                    }
                    if (sg.OutboundRules[i].FromPort) {
                        ports = sg.OutboundRules[i].FromPort + "-";
                        ports += sg.OutboundRules[i].ToPort;
                    } else {
                        ports = "all";
                    }
                    for (let j = 0; j < sg.OutboundRules[i].IpRanges.length; j++) {
                        rules.push({
                            "Destination": sg.OutboundRules[i].IpRanges[j].CidrIp,
                            "Ports": ports,
                            "Protocol": protocol
                        });
                    }

                    for (let j = 0; j < sg.OutboundRules[i].UserIdGroupPairs.length; j++) {
                        rules.push({
                            "Destination": sg.OutboundRules[i].UserIdGroupPairs[j].GroupId,
                            "Ports": ports,
                            "Protocol": protocol
                        });
                    }
                }
            } finally {}
            return rules;
        };

        const sgId = $routeParams.sgId;
        const accountNum = $routeParams.accountNum;
        const region = $routeParams.region;
        const params = {
            account: accountNum,
            group: sgId,
            region: region
        };

        $http({
                method: "GET",
                url: endpoint + "/securitygroup",
                params: params
            })
            .then(function (response) {
                $scope.securitygroup = response.data.SecurityGroup;
                $scope.account = response.data.Account;
                $scope.instances = response.data.Instances;
                $scope.elbs = response.data.ELB;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });

    }])

    .controller("UserController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitUser = function (accountNum, user) {
            $location.path("users/" + accountNum + "/" + user);
        };

        const accountNum = $routeParams.accountNum;
        const user = $routeParams.user;
        const params = {
            account: accountNum,
            user: user
        };

        $http({
                method: "GET",
                url: endpoint + "/user",
                params: params
            })
            .then(function (response) {
                $scope.user = response.data.User;
                $scope.account = response.data.Account;
                $scope.accesskeys = response.data.AccessKeys;
                $scope.message = response.data.Message;
                $scope.error = !!$scope.message;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });
    }])

    .controller("InstanceController", ["$scope", "$location", "$routeParams", "$http", function ($scope, $location, $routeParams, $http) {
        "use strict";
        $scope.loading = true;

        $scope.visitAccount = function (accountNum) {
            $location.path("accounts/" + accountNum);
        };

        $scope.visitSecurityGroup = function (accountNum, region, sg) {
            $location.path("securitygroups/" + accountNum + "/" + region + "/" + sg);
        };

        $scope.getDate = function (inDate) {
            const date = new Date(inDate * 1000);
            const formatted = date.toLocaleDateString("de-DE", {
                year: "numeric",
                month: "2-digit",
                day: "2-digit"
            }).replace(/\./g, "/");

            return formatted;
        };
        const instanceId = $routeParams.instanceId;
        const accountNum = $routeParams.accountNum;
        const region = $routeParams.region;
        const params = {
            account: accountNum,
            instance: instanceId,
            region: region
        };

        $http({
                method: "GET",
                url: endpoint + "/instance",
                params: params
            })
            .then(function (response) {
                $scope.instance = response.data.Instance;
                $scope.account = response.data.Account;
                $scope.routes = response.data.Routes;
                $scope.loading = false;
            }, function (reason) {
                $scope.loading = false;
            });
    }])

    .controller('AddAccountModalController', ['$scope', '$uibModalInstance', '$http', function ($scope, $uibModalInstance, $http) {
        var d = new Date();
        $scope.ok = function (accountNum, alias, email, owner) {
            $uibModalInstance.close();

            if (alias === null || typeof alias === "undefined") {
                alias = '';
            }
            if (email === null || typeof email === "undefined") {
                email = '';
            }
            if (owner === null || typeof owner === "undefined") {
                owner = '';
            }

            var params = {
                accountNum: accountNum,
                alias: alias,
                email: email,
                owner: owner
            }
            console.log(accountNum,alias,email,owner);
            var url = endpoint + "/addAccount";
            $http.post(url, params, config)
                .then(function (response) {
                    $scope.loading = false;
                }, function (reason) {
                    $scope.loading = false;
                });

        };

        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };
    }]);