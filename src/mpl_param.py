class Knob:
    """
    ---- Taken from the Matplotlib gallery
    Knob - simple class with a "setKnob" method.
    A Knob instance is attached to a Param instance, e.g., param.attach(knob)
    Base class is for documentation purposes.
    """
    def set_knob(self, value):
        """Set knob is the function we want to call, whenever the value of
        a param changes. To everything you attach the param too, you must
        define a set_knob function, or it must be a subclass of Knob.

        In this case, we do nothing, but you might want to update some values
        or call a function.
        """
        pass

class Param:
    """
    ---- Taken from the Matplotlib gallery
    The idea of the "Param" class is that some parameter in the GUI may have
    several knobs that both control it and reflect the parameter's state, e.g.
    a slider, text, and dragging can all change the value of the frequency in
    the waveform of this example.
    The class allows a cleaner way to update/"feedback" to the other knobs when
    one is being changed.  Also, this class handles min/max constraints for all
    the knobs.
    Idea - knob list - in "set" method, knob object is passed as well
      - the other knobs in the knob list have a "set" method which gets
        called for the others.
    """
    def __init__(self, initial_value=None, minimum=0., maximum=1.):
        self.minimum = minimum
        self.maximum = maximum
        if initial_value != self.constrain(initial_value):
            raise ValueError('illegal initial value')
        self.value = initial_value
        self.knobs = []

    def attach(self, knob):
        self.knobs += [knob]

    def set(self, value, knob=None):
        if self.value != self.constrain(value):
            self.value = self.constrain(value)
            for feedback_knob in self.knobs:
                if feedback_knob != knob:
                    feedback_knob.set_knob(self.value)
        # Adding a new feature that allows one to loop backwards or forwards:
        elif self.maximum != self.minimum:

            if self.value == self.maximum:
                self.value = self.minimum
                for feedback_knob in self.knobs:
                    if feedback_knob != knob:
                        feedback_knob.set_knob(self.value)

            elif self.value == self.minimum:
                self.value = self.maximum
                for feedback_knob in self.knobs:
                    if feedback_knob != knob:
                        feedback_knob.set_knob(self.value)
        return self.value

    def set_max(self, max_arg, knob=None):
        self.maximum = max_arg
        self.value = self.constrain(self.value)
        for feedback_knob in self.knobs:
            if feedback_knob != knob:
                feedback_knob.set_knob(self.value)
        return self.value

    def constrain(self, value):
        if value <= self.minimum:
            value = self.minimum
        if value >= self.maximum:
            value = self.maximum
        return value
