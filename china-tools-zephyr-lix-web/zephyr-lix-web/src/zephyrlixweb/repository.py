import logging
import os
import urllib2
import urllib
import tarfile
import zipfile
from constants import GIT_URL

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(name)s) %(message)s')
log = logging.getLogger(__name__)


class repository(object):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    # @staticmethod
    def mkdir(self):
        if not os.path.exists(self.repo_path):
            os.mkdir(self.repo_path, 0755)
        return self.repo_path

    def get_latest_revision_in_git(self, repo):
        starturl = GIT_URL + repo
        print starturl
        log.info('starturl: %s' % starturl)
        req = urllib2.Request(starturl)
        res = urllib2.urlopen(req)
        finalurl = res.geturl()
        log.info('finalurl: %s' % finalurl)
        if not finalurl:
            log.info('invalid git url')
            return None
        index = finalurl.rfind('/')
        if index <= 0:
            log.info('cannot find / in url %s' % finalurl)
            return None
        url_len = len(finalurl)
        if index + 1 >= url_len - 1:
            log.info('cannot find revision in url %s' % finalurl)
            return None
        revision = finalurl[index + 1:url_len - 1]
        return revision

    def download_repo_from_git(self, repo, revision):
        url = '{0}{1}/archive/{2}.tar.gz'.format(GIT_URL, repo, revision)
        try:
            testfile = urllib.URLopener()
            testfile.retrieve(url, '{0}/{1}-{2}.tar.gz'.format(self.repo_path, repo, revision))
            return '{0}/{1}-{2}.tar.gz'.format(self.repo_path, repo, revision)
        except Exception as e:
            log.exception(e)
            return None

    def unzip_tar_gz_zip(self, rawfile, target_folder):
        if not rawfile:
            return False
        log.info(rawfile)
        log.info(target_folder)
        if not os.path.exists(target_folder):
            os.mkdir(target_folder, 0755)
        try:
            if (rawfile.endswith("tar.gz")):
                tar = tarfile.open(rawfile, "r:gz")
                tar.extractall(path=target_folder)
                tar.close()
            elif (rawfile.endswith("tar")):
                tar = tarfile.open(rawfile, "r:")
                tar.extractall(path=target_folder)
                tar.close()
            elif (rawfile.endswith("zip")):
                zip_ref = zipfile.ZipFile(rawfile, 'r')
                zip_ref.extractall(target_folder)
                zip_ref.close()
            os.remove(rawfile)
            return True
        except Exception as e:
            log.exception("Error while unzip the file: {0}".format(e))
            if rawfile:
                os.remove(rawfile)
            return False
