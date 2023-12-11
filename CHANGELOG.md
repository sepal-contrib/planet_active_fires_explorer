## 0.2.0 (2023-12-11)

### Feat

- use sepal_ui==2.17 to avoid conflicts with ipyleaflet

### Fix

- fix wrong css id for waiting message

### Refactor

- **decorator**: remove debug arg

## 0.1.0 (2023-10-06)

### Feat

- set minimun height to map
- add full screen button
- update python entry point
- use FIRMS API service to retrieve alerts and difine fronted.
- improve process to retrieve alerts from API. Aims to close #28, #36, and close #45
- simplify alerts download process
- set structure to consume alerts from FIRMSapi as csv
- introduce missing keys
- upgrade UI to latest sepal_ui version
- replace ipywidgets btn with sepal map buttons
- adapt to full screen layout
- use planet view and last sepal_ui version
- use default new sepal_ui visualizaiton. once approved https://github.com/12rambau/sepal_ui/pull/441

### Fix

- deprecate PSC3 and PSC4
- fix #52. change firms_api_key validation workflow
- update old fas-fa awesome icon names to align with: https://github.com/12rambau/sepal_ui/pull/645
- listen planet view validation event
- make datek picker customizable by tuning its parameters
- fix input method parameters
- remove items as protected key from messages
- reset index to fix bug. close #40
- change validate by reviewed header in the metadata card. - closes #29
- importing sw in UI notebook
- **docs**: update process image link

### Refactor

- use planetapi from sepal_ui
- clean ui notebooks
- raise error when there's no sepal key
- fix style
- remove legacy code
- update to sepal_ui version which uses planet>=2
- fix #44
- remove legacy datepicker. copy prev-next behave from alert module
- adapt colors to use sepal_ui 2.7.0
- use last sepal_ui datepicker, add sepal_ui fullscreen control
- fix imports and avoid using import * due to bad practices
