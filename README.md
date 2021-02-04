omega|ml sample apps
====================

This is a collection of sample applications using omega|ml, the DataOps and MLOps platform for humans.
See the README in each directory for details on how to run each application.

How omega|ml apps work
----------------------

omega|ml provides all components to develop and run analytics and machine learning applications, from lab to production:

* **data store** - ready to go, without a need to set it up (using MongoDB by default, supporting any third-party DBMS and storage through plugins)
* **model store** - store and version models with a single line of code, `om.models.put(model, 'name'))` 
* **runtime** - fit and run models in the cloud (`om.runtime.model('name').fit()/predict()` - other methods available, supporting scikit-learn, Tensorflow, Keras and PyTorch* out of the box)
* **notebooks** - interative or scheduled execution of Jupyter notebooks   
* **scripts** - lambda-style and serverless apps run on request/continously

In addition omega|ml integrates minibatch, a Python streaming framework that supports many different streaming technologies (Kafka, MQTT, Websockets, etc.).
Leveraging minibatch you can build analytics applications from simple to complex.

Ok now how do *apps* work?

1. Build and pip-setup your Flask or Plotly Dash(c) app 
2. Store the app `$ om scripts put <./path/with/setup.py> apps/<app-name>`
3. Open at https://hub.omegaml.io/apps/<userid>/<app-name>

*omega|ml apps are just Python Flask apps* that can access omega|ml's stores and runtime environment (technically, any app that provides a http server at port 80 can be started, however currently Flask apps are best supported. Plotly Dash is based on Flask.).
The way to access omega|ml is by simply importing omega|ml:

```python
# somewhere in your app
import omegaml as om 

X = <data provided by user> 
yhat = om.runtime.model('mymodel').predict(X)
``` 

This is just one example. Of course you can use the full omega|ml functionality.


Logging
-------

Basic setup, straight forward. This will only log messages submitted through
`om.logger`. 

```
import omegaml as om 
om.logger.info('my log message') 
om.logger.error('my log message')
om.logger.debug('my log message')
```

View the logs from any omega|ml client:

```bash
$ om runtime log
```

or use the Python API to do the same

```python
$ om shell
[] om.logger.dataset.get() # returns a dataframe

# filter (any filter is applicable -- this is a normal omega|ml dataset) 
[] om.logger.dataset.get(levelname='INFO') # ERROR, DEBUG
[] om.logger.dataset.get(msg__contains='logger') # ERROR, DEBUG
```

More complex setup, supporting Python's logging module:

```python
import logging
from omegaml.store.logging import OmegaLoggingHandler 
# attach the omega-ml logging handler to any Python logger
logger = logging.getLogger(__file__)
handler = OmegaLoggingHandler.setup(reset=True, logger=logger)
``` 

To route the Flask log to om.logger do this:

```python
import logging
from omegaml.store.logging import OmegaLoggingHandler
handler = OmegaLoggingHandler.setup(logger=logging.getLogger('root'), level='DEBUG')
# server is the Flask() instance
[logging.getLogger(l).addHandler(handler) for l in ('werkzeug', 'flask.app', server.name)]
```

*) in development. any framework can be supported by adding a omega|ml plugin 


How apphub starts apps
----------------------

Apphub essentially does the following upon app start up

```python
server = Flask()
base_uri = 'apps/<username>/<appname>'
mod = om.scripts.get('apps/<appname>')
mod.create_app(server=server, uri=base_uri)
server.run()
```

Restarting my app
-----------------

Apps can be restarted either via the apphub UI at https://omegaml.io/apps or via
the omegaml cli:

```
$ om runtime restart app <appname>
```

How are apps packaged?
----------------------

* `om.scripts.put` calls `python setup sdist` within the provided path. This creates
  a tar file with the package, using the package's setup.py. The tar file is then
  copied to the om.scripts database as a binary file.
 
* `om.scripts.get` copies the tar file to a temporary directory, then
  calls `pip install <package>`, then loads the `<appname>` module
  
Example:

```
$ om scripts put path/to/mypackage apps/mypackage
=> python path/to/mypackage/setup.py sdist

om.scripts.get('apps/mypackage') 
=> copy from database to /tmp/path/mypackage.tar.gz
=> pip install mypackage.tar.gz
=> import mypackage
```

Notes:

* By default, Flask assumes that static files and templates are packaged within 
  the application module. 

* To include files in packages, such as html templates, css or js files, be 
  sure to provide a MANIFEST.in *and* use include_package_data=True in setup.py.
  Read more about this here https://stackoverflow.com/questions/7522250/how-to-include-package-data-with-setuptools-distutils 

* Detailed advise to package Flask apps can be found here https://flask.palletsprojects.com/en/1.1.x/tutorial/install/


How can I specify dependencies?
-------------------------------

Dependencies can be specified using setup.py, as with any pip installable 
package.

```
# setup.py 
...
setup(...., 
      install_requires=['package==version']
)
```

Read more on how to create pip installable packages at
https://packaging.python.org/overview/#packaging-python-libraries-and-tools


How can I serve static files and templates?
-------------------------------------------

Static files are packaged with your application and can be served using
Flask's `url_for` function. Note the use of the Blueprint syntax `.static` 
instead of the global `static`. This is to ensure that your application can
run from any URL.

```html
<!-- index.html -->
<link rel="shortcut icon" href="{{ url_for('.static', filename='favicon.ico') }}">
```  

Templates are also packaged with your application. Use Flask's `render_template`
function.

```python
def create_app(...., uri=None):
    app = Blueprint(..., url_prefix=uri,
                    static_folder='static',
                    template_folder='templates')
    @app.route('/'):
        return render_template('myapp/index.html')
```

By default Flask loads static files and templates from the local disk, which in 
docker and kubernetes is provided by emphemeral storage. It is however possible 
to serve  static files and templates from om.datasets, effectively enabling 
the separation of these assets from code. See the helloflask app for details.

Why is there no permanent per-node file system?
-----------------------------------------------

omega|ml provides persistent, distributed and horizontally scalable storage
through the om.datasets/models/scripts API. This storage is easily accessible by
any omega|ml client, making it well suited for remote collaboration as well as
to build scalable applications. The storage, backed by MongoDB and optionally 
other databases and file systems, provides the ability to easily store 
structured, unstructured and binary data in an efficient manner.

Rationale:

omega|ml is designed according to the 12factor methodology (https://12factor.net).
These are a set of best practices to design and implement scalable, portable and 
resilient applications built for the cloud. Two key principles are that
applications should only rely on attached resources for persistency, and that
processes should not share runtime state. These principles ensure that applications
can be scaled easily and fast. A permanent file system on the other hand would 
break these principles as applications would start relying on the particular state
of the files in a particular node, which would break scalability and resiliency.

   
Why do I get module import errors?
----------------------------------

If your application is composed of many different modules which are loaded at
runtime this can lead to import errors, even though the package is installed
on the system. This is because packages and all its depdencies are loaded 
from a temporary path that is not part of `sys.path`. This can cause import errors
for packages that have not been loaded at startup time. 

To add the temporary path, in your packages `__init__.py` add the following snipped:

```python 
import os 
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) 
``` 

Contributing
------------

We welcome any contributions - examples, issues, bug reports, documentation, code. Please see [CONTRIBUTING.md]( https://github.com/omegaml/apps/blog/master/CONTRIBUTING.md)
for details. All submitted work is licensed under the MIT license, see LICENSE file for details.

License
-------

All contributed content in this repository is licensed under Apache 2.0 License. See the LICENSE file for details.
Any third party software that may be required to run these apps are licensed under their respective license. It is your responsibility to comply with all licenses.
  
 


