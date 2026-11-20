"""
Group 6: Phenolphthalein Indicator Module
Filename: group6.py

Description:
Models the colour response of phenolphthalein indicator to solution pH.
- Below pH 8.2: Colourless (acidic/neutral state)
- pH 8.2 to 10.0: Transition region (faint pink to pink at the endpoint)
- Above pH 10.0: Pink / Magenta (strongly basic state)
"""


class PhenolphthaleinIndicator:
    """
    Represents the phenolphthalein indicator in the acid-base titration.
    Standard transition range: pH 8.2 to 10.0.
    """

    def __init__(self, low_ph: float = 8.2, high_ph: float = 10.0):
        self.low_ph = low_ph
        self.high_ph = high_ph

    def get_color(self, ph: float) -> str:
        """
        Determines the visual appearance/colour of the solution containing
        phenolphthalein based on the current pH.
        """
        if ph < self.low_ph:
            return "Colourless"
        elif self.low_ph <= ph <= self.high_ph:
            return "Faint Pink (Transition Region / Endpoint)"
        else:
            return "Pink / Magenta"

    def is_endpoint_reached(self, ph: float) -> bool:
        """
        Detects if the virtual endpoint has been reached
        (marked by the first persistent faint pink colour at pH >= 8.2).
        """
        return ph >= self.low_ph


def test_indicator():
    """
    Independent test cases for Group 6 component as per general instructions.
    """
    indicator = PhenolphthaleinIndicator()

    test_cases = [
        (1.0, "Colourless"),
        (7.0, "Colourless"),
        (8.1, "Colourless"),
        (8.5, "Faint Pink (Transition Region / Endpoint)"),
        (9.0, "Faint Pink (Transition Region / Endpoint)"),
        (10.5, "Pink / Magenta"),
    ]

    print("=" * 60)
    print("GROUP 6: Phenolphthalein Indicator - Test Output")
    print("=" * 60)
    for ph, expected in test_cases:
        color = indicator.get_color(ph)
        passed = expected in color
        status = "PASS" if passed else "FAIL"
        print(f"pH: {ph:4.1f} | Result: {color:<42} | Status: {status}")
    print("=" * 60)


if __name__ == "__main__":
    test_indicator()
