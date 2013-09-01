bottle_i18n
============

A very simple I18N plugin for Bottle apps.

Here is an example:

```python
from bottle import Bottle, view
from bottle_i18n import I18NPlugin

myapp = Bottle()

i18n = I18NPlugin(domain='myapp')
myapp.install(i18n)


@myapp.get('/')
@view('index')
def index():
    return {}
```

You index.tpl may look like this:

```python
<p>
    {{ _('test i18n in bottle template') }}
    {{ _('A person', '%(count)d people', 1, {'count': 1}) }}
    {{ _('A person', '%(count)d people', 2, {'count': 2}) }}
</p>
```

Put your .mo files at `localedir/language/LC_MESSAGES/domain.mo`
