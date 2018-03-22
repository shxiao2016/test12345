from __future__ import absolute_import

import click

from linkedin.clix import setup_cli
from linkedin.clix.ext import PexEntryPointCommand


@setup_cli(pass_cli=True)
@click.command(cls=PexEntryPointCommand, context_settings=dict(help_option_names=['-h', '--help']))
def main(cli):

    # Log exception metrics to UMP/Raptor
    cli.register_exception_reporter()

    click.secho('Your CLI Tool here!', fg='green')
