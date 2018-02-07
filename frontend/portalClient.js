//import {URITemplate} from "./node_modules/urijs/src/URITemplate";
/*global location, console, apiGateway */

var portalClient = {};
portalClient.newClient = function (config) {
    "use strict";
    const apigClient = {};
    if (config === undefined) {
        config = {
            accessKey: "",
            secretKey: "",
            sessionToken: "",
            region: "",
            apiKey: undefined,
            defaultContentType: "application/json",
            defaultAcceptType: "application/json"
        };
    }
    if (config.accessKey === undefined) {
        config.accessKey = "";
    }
    if (config.secretKey === undefined) {
        config.secretKey = "";
    }
    if (config.apiKey === undefined) {
        config.apiKey = "";
    }
    if (config.sessionToken === undefined) {
        config.sessionToken = "";
    }
    if (config.region === undefined) {
        config.region = "us-east-1";
    }
    //If defaultContentType is not defined then default to application/json
    if (config.defaultContentType === undefined) {
        config.defaultContentType = "application/json";
    }
    //If defaultAcceptType is not defined then default to application/json
    if (config.defaultAcceptType === undefined) {
        config.defaultAcceptType = "application/json";
    }


    // extract endpoint and path from url
    let endpoint = "";
    let pathComponent = null;
    if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
        endpoint = location.origin;
        pathComponent = "/test-data";
    } else {
        endpoint = "https://" + location.host + "/api";
        console.log(endpoint);
        pathComponent = "";
    }
    console.log(pathComponent);

    let sigV4ClientConfig = {
        accessKey: config.accessKey,
        secretKey: config.secretKey,
        sessionToken: config.sessionToken,
        serviceName: "execute-api",
        region: config.region,
        endpoint: endpoint,
        defaultContentType: config.defaultContentType,
        defaultAcceptType: config.defaultAcceptType
    };

    let authType = "NONE";
    if (sigV4ClientConfig.accessKey !== undefined && sigV4ClientConfig.accessKey !== "" && sigV4ClientConfig.secretKey !== undefined && sigV4ClientConfig.secretKey !== "") {
        authType = "AWS_IAM";
    }

    let simpleHttpClientConfig = {
        endpoint: endpoint,
        defaultContentType: config.defaultContentType,
        defaultAcceptType: config.defaultAcceptType
    };

    let apiGatewayClient = apiGateway.core.apiGatewayClientFactory.newClient(simpleHttpClientConfig, sigV4ClientConfig);


    apigClient.rootOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const rootOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(rootOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.accountregPost = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const accountregPostRequest = {
            verb: "post".toUpperCase(),
            path: pathComponent + URITemplate("/accountreg").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(accountregPostRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.bastionregPost = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const bastionregPostRequest = {
            verb: "post".toUpperCase(),
            path: pathComponent + URITemplate("/bastionreg").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(bastionregPostRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.bastionsetupGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const bastionsetupGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/bastionsetup").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(bastionsetupGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.getaccountsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const getaccountsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/getaccounts").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(getaccountsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.getpublicipGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const getpublicipGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/getpublicip").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(getpublicipGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAccountsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAccountsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/accounts").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAccountsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAccountsOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAccountsOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/accounts").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAccountsOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAccountsGetaccountGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAccountsGetaccountGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/accounts/getaccount").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAccountsGetaccountGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAccountsGetaccountOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAccountsGetaccountOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/accounts/getaccount").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAccountsGetaccountOptionsRequest, authType, additionalParams, config.apiKey);
    };

    apigClient.portalComplianceOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalComplianceOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/reports/latest").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalComplianceOptionsRequest, authType, additionalParams, config.apiKey);
    };

    apigClient.lastestComplianceReportGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalComplianceGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/reports/latest").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalComplianceGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalReportsListGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalReportsListGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/reports/").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalReportsListGetRequest, authType, additionalParams, config.apiKey);
    };

    apigClient.portalComplianceRun = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalComplianceRunRequest = {
            verb: "post".toUpperCase(),
            path: pathComponent + URITemplate("/compliance/run").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalComplianceRunRequest, authType, additionalParams, config.apiKey);
    };

    apigClient.portalAlertsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAlertsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/alerts").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAlertsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAlertsPost = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAlertsPostRequest = {
            verb: "post".toUpperCase(),
            path: pathComponent + URITemplate("/portal/alerts").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAlertsPostRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAlertsOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAlertsOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/alerts").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAlertsOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAlertsAccountGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAlertsAccountGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/alerts/account").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAlertsAccountGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalAlertsAccountOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalAlertsAccountOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/alerts/account").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalAlertsAccountOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalDatabasesGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalDatabasesGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/databases").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalDatabasesGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalDatabasesOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalDatabasesOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/databases").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalDatabasesOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalDynamotablesGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalDynamotablesGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/dynamotables").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalDynamotablesGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalDynamotablesOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalDynamotablesOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/dynamotables").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalDynamotablesOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalElbsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalElbsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/elbs").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalElbsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalElbsOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalElbsOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/elbs").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalElbsOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalElbsGetelbGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalElbsGetelbGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/elbs/getelb").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalElbsGetelbGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalElbsGetelbOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalElbsGetelbOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/elbs/getelb").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalElbsGetelbOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalGetregionsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalGetregionsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/getregions").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalGetregionsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalGetregionsOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalGetregionsOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/getregions").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalGetregionsOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalIamOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalIamOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/iam").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalIamOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalIamRolesGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalIamRolesGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/iam/roles").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalIamRolesGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalIamRolesOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalIamRolesOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/iam/roles").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalIamRolesOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalInstancesGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalInstancesGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/instances").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalInstancesGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalInstancesOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalInstancesOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/instances").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalInstancesOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalInstancesGetinstanceGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalInstancesGetinstanceGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/instances/getinstance").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalInstancesGetinstanceGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalInstancesGetinstanceOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalInstancesGetinstanceOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/instances/getinstance").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalInstancesGetinstanceOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalPingGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalPingGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/ping").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalPingGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalPingOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalPingOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/ping").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalPingOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalPublicipsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalPublicipsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/publicips").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalPublicipsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalPublicipsOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalPublicipsOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/publicips").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalPublicipsOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalRedshiftclustersGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalRedshiftclustersGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/redshiftclusters").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalRedshiftclustersGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalRedshiftclustersOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalRedshiftclustersOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/redshiftclusters").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalRedshiftclustersOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalS3Get = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalS3GetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/s3").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalS3GetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalS3Options = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalS3OptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/s3").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalS3OptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalS3BucketGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalS3BucketGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/s3/bucket").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalS3BucketGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalS3BucketOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalS3BucketOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/s3/bucket").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalS3BucketOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalSecuritygroupsGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalSecuritygroupsGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/securitygroups").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalSecuritygroupsGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalSecuritygroupsOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalSecuritygroupsOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/securitygroups").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalSecuritygroupsOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalSecuritygroupsGetsgGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalSecuritygroupsGetsgGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/securitygroups/getsg").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalSecuritygroupsGetsgGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalSecuritygroupsGetsgOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalSecuritygroupsGetsgOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/securitygroups/getsg").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalSecuritygroupsGetsgOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalSummaryGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalSummaryGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/summary").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalSummaryGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalSummaryOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalSummaryOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/summary").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalSummaryOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalUsersGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalUsersGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/users").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalUsersGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalUsersOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalUsersOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/users").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalUsersOptionsRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalUsersGetuserGet = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalUsersGetuserGetRequest = {
            verb: "get".toUpperCase(),
            path: pathComponent + URITemplate("/portal/users/getuser").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalUsersGetuserGetRequest, authType, additionalParams, config.apiKey);
    };


    apigClient.portalUsersGetuserOptions = function (params, body, additionalParams) {
        if (additionalParams === undefined) {
            additionalParams = {};
        }

        apiGateway.core.utils.assertParametersDefined(params, [], ["body"]);

        const portalUsersGetuserOptionsRequest = {
            verb: "options".toUpperCase(),
            path: pathComponent + URITemplate("/portal/users/getuser").expand(apiGateway.core.utils.parseParametersToObject(params, [])),
            headers: apiGateway.core.utils.parseParametersToObject(params, []),
            queryParams: apiGateway.core.utils.parseParametersToObject(params, []),
            body: body
        };


        return apiGatewayClient.makeRequest(portalUsersGetuserOptionsRequest, authType, additionalParams, config.apiKey);
    };


    return apigClient;
};
