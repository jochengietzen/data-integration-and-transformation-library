from ditl.models.supported_library import SupportedLibraries


class DITL:
    """
    The central state manager of the package as a singleton class
    """

    def __init__(self):
        self.library_manager = SupportedLibraries()
