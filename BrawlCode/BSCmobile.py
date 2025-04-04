import sys

class LongToCodeConverter:
    CONVERSION_CHARS = "0289PYLQGRJCUV"
    HASH_TAG = "#"
    TEAM_CONVERSION_CHARS = "QWERTYUPASDFGHJKLZCVBNM23456789"
    TEAM_TAG = "X"
    
    def __init__(self, is_team_converter=False):
        self.conversion_chars = self.TEAM_CONVERSION_CHARS if is_team_converter else self.CONVERSION_CHARS
        self.code_suffix = self.TEAM_TAG if is_team_converter else self.HASH_TAG

    def to_code(self, high_int, low_int):
        if high_int < 256:
            l = self.to_long(low_int >> 24, high_int | (low_int << 8))
            res = self.convert(l)
            return self.code_suffix + res
        else:
            print("Higher int value too large", file=sys.stderr)
            return None

    def generate_neighbor_codes(self, code, count):
        base_id = self.to_id(code)
        if base_id == -1:
            return

        print("\nPrevious codes:")
        for i in range(base_id - count, base_id):
            if i >= 0:
                parts = self.extract_high_low(i)
                gen_code = self.to_code(parts[0], parts[1])
                if gen_code:
                    print(gen_code)

        print("\nThe following codes:")
        for i in range(base_id + 1, base_id + count + 1):
            parts = self.extract_high_low(i)
            gen_code = self.to_code(parts[0], parts[1])
            if gen_code:
                print(gen_code)

    def extract_high_low(self, value):
        low = value & 0xFFFFFFFF
        high = value >> 32
        return [high, low]

    def convert(self, id):
        tag = []
        length = len(self.conversion_chars)
        while id > 0:
            char_index = id % length
            tag.insert(0, self.conversion_chars[char_index])
            id //= length
        return ''.join(tag)

    def to_id(self, code):
        if not code.startswith(self.code_suffix):
            print(f"Invalid prefix. Expected: {self.code_suffix}", file=sys.stderr)
            return -1

        if len(code) < 14:
            code_substring = code[1:]

            if not code_substring:
                v13 = 0
                lo_int = int(v13 & 0x7FFFFFFF)
                hi_int = 0
            else:
                unk6 = 0
                unk7 = 0

                for i in range(len(code_substring)):
                    sub_str = code_substring[i]
                    sub_str_idx = self.conversion_chars.find(sub_str)
                    if sub_str_idx == -1:
                        print("Invalid character in code", file=sys.stderr)
                        return -1

                    unk12 = unk6 * len(self.conversion_chars) + sub_str_idx
                    unk7 = (self.to_long_s(unk7, unk6) * len(self.conversion_chars) + sub_str_idx) >> 32
                    unk6 = unk12

                if (unk12 & unk7) != -1:
                    v13 = self.to_long_s(unk7, unk12) >> 8
                    lo_int = int(v13 & 0x7FFFFFFF)
                    hi_int = unk6 & 0xFF
                    return self.to_long(hi_int, lo_int)
                hi_int = -1
                lo_int = -1
            return self.to_long(hi_int, lo_int)
        else:
            print("Code too long", file=sys.stderr)
            return -1

    def to_long(self, hi_int, lo_int):
        return (hi_int << 32) | (lo_int & 0xFFFFFFFF)

    def to_long_s(self, hi_int, lo_int):
        return (hi_int << 32) | lo_int

    def interactive_console(self):
        print("Variant:")
        print("1 - Code in ID")
        print("2 - ID in code")
        print("3 - neighboring codes")
        mode = input("Choose: ")

        if mode == "1":
            code = input("Enter code: ")
            id = self.to_id(code)
            if id != -1:
                print(f"ID: {id}")
        elif mode == "2":
            id = int(input("Enter ID: "))
            parts = self.extract_high_low(id)
            code = self.to_code(parts[0], parts[1])
            if code:
                print(f"Код: {code}")
        elif mode == "3":
            code = input("Enter code: ")
            self.generate_neighbor_codes(code, 10)
        else:
            print("incorrect variant", file=sys.stderr)

if __name__ == "__main__":
    converter = LongToCodeConverter(is_team_converter=True)
    converter.interactive_console()
