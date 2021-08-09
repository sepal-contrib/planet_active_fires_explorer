======
SEPAFE
======

The Sepal Planet Active Fires Explorer (SEPAFE) is a module developed on the SEPAL platform based on the Fire Information for Resource Management System (FIRMS) and using Planet Scope imagery from Planet Labs.

The aim of SEPAFE is to provide users with a quick way to get and validate fire alerts from the FIRMS program by using daily planet imagery.


.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/img/sepal_active_fires_home.png


Settings panel
-------------

The settings panel is composed by three tabs: :code:`Planet Imagery`, :code:`Area of Interest` and :code:`Alerts`, each of them is a neccessary step to get the fire alerts.

.. tip:: The settings panel can be open/closed by clicking on the settings |settings| button.

1. Connect your Planet API Key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Validate your Planet API Key: provide a valid API Key in the input box and click over the validation button, the module will check whether the key is valid or not and the messages of its connection will be displayed directly into the alerts widget. Once your validation is done, you can open the advanced settings expansion panel and modify its inputs. 

.. note:: This step is optional but highly recommended. Although you can go trhough the next tabs and get the fire alerts from the different satellite sources, to get the most advantage of the module, you will need a Planet API Key with access to daily imagery. 


  - Open the Advanced settings panel
  
    - :code:`Max number of images`: maximum number of planet images to be displayed at once in each alert.
    - :code:`Search up to 'x' days before`: number of days before the fire alert date to look up for the best image available.
    - :code:`Search up to 'x' days after`: number of days after the fire alert date to look up for the best image available.
    - :code:`Cloud cover threshold`: maximum cloud cover threshold accepted in the images (based on the planet metadata).
   
 
.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/gif/planet.gif
   :align: center

2. Select and area of interest (AOI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The module has two options to select and area of interest and filter alerts based on the given parameters.

- Draw a shape: when this option is selected, three drawing tools will be displayed in the top-left map corner, you can select a `square`, `circle` and a `polygon`
- Select a country: type the name of the country directly into the search box or navigate though it by using the scroll bar, and select the desired country. Once the country is selected, it will be displayed in the map view.
  
.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/gif/aoi.gif
   :align: center
   
3. Get fire alerts
^^^^^^^^^^^^^^^^^^

- Recent: the products to be downloaded are comming from the Moderate Resolution Imaging Spectroradiometer (MODIS) and the Visible Infrared Imaging Radiometer Suite (VIIRS) for the last 24, 28 hours and the last 7 days.

- Historical: for the historical products, you will be able to download alerts from 2000 until the last finished year from the MODIS satellite. Click over the historical button and filter by the dates.

After clicking over the `get alerts` button, the module will start the download process and will clip the alerts to the given AOI. The alerts will be displayed on the map according with a color map for the alert confidence, ranging from green, orange, to red for the confidence values high, nominal and low (for VIIRS) and >80, >70 < 80, <50 for MODIS.

.. warning:: depending on the sensor source and whether your alert request are recent or historical, the download/clip process could take more time. This module is intended to get a quick and fast validation of fire alerts, if you are requesting an area with more than 10,000 fire alerts, you will be asked if you want to display all the alerts in the map —which could highly affect the performance of the tool— or if you want to download them to your desktop/SEPAL environment.

Navigate through alerts
-----------------------

Once the alerts are being displayed on the map, you will be able to navigate trhough each of them by using the :code:`navigation widget`. Click :code:`next` and :code:`prev` button to navigate over the fire alerts, and use the :code:`confidence` dropdown to filter the alerts by its confidence (`What is the detection confidence? <https://earthdata.nasa.gov/faq/firms-faq>`_).

.. tip:: You can activate/deactive the firee navigation widget by clicking over the fires |fires| button.

.. tip:: Planet parameters can be changed at any time, to refresh the results from the current alert click over the refresh |refresh| icon.

  The confidence value was added to help users gauge the quality of individual fire pixels is included in the Level 2 fire product. The confidence field should be used with caution; it is likely that it will vary in meaning in different parts of the world. Nevertheless some of our end users have found such a field to be useful in excluding false positive occurrences of fire. They are different for MODIS and VIIRS.



.. |fires| image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/img/alerts_icon.png
.. |settings| image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/img/settings_icon.png
.. |refresh| image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/img/refresh_icon.png
