from sys import stdin,stderr,stdout
from pprint import pprint
from sys import argv

class BoookAnalyzer(object):
    """The Book Analyzer."""

    def __init__(self) -> None:
        """Set attributes."""
        super().__init__()
        self.bids = {}
        self.asks = {}
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
                    income = self.process_bids()
                    if income:
                        stdout.write("{time} S {income}".format(time=record["time"], income=income))
                if action == ("A", "S"):
                    self.asks[order_id] = record
                    expense = self.process_asks()
                    if expense:
                        stdout.write("{time} B {expense}".format(time=record["time"], expense=expense))
                elif action == "R":
                    self.reduce_record(record["size"], order_id)
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
            # new_size = eval(self.bids[order_id]["size"]) - eval(size)
            # if new_size > 0:
            #     self.bids[order_id]["size"] = str(new_size)
            # elif new_size == 0:
            #     del self.bids[order_id]
            # elif new_size < 0:
            #     stderr.write("REDUCE ERROR: Can't reduce order {id} with size {cur_size} by {req_size} as resulting value would be below 0.\n".format(id=order_id, cur_size=self.bids[order_id]["size"], req_size=record["size"]))
        elif order_id in self.asks.keys():
            self.asks = _reduce(self.asks, size, order_id)
        else:
            stderr.write("REDUCE ERROR: ID %s is not found.\n" % order_id)

    # def is_book_size_ok(self):
    #     """Check if bids and asks meet target-size."""
    #     def _check_size(book, target_size):
    #         size = 0
    #         for order_id in book:
    #             size += eval(book[order_id]["size"])
    #             if size >= target_size:
    #                 return True
    #         return False
    #     bids_ok = _check_size(self.bids, self.target_size)
    #     asks_ok = _check_size(self.asks, self.target_size)
    #     if bids_ok or asks_ok:
    #         return True
    #     else:
    #         return False

    @staticmethod
    def is_book_size_ok(book, target_size):
        """Check if total size of the bids/asks meet target-size."""
        size = 0
        for order_id in book:
            size += eval(book[order_id]["size"])
            if size >= target_size:
                return True
        return False

    def process_bids(self):
        """Process bid according to requested logic."""
        if self.is_book_size_ok(self.bids, self.target_size):
            target_size = eval(self.target_size)
            income = 0
            while True:
                if target_size != 0:
                    highest = self.find_highest_bid(self.bids)
                    if target_size >= eval(self.book[highest]["size"]):
                        target_size -= eval(self.book[highest]["size"])
                        income += eval(self.book[highest]["price"])*eval(self.book[highest]["size"])
                        del self.book[highest]
                    else:
                        remaining = eval(self.book[highest]["size"]) - target_size
                        # Update record with new size
                        self.book[highest]["size"] = str(remaining)
                        income += eval(self.book[highest]["price"])*target_size
                        break
                else:
                    break
            return income
        else:
            return False

    def process_asks(self):
        """Process ask according to requested logic."""
        if self.is_book_size_ok(self.asks, self.target_size):
            target_size = eval(self.target_size)
            expense = 0
            while True:
                if target_size != 0:
                    lowest = self.find_lowest_ask(self.asks)
                    if target_size >= eval(self.book[lowest]["size"]):
                        target_size -= eval(self.book[lowest]["size"])
                        expense += eval(self.book[lowest]["price"])*eval(self.book[lowest]["size"])
                        del self.book[lowest]
                    else:
                        remaining = eval(self.book[lowest]["size"]) - target_size
                        # Update record with new size
                        self.book[lowest]["size"] = str(remaining)
                        expense += eval(self.book[lowest]["price"])*target_size
                        break
                else:
                    break
            return expense
        else:
            return False

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
            if lowest:
                price = eval(book[order_id]["price"])
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
                if highest:
                    price = eval(book[order_id]["price"])
                    if highest < price:
                        highest = price
                        id = order_id
                else:
                    highest = price
                    id = order_id
        return id

    # @staticmethod
    # def find_highest_bid(book):
    #     """Find the highest ask in the Book."""
    #     highest = {}
    #     for order_id in book.keys():
    #         if highest:
    #             price = eval(book[order_id]["price"])
    #             if highest[order_id] < price:
    #                 highest = {order_id: price}
    #         else:
    #             highest = {order_id: price}
    #     return highest


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
    print("Bids:")
    pprint(ba.bids)
    print("\n\n")
    print("Asks:")
    pprint(ba.asks)
    # while True:
    #     ba.fill_book()


if __name__ == "__main__":
    main()
