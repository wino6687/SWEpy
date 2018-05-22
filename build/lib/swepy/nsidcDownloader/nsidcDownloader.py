import os
import requests

from tqdm import tqdm
from datetime import datetime
from functools import partial
from string import Formatter

import pandas as pd

try:
    if get_ipython().config['IPKernelApp']['parent_appname'] == 'ipython-notebook':
        from tqdm import tqdm_notebook as tqdm
except:
    pass

class nsidcDownloader():

    url_template = "{protocol}://{server}/{datapool}/{dataset}.{version}/{date:%Y.%m.%d}" \
                    "/{dataset}-{projection}_{grid}{resolution}-{platform}_{sensor}" \
                    "-{date:%Y%j}-{channel}-{pass}-{algorithm}-{input}-{dataversion}.nc"

    defaults = {
        "protocol": "https",
        "server": "n5eil01u.ecs.nsidc.org",
        "datapool": "MEASURES",
        "dataset": "NSIDC-0630",
        "version": "001",
        "projection": "EASE2",
        "grid": "N",
        "pass": "M",
        "algorithm": "SIR",
        "input": "CSU",
        "dataversion": "v1.2"
    }

    def __init__(self, username=None, password=None, folder=".", **kwargs):
        '''
        Snow Water Equivalence downloader.

        :param username: NASA Earthdata username
        :param password: NASA Earthdata password
        :param kwargs: keys to use as default in url_template
        '''

        ## Get formatting keys of url_template
        self.url_keys = [k[1] for k in Formatter().parse(self.url_template)]

        ## Function to format URL
        self.format_url = partial(self.url_template.format)

        ## Set url template defaults to specified defaults
        self.set_defaults(**self.defaults) ## global defaults (in this class)
        self.set_defaults(**kwargs)        ## instance defaults

        ## Auth Detauls
        self.username = username
        self.password = password

        ## Tet up session
        self.session = requests.session()
        self.get_auth()

        ## Output
        self.folder = folder

    def set_defaults(self, **kwargs):
        '''
        Set defaults for url template
        '''

        for key in kwargs:
            if key in self.url_keys:
                self.format_url.keywords[key] = kwargs[key]

        return(self.format_url.keywords)

    def get_auth(self):
        '''
        Get download authentication

        How authentication works:
        (1) request to some sort of NSIDC URL
        (2) get HTTP 302 response redirecting to urs.earthdata.nasa.gov OAuth
        (3) login at urs.earthdata.nasa.gov oauth
        (4) use oauth tokens from urs.earthdata.nasa.gov to request any download url
        '''

        test_url = "{protocol}://{server}/SMAP/".format(**self.format_url.keywords)

        ## User / pass to use with auth.
        ## Will attempt to use auth in ~/.netrc if not passed
        if self.username and self.password:
            self.session.auth = (self.username, self.password)

        ## Send test request, keep following the redirects and scoop
        ## up all of the cookies along the way in self.session
        try:
            req = self.session.get(test_url, allow_redirects = False)

            while req.status_code == 302:
                req = self.session.get(req.headers["Location"],
                                       allow_redirects = False)
        except requests.ConnectionError:
            pass

        ## If the final request is 401 (Bad Auth), throw exception
        if req.status_code == 401:
            raise PermissionError("Bad NASA Earthdata Authentication!")

    def download_file(self, folder=None, overwrite=False, **kwargs):
        '''
        Download a file of particular kwargs
        '''

        url = self.format_url(**kwargs)

        ## Dict of all the keywords:vals going into URL
        all_keywords = {**kwargs, **self.format_url.keywords}

        ## Format output dir with keywords if there's none passed
        if not folder:
            folder = self.folder.format(all_keywords)

        ## Prepare file system
        filename = url.split("/")[-1]
        filepath = "{}/{}".format(folder, filename)
        block_size = 1024
        #print("{}".format(filename))

        if os.path.exists(filepath):
            if overwrite:
                os.remove(filepath)
            else:
                print(" ** (skipping...) **")
                return filename

        ## Download the dang thing
        with self.session.get(url, stream=True) as r:

            if r.status_code == 404:
                raise FileNotFoundError("File Not Found: {}".format(url))

            ## Open file
            with open(filepath, 'wb') as f:

                pbar = tqdm(initial=0,
                            total=int(r.headers['content-length']),
                            unit='B',
                            unit_scale=True)

                ## Create dest folder if not exist
                if not os.path.exists(folder):
                    os.makedirs(folder)

                ## Stream content to file in chunks
                for chunk in r.iter_content(block_size):
                    f.write(chunk)
                    pbar.update(block_size)

            pbar.close()

        return filename  ## changed to filename from filepath to fix another script

    def download_range(self, date, **kwargs):
        '''
        Download a range of dates for a particular sensor
        '''

        assert isinstance(date, list), "Range passed must be list of dates"

        for date in pd.date_range(date[0], date[1]):
            kwargs["date"] = date
            self.download_file(**kwargs)

#dataset = {
    #"resolution": "3.125km",
    #"platform": "F17",
    #"sensor": "SSMIS",
    #"date": datetime(2015,10,10),
    #"channel": "37H"
#}
