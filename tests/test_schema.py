from __future__ import unicode_literals

import io
import json
import os
import unittest

from clkhash import schema
from clkhash.schema import SchemaError, MasterSchemaError

DATA_DIRECTORY = os.path.join(os.path.dirname(__file__),
                              '..', 'clkhash', 'data')

TEST_DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), 'testdata')

def _test_data_file_path(file_name):
    return os.path.join(TEST_DATA_DIRECTORY, file_name)

def _schema_dict(dir_name, file_name):
    with open(os.path.join(dir_name, file_name)) as f:
        return json.load(f)


class TestSchemaValidation(unittest.TestCase):
    def test_good_schema(self):
        # These are some perfectly fine schemas.
        with open(_test_data_file_path('good-schema-v1.json')) as f:
            schema.from_json_file(f)

    def test_good_schema_repr(self):
        with open(_test_data_file_path('good-schema-v1.json')) as f:
            s = schema.from_json_file(f)
        schema_repr = repr(s)
        assert "v2" in schema_repr  # v1 schema is converted to v2
        assert "12 fields" in schema_repr

    def test_invalid_schema(self):
        # This schema is not valid (missing encoding in its feature).
        with open(_test_data_file_path('bad-schema-v1.json')) as f:
            with self.assertRaises(SchemaError):
                schema.from_json_file(f)

    def test_valid_but_unsupported_schema(self):
        # This schema has an unsupported version.
        with open(_test_data_file_path(
                'good-but-unsupported-schema-v1.json')) as f:
            with self.assertRaises(SchemaError):
                schema.from_json_file(f)

    def test_invalid_json_schema(self):
        invalid_schema_file = io.StringIO('{')  # Invalid json.
        msg = 'Invalid JSON in schema should raise SchemaError.'
        with self.assertRaises(SchemaError, msg=msg):
            schema.from_json_file(invalid_schema_file)

    def test_list_schema(self):
        invalid_schema_file = io.StringIO('[]')  # Must be dict instead.
        msg = 'List as top element should raise SchemaError.'
        with self.assertRaises(SchemaError, msg=msg):
            schema.from_json_file(invalid_schema_file)

    def test_string_schema(self):
        invalid_schema_file = io.StringIO('"foo"')  # Must be dict.
        msg = 'Literal as top element should raise SchemaError.'
        with self.assertRaises(SchemaError, msg=msg):
            schema.from_json_file(invalid_schema_file)

    def test_no_version(self):
        invalid_schema_file = io.StringIO('{}')  # Missing version.
        msg = 'Schema with no version should raise SchemaError.'
        with self.assertRaises(SchemaError, msg=msg):
            schema.from_json_file(invalid_schema_file)

    def test_missing_master(self):
        # This shouldn't happen but we need to be able to handle it if,
        # for example, we have a corrupt install.
        original_paths = schema.MASTER_SCHEMA_FILE_NAMES
        schema.MASTER_SCHEMA_FILE_NAMES = {1: 'nonexistent.json'}

        msg = 'Missing master schema should raise MasterSchemaError.'
        with self.assertRaises(MasterSchemaError, msg=msg):
            schema.validate_schema_dict({'version': 1})

        schema.MASTER_SCHEMA_FILE_NAMES = original_paths

    def test_convert_v1_to_v2(self):
        schema_v1 = _schema_dict(DATA_DIRECTORY, 'randomnames-schema.json')
        schema.validate_schema_dict(schema_v1)
        schema_v2 = schema.convert_v1_to_v2(schema_v1)
        schema.validate_schema_dict(schema_v2)

    def test_good_schema2_repr(self):
        with open(_test_data_file_path('good-schema-v2.json')) as f:
            s = schema.from_json_file(f)
        schema_repr = repr(s)
        assert "v2" in schema_repr
        assert "12 fields" in schema_repr


class TestSchemaLoading(unittest.TestCase):
    def test_issue_111(self):
        schema_dict = {
            'version': 1,
            'clkConfig': {
                'l': 1024,
                'k': 20,
                'hash': {
                    'type': 'doubleHash'},
                'kdf': {
                    'type': 'HKDF'}},
            'features': [
                {
                    'identifier': 'rec_id',
                    'ignored': True},
                {
                    'identifier': 'given_name',
                    'format': {
                        'type': 'string',
                        'encoding': 'utf-8'},
                    'hashing': {
                        'ngram': 2,
                        'weight': 1}},
                {
                    'identifier': 'surname',
                    'format': {
                        'type': 'string',
                        'encoding': 'utf-8'},
                    'hashing': {
                        'ngram': 2,
                        'weight': 1}},
                {
                    'identifier': 'street_number',
                    'format': {
                        'type': 'integer'},
                    'hashing': {
                        'ngram': 1,
                        'positional': True,
                        'weight': 1 }},
                {
                    'identifier': 'address_1',
                    'format': {
                        'type': 'string',
                        'encoding': 'utf-8'},
                    'hashing': {
                        'ngram': 2,
                        'weight': 1}},
                {
                    'identifier': 'address_2',
                    'format': {
                        'type': 'string',
                        'encoding': 'utf-8'},
                    'hashing': {
                        'ngram': 2,
                        'weight': 1}},
                {
                    'identifier': 'suburb',
                    'format': {
                        'type': 'string',
                        'encoding': 'utf-8'},
                    'hashing': {
                        'ngram': 2,
                        'weight': 1}},
                {
                    'identifier': 'postcode',
                    'format': {
                        'type': 'integer',
                        'minimum': 1000,
                        'maximum': 9999},
                    'hashing': {
                        'ngram': 1,
                        'positional': True,
                        'weight': 1}},
                {
                    'identifier': 'state',
                    'format': {
                        'type': 'string',
                        'encoding': 'utf-8',
                        'maxLength': 3},
                    'hashing': {
                        'ngram': 2,
                        'weight': 1}},
                {
                    'identifier': 'day_of_birth',
                    'format': {
                        'type': 'integer'},
                    'hashing': {
                        'ngram': 1,
                        'positional': True,
                        'weight': 1}},
                {
                    'identifier': 'soc_sec_id',
                    'ignored': True}
            ]
        }

        # This fails in #111. Now it shouldn't.
        schema.from_json_dict(schema_dict)
