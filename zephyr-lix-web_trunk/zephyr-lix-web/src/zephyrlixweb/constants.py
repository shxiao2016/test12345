import re

FP_BEYOND_10 = 'fully ramped > 10 days'
FP_LESS_THAN_10 = 'fully ramped < 10 days'
SUBTOTAL = 'subtotal'
OUTLIERS = 'outliers'
UNKNOWN_PERIOD = 'unknown_period'
GREATER_THAN_90 = '>90 days'
GREATER_THAN_60 = '>60 days'
GREATER_THAN_30 = '30-60 days'
NEWER_THAN_30 = '<30 days'
ALL_PILLARS = 'all_pillars'
PILLAR_KEY = 'pillar'
PLATFORM_KEY = 'platform'
RAMPED_OUTLIERS = 'ramped_outliers'
NON_RAMPED_OUTLIERS = 'non_ramped_outliers'

OVERDUE = 'overdue'
WHITELISTED = 'whitelisted'
CLEANED = 'cleaned'
FIX_RATE = 'fix_rate'

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
PILLARS = ['career', 'content', 'profile', 'growth']

MP_RE = re.compile('\(string-property "mpName"\)')
PLATFORMS = {'android': 'zephyr-android', 'ios': 'zephyr-ios', 'api': 'zephyr-api'}
ZEPHYR_LIX_COUNT = 'zephyr_lix_count'
ZEPHYR = "zephyr"
VOYAGER = "voyager"

PROFILE_VOYAGER_PILLARS = ['me', 'guidededit', 'axle', 'l2m', 'edit', 'profile', 'mePortal', 'gamification', 'identity']
CAREER_VOYAGER_PILLARS = ['jobs', 'entities', 'search', 'premium', 'job', 'organizations', 'organization',
                          'infra', 'typeahead', 'career', 'companyReview', 'companyReviewList']
CONTENT_VOYAGER_PILLARS = ['feed', 'publishing', 'messaging', 'content', 'video']
GROWTH_VOYAGER_PILLARS = ['people', 'growth', 'onboarding', 'setting', 'mynetwork', 'relationships', 'settings']

KEY_API = "api"
KEY_ANDROID = "android"
KEY_IOS = "ios"
ZEPHYR_LIX_COUNT = 'zephyr_lix_count'

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

ZEPHYR_GIT_REPOS_LOCAL = {}

VOYAGER_GIT_REPOS_LOCAL = {}
VOYAGER_LIXES_FROM_CODE = {}

ONE_DAY_MILLI_SECONDS = 24 * 3600 * 1000
TEN_DAYS_MILLI_SECONDS = ONE_DAY_MILLI_SECONDS * 10
SIXTEEN_DAYS_MILLI_SECONDS = ONE_DAY_MILLI_SECONDS * 16
THIRTY_DAYS_MILLI_SECONDS = ONE_DAY_MILLI_SECONDS * 30
SIXTY_DAYS_MILLI_SECONDS = ONE_DAY_MILLI_SECONDS * 60
NINETY_DAYS_MILLI_SECONDS = ONE_DAY_MILLI_SECONDS * 90
TWO_DAYS_MILLI_SECONDS = ONE_DAY_MILLI_SECONDS * 2

WORK_DIR = "/export/content/data/zephyr-lix-web/trunks"

ZEPHYR_GIT_REPOS = {KEY_API: "git@gitli.corp.linkedin.com:zephyr/zephyr-api.git",
                    KEY_IOS: "git@gitli.corp.linkedin.com:zephyr/zephyr-ios.git",
                    KEY_ANDROID: "git@gitli.corp.linkedin.com:zephyr/zephyr-android.git"}

ZEPHYR_MP_VERSION_FILE = {KEY_API: "product-spec.json",
                          KEY_IOS: "zephyr-product-spec.json",
                          KEY_ANDROID: "Flagship/build.gradle"}

ZEPHYR_MP_VERSION_KEY_WORDS = {KEY_API: '"version"',
                               KEY_IOS: '"mergedVoyagerMpVersion"',
                               KEY_ANDROID: 'versionName'}

VOYAGER_GIT_REPOS = {KEY_API: "git@gitli.corp.linkedin.com:voyager/voyager-api.git",
                     KEY_IOS: "git@gitli.corp.linkedin.com:voyager/voyager-ios.git",
                     KEY_ANDROID: "git@gitli.corp.linkedin.com:voyager/voyager-android.git"}

LIX_FILE_PATTERN = {KEY_API: re.compile('.*LixKey\.java$'),
                    KEY_IOS: re.compile(".*LixTests\.plist$"),
                    KEY_ANDROID: ["Flagship/src/main/java/com/linkedin/android/infra/lix/Lix.java",
                                  "Flagship/src/main/java/com/linkedin/android/infra/lix/GuestLix.java"]}

LIX_STRING_PATTERN = {KEY_API: re.compile('[_A-Z0-9]+\("([^\"]+)"'),
                      KEY_IOS: re.compile('<key>([^\"]+)</key>'),
                      KEY_ANDROID: re.compile('[_A-Z0-9]*\(?"([^\"]+)"')}

OPTION_DAYS = "option_days"
OPTION_BETWEEN = "option_between"

ZEPHYR_LIX_WEB_URL = "https://tools.corp.linkedin.com/apps/tools/zephyr_lix"
VOYAGER_NEWLY_INTRODUCED = "/voyager_newly_introduced/"
VOYAGER_RAMP_STATUS_CHANGE = "/ramp_status_change/"

LI_SMTP = 'email.corp.linkedin.com'
MAX_VOYAGER_LIX_PREIVIEW_COUNT = 50

FULLY_RAMPED_TIME_RANGE = "fully_ramp_time_range"
KEY_VAGUE_SEARCH = "key_vague_search"
NON_FULLY_RAMPED = "non_fully_ramped_lix"
SEPARATOR = "##"
GIT_URL = 'https://gitli.corp.linkedin.com/zephyr/'
HEADERS = ['platform', 'pillar', 'period', 'name', 'fully_ramped', 'owners', 'description', 'spec_url', 'comment', 'url', 'cleaned', 'sprint_version']
SPRINT_VERSION = 'sprint_version'
