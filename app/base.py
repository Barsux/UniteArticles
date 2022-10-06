class SQL_Divider:
    @classmethod
    def add_element(cls, elements: str, element: str) -> str:
        if not elements:
            elements = [element,]
        else:
            if element in elements:
                return elements
            elements = list(elements.strip().split(';'))
            elements.append(element)
        return ';'.join(sorted(elements))

    @classmethod
    def remove_element(cls, elements: str, element: str) -> str:
        if not elements or elements and element not in elements:
            return elements
        elements = list(elements.strip().split(';'))
        elements.remove(element)
        return ';'.join(sorted(elements))

    @classmethod
    def check_is_inside(cls, elements: str, element: str) -> bool:
        if len(elements) == 0:
            return False
        elements = list(elements.strip().split(';'))
        return element in elements

    @classmethod
    def check_intersection(cls, elements: str, elements_to_check: tuple) -> bool:
        if len(elements) == 0:
            return False
        elements = set(elements.strip().split(';'))
        elements_to_check = set(elements_to_check)
        return bool(len(elements & elements_to_check))