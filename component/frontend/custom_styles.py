from pathlib import Path

import ipyvuetify as v
from traitlets import Unicode


class Styles(v.VuetifyTemplate):
    """"""

    css = (Path(__file__).parent / "custom_styles.css").read_text()
    template: Unicode = Unicode(f"<style>{css}</style>").tag(sync=True)


display(Styles())
