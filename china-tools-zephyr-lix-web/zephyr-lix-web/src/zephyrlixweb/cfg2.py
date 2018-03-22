from linkedin.config.base import framework
from linkedin.config.base.framework import types


class IrisClientConfiguration(framework.AppDefPlugin):
    """
    All Iris client configurations
    """
    API_KEY = types.Entry(types.String(), default=None, description='API Key.')
