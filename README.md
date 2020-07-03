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
# attach the omega-ml logging handler to any Python logger
logger = logging.getLogger(__file__)
handler = OmegaLoggingHandler.setup(reset=True, logger=logger)
``` 

*) in development. any framework can be supported by adding a omega|ml plugin 

Contributing
------------

We welcome any contributions - examples, issues, bug reports, documentation, code. Please see [CONTRIBUTING.md]( https://github.com/omegaml/apps/blog/master/CONTRIBUTING.md)
for details. All submitted work is licensed under the MIT license, see LICENSE file for details.

License
-------

All contributed content in this repository is licensed under Apache 2.0 License. See the LICENSE file for details.
Any third party software that may be required to run these apps are licensed under their respective license. It is your responsibility to comply with all licenses.
  
 


