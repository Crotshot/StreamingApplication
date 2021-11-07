import stream

streamScript = stream


def inputOption(text, successList):
    choice = input(text)
    if choice in successList:
        return True
    else:
        return False


def inputs():
    if inputOption("Are you joining or hosting a stream (j/h)? ", ['h', 'H']):
        if inputOption("Would you like to stream your webcam or screen (w/s)? ", ['w', 'W']):
            choice = input("Which webcam would you like to use (0 for primary, 1 for secondary etc etc)? ")
            streamScript.webcamNumber = int(choice)
            streamScript.source = "Webcam"
        else:
            print("Showing screen")
    else:
        return

if __name__ == '__main__':
    inputs()
    streamScript.app.run(debug=True)
