# -*- coding: utf-8 -*-
import os
from datetime import datetime
from datetime import timedelta
from pathlib import Path

from db import db
import i18n
import i18n_tool
import journalist_app
import source_app
import template_filters
from flask import session
from sh import pybabel
from .utils.env import TESTS_DIR


def verify_rel_datetime_format(app):
    with app.test_client() as c:
        c.get('/')
        assert session.get('locale') == "en_US"
        result = template_filters.rel_datetime_format(
            datetime(2016, 1, 1, 1, 1, 1))
        assert "January 1, 2016 at 1:01:01 AM UTC" == result

        result = template_filters.rel_datetime_format(
            datetime(2016, 1, 1, 1, 1, 1), fmt="yyyy")
        assert "2016" == result

        test_time = datetime.utcnow() - timedelta(hours=2)
        result = template_filters.rel_datetime_format(test_time,
                                                      relative=True)
        assert "2 hours ago" == result

        c.get('/?l=fr_FR')
        assert session.get('locale') == 'fr_FR'
        result = template_filters.rel_datetime_format(
            datetime(2016, 1, 1, 1, 1, 1))
        assert "1 janvier 2016 à 01:01:01 TU" == result

        result = template_filters.rel_datetime_format(
            datetime(2016, 1, 1, 1, 1, 1), fmt="yyyy")
        assert "2016" == result

        test_time = datetime.utcnow() - timedelta(hours=2)
        result = template_filters.rel_datetime_format(test_time,
                                                      relative=True)
        assert u"2\xa0heures" in result


def verify_filesizeformat(app):
    with app.test_client() as c:
        c.get('/')
        assert session.get('locale') == "en_US"
        assert "1 byte" == template_filters.filesizeformat(1)
        assert "2 bytes" == template_filters.filesizeformat(2)
        value = 1024 * 3
        assert "3 kB" == template_filters.filesizeformat(value)
        value *= 1024
        assert "3 MB" == template_filters.filesizeformat(value)
        value *= 1024
        assert "3 GB" == template_filters.filesizeformat(value)
        value *= 1024
        assert "3 TB" == template_filters.filesizeformat(value)
        value *= 1024
        assert "3,072 TB" == template_filters.filesizeformat(value)

        c.get('/?l=fr_FR')
        assert session.get('locale') == 'fr_FR'
        assert u'1\xa0octet' == template_filters.filesizeformat(1)
        assert u"2\xa0octets" == template_filters.filesizeformat(2)
        value = 1024 * 3
        assert u"3\u202fko" == template_filters.filesizeformat(value)
        value *= 1024
        assert u"3\u202fMo" == template_filters.filesizeformat(value)
        value *= 1024
        assert u"3\u202fGo" == template_filters.filesizeformat(value)
        value *= 1024
        assert u"3\u202fTo" == template_filters.filesizeformat(value)
        value *= 1024
        assert u"072\u202fTo" in template_filters.filesizeformat(value)


# We can't use fixtures because these options are set at app init time, and we
# can't modify them after.
def test_source_filters(config):
    do_test(config, source_app.create_app)


# We can't use fixtures because these options are set at app init time, and we
# can't modify them after.
def test_journalist_filters(config):
    do_test(config, journalist_app.create_app)


def do_test(config, create_app):
    config.SUPPORTED_LOCALES = ['en_US', 'fr_FR']
    config.TRANSLATION_DIRS = Path(config.TEMP_DIR)
    i18n_tool.I18NTool().main([
        '--verbose',
        'translate-messages',
        '--mapping', os.path.join(TESTS_DIR, 'i18n/babel.cfg'),
        '--translations-dir', config.TEMP_DIR,
        '--sources', os.path.join(TESTS_DIR, 'i18n/code.py'),
        '--extract-update',
        '--compile',
    ])

    for l in ('en_US', 'fr_FR'):
        pot = os.path.join(config.TEMP_DIR, 'messages.pot')
        pybabel('init', '-i', pot, '-d', config.TEMP_DIR, '-l', l)

    app = create_app(config)
    with app.app_context():
        db.create_all()

    assert list(i18n.LOCALES.keys()) == config.SUPPORTED_LOCALES
    verify_filesizeformat(app)
    verify_rel_datetime_format(app)
