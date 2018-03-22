import json
import urllib2
import ssl
import logging


LIX_ENDPOINT = 'https://lix.corp.linkedin.com/api/v2/PROD/tests/key/'


def get_lix_labels(lix_name, context=None):
    lix_url = "%s%s" % (LIX_ENDPOINT, lix_name)
    try:
        if context is None:
            req = urllib2.urlopen(lix_url, timeout=60)
        else:
            req = urllib2.urlopen(lix_url, context=context, timeout=60)

    except (urllib2.HTTPError, urllib2.URLError) as e:
        if context is None:
            return get_lix_labels(lix_url, ssl.SSLContext(ssl.PROTOCOL_TLSv1))
        else:
            logging.info("Lix label exception : %s" % e)
            return ('None')
    except Exception as e:
        logging.info("Lix label exception: %s" % e)
        return ('None')

    lix_json = json.loads(req.read())
    if lix_json:
        labels = str(lix_json[0]['labels'])
        if labels:
            return labels
        else:
            return ('None')
    else:
        return ('None')  # This returns the list of labels for a lix based on lix name
