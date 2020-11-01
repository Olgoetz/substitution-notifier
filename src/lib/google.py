import logging
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

from jinja2 import Environment, FileSystemLoader


class GoogleSuiteFactory():
    def __init__(self, googleApp, version, SCOPES):
        self.googleApp = googleApp
        self.version = version
        self.SCOPES = SCOPES

        self.logger = logging.getLogger(__name__)

        try:
            self.logger.info('Starting authentication with GoogleService...')
            self.credentials = self._authenticate()
            self.logger.info('Successfully authenticated!')
        except Exception as e:
            self.logger.error('Authentication failed!')
            raise e
            sys.exit(1)

    def _authenticate(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.

        if os.path.exists(
                os.path.join(os.path.dirname(__file__), 'token.pickle')):
            self.logger.info('Token file found!')
            with open(os.path.join(os.path.dirname(__file__), 'token.pickle'),
                      'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            self.logger.info('Creating new credentials!')
            if creds and creds.expired and creds.refresh_token:

                creds.refresh(Request())
            else:
                credFile = os.path.join(os.path.dirname(__file__), "creds",
                                        "credentials.json")
                print(credFile)
                flow = InstalledAppFlow.from_client_secrets_file(
                    credFile, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(os.path.join(os.path.dirname(__file__), 'token.pickle'),
                      'wb') as token:
                pickle.dump(creds, token)

        return creds

    def buildService(self):
        self.logger.debug("Building the service...")
        try:
            self.service = build(self.googleApp,
                                 self.version,
                                 credentials=self.credentials,
                                 cache_discovery=False)
            return
        except Exception as e:
            self.logger.error('Failed to built the service: ', e)
            raise e


class GmailService(GoogleSuiteFactory):
    def __init__(self, googleApp, version, SCOPES):
        super().__init__(googleApp, version, SCOPES)

    def _render_template(self, emailContent):
        self.logger.debug("Rendering the template...")
        env = Environment(loader=FileSystemLoader(
            searchpath=os.path.join(os.path.dirname(__file__), 'templates')))

        template = env.get_template('mail.html')

        message_body = template.render(emailContent=emailContent)
        return message_body

    def _create_message(self,
                        sender,
                        to,
                        subject,
                        message_text,
                        cc=None,
                        bcc=None):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """

        self.logger.debug("Creating the message...")
        message = MIMEMultipart('alternative')
        if bcc is None:
            val_bcc = None
        else:
            val_bcc = (',').join(bcc)
        body = MIMEText(message_text, 'html')
        message['to'] = to
        message['bcc'] = val_bcc
        message['cc'] = cc
        message['from'] = sender
        message['subject'] = subject
        message.attach(body)
        return {
            'raw':
            base64.urlsafe_b64encode(message.as_string().encode()).decode()
        }

    def send_message(self,
                     sender,
                     to,
                     subject,
                     emailContent,
                     cc=None,
                     bcc=None):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """

        self.logger.debug("Sending the message...")
        message_body = self._render_template(emailContent)
        message = self._create_message(sender, to, subject, message_body, cc,
                                       bcc)
        try:
            self.logger.info("Compiling message...")
            compiledMessage = (self.service.users().messages().send(
                userId=sender, body=message).execute())
            self.logger.debug('Message Id: %s' % compiledMessage['id'])
            return compiledMessage
        except Exception as error:
            print('An error occurred: %s' % error)
