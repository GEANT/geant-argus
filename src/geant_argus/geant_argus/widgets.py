from django.forms import widgets


class FancyWidget(widgets.Widget):
    input_class = ""
    label_class = ""
    wrapper_class = ""

    def __init__(self, attrs=None):
        if attrs is not None:
            self.input_class = attrs.pop("input_class", self.input_class)
            self.label_class = attrs.pop("label_class", self.label_class)
            self.wrapper_class = attrs.pop("wrapper_class", self.wrapper_class)
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["input_class"] = self.input_class
        context["widget"]["label_class"] = self.label_class
        context["widget"]["wrapper_class"] = self.wrapper_class
        return context


class FancyChoiceWidget(FancyWidget, widgets.ChoiceWidget):
    def create_option(self, name, value, label, selected, index, subindex, attrs):
        return {
            **super().create_option(name, value, label, selected, index, subindex, attrs),
            "input_class": self.input_class,
        }


class FancyInput(FancyWidget, widgets.Input):
    template_name = "forms/_input.html"


class DaisyTextInput(FancyInput):
    input_type = "text"
    input_class = "input input-accent input-bordered border"
    label_class = "label text-xs"


class DaisySelect(FancyWidget, widgets.Select):
    template_name = "forms/_select.html"

    input_type = "select"
    input_class = "select select-accent border"
    label_class = "label text-xs"

    def __init__(self, attrs=None):
        widgets.Select.__init__(self, attrs)
        FancyInput.__init__(self, attrs)


class DaisyCheckboxInput(FancyInput, widgets.CheckboxInput):
    input_type = "checkbox"
    input_class = "checkbox checkbox-accent border"
    label_class = "label"
    wrapper_class = "flex flex-row items-center gap-2"


class DaisyCheckboxSelectMultiple(FancyChoiceWidget, widgets.CheckboxSelectMultiple):
    template_name = "forms/_multiple_select_checkbox.html"
    input_class = "checkbox checkbox-xs checkbox-primary"
    label_class = "label"
    use_fieldset = False
    wrapper_class = "flex flex-row gap-2 items-center"
