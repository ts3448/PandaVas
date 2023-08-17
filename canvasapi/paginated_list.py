import re
import pandas as pd


class PaginatedList(object):
    """
    Abstracts `pagination of Canvas API \
    <https://canvas.instructure.com/doc/api/file.pagination.html>`_.
    """
    def __str__(self):
        return str(self._df)

    def __getitem__(self, item):
        # If item is an integer or slice, return rows from the DataFrame
        if isinstance(item, (int, slice)):
            return self._df.iloc[item]
        # If item is a string, return the column with that name
        elif isinstance(item, str):
            if item in self._df.columns:
                return self._df[item]
            else:
                raise KeyError(f"Column '{item}' not found in the DataFrame.")
        else:
            raise TypeError("Invalid index type for PaginatedList")

    def __init__(
        self,
        content_class,
        requester,
        request_method,
        first_url,
        filters=None,
        extra_attribs=None,
        _root=None,
        _url_override=None,
        **kwargs
    ):
        self._df = pd.DataFrame()
        self._filters = filters or {}

        self._requester = requester
        self._content_class = content_class
        self._first_url = first_url
        self._first_params = kwargs or {}
        self._first_params["per_page"] = kwargs.get("per_page", 100)
        self._next_url = first_url
        self._next_params = self._first_params
        self._extra_attribs = extra_attribs or {}
        self._request_method = request_method
        self._root = _root
        self._url_override = _url_override

        # Make the initial API call to populate the DataFrame with the first page of data
        self._grow()

    def __iter__(self):
        for _, row in self._df.iterrows():
            yield row

    def __repr__(self):
        return "<PaginatedList of type {}>".format(self._content_class.__name__)

    def _get_next_page(self):
        response = self._requester.request(
            self._request_method,
            self._next_url,
            _url=self._url_override,
            **self._next_params,
        )
        data = response.json()
        self._next_url = None
        # Check the response headers first. This is the normal Canvas convention
        # for pagination, but there are endpoints which return a `meta` property
        # for pagination instead.
        # See https://github.com/ucfopen/canvasapi/discussions/605
        if response.links:
            next_link = response.links.get("next")
        elif isinstance(data, dict) and "meta" in data:
            # requests parses headers into dicts, this returns the same
            # structure so the regex will still work.
            try:
                next_link = {"url": data["meta"]["pagination"]["next"], "rel": "next"}
            except KeyError:
                next_link = None
        else:
            next_link = None

        regex = r"{}(.*)".format(re.escape(self._requester.base_url))

        self._next_url = (
            re.search(regex, next_link["url"]).group(1) if next_link else None
        )

        self._next_params = {}

        content = []

        if self._root:
            try:
                data = data[self._root]
            except KeyError:
                raise ValueError(
                    "The key <{}> does not exist in the response.".format(self._root)
                )

        for element in data:
            if element is not None:
                content.append(element)

        new_df = pd.DataFrame(content)

        # If there are extra attributes, add them as new columns
        if self._extra_attribs:
            for key, value in self._extra_attribs.items():
                new_df[key] = value

        return new_df

    def _get_up_to_index(self, index):
        while len(self._df) <= index and self._has_next():
            self._grow()

    def _grow(self):
        new_elements = self._get_next_page()
        if self._filters:
            new_elements = self.apply_filters(new_elements, self._filters)
        new_df = pd.DataFrame(new_elements)
        self._df = pd.concat([self._df, new_df], ignore_index=True)

    def _has_next(self):
        return self._next_url is not None

    def _is_larger_than(self, index):
        return len(self._df) > index or self._has_next()
    
    def apply_filters(self, items, filters):
        operators_pattern = re.compile(r'^([><≥≤!=≠<>]+)')

        # Helper function to determine if a value is numeric
        def is_numeric(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        # Helper function to handle numeric filters
        def handle_numeric_filter(item_value, filter_value):
            operator_match = operators_pattern.match(filter_value)
            operator = operator_match.group(0) if operator_match else None
            numeric_value = float(re.sub(operators_pattern, '', filter_value))

            if operator in ['>', '≥']:
                return item_value > numeric_value
            elif operator in ['<', '≤']:
                return item_value < numeric_value
            elif operator in ['!=', '≠', '<>']:
                return item_value != numeric_value
            else:
                return item_value == numeric_value

        # Helper function to handle non-numeric filters
        def handle_non_numeric_filter(item_value, filter_value):
            if filter_value.startswith(('!=', '≠', '<>')):
                excluded_value = re.sub(operators_pattern, '', filter_value)
                return item_value != excluded_value
            regex_pattern = '^' + filter_value.replace('*', '.*') + '$'
            return re.match(regex_pattern, item_value)

        # If filters is empty, return the original items
        if not filters:
            return items

        # Main filtering logic
        filtered_items = []
        for item in items:
            valid = True
            for filter_key, filter_values in filters.items():
                if filter_key not in item:
                    print(f"Item does not have a property named {filter_key}")
                    valid = False
                    break

                for filter_value in filter_values:
                    if is_numeric(re.sub(operators_pattern, '', filter_value)):
                        if not handle_numeric_filter(item[filter_key], filter_value):
                            valid = False
                            break
                    else:
                        if not handle_non_numeric_filter(item[filter_key], filter_value):
                            valid = False
                            break

            if valid:
                filtered_items.append(item)

        return filtered_items
