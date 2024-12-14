from bypy import BarTender

bt = BarTender()  # Connect to Bartender
bt.open('C:/YourDirectory/YourLabel.btw')  # Open your label file
bt.set_named_sub_string('YourField', 'YourData')  # Set data in a field on your label
bt.print_out(1, 'YourPrinter')  # Print 1 label on YourPrinter
bt.quit()  # Close Bartender
