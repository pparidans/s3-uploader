from os import path, environ
from hashlib import sha1
from tinys3 import Connection
import click
import string

BUCKETS = {
    "alice": "alice-paridans-com",
    "romain": "romain-paridans-com",
    # "test": "pparidans-test",
}

def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s.strip() if c in valid_chars)
    filename = filename.replace(' ','-') # no spaces in filenames.
    return filename.lower()

def sha1sum(filename):
    with open(filename, "rb") as f:
        return sha1(f.read()).hexdigest()

@click.group()
def cli():
    pass

@cli.command()
@click.argument("file_path")
@click.option("-c", "--category", type=click.Choice(BUCKETS.keys()))
@click.option("-n", "--dry-run", "dry_run", is_flag=True, default=False)
def add(file_path, category, dry_run):
    click.secho("Uploading %s :" % file_path, fg="green")

    bucket_name = BUCKETS[category]
    abs_path = path.abspath(file_path)
    filename = format_filename(path.basename(abs_path))
    shasum = sha1sum(abs_path)
    dest_path = "pub/%s/%s" % (shasum, filename)
    public_url = "https://%s.paridans.com/%s" % (category, dest_path)

    click.echo("Ready to upload into '%s' with path '%s'" % (bucket_name, dest_path))

    if not dry_run:
        s3_conn = Connection(environ.get("S3_ACCESS_KEY"), environ.get("S3_SECRET_KEY"), tls=True, endpoint='s3-eu-west-1.amazonaws.com')
        with open(abs_path, "rb") as f:
            s3_conn.upload(dest_path, f, bucket_name)
        click.secho("Uploaded successfully to '%s'" % public_url, fg="green")
    else:
        click.secho("Dry run", fg="red")


@cli.command()
def list():
    # TODO: implement bucket listing
    pass

if __name__ == "__main__":
    cli()