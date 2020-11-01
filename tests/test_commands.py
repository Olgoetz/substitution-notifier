from click.testing import CliRunner
from src.lib.commands import cli
import click


def test_cli():
    runner = CliRunner()
    result = runner.invoke(cli, [
        '10.10.2020', '-n', 'Foobar', '-cc', 'Test@mail.com', '-l', 'Raboof',
        '--dryrun'
    ],
                           input="bike,12")
    assert result.exit_code == 0
    assert "Dry run. No mail sent." in result.output
