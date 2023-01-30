"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Homework 1 Text Processing
Henry Kim HTK180000
Due: Feb. 4, 2023

This program reads in an employee file specified by the user as a sysarg and corrects prompts the user to correct
formatting issues. The employee information is also saved as a pickle file.
"""

import sys
import pickle
import re

class Person:
    """This class has fields to represent a person and method to display them"""
    def __init__(self, last, first, mi, p_id, phone):
        """Initialize the employee object with a last name, first name, middle initial, id, and phone number"""
        self.last = last
        self.first = first
        self.mi = mi
        self.p_id = p_id
        self.phone = phone

    def display(self):
        """Prints information about the employee"""
        print("Employee ID:", self.p_id)
        print("\t", self.first, self.mi, self.last)
        print("\t", self.phone)


def validate_middle_initial(val):
    """
    Validates the middle initial and makes sure it's an uppercase letter
    :arg:
        val: The middle initial to validate
    :return: string
        The middle initial
    """
    if not val:
        # Return X if no initial
        return 'X'
    elif re.fullmatch('[a-zA-Z]', val):
        # Return the letter in uppercase
        return val[0].upper()
    else:
        # Prompt for correction and recurse until input is correct
        print('Middle initial', val, 'is invalid')
        new_val = input('Enter middle initial that is one letter: ')
        return validate_middle_initial(new_val)


def validate_id(val, id_list):
    """
    Validates the ID and makes sure it's two uppercase letters followed by four digits and not already in use
    :arg:
        val: The ID to validate
        id_list: List of IDs already in use
    :return: string
        The ID
    """
    # Use regex to check if ID is two letters and four digits
    if re.fullmatch('[a-zA-Z]{2}[0-9]{4}', val):
        # Format ID to make letters uppercase
        formatted_val = val[0:2].upper() + val[2:]

        # Make sure ID is not already used
        if formatted_val in id_list:
            # Recursively prompt for new ID
            print('ID', formatted_val, 'is already in use')
            new_val = input('Please enter a new ID that is two letters followed by four digits: ')
            return validate_id(new_val, id_list)
        else:
            return formatted_val
    else:
        # Prompt for correction and recurse until input is correct
        print('ID', val, 'is invalid')
        new_val = input('Please enter a valid ID that is two letters followed by four digits: ')
        return validate_id(new_val, id_list)


def validate_phone(val):
    """
    Validates the phone number and makes sure it's in the form 123-456-7890
    :arg:
        val: The phone number to validate
    :return: string
        The phone number
    """
    val = re.sub('\s', '', val) # Remove white space
    # Check for 10 digits that can have a period, comma, or dash between them
    if re.fullmatch('([\.,-]*[0-9][\.,-]*){10}', val):
        # Reformat the phone number
        digits = re.findall('[0-9]', val)
        formatted_val = digits[0] + digits[1] + digits[2] + '-' +\
                        digits[3] + digits[4] + digits[5 ] + '-' +\
                        digits[6] + digits[7] + digits[8] + digits[9]
        return formatted_val
    else:
        # Prompt for correction and recurse until input is correct
        print('Phone', val, 'is invalid')
        new_val = input('Please enter phone number in form 123-456-7890: ')
        return validate_phone(new_val)


def process_input_file(filepath):
    """
    Processes the employee data file and asks for corrections on incorrect formatting
    :arg:
        filepath: a path to the file to open
    :return: dictionary
        A dictionary of Person objects with p_id as the key
    """
    # Initialize dictionary to return
    people_dict = {}

    # Open file for reading
    file = open(filepath, 'r')

    # Skip the first line with the headers
    file.readline()

    # Process the remaining lines
    for line in file:
        # Read the entries as written from file
        # fields = [Last,First,Middle Initial,ID,Office phone]
        fields = line.split(',')

        # Use title case for names
        last_name = fields[0].title()
        first_name = fields[1].title()
        # Validate and correct the other fields
        middle_initial = validate_middle_initial(fields[2])
        employee_id = validate_id(fields[3], people_dict.keys())
        phone_number = validate_phone(fields[4])

        # Add person to dictionary
        new_person = Person(last_name, first_name, middle_initial, employee_id, phone_number)
        people_dict[new_person.p_id] = new_person

    # Close file
    file.close()

    # Return the dictionary
    return people_dict


# Main execution
if __name__ == '__main__':
    # Read filepath from sysarg
    if len(sys.argv) < 2:
        # Error if no filepath given
        print('Error: Please enter a filepath as a system arg')
    else:
        # Process the file
        employees_dict = process_input_file(sys.argv[1])

        # Save the pickle file of employee dict
        pickle.dump(employees_dict, open('save.p', 'wb'))

        # Read the pickle file back in
        read_dict = pickle.load(open('save.p', 'rb'))

        # Output the employee list
        print()
        print('Employee list:')
        for person in read_dict.values():
            person.display()
            print()
