from random import randint

str_answer = input("Welcome in number guessing game!\nDo you want to play? y/n ")


def play():
    print("You cant quit the game anytime you want, just enter q")
    str_ans = "y"

    while str_ans == "y":
        print("I remembered a number from 0 to 100. Try to guess it!")

        number_to_guess = randint(0, 100)
        int_attempt = 0
        suggested_number = None

        while suggested_number != number_to_guess:
            suggested_number = input("Your suggested number: ")

            if suggested_number == "q" or " ":
                break
            elif int(suggested_number) == number_to_guess:
                print("You guessed the number!")
                print("Total attempts: ", int_attempt + 1)
                break
            else:
                if int(suggested_number) < number_to_guess:
                    print("The number I remembered is bigger")
                else:
                    print("The number I remembered is smaller")
                int_attempt += 1

        if suggested_number == "q" or " ":
            print("Game was stopped!\n")
            break
        else:
            str_ans = input("Do you want to play one more time? y/n ")


if str_answer == "y":
    play()
elif str_answer == "n":
    print("Game over!")
else:
    print("Incorrect input!")
