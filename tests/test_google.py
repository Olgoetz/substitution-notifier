from src.lib.google import GmailService


def test_gmailService(capsys):
    scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]

    gmail = GmailService('gmail', 'v1', scopes)
    gmail.buildService()
    assert isinstance(gmail, GmailService)

    message_body = gmail._render_template('test')
    assert isinstance(message_body, str)

    message_full = gmail._create_message("me", "you", "Foo", message_body)
    assert isinstance(message_full["raw"], str)

    gmail.send_message("me", "you", "Foo", message_body)
    captured = capsys.readouterr()
    assert 'An error occurred: <HttpError 400 when requesting https://gmail.googleapis.com/gmail/v1/users/me/messages/send?alt=json returned "Invalid To header">' in captured.out
