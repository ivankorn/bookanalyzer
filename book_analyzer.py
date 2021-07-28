from sys import stdin,stderr,stdout
from pprint import pprint


class BookAnalyzerException(Exception):
    """Book Analyzer Exception."""

    pass


class BoookAnalyzer(object):
    """Run BookAnalyzer."""

    def __init__(self) -> None:
        """Create in memory objects."""
        super().__init__()
        self.bids = {}
        self.asks = {}

    def update_book(self):
        """Update book according to input."""
        for line in stdin:
            try:
                (action, order_id, record) = self.parse_input(line)
                if action == ("A", "B"):
                    self.bids[order_id] = record
                if action == ("A", "S"):
                    self.asks[order_id] = record
                elif action == "R":
                    raise Exception("NOT IMPLEMENTED")
                else:
                    raise Exception("ACTION: %s IS NOT SUPPORTED" % action)
            except TypeError:
                pass

    @staticmethod
    def is_int_or_float_greater_zero(obj):
        """Check if a value of evaluated object is Integer or Float and greater than zero."""
        try:
            value = eval(obj)
            obj_type = type(value)
            if (obj_type is int or obj_type is float) and value > 0:
                return True
            else:
                raise ValueError
        except (ValueError, TypeError, NameError):
            return False

    def parse_input(self, line):
        """
        Parse input and check if format is expected.

        Validate input against expected format:
        1) Add Order to Book:
        timestamp(milliseconds since midnight) action("A"), order-id(side) side("S" or "B") price(Integer or Float, greater than zero) size(Integer or Float, greater than zero)
        Example: 55784570 A yithb S 44.49 300

        2) Reduce Order
        timestamp(milliseconds since midnight) action("R") order-id(string) size(Integer or Float, greater than zero)
        Example: 55784571 R sithb 100

        Returns:
        1) Format is not expected
        False object

        2) Order is valid and is "A" action
        Tuple object: (("A", side(str( "S" | "B" )), Dictionary object)
        Dictionary object:
          {"order_id": {"price": ( int | float ) > 0,
                        "size": ( int | float ) > 0,
                        "time": ( int < 8.64e+7 && int >= 1 )}}
        3) Order is valida and is "R" action
        Tuple object: ("R", Dictionary object)
        Dictionary object:
          {"order_id": {"size": ( int | float ) > 0,
                        "time": ( int < 8.64e+7 && int >= 1 )}}
        """
        spline = line.split()
        size = spline.__len__()
        try:
            action = spline[1]
            # validate timestamp and order_id
            time = eval(spline[0])
            order_id = spline[2]
            if (type(time) is int and time < 8.64e+7 and time >= 1) and \
                type(order_id) is str and \
                    not self.is_int_or_float_greater_zero(order_id):
                pass
            else:
                raise ValueError
            # validate action, side, price and size
            # validate adding order
            if size == 6:
                # validate action, side, price and size
                side = spline[3]
                price = spline[4]
                shares = spline[5]
                if action == "A" and (side == "S" or side == "B") and \
                    self.is_int_or_float_greater_zero(price) and \
                        self.is_int_or_float_greater_zero(shares):
                    return ((action, side), order_id, {"time": time, "price": price, "size": shares})
                else:
                    raise ValueError
            # validate reducing order
            elif size == 4:
                # validate size and action
                shares = spline[3]
                if self.is_int_or_float_greater_zero(shares) and \
                        action == "R":
                    return (action, order_id, {"time": time, "size": shares})
                else:
                    raise ValueError
            else:
                raise ValueError
        except (ValueError, IndexError, SyntaxError):
            stderr.write("ERROR: Input Format is INVALID\n")
            return False

    def find_lowest(self):
        """Find."""

    def find_highest(self):
        """Find."""


def main():
    """Execute BookAnalyzer in CLI mode."""
    ba = BoookAnalyzer()
    ba.update_book()
    # ba.check_input("55784570F A yithb S 44.49") # not ok 1
    # ba.check_input("55784570 A yithb S 44.49 300") # ok
    # ba.check_input("55784570 R yithb S 44.49 300") # not ok 2
    # ba.check_input("55784570 A 1 S 44.49 300") # not ok 3
    # ba.check_input("55784570 A yithb F 44.49 300") # not ok 4
    # ba.check_input("55784570 R yithb S 44.49") # not ok 5
    # ba.check_input("55784571 A sithb 100") # not ok 6
    # ba.check_input("55784571 R sithb s") # not ok 7
    # ba.check_input("55784571 R sithb 1 1") # not ok 8
    # ba.check_input("55784571 R sithb 100") # ok

    pprint(ba.bids)
    pprint(ba.asks)
    # while True:
    #     ba.fill_book()


if __name__ == "__main__":
    main()
