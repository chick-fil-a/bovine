#!/usr/bin/python

import json
import boto3
import logging
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    logger.info(context)

    html = """
    <html>

<body>
    <script>
        var params = {}, queryString = location.hash.substring(1),
            regex = /([^&=]+)=([^&]*)/g, m;
        while (m = regex.exec(queryString)) {
            params[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
        }
        function createCookie(name, value, minutes) {
            var expires = "";
            if (minutes) {
                var date = new Date();
                date.setTime(date.getTime() + (minutes * 1000));
                expires = "; expires=" + date.toUTCString();
            }
            document.cookie = name + "=" + value + expires + "; path=/;secure";
        }
        createCookie('portal_cookie', params.id_token, params.expires_in);
        if (typeof (return_to) === 'undefined') {
            return_to = '/';
        }

        window.location.href = return_to;
    </script>
</body>

</html>
"""

    headers = {
        "Content-Type" : "text/html"
    }
    response = {
        "statusCode": 200,
        "body": html,
        "headers": headers
    }
    return response

if __name__ == "__main__":
    handler(None, None)
