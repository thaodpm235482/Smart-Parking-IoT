import time

class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 0x08
        time.sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        self.hal_write_init_nibble(0x02)
        self.hal_write_command(0x28)
        self.hal_write_command(0x0C)
        self.clear()
        self.hal_write_command(0x06)

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << 4) | self.backlight
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04, byte]))

    def hal_write_command(self, cmd):
        byte = (cmd & 0xF0) | self.backlight
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04, byte]))
        byte = ((cmd << 4) & 0xF0) | self.backlight
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04, byte]))

    def hal_write_data(self, data):
        byte = (data & 0xF0) | self.backlight | 0x01
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04, byte]))
        byte = ((data << 4) & 0xF0) | self.backlight | 0x01
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04, byte]))

    def clear(self):
        self.hal_write_command(0x01)
        time.sleep_ms(2)

    def putstr(self, string):
        for char in string:
            if char == '\n':
                self.hal_write_command(0xC0)
            else:
                self.hal_write_data(ord(char))