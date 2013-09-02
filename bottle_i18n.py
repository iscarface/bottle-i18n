import gettext
import os
import re

from bottle import BaseTemplate, PluginError, request

# Format of http.request.header.Accept-Language.
# refs: http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
REQUEST_ACCEPT_LANGUAGE_RE = re.compile(r"""
    (\w{1,8}(?:-\w{1,8})*|\*)               # "en", "en-au", "*"
    (?:;q=(0(?:\.\d{,3})?|1(?:.0{,3})?))?   # Optional "q=1.00", "q=0.8"
    """, re.VERBOSE)

class I18NPlugin(object):
    name = 'i18n'
    api = 2

    def __init__(self, domain, locale_dir=None, lang_code=None):
        self.domain = domain
        if locale_dir is None:
            locale_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale'))
        if not os.path.exists(locale_dir):
            raise PluginError('No locale directory found, please assign a right one.')
        self.locale_dir = locale_dir
        self.lang_code = lang_code
        self.lang_cache = {}


    def setup(self, app):
        BaseTemplate.defaults['_'] = self.gettext


    def close(self):
        del BaseTemplate.defaults['_']


    def gettext(self, message, plural=None, n=None, expansion=None):
        trans = self.get_translation(self.lang_code)
        if plural is None or n is None:
            return trans.ugettext(message)
        else:
            if expansion is None:
                expansion = {}
            return trans.ungettext(message, plural, n) % expansion


    def get_http_accepted_languages(self):
        """Return language list from http.request.header.Accept-Language, ordered by 'q'."""
        from operator import itemgetter
        # Workaround: RFC2616 doesn't allow underscore in language code, but some client use it.
        accept_lang = request.headers.get('Accept-Language', '').replace('_', '-')
        result = REQUEST_ACCEPT_LANGUAGE_RE.findall(accept_lang)
        result = ((lang, float(quality) if quality else 1.) for (lang, quality) in result)
        result = sorted(result, key=itemgetter(1), reverse=True)
        return result


    def get_language_list(self):
        if self.lang_code is not None:
            return [self.lang_code]

        accepted_langs = self.get_http_accepted_languages()
        lang_codes = []

        # flatten language list
        # if "zh-Hant-TW" is accepted, try to find "zh-Hant" and "zh" as well
        for lang, quality in accepted_langs:
            lang_culture = lang.split('-')
            for i in xrange(len(lang_culture), 0, -1):
                lang_code = '_'.join(lang_culture[:i])
                if lang_code not in lang_codes:
                    lang_codes.append(lang_code)

        return lang_codes


    def get_translation(self, langs=None):
        if langs is None:
            langs = self.get_language_list()

        cache_key = tuple(langs)
        if not cache_key in self.lang_cache:
            trans = gettext.translation(self.domain, self.locale_dir,
                                        languages=langs, fallback=True)
            self.lang_cache[cache_key] = trans

        return self.lang_cache[cache_key]


    def apply(self, callback, route):
        return callback
