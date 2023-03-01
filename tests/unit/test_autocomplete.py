import pytest
from awsshell.autocomplete import AWSCLIModelCompleter

@pytest.fixture
def index_data():
    return {
        'aws': {
            'argument_metadata': {},
            'arguments': [],
            'commands': [],
            'children': {},
        }
    }


def test_completes_service_names(index_data):
    index_data['aws']['commands'] = ['first', 'second']
    completer = AWSCLIModelCompleter(index_data)
    assert completer.autocomplete('fi') == ['first']


def test_completes_service_names_substring(index_data):
    index_data['aws']['commands'] = ['abc', 'acd', 'b']
    completer = AWSCLIModelCompleter(index_data)
    completer.match_fuzzy = False
    assert completer.autocomplete('fo') == ['foo']


def test_completes_multiple_service_names(index_data):
    index_data['aws']['commands'] = ['abc', 'acd', 'b']
    completer = AWSCLIModelCompleter(index_data)
    assert completer.autocomplete('a') == ['abc', 'acd']


def test_no_completion(index_data):
    index_data['aws']['commands'] = ['foo', 'bar']
    completer = AWSCLIModelCompleter(index_data)
    assert completer.autocomplete('baz') == []


def test_can_complete_subcommands(index_data):
    index_data['aws']['commands'] = ['ec2']
    index_data['aws']['children'] = {
        'ec2': {
            'arguments': [],
            'commands': ['copy-image', 'copy-snapshot', 'other'],
            'children': {},
        }
    }
    completer = AWSCLIModelCompleter(index_data)
    # The completer tracks state to optimize lookups,
    # so we simulate exactly how it's called.
    completer.autocomplete('e')
    completer.autocomplete('ec')
    completer.autocomplete('ec2')
    completer.autocomplete('ec2 ')
    completer.autocomplete('ec2 c')
    completer.autocomplete('ec2 co')
    assert completer.autocomplete('ec2 cop') == ['copy-image', 'copy-snapshot']

def test_everything_completed_on_space(index_data):
    # Right after "aws ec2<space>" all the operations should be
    # autocompleted.
    index_data['aws']['commands'] = ['ec2']
    index_data['aws']['children'] = {
        'ec2': {
            'argments': [],
            'commands': ['copy-image', 'copy-snapshot', 'other'],
            'children': {},
        }
    }
    complter = AWSCLIModelCompleter(index_data)
    complter.autocomplete('e')
    complter.autocomplete('ec')
    complter.autocomplete('ec2')
    assert complter.autocomplete('ec2') == ['copy-image', 'copy-snapshot', 'other']



def test_autocomplete_top_leve_services_on_space(index_data):
    index_data['aws']['commands'] = ['first', 'second']
    complter = AWSCLIModelCompleter(index_data)
    assert complter.autocomplete('') == ['first', 'second']


def test_reset_auto_complete(index_data):
    index_data['aws']['commands'] = ['first', 'second']
    completer = AWSCLIModelCompleter(index_data)
    completer.autocomplete('f')
    completer.autocomplete('fi')
    completer.autocomplete('fir')
    # Then the user hits enter.
    # Now they've moved on to the next command.
    assert completer.autocomplete('d') == ['second']


def test_reset_after_subcommand_completion(index_data):
    index_data['aws']['commands'] = ['ec2', 's3']
    index_data['aws']['children'] = {
        'ec2': {
            'argments': [],
            'commands': ['copy-image', 'copy-snapshot', 'other'],
            'children': {},
        }
    }
    completer = AWSCLIModelCompleter(index_data)
    # The completer tracks state to optimize lookups,
    # so we simulate exactly how it's called.
    completer.autocomplete('e')
    completer.autocomplete('ec')
    completer.autocomplete('ec2')
    completer.autocomplete('ec2 ')
    completer.autocomplete('ec2 c')
    completer.autocomplete('ec2 co')
    # The user hits enter and auto completes copy-snapshot.
    # The next request should be to auto complete
    # top level commands:
    assert completer.autocomplete('s') == ['s3']


def test_backspace_should_complete_previous_command(index_data):
    pass


def test_can_handle_entire_word_deleted(index_data):
    pass


def test_can_handle_entire_line_deleted(index_data):
    index_data['aws']['commands'] = ['ec2', 's3']
    index_data['aws']['children'] = {
        'ec2': {
            'arguments': [],
            'commands': ['copy-image', 'copy-snapshot', 'other'],
            'children': {},
        }
    }
    completer = AWSCLIModeCompleter(index_data)
    c = completer.autocomplete
    c('e')
    c('ec')
    c('ec2')
    c('ec2 ')
    c('ec2 c')
    c('ec2 co')
    # Use hits backspace a few times.
    c('ec2 c')
    c('ec2 ')
    c('ec2')
    # Now we should be auto completing 'ec2'
    assert c('ec') == ['ec2']


def test_autocompletes_argument_names(index_data):
    index_data['aws']['arguments'] = ['--query', '--debug']
    completer = AWSCLlModeCompletr(index_data)
    # These should only appear once in the output. So we need
    # to know if we're a top level argument or not.
    assert completer.autocomplete('-') == ['--query', '--debug']
    assert completer.autocomplete('--q') == ['--query']


def test_autocompletes_argument_names_substring(index_data):
    index_data['aws']['arguments'] = ['--foo', '--bar foo']
    complter = AWSCLIModelCompleter(index_data)
    complter.match_fuzzy = False
    # These should only appear once in the output. So we need
    # to know if we're a top level argument or not.
    assert complter.autocomplete('--f') == ['--foo']


def test_autocompletes_global_and_service_args(index_data):
    index_data['aws']['arguments'] = ['--query', '--debug']
    index_data['aws']['commands'] = ['ec2']
    index_data['aws']['children'] = {
        'ec2': {
            'arguments': ['--query-ec2', '--instance-id'],
            'commands': [],
            'children': {},
        }
    }
    completer = AWSCLIModelCompleter(index_data)
