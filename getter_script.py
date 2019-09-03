import swepy.pipeline as pipe
import swepy.process as process
from swepy.analysis import Analysis
import datetime
import os
import boto3
import logging
from botocore.exceptions import ClientError


def upload_directory_s3(path, bucketname, directory):
    """
    Recursively walk the zarr directory we want to upload
    """
    s3c = boto3.client("s3")
    for root, dirs, files in os.walk(path):
        for file in files:
            s3c.upload_file(
                os.path.join(root, file), bucketname, directory + file
            )


if __name__ == "__main__":
    ul = [60, -130]
    lr = [69, -147]

    start = datetime.date(1992, 1, 1)
    end = datetime.date(1992, 1, 3)
    username = "wino6687"
    password = "Desmo12@"

    swe_obj = pipe.Swepy(
        os.getcwd(), start, end, ul, lr, username, password, high_res=True
    )
    swe_obj.clean_dirs()
    files = swe_obj.scrape_all()
    zarrs = swe_obj.convert_netcdf_zarr()
    upload_directory_s3("zarr19", "earthlab-will-lstm", "Russia19/")
    upload_directory_s3("zarr37", "earthlab-will-lstm", "Russia37/")
