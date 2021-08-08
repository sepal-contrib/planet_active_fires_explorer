======
SEPAFE
======


The Sepal Planet Active Fires Explorer (SEPAFE) is a module developed on the SEPAL enviroment based on the Fire Information for Resource Management System (FIRMS) and using Planet Scope imagery from Planet Labs.

The aim of SEPAFE module is to provide users with a quick way to get and validate the fire alerts from the FIRMS program by using the daily planet scope imagery
The aim of this tool is to provide users a way to validate in an easy way the fire alerts that are 


.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/img/sepal_active_fires_home.png

The module options panel is divided into three tabs: - :code:`Planet Imagery`, `:code:`Area of Interest` and :code:`Alerts`. 

1. Connect your Planet API Key
------------------------------


.. note:: This step is optional but highly recommended. Although you can go trhough the next tabs and get the fire alerts from the different satellite sources, to get the most advantage of the module, you will need a Planet API Key with access to daily imagery. 

- Validate your Planet API Key: provide a valid API Key in the input box and click over the validation button, the module will check whether the key is valid or not and the messages of its connection will be displayed directly into the alerts widget. Once your validation is done, you can open the advanced settings expansion panel and modify its inputs. 

  - Open the Advanced settings panel
    - Max number of images: maximum number of planet images to be displayed at once in each alert.
    - Search up to 'x' days before: number of days before the fire alert date to look up for the best image available.
    - Search up to 'x' days after: number of days after the fire alert date to look up for the best image available.
    - Cloud cover threshold: maximum cloud cover threshold accepted in the images (based on the planet metadata).
   
 
.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/gif/planet.gif


1. Select and area of interest (AOI)
------------------------------------

The module has to options to select and area of interest and filter alerts based on the given parameters.

- Draw a shape: when this option is selected, three drawing tools will be displayed in the top-left corner, you can select a `square`, `circle` and a `polygon`
- Select a country: type the name of the country directly into the search box or navigate though it by using the scroll bar, and select the desired country. Once the country is selected, it will be displayed in the map view.
  
.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/gif/aoi.gif

that was originally developed by the University of Maryland, with funds from NASA’s Applied Sciences Program and the United Nations Food and Agriculture Organization (UN FAO)


3. Get fire alerts
------------------


- Recent: the products to be downloaded are comming from the Moderate Resolution Imaging Spectroradiometer (MODIS) and the Visible Infrared Imaging Radiometer Suite (VIIRS) for the last 24, 28 hours and the last 7 days.

- Historical: for the historical products, you will be able to download alerts from 2000 until the last finished year from the MODIS satellite. Click over the historical button and filter by the dates.

After clicking over the `get alerts` button, the module will retrieve the alerts 


Use the navigation widget
-------------------------

Once the alerts are being displayed on the map, you will be able to navigate trhough each of them by using the :code:`navigation widget`. Use the :code:`next` and :code:`prev` button to navigate over the fire alerts, and use the :code:`confidence` dropdown to filter the alerts (What is the detection confidence?)

You can activate/deactive the navigation widget by clicking over the `button`.


  The confidence value was added to help users gauge the quality of individual fire pixels is included in the Level 2 fire product. The confidence field should be used with caution; it is likely that it will vary in meaning in different parts of the world. Nevertheless some of our end users have found such a field to be useful in excluding false positive occurrences of fire. They are different for MODIS and VIIRS.


Download active fire products from the Moderate Resolution Imaging Spectroradiometer (MODIS) and Visible Infrared Imaging Radiometer Suite (VIIRS) for the last 24, 48 hours and 7 days in shapefile, KML or text file formats.

There are 

The module has two options to get the alerts: recent and historical, both of them will be 

