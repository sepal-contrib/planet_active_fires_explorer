======
SEPAFE
======


The Sepal Planet Active Fires Explorer (SEPAFE) is a module developed on the SEPAL enviroment based on the Fire Information for Resource Management System (FIRMS) and with Planet Scope imagery from Planet Labs.

The aim of this tool is to provide users a way to validate in an easy way the fire alerts that are 

The module has been built as a 


.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/img/sepal_active_fires_home.png

The module options panel is divided into three tabs: - Planet Imagery, - Area of Interest and Alerts. 

Connect your Planet API Key
---------------------------


.. note:: This step is optional but highly recommended. Although you can go trhough the next tabs and get the fire alerts from the different satellite sources, to get the most advantage of the module, you will need a Planet API Key with access to daily imagery. 

- Validate your Planet API Key: provide a valid API Key in the input box and click over the validation button, the module will check whether the key is valid or not and the messages of its connection will be displayed directly into the alerts widget. Once your validation is done, you can open the advanced settings expansion panel and modify its inputs.

  - Open the Advanced settings panel: 
    - Max number of images
    - Search up to 'x' days before
    - Search up to 'x' days after
    - Cloud cover threshold 
   
 The module will search the mos 
 
.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/gif/planet.gif


Select and area of interest (AOI)
---------------------------------

The module has to options to select and area of interest and filter alerts based on the given parameters.

- Draw a shape: when this option is selected, three drawing tools will be displayed in the top-left corner, you can select a `square`, `circle` and a `polygon`
- Select a country: type the name of the country directly into the search box or navigate though it by using the scroll bar, and select the desired country. Once the country is selected, it will be displayed in the map view.
  
.. image:: https://raw.githubusercontent.com/dfguerrerom/planet_active_fires_explorer/main/doc/gif/aoi.gif

that was originally developed by the University of Maryland, with funds from NASA’s Applied Sciences Program and the United Nations Food and Agriculture Organization (UN FAO)

