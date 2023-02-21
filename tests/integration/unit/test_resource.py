"""Index and retrive information from the resource JSON."""
import pytest
import mock

from botocore.exceptions import NoRegionError

from awsshell.resource import index


@pytest.fixture
def describer_creator():
    class FakeDescriberCreator(object):
        SERVICES = ['ec2']

        def services_with_completions(self):
            return self.SERVICES

    return FakeDescriberCreator()


def test_build_from_has_many():
    resource = {
        'service': {
            'hasMany': {
                'Tables': {
                    'request': {'operation': 'ListTables'},
                    'resource': {
                        'type': 'Table',
                        'identifiers': [
                            {'target': 'Name',
                             'source': 'response',
                             'path': 'TableNames[]',
                            }
                        ]
                    }
                }
            }
        },
        'resources': {
            'Table': {
                'actions': {
                    'Delete': {
                        'request': {
                            'operation': 'DeleteTable',
                            'params': [
                                {'target': 'TableName',
                                 'source': 'identifier',
                                 'name': 'Name'},
                            ]
                        }
                    }
                }
            }
        }
    }
    builder = index.ResourceIndexBuilder()
    built_index = builder.build_index(resource)
    assert built_index == {
        'operations': {
            'DeleteTable': {
                'TableName': {
                    'resourceName': 'Table',
                    'resourceIdentifier': 'Name',
                }
            }
        },
        'resources': {
            'Table': {
                'operation': 'ListTables',
                'resourceIdentifier': {
                    'Name': 'TableNames[]',
                }
            }
        }
    }


def test_
