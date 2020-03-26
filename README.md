# parselog
Crappy parser sql log for Odoo

## 0. Pre-config
Dir /tmp/parselog created, with surge confgured if needed to publish online

## 1. APPLY THIS DIFF

```diff
diff --git odoo/sql_db.py odoo/sql_db.py
index 922540220b7..9226575178a 100644
--- odoo/sql_db.py
+++ odoo/sql_db.py
@@ -234,6 +234,10 @@ class Cursor(object):
      if self.sql_log:
          encoding = psycopg2.extensions.encodings[self.connection.encoding]
          _logger.debug("query: %s", self._obj.mogrify(query, params).decode(encoding, 'replace'))
+
+            import traceback
+            _logger.debug("stack: " + "".join(['File: %r | line %d | %s | %s\n' % (filename, lineno, name, line) for filename, lineno, name, line in traceback.extract_stack()[:-3] if '/odoo/' in filename]))
+
      now = time.time()
          try:
             params = params or None
```
```python
import traceback;_logger.debug("stack: " + "".join(['File: %r | line %d | %s | %s\n' % (filename, lineno, name, line) for filename, lineno, name, line in traceback.extract_stack()[:-3] if '/odoo/' in filename]))
```


## 2. Run Server

./odoo-bin --log-sql --logfile=/tmp/log -d dbname


## 3. Call SCRIPT
url='/' && server='http://127.0.0.123:8069' && curl -s $server$url > /dev/null && echo "" > /tmp/log && curl -s $server$url > /dev/null && ~/src/private/parselog/parselog.py $url $online

### Publish Online with surge
online='parselog-jke'

### Local file
unset online
