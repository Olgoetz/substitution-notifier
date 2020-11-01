import click
import os
import re
import logging

from pathlib import Path
from pyfiglet import Figlet

from src.lib import config
from src.lib.google import GmailService

#***************** GLOBALS *****************
classes = list(dict())


#***************** CUSTOM VALIDATORS *****************
def validate_email(ctx, param, value):
    regex = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(regex, value):
        raise click.BadParameter(
            'Recipient needs to be a proper email address')
    return value


#***************** CLICK COMMAND *****************
@click.command()
@click.option('-r',
              '--recipient',
              help="Recipient of the email",
              type=str,
              callback=validate_email,
              default="oliver.goetz@iron-system.com")
@click.option('--debug', is_flag=True, help="Switch on/off debug mode")
@click.option('--dryrun',
              is_flag=True,
              help="Executes the programm without sending an email")
@click.option('-cc', '--copy', help="Email for CC", required=True, type=str)
@click.option('-n',
              '--name',
              help="Name of the substitutor",
              required=True,
              type=str)
@click.option('-l',
              '--location',
              help="Name of the gym",
              required=True,
              type=str)
@click.argument('date', type=str)
def cli(name, date, copy, location, recipient, dryrun, debug):

    f = Figlet(font='slant')
    print(f.renderText('Substitutor Notifier CLI'))

    # Decide on the log level
    os.environ["SUBSTITUTION_NOTIFIER_LOG"] = "INFO"
    if debug:
        os.environ["SUBSTITUTION_NOTIFIER_LOG"] = "DEBUG"

    # Set the loglevel
    logging.basicConfig(format=os.environ["SUBSTITUTION_NOTIFIER_LOGFORMAT"],
                        level=os.environ["SUBSTITUTION_NOTIFIER_LOG"])

    # Declare the condition for the while loop prompting the user for classes
    toContinue = True

    # Prompt the user for the classes to substitute
    while toContinue:
        course = click.prompt(
            "State the class name with its start- and endtime (name, hhmm-hhmm)"
        )
        logging.debug(f"toContinue: {toContinue}")
        singleCourse = course.split(',')

        # Make sure that the user enters the proper format, only 1 ',' is allowed
        if len(singleCourse) > 2:
            click.echo(
                "Wrong format. The expression must contain only one ','.")
            continue

        # Build a list of classes
        classes.append({"name": singleCourse[0], "time": singleCourse[1]})

        # Ask the user for another input
        toContinue = click.confirm("Do you want to add more classes")

    # Declare an emailContent object
    emailContent = {
        "date": date,
        "name": name,
        "copy": copy,
        "location": location,
        "classes": classes
    }

    logging.debug(emailContent)

    # Configure and use gmail
    scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]

    gmail = GmailService('gmail', 'v1', scopes)
    gmail.buildService()

    # Handle the dryrun flug
    if dryrun:
        click.echo("Dry run. No mail sent.")
        return

    click.echo('Sending mail...')
    gmail.send_message("me", recipient, f'[Vertretung]: {location} | {date}',
                       emailContent, emailContent['copy'])

    click.echo('Email sent!')
