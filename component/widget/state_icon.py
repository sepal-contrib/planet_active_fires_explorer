import sepal_ui.sepalwidgets as sw
from sepal_ui import color
from traitlets import Any, link, observe

__all__ = ["StateIcon"]


class StateIcon(sw.Tooltip):
    """
    Custom icon with multiple state colors.

    Args:
        model (sepal_ui.Model): Model to manage StateIcon behaviour from outside.
        model_trait (str): Name of trait to be linked with state icon. Must exists in model.
        states (dict): Dictionary where keys are the state name to be linked with self value and value represented by a tuple of two elements. {"key":(tooltip_msg, color)}.
        kwargs: Any arguments from a v.Tooltip
    """

    values = Any().tag(sync=True)
    "bool, str, int: key name of the current state of component. Values must be same as states_dict keys."

    states = None
    'dict: Dictionary where keys are the state name to be linked with self value and value represented by a tuple of two elements. {"key":(tooltip_msg, color)}.'

    icon = None
    "v.Icon: the colored Icon of the tooltip"

    def __init__(self, model=None, model_trait=None, states=None, **kwargs):

        # set the default parameter of the tooltip
        kwargs["right"] = kwargs.pop("right", True)

        # init the states
        default_states = {
            "valid": ("Valid", color.success),
            "non_valid": ("Not valid", color.error),
        }
        self.states = default_states if not states else states

        # Get the first value (states first key) to use as default one
        init_value = self.states[next(iter(self.states))]

        self.icon = sw.Icon(children=["mdi-circle"], color=init_value[1], small=True)

        super().__init__(self.icon, init_value[0], **kwargs)

        # Directional from there to link here.
        if all([model, model_trait]):
            link((model, model_trait), (self, "values"))

    @observe("values")
    def _swap(self, change):
        """Swap between states"""

        new_val = change["new"]

        if not new_val:
            # Use the first value when there is not initial value.
            self.value = next(iter(self.states))
            return

        # Perform a little check with comprehensive error message
        if new_val not in self.states:
            raise ValueError(
                f"Value '{new_val}' is not a valid value. Use {list(self.states.keys())}"
            )
        self.icon.color = self.states[new_val][1]
        self.children = [self.states[new_val][0]]

        return
