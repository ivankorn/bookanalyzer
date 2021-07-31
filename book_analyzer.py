"""Book Analyzer Module."""

from sys import stdin, stderr, stdout
from pprint import pprint
from sys import argv, exit
from copy import copy


class BoookAnalyzer():
    """The Book Analyzer."""

    def __init__(self) -> None:
        """Set attributes."""
        super().__init__()
        self.bids = {}
        self.asks = {}
        self.income = False
        self.expense = False
        self.target_size = self.get_target_size()

    @staticmethod
    def get_target_size():
        """Validate argument and return target-size."""
        try:
            if len(argv) != 2 or eval(argv[1]) <= 0:
                raise RuntimeError
        except (IndexError, RuntimeError, NameError):
            stderr.write("ARGUMENT ERROR: Script takes exactly one argument: size(int > 0).\n")
            exit(1)
        return argv[1]

    def update_book(self):
        """Update book according to input."""
        for line in stdin:
            try:
                (action, order_id, record) = self.parse_input(line)
                if action == ("A", "B"):
                    self.bids[order_id] = record
                    self.income = self.process_bids(copy(self.bids), self.target_size, record["time"])
                if action == ("A", "S"):
                    self.asks[order_id] = record
                    self.expense = self.process_asks(copy(self.asks), self.target_size, record["time"])
                elif action == "R":
                    self.reduce_record(record["size"], order_id)
                    if self.income and self.income != "NA":
                        income = self.process_bids(copy(self.bids), self.target_size, record["time"])
                        if not income:
                            self.income = "NA"
                            stdout.write("%s B NA\n" % record["time"])
                    if self.expense and self.expense != "NA":
                        expense = self.process_asks(copy(self.asks), self.target_size, record["time"])
                        if not expense:
                            self.expense = "NA"
                            stdout.write("%s S NA\n" % record["time"])
                else:
                    stderr.write("INPUT ERROR: Action %s is not supported\n" % action)
            except TypeError:
                pass

    def reduce_record(self, size, order_id):
        """Reduce Bid or Ask size."""
        def _reduce(book, size, order_id):
            new_size = eval(book[order_id]["size"]) - eval(size)
            if new_size > 0:
                book[order_id]["size"] = str(new_size)
            elif new_size == 0:
                del book[order_id]
            elif new_size < 0:
                stderr.write("REDUCE ERROR: Can't reduce order {id} with size {cur_size} by {req_size} as resulting value would be below 0.\n".format(id=order_id, cur_size=book[order_id]["size"], req_size=size))
            return book
        if order_id in self.bids.keys():
            self.bids = _reduce(self.bids, size, order_id)
        elif order_id in self.asks.keys():
            self.asks = _reduce(self.asks, size, order_id)
        else:
            stderr.write("REDUCE ERROR: ID %s is not found.\n" % order_id)

    @staticmethod
    def is_book_size_ok(book, target_size):
        """Check if total size of the bids/asks meet target-size."""
        size = 0
        target_size = eval(target_size)
        for order_id in book:
            size += eval(book[order_id]["size"])
            if size >= target_size:
                return True
        return False

    def process_bids(self, book, target_size, time):
        """Process bid according to requested logic."""
        income = 0
        if self.is_book_size_ok(book, target_size):
            target_size = eval(target_size)
            while True:
                if target_size != 0:
                    highest = self.find_highest_bid(book)
                    if target_size >= eval(book[highest]["size"]):
                        target_size -= eval(book[highest]["size"])
                        income += eval(book[highest]["price"])*eval(book[highest]["size"])
                        del book[highest]
                    else:
                        remaining = eval(book[highest]["size"]) - target_size
                        # Update record with new size
                        book[highest]["size"] = str(remaining)
                        income += eval(book[highest]["price"])*target_size
                        break
                else:
                    break
            if income > 0:
                stdout.write("{time} S {income}\n".format(time=time, income=income))
        return income

    def process_asks(self, book, target_size, time):
        """Process ask according to requested logic."""
        expense = 0
        if self.is_book_size_ok(book, target_size):
            target_size = eval(target_size)
            while True:
                if target_size != 0:
                    lowest = self.find_lowest_ask(book)
                    if target_size >= eval(book[lowest]["size"]):
                        target_size -= eval(book[lowest]["size"])
                        expense += eval(book[lowest]["price"])*eval(book[lowest]["size"])
                        del book[lowest]
                    else:
                        remaining = eval(book[lowest]["size"]) - target_size
                        # Update record with new size
                        book[lowest]["size"] = str(remaining)
                        expense += eval(book[lowest]["price"])*target_size
                        break
                else:
                    break
            if expense > 0:
                stdout.write("{time} B {expense}\n".format(time=time, expense=expense))
        return expense

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
        size = len(spline)
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
            stderr.write("INPUT ERROR: Input format is invalid.\n")
            return False

    @staticmethod
    def find_lowest_ask(book):
        """Find the lowest bid in the Book."""
        lowest = False
        id = None
        for order_id in book.keys():
            price = eval(book[order_id]["price"])
            if lowest:
                if lowest > price:
                    lowest = price
                    id = order_id
            else:
                lowest = price
                id = order_id
        return id

    @staticmethod
    def find_highest_bid(book):
        """Find the highest bid in the Book."""
        highest = False
        id = None
        if book:
            for order_id in book.keys():
                price = eval(book[order_id]["price"])
                if highest:
                    if highest < price:
                        highest = price
                        id = order_id
                else:
                    highest = price
                    id = order_id
        return id


def main():
    """Execute BookAnalyzer in CLI mode."""
    ba = BoookAnalyzer()
    ba.update_book()
    print("Bids:")
    pprint(ba.bids)
    print("\n\n")
    print("Asks:")
    pprint(ba.asks)


if __name__ == "__main__":
    main()
