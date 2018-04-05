""" BOVI(n)E login lambda. """
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


def lambda_handler(*kwargs):
    """ Login lambda. """
    LOGGER.info(kwargs[0])
    LOGGER.info(kwargs[1])

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
        "Content-Type": "text/html"
    }
    response = {
        "statusCode": 200,
        "body": html,
        "headers": headers
    }
    return response
