import pandas as pd


class CanvasObject(object):
    """
    Base class for all classes representing objects returned by the API.

    This makes a call to :func:`canvasapi.canvas_object.CanvasObject.set_attributes`
    to dynamically construct this object's attributes with a JSON object.
    """

    def __getattr__(self, name):
        # Check if attribute exists in the main dataframe
        if name in self.dataframe.columns:
            return self.dataframe[name].iloc[0]

        # If attribute doesn't exist, raise an AttributeError
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __init__(self, requester, attributes, context=None):
        """
        :param requester: The requester to pass HTTP requests through.
        :type requester: :class:`canvasapi.requester.Requester`
        :param attributes: The JSON object to build this object with.
        :type attributes: dict
        """
        self._requester = requester
        self._context = context

        self.set_attributes(attributes)

    def __repr__(self):  # pragma: no cover
        classname = self.__class__.__name__

        # Extracting column names from the DataFrame
        attrs = ", ".join(self.dataframe.columns)

        return "{}({})".format(classname, attrs)

    def set_attributes(self, attributes):
        """
        Load this object with attributes as a DataFrame.

        :param attributes: The JSON object to build this object with.
        :type attributes: dict
        """
        self.dataframe = pd.DataFrame([attributes])

        # Convert specific columns to datetime format
        date_columns = ["start_at", "end_at"]
        for col in date_columns:
            if col in self.dataframe.columns:
                self.dataframe[col] = pd.to_datetime(self.dataframe[col])

    def get_context(self, return_type):
        """
        Retrieve the context based on the return_type.
        """
        if return_type == type(self).__name__:
            return self
        elif self._context:
            return self._context.get_context(return_type)
        else:
            raise ValueError(f"Context of type '{return_type}' not found in the method chain.")
