import plib


class Path(plib.Path):
    @property
    def has_text_content(self) -> bool:
        try:
            self.text
            has_text = True
        except UnicodeDecodeError:
            has_text = False
        return has_text
