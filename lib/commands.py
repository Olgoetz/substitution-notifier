import click
import os
import re
from lib.google import GmailService
import logging
import configparser
from pathlib import Path

#***************** GLOBALS *****************
classes = list(dict())


#***************** CUSTOM VALIDATORS *****************
def validate_email(ctx, param, value):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if not re.match(regex, value):
        raise click.BadParameter(
            'Recipient needs to be a proper email address')


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
def main(name, date, copy, location, recipient, dryrun, debug):

    # Decide on the log level
    os.environ["SUBSTITUTION_NOTIFIER_LOG"] = "INFO"
    if debug:
        os.environ["SUBSTITUTION_NOTIFIER_LOG"] = "DEBUG"

    # Set the loglevel
    logging.basicConfig(level=os.environ["SUBSTITUTION_NOTIFIER_LOG"])

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

    # Handle the dryrun flug
    if dryrun:
        click.echo("Dry run. No mail sent.")
        return

    click.echo('Sending mail...')

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
    gmail.send_message("me", recipient, f'[Vertretung]: {location} | {date}',
                       emailContent, emailContent['copy'])

    click.echo('Email sent!')
